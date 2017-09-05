#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict()
ERROR_MAP = OrderedDict(
    [(r'[Ee]rror:', 'Command error'), (r'[Uu]nknown\scommand\s\'duplex', 'Duplex is not supported for this port type'),
     (r'[Uu]nknown\scommand\s.+auto-negotiation', 'Auto-negotiation is not supported for this port type')])

SET_DUPLEX = CommandTemplate('duplex {duplex_value}', ACTION_MAP, ERROR_MAP)
AUTO_NEG_ON = CommandTemplate('auto-negotiation', ACTION_MAP, ERROR_MAP)
AUTO_NEG_OFF = CommandTemplate('no auto-negotiation', ACTION_MAP, ERROR_MAP)
