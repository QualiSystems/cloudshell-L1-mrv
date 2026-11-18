"""py3 driver behaviour the py2 driver never had (or had broken)."""

from __future__ import annotations

import sys

from tests.parity.l1_harness import REPO, Run

IP = "127.0.0.1"
LOGIN = [("Address", IP), ("User", "admin"), ("Password", "admin")]
MAP = [("MapPort_A", f"{IP}/1/1"), ("MapPort_B", f"{IP}/2/2")]


def _run(emulator_args, steps):
    with Run(sys.executable, REPO, emulator_args) as run:
        return (
            [run.send(n, *p) for n, p in steps],
            run.switch_commands(),
            run.driver_logs(),
        )


def test_password_prompt_on_configure_terminal():
    # 2.0.6 broke here too (send_line without logger)
    responses, commands, _ = _run(
        ["--config-password"], [("Login", LOGIN), ("MapBidi", MAP)]
    )
    assert [r["success"] for r in responses] == ["true", "true"], responses
    assert commands[-2:] == ["<password>", "map bidir 1.1.1 1.2.2"]


def test_device_io_reaches_driver_log():
    # support relies on the CLI transcript in Logs/mrv/*.log
    _, _, logs = _run([], [("Login", LOGIN), ("MapBidi", MAP)])
    cli_log = "\n".join(
        part
        for part in logs.split("== ")[1:]
        if part.split("\n", 1)[0].endswith(".log")
    )
    assert "map bidir 1.1.1 1.2.2" in cli_log
    assert "fiberdriver(config)#" in cli_log


def test_legacy_ssh_algorithms():
    # 2008-era MRV NM firmware: group1-sha1 kex, CBC ciphers, ssh-rsa host key
    responses, commands, _ = _run(
        ["--legacy-ssh"], [("Login", LOGIN), ("MapBidi", MAP)]
    )
    assert [r["success"] for r in responses] == ["true", "true"], responses
    assert "map bidir 1.1.1 1.2.2" in commands


def test_telnet_fallback():
    # SSH refused -> TELNET from CLI.TYPE; cli 6 ships its own telnetlib (gone in 3.13)
    responses, commands, _ = _run(["--telnet"], [("Login", LOGIN), ("MapBidi", MAP)])
    assert [r["success"] for r in responses] == ["true", "true"], responses
    assert commands[:2] == ["admin", "<password>"]
    assert "map bidir 1.1.1 1.2.2" in commands
