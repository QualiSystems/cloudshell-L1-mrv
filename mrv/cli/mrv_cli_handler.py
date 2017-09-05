#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.cli.command_mode_helper import CommandModeHelper
from mrv.cli.l1_cli_handler import L1CliHandler
from mrv.cli.mrv_command_modes import DefaultCommandMode, ConfigCommandMode


class MrvCliHandler(L1CliHandler):
    def __init__(self, logger):
        super(MrvCliHandler, self).__init__(logger)
        self.modes = CommandModeHelper.create_command_mode()

    @property
    def _default_mode(self):
        return self.modes[DefaultCommandMode]

    @property
    def _config_mode(self):
        """
        :return:
        :rtype: cloudshell.cli.command_mode.CommandMode
        """
        return self.modes[ConfigCommandMode]

    def default_mode_service(self):
        """
        Default mode session
        :return:
        :rtype: cloudshell.cli.cli_service.CliService
        """
        return self.get_cli_service(self._default_mode)

    def config_mode_service(self):
        """
        Config mode session
        :return:
        :rtype: cloudshell.cli.cli_service.CliService
        """
        return self.get_cli_service(self._config_mode)
