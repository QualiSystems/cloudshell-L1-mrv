from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict()
ERROR_MAP = OrderedDict([(r'[Ee]rror:', 'Command error')])

MAP_BIDI = CommandTemplate('map bidir {src_port} {dst_port}', ACTION_MAP, ERROR_MAP)
MAP_UNI = CommandTemplate('map unidir {src_port} {dst_port}', ACTION_MAP, ERROR_MAP)
