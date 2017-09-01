#!/usr/bin/python
# -*- coding: utf-8 -*-

import mrv.command_templates.system as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor


class SystemActions(object):
    """System actions"""

    def __init__(self, cli_service, logger):
        """
        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def device_info(self):
        """
        Device info
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.DEVICE_INFO).execute_command()
        return output
