"""py3 driver must behave exactly like the shipped py2.7 driver (master, 2.0.6).

Both run as real driver processes against the same emulated MRV switch; every L1
response and the command stream the switch received must match.

Needs the baseline checked out and a py2.7 env with master's requirements:
    git worktree add ../mrv-master origin/master
    MRV_PY27=<py2.7 python with master requirements>  (default .venv27)
Skipped when either is missing.
"""

from __future__ import annotations

import os
import re
import sys

import pytest

from tests.parity.l1_harness import REPO, Run

PY27 = os.environ.get(
    "MRV_PY27", os.path.join(REPO, ".venv27", "Scripts", "python.exe")
)
BASELINE = os.environ.get("MRV_BASELINE", os.path.join(REPO, "..", "mrv-master"))
# point these at an installed release (Drivers\cloudshell-L1-mrv) to test the zip
NEW_PY = os.environ.get("MRV_PY3", sys.executable)
NEW_SRC = os.environ.get("MRV_SRC", REPO)

pytestmark = pytest.mark.skipif(
    not (os.path.isfile(PY27) and os.path.isdir(os.path.join(BASELINE, "mrv"))),
    reason="py2.7 baseline driver not available",
)

IP = "127.0.0.1"


def p(port: str) -> str:
    return f"{IP}/{port}"


SCENARIO = [
    ("Login", [("Address", IP), ("User", "admin"), ("Password", "admin")]),
    ("GetResourceDescription", [("Address", IP)]),
    ("GetStateId", []),
    ("SetStateId", [("StateId", "cs-sync-42")]),
    ("GetStateId", []),
    ("MapBidi", [("MapPort_A", p("1/1")), ("MapPort_B", p("2/2"))]),
    ("MapUni", [("SrcPort", p("2/3")), ("DstPort", p("2/4")), ("DstPort", p("2/5"))]),
    ("MapTap", [("SrcPort", p("1/5")), ("DstPort", p("1/6"))]),
    ("GetResourceDescription", [("Address", IP)]),
    ("MapClearTo", [("SrcPort", p("2/3")), ("DstPort", p("2/4"))]),
    ("MapClear", [("MapPort", p("1/1")), ("MapPort", p("2/5"))]),
    ("MapBidi", [("MapPort_A", p("9/1")), ("MapPort_B", p("2/2"))]),  # bad port
    (
        "SetAttributeValue",
        [("Address", p("1/2")), ("Attribute", "Duplex"), ("Value", "2")],
    ),
    (
        "SetAttributeValue",
        [("Address", p("1/2")), ("Attribute", "Auto Negotiation"), ("Value", "False")],
    ),
    (
        "SetAttributeValue",
        [("Address", p("1/3")), ("Attribute", "Auto Negotiation"), ("Value", "True")],
    ),
    (
        "SetAttributeValue",
        [("Address", p("1/3")), ("Attribute", "Protocol"), ("Value", "5")],
    ),
    (
        "SetAttributeValue",
        [("Address", p("1/3")), ("Attribute", "Port Speed"), ("Value", "1")],
    ),
    (
        "SetAttributeValue",
        [("Address", p("1")), ("Attribute", "Duplex"), ("Value", "2")],
    ),
    ("GetAttributeValue", [("Address", p("1/3")), ("Attribute", "Duplex")]),
    (
        "SetSpeedManual",
        [
            ("SrcPort", p("1/1")),
            ("DstPort", p("1/2")),
            ("Speed", "1"),
            ("Duplex", "full"),
        ],
    ),
    ("GetResourceDescription", [("Address", IP)]),
]

VARIANTS = {
    "default": [],
    "telnet": ["--telnet"],
    # firmware that only takes 1203-style port ids: exercises map_bidi's fallback
    "legacy-address": ["--legacy-address"],
}


def _py2_log(log: str) -> str:
    """py2 errors are str(('DriverCommands', 'msg')); py3 drops the tuple dump."""
    m = re.fullmatch(r"\('\w+', '(.*)'\)", log)
    return m.group(1) if m else log


def _same(old: dict, new: dict) -> bool:
    old = dict(old, Log=_py2_log(old.get("Log", "")))
    return old == new


def run_scenario(
    python: str, src: str, emulator_args
) -> tuple[list[dict], list[str], str]:
    with Run(python, src, emulator_args) as run:
        responses = [run.send(name, *params) for name, params in SCENARIO]
        return responses, run.switch_commands(), run.workdir


_cache: dict = {}


def results(which: str, variant: str):
    key = (which, variant)
    if key not in _cache:
        python, src = (PY27, BASELINE) if which == "old" else (NEW_PY, NEW_SRC)
        _cache[key] = run_scenario(python, src, VARIANTS[variant])
    return _cache[key]


def _label(i: int) -> str:
    return f"step {i}: {SCENARIO[i][0]}"


@pytest.mark.parametrize("variant", VARIANTS)
def test_responses_match_py2_driver(variant):
    old, _, old_dir = results("old", variant)
    new, _, new_dir = results("new", variant)
    diffs = [
        f"{_label(i)}\n  py2: {o}\n  py3: {n}"
        for i, (o, n) in enumerate(zip(old, new))
        if not _same(o, n)
    ]
    assert not diffs, f"logs: {old_dir} vs {new_dir}\n" + "\n".join(diffs)


@pytest.mark.parametrize("variant", VARIANTS)
def test_switch_receives_same_commands(variant):
    _, old, _ = results("old", variant)
    _, new, _ = results("new", variant)
    assert new == old


def test_baseline_is_not_trivially_failing():
    """Guard: if the baseline itself fails everything, parity proves nothing."""
    old, cmds, _ = results("old", "default")
    assert old[0]["success"] == "true"
    assert old[1]["success"] == "true"
    assert "map bidir 1.1.1 1.2.2" in cmds
