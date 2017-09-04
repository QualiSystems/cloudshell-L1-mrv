#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.layer_one.core.command_executor import CommandExecutor
from mrv.cli.mrv_cli_handler import MrvCliHandler
from mrv.mrv_driver_commands import MrvDriverCommands


class MrvCommandExecutor(CommandExecutor):
    """
    Mrv command executor
    """

    def __init__(self, logger):
        super(MrvCommandExecutor, self).__init__(logger)
        self._driver_instance = MrvDriverCommands(MrvCliHandler(self._logger), self._logger)

    def driver_instance(self):
        return self._driver_instance
