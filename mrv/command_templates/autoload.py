from __future__ import annotations

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = {r"[Ee]rror:": "Command error"}

CHASSIS_TABLE = CommandTemplate("show table chassis dump", error_map=ERROR_MAP)
SLOT_TABLE = CommandTemplate("show table slot dump", error_map=ERROR_MAP)
PORT_TABLE = CommandTemplate("show table port dump", error_map=ERROR_MAP)
PROTOCOL_TABLE = CommandTemplate("show table protocol dump", error_map=ERROR_MAP)
