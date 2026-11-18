from __future__ import annotations

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = {
    r"[Ee]rror:": "Command error",
    r"[Hh]ardware\s[Ii]ncompatibility": "Mapping error, Hardware incompatibility",
    r"%\s[Cc]ommand\sincomplete": "Incorrect command",
}

MAP_BIDI = CommandTemplate("map bidir {src_port} {dst_port}", error_map=ERROR_MAP)
MAP_UNI = CommandTemplate("map {src_port} also-to {dst_port}", error_map=ERROR_MAP)
MAP_CLEAR_TO = CommandTemplate("map {src_port} not-to {dst_port}", error_map=ERROR_MAP)
MAP_CLEAR = CommandTemplate("map {port} clear-all", error_map=ERROR_MAP)
