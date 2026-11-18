"""MRV MCC CLI emulator, seeded from the tables captured in mrv/cli/simulator/data.

No networking here: handle(line) returns what the device prints before the next
prompt. Runs under py3 only, as a separate process from the drivers under test.
"""

from __future__ import annotations

import copy
import csv
import io
import os
import re

DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "mrv", "cli", "simulator", "data"
)
HOSTNAME = "fiberdriver"
UNKNOWN = "% Unknown command."


def _read(name: str) -> str:
    with open(os.path.join(DATA_DIR, name), newline="") as f:
        return f.read()


class MrvDevice:
    def __init__(
        self,
        password: str = "admin",
        config_password: bool = False,
        legacy_address: bool = False,
    ):
        """legacy_address: reject dotted port ids (1.2.3) and accept 1203 instead."""
        self.password = password
        self.config_password = config_password
        self.legacy_address = legacy_address
        self.mode = "default"  # default | config | chassis/N | port/X.Y.Z
        self.pending_password = False
        self.login_stage = None  # telnet: "username" -> "password" -> None

        version = _read("show_version.txt").replace("\r\n", "\n")
        self.version = version.split(HOSTNAME + "#")[0].rstrip("\n")
        self.chassis = self._load("show_table_chassis_dump.txt")
        self.slots = self._load("show_table_slot_dump.txt")
        self.ports = self._load("show_table_port_dump.txt")
        self.protocols = self._load("show_table_protocol_dump.txt")

    def new_session(self) -> MrvDevice:
        """CLI session: own mode, shared (mutated in place) device tables."""
        session = copy.copy(self)
        session.mode = "default"
        session.pending_password = False
        session.login_stage = None
        return session

    @staticmethod
    def _load(name: str) -> tuple[list[str], list[list[str]], bool]:
        text = _read(name).replace("\r\n", "\n")
        trailing_comma = text.splitlines()[0].endswith(",")
        rows = [r for r in csv.reader(io.StringIO(text)) if r]
        if trailing_comma:
            rows = [r[:-1] if r and r[-1] == "" else r for r in rows]
        return rows[0], rows[1:], trailing_comma

    @staticmethod
    def _dump(table) -> str:
        header, rows, trailing_comma = table
        end = "," if trailing_comma else ""
        lines = [",".join(f'"{v}"' for v in r) + end for r in [header] + rows]
        return "\n".join(lines)

    # ---- prompt / state ----
    @property
    def secret_input(self) -> bool:
        return self.pending_password or self.login_stage == "password"

    @property
    def prompt(self) -> str:
        if self.login_stage == "username":
            return "Username: "
        if self.login_stage == "password":
            return "Password: "
        if self.pending_password:
            return "Password: "
        if self.mode == "default":
            return f"{HOSTNAME}# "
        return f"{HOSTNAME}({self.mode})# "

    def _port_row(self, port_id: str) -> list[str] | None:
        if self.legacy_address:
            m = re.fullmatch(r"(\d)(\d)(\d\d)", port_id)
            if not m:
                return None
            key = (m.group(1), m.group(2), str(int(m.group(3))))
        else:
            parts = port_id.split(".")
            if len(parts) != 3:
                return None
            key = tuple(parts)
        header, rows, _ = self.ports
        ci, si, pi = (header.index(c) for c in ("ChassisIndex", "SlotIndex", "Index"))
        for r in rows:
            if (r[ci], r[si], r[pi]) == key:
                return r
        return None

    def _set_zone(self, row: list[str], target: list[str] | None) -> None:
        header = self.ports[0]
        if target is None:
            values = ("1", "0", "0")
        else:
            values = tuple(
                target[header.index(c)] for c in ("ChassisIndex", "SlotIndex", "Index")
            )
        for prefix in ("Oper", "Admin"):
            for col, val in zip(("ZoneChassis", "ZoneSlot", "ZoneId"), values):
                row[header.index(col + prefix)] = val

    def _zone_of(self, row: list[str]) -> tuple[str, str, str]:
        header = self.ports[0]
        return tuple(
            row[header.index(c)]
            for c in ("ZoneChassisOper", "ZoneSlotOper", "ZoneIdOper")
        )

    def _id_of(self, row: list[str]) -> tuple[str, str, str]:
        header = self.ports[0]
        return tuple(
            row[header.index(c)] for c in ("ChassisIndex", "SlotIndex", "Index")
        )

    # ---- command handling ----
    def handle(self, line: str) -> str:
        if self.login_stage == "username":
            self.login_stage = "password"
            return ""
        if self.login_stage == "password":
            self.login_stage = None if line == self.password else "username"
            return "" if self.login_stage is None else "Login incorrect"
        if self.pending_password:
            self.pending_password = False
            if line == self.password:
                self.mode = "config"
                return ""
            return "Error: wrong password"

        cmd = line.strip()
        if not cmd:
            return ""
        if cmd == "exit":
            if self.mode == "default":
                return ""
            self.mode = "default" if self.mode == "config" else "config"
            return ""
        if cmd == "terminal length 0":
            return ""
        if cmd == "show version":
            return self.version
        m = re.fullmatch(r"show table (chassis|slot|port|protocol) dump", cmd)
        if m:
            table = {
                "chassis": self.chassis,
                "slot": self.slots,
                "port": self.ports,
                "protocol": self.protocols,
            }[m.group(1)]
            return self._dump(table)
        if cmd == "configure terminal" and self.mode == "default":
            if self.config_password:
                self.pending_password = True
            else:
                self.mode = "config"
            return ""
        if self.mode == "config":
            return self._handle_config(cmd)
        if self.mode.startswith("chassis/"):
            return self._handle_chassis(cmd)
        if self.mode.startswith("port/"):
            return self._handle_port(cmd)
        return UNKNOWN

    def _handle_config(self, cmd: str) -> str:
        m = re.fullmatch(r"chassis (\d+)", cmd)
        if m:
            self.mode = f"chassis/{m.group(1)}"
            return ""
        m = re.fullmatch(r"port (\d+\.\d+\.\d+)", cmd)
        if m:
            if not self._port_row(m.group(1)) and not self.legacy_address:
                return f"Error: port {m.group(1)} does not exist"
            self.mode = f"port/{m.group(1)}"
            return ""
        m = re.fullmatch(
            r"map (?:(bidir) (\S+) (\S+)|(\S+) (also-to|not-to) (\S+)|(\S+) clear-all)",
            cmd,
        )
        if not m:
            if cmd.startswith("map"):
                return "% Command incomplete."
            return UNKNOWN
        if m.group(1):
            a, b = self._port_row(m.group(2)), self._port_row(m.group(3))
            if a is None or b is None:
                return "Error: invalid port"
            self._set_zone(a, b)
            self._set_zone(b, a)
            return ""
        if m.group(5):
            a, b = self._port_row(m.group(4)), self._port_row(m.group(6))
            if a is None or b is None:
                return "Error: invalid port"
            if m.group(5) == "also-to":
                self._set_zone(b, a)
            elif self._zone_of(b) == self._id_of(a):
                self._set_zone(b, None)
            return ""
        a = self._port_row(m.group(7))
        if a is None:
            return "Error: invalid port"
        a_id = self._id_of(a)
        for row in self.ports[1]:
            if self._zone_of(row) == a_id:
                self._set_zone(row, None)
        self._set_zone(a, None)
        return ""

    def _handle_chassis(self, cmd: str) -> str:
        m = re.fullmatch(r"description (.+)", cmd)
        if m:
            header, rows, _ = self.chassis
            rows[0][header.index("Name")] = m.group(1)
            return ""
        return UNKNOWN

    def _handle_port(self, cmd: str) -> str:
        header = self.ports[0]
        row = self._port_row(self.mode.split("/", 1)[1])
        if row is None:
            return UNKNOWN
        m = re.fullmatch(r"duplex (half|full)", cmd)
        if m:
            row[header.index("Duplex")] = m.group(1)
            return ""
        if cmd in ("auto-negotiation", "no auto-negotiation"):
            row[header.index("AutoNegotiation")] = (
                "off" if cmd.startswith("no") else "on"
            )
            return ""
        return UNKNOWN
