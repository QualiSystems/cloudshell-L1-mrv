from __future__ import annotations

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = {
    r"[Ee]rror:": "Command error",
    r"[Uu]nknown\scommand\s\'duplex": "Duplex is not supported for this port type",
    r"[Uu]nknown\scommand\s.+auto-negotiation": "Auto-negotiation is not supported for this port type",  # noqa: E501
}

SET_DUPLEX = CommandTemplate("duplex {duplex_value}", error_map=ERROR_MAP)
AUTO_NEG_ON = CommandTemplate("auto-negotiation", error_map=ERROR_MAP)
AUTO_NEG_OFF = CommandTemplate("no auto-negotiation", error_map=ERROR_MAP)
