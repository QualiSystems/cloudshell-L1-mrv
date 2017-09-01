#!/usr/bin/python
# -*- coding: utf-8 -*-

import mrv.command_templates.chassis_configuration as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor


class ChassisConfigurationActions(object):
    """
    Chassis configuration actions
    """

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

    def set_chassis_name(self, chassis_name):
        """
        Set chassis name
        :param chassis_name: 
        :return: 
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.SET_CHASSIS_NAME).execute_command(
            chassis_name=chassis_name)
        return output
