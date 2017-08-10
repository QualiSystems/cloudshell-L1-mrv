#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict()
ERROR_MAP = OrderedDict([(r'[Ee]rror:', 'Command error')])

MAP_BIDI = CommandTemplate('map bidir {src_port} {dst_port}', ACTION_MAP, ERROR_MAP)
MAP_UNI = CommandTemplate('map unidir {src_port} {dst_port}', ACTION_MAP, ERROR_MAP)
MAP_CLEAR_TO = CommandTemplate('map {src_port} not-to {dst_port}', ACTION_MAP, ERROR_MAP)
MAP_CLEAR = CommandTemplate('map {src_port} clear-all', ACTION_MAP, ERROR_MAP)
