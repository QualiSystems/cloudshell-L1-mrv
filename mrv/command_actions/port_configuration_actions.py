#!/usr/bin/python
# -*- coding: utf-8 -*-

import mrv.command_templates.port_configuration as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor


class PortConfigurationActions(object):
    """Port configuration actions"""

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

    def set_port_duplex(self, duplex_value):
        """
        Set port duplex
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.SET_DUPLEX).execute_command(
            duplex_value=duplex_value)
        return output

    def set_auto_neg_on(self):
        """
        Set port auto-negotiation ON
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.AUTO_NEG_ON).execute_command()
        return output

    def set_auto_neg_off(self):
        """
        Set port auto-negotiation OFF
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.AUTO_NEG_OFF).execute_command()
        return output
