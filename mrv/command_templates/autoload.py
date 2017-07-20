from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict()
ERROR_MAP = OrderedDict([(r'[Ee]rror:', 'Command error')])

CHASSIS_TABLE = CommandTemplate('show table chassis dump', ACTION_MAP, ERROR_MAP)
SLOT_TABLE = CommandTemplate('show table slot dump', ACTION_MAP, ERROR_MAP)
PORT_TABLE = CommandTemplate('show table port dump', ACTION_MAP, ERROR_MAP)

