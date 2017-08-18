from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict()
ERROR_MAP = OrderedDict([(r'[Ee]rror:', 'Command error')])

SET_CHASSIS_NAME = CommandTemplate('description {chassis_name}', ACTION_MAP, ERROR_MAP)
