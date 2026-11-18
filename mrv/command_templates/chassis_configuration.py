from __future__ import annotations

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = {r"[Ee]rror:": "Command error"}

SET_CHASSIS_NAME = CommandTemplate("description {chassis_name}", error_map=ERROR_MAP)
