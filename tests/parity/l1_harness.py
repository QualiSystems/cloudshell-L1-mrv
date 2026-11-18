"""Run one driver build against the MRV emulator, the way CloudShell drives it.

Starts the emulator and the driver (main.py under any interpreter, so the py2.7
master driver can be the baseline), sends L1 XML commands over TCP, and returns
normalized responses plus the exact command stream the switch received.
"""

from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from xml.etree import ElementTree

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REQUEST_NS = "http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd"
DRIVER_FILES = ("main.py", "mrv", "mrv_runtime_config.yml")


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _wait_port(port: int, proc: subprocess.Popen, timeout: float = 30) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"process exited early: {proc.returncode}")
        try:
            socket.create_connection(("127.0.0.1", port), 0.5).close()
            return
        except OSError:
            time.sleep(0.2)
    raise TimeoutError(f"port {port} not listening")


def _command_xml(name: str, params: list[tuple[str, str]]) -> str:
    body = "".join(f"<{k}>{v}</{k}>" for k, v in params)
    return (
        f'<Commands xmlns="{REQUEST_NS}">'
        f'<Command CommandName="{name}" CommandId="{uuid.uuid4()}">'
        f"<Parameters>{body}</Parameters></Command></Commands>"
    )


def _canon(node: ElementTree.Element):
    """Order-insensitive, namespace-free view of an XML node."""
    tag = re.sub(r"{.*}", "", node.tag)
    children = sorted((_canon(c) for c in node), key=repr)
    text = (node.text or "").strip()
    return (tag, tuple(sorted(node.attrib.items())), text, tuple(children))


def normalize_response(raw: str) -> dict:
    root = ElementTree.fromstring(raw)
    resp = next((n for n in root if n.tag.endswith("CommandResponse")), None)
    if resp is None:
        # top-level error envelope (unparseable request / driver crash)
        return {"envelope": _canon(root)}
    out = {"success": resp.get("Success")}
    for child in resp:
        tag = re.sub(r"{.*}", "", child.tag)
        if tag == "Timestamp":
            continue
        if tag in ("Error", "Log"):
            out[tag] = (child.text or "").strip()
        else:
            out[tag] = _canon(child)
    return out


class Run:
    def __init__(self, python: str, driver_src: str, emulator_args=(), workdir=None):
        self.python = python
        self.driver_src = driver_src
        self.emulator_args = list(emulator_args)
        self.workdir = workdir or tempfile.mkdtemp(prefix="mrv-parity-")
        self._procs: list[subprocess.Popen] = []

    def __enter__(self):
        self.emu_port, self.drv_port = free_port(), free_port()
        self.transcript = os.path.join(self.workdir, "switch_transcript.txt")
        emu = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "tests.emulator.ssh_server",
                "--port",
                str(self.emu_port),
                "--transcript",
                self.transcript,
                *self.emulator_args,
            ],
            cwd=REPO,
            stdout=subprocess.PIPE,
            stderr=open(os.path.join(self.workdir, "emulator.err"), "w"),
        )
        self._procs.append(emu)
        _wait_port(self.emu_port, emu)

        drv_dir = os.path.join(self.workdir, "driver")
        os.makedirs(drv_dir)
        for name in DRIVER_FILES:
            src = os.path.join(self.driver_src, name)
            dst = os.path.join(drv_dir, name)
            (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, dst)
        ssh, telnet = self.emu_port, free_port()
        if "--telnet" in self.emulator_args:
            ssh, telnet = telnet, ssh  # SSH hits a closed port, driver falls back
        with open(os.path.join(drv_dir, "mrv_runtime_config.yml"), "w") as f:
            f.write(
                "CLI:\n  TYPE: [SSH,TELNET]\n  PORTS:\n"
                f"    SSH: {ssh}\n    TELNET: {telnet}\n"
                "LOGGING:\n  LEVEL: DEBUG\nDEBUG_ENABLED: FALSE\n"
            )
        self.log_dir = os.path.join(self.workdir, "Logs")
        os.makedirs(self.log_dir)
        drv = subprocess.Popen(
            [
                self.python,
                os.path.join(drv_dir, "main.py"),
                str(self.drv_port),
                self.log_dir,
            ],
            cwd=drv_dir,
            stdout=open(os.path.join(self.workdir, "driver.out"), "w"),
            stderr=subprocess.STDOUT,
        )
        self._procs.append(drv)
        _wait_port(self.drv_port, drv)
        self.sock = socket.create_connection(("127.0.0.1", self.drv_port), 120)
        return self

    def __exit__(self, *exc):
        try:
            self.sock.close()
        finally:
            for p in self._procs:
                p.kill()
                p.wait()

    def send(self, name: str, *params: tuple[str, str]) -> dict:
        self.sock.sendall(_command_xml(name, list(params)).encode())
        data = b""
        while not data.endswith(b"\r\n\r\n"):
            chunk = self.sock.recv(65536)
            if not chunk:
                break
            data += chunk
        return normalize_response(data.decode())

    def switch_commands(self) -> list[str]:
        with open(self.transcript, encoding="utf-8") as f:
            return f.read().splitlines()

    def driver_logs(self) -> str:
        parts = []
        for root, _, files in os.walk(self.log_dir):
            for name in files:
                with open(
                    os.path.join(root, name), encoding="utf-8", errors="replace"
                ) as f:
                    parts.append(f"== {name}\n{f.read()}")
        return "\n".join(parts)
