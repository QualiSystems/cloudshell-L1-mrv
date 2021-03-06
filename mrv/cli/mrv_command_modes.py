#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import OrderedDict

from cloudshell.cli.command_mode import CommandMode


class DefaultCommandMode(CommandMode):
    PROMPT = r'.+[^\)]#'
    ENTER_COMMAND = ''
    EXIT_COMMAND = 'exit'

    def __init__(self):
        CommandMode.__init__(self, self.PROMPT, self.ENTER_COMMAND, self.EXIT_COMMAND,
                             enter_action_map=self.enter_action_map(),
                             exit_action_map=self.exit_action_map(), enter_error_map=self.enter_error_map(),
                             exit_error_map=self.exit_error_map())

    def enter_actions(self, cli_operations):
        cli_operations.send_command('terminal length 0')

    def enter_action_map(self):
        return OrderedDict()

    def enter_error_map(self):
        return OrderedDict([(r'[Ee]rror:', 'Command error')])

    def exit_action_map(self):
        return OrderedDict()

    def exit_error_map(self):
        return OrderedDict([(r'[Ee]rror:', 'Command error')])


class ConfigCommandMode(CommandMode):
    PROMPT = r'.+\(config\)#'
    ENTER_COMMAND = 'configure terminal'
    EXIT_COMMAND = 'exit'

    def __init__(self):
        CommandMode.__init__(self, self.PROMPT, self.ENTER_COMMAND, self.EXIT_COMMAND,
                             enter_action_map=self.enter_action_map(),
                             exit_action_map=self.exit_action_map(), enter_error_map=self.enter_error_map(),
                             exit_error_map=self.exit_error_map())

    def enter_action_map(self):
        return OrderedDict([(r'[Pp]assword', lambda session, logger: session.send_line(session.password))])

    def enter_error_map(self):
        return OrderedDict([(r'[Ee]rror:', 'Command error')])

    def exit_action_map(self):
        return OrderedDict()

    def exit_error_map(self):
        return OrderedDict([(r'[Ee]rror:', 'Command error')])


class ConfigChassisCommandMode(CommandMode):
    PROMPT = r'.+\(chassis/\d+\)#'
    ENTER_COMMAND = 'unknown command'
    ENTER_COMMAND_TEMPLATE = r'chassis {}'
    EXIT_COMMAND = 'exit'

    def __init__(self):
        CommandMode.__init__(self, self.PROMPT, self.ENTER_COMMAND, self.EXIT_COMMAND,
                             enter_action_map=self.enter_action_map(),
                             exit_action_map=self.exit_action_map(), enter_error_map=self.enter_error_map(),
                             exit_error_map=self.exit_error_map())

    def enter_action_map(self):
        return OrderedDict([(r'[Pp]assword', lambda session, logger: session.send_line(session.password))])

    def enter_error_map(self):
        return OrderedDict([(r'[Ee]rror:', 'Command error'), (r'[Uu]nknown\scommand', 'Unknown command')])

    def exit_action_map(self):
        return OrderedDict()

    def exit_error_map(self):
        return OrderedDict([(r'[Ee]rror:', 'Command error')])

    def _set_enter_command(self, chassis_address):
        self._enter_command = self.ENTER_COMMAND_TEMPLATE.format(chassis_address)

    @staticmethod
    def detached_instance(chassis_address, parent_mode):
        instance = ConfigChassisCommandMode()
        instance._set_enter_command(chassis_address)
        instance.parent_node = parent_mode
        return instance


class ConfigPortCommandMode(CommandMode):
    PROMPT = r'.+\(port/\d+\.\d+.\d+\)#'
    ENTER_COMMAND = 'unknown command'
    ENTER_COMMAND_TEMPLATE = 'port {}'
    EXIT_COMMAND = 'exit'

    def __init__(self):
        CommandMode.__init__(self, self.PROMPT, self.ENTER_COMMAND, self.EXIT_COMMAND,
                             enter_action_map=self.enter_action_map(),
                             exit_action_map=self.exit_action_map(), enter_error_map=self.enter_error_map(),
                             exit_error_map=self.exit_error_map())

    def enter_action_map(self):
        return OrderedDict([(r'[Pp]assword', lambda session, logger: session.send_line(session.password))])

    def enter_error_map(self):
        return OrderedDict([(r'[Ee]rror:', 'Command error'), (r'[Uu]nknown\scommand', 'Unknown command')])

    def exit_action_map(self):
        return OrderedDict()

    def exit_error_map(self):
        return OrderedDict([(r'[Ee]rror:', 'Command error')])

    def _set_enter_command(self, port_address):
        self._enter_command = self.ENTER_COMMAND_TEMPLATE.format(port_address)

    @staticmethod
    def detached_instance(port_address, parent_mode):
        instance = ConfigPortCommandMode()
        instance._set_enter_command(port_address)
        instance.parent_node = parent_mode
        return instance


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {
        ConfigCommandMode: {
            ConfigChassisCommandMode: {},
            ConfigPortCommandMode: {}}
    }
}
