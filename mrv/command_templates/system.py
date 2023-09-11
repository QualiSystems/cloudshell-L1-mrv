from __future__ import annotations

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = {r"[Ee]rror:": "Command error"}

DEVICE_INFO = CommandTemplate("show version", error_map=ERROR_MAP)
