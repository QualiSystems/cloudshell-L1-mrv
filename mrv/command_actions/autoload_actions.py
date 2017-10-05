#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

import mrv.command_templates.autoload as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor


class AutoloadActions(object):
    """
    Autoload actions
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

    def chassis_table(self):
        """
        Chassis table
        :return: list of chassis data, [{'index': '1', 'model': 'MRV Chassis', 'serial': '1ndsKsf'}, ]
        :rtype: list
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.CHASSIS_TABLE).execute_command()
        result = self._parse_table(output)
        return result

    def slot_table(self):
        """
        Slot table
        :return: list of slot data, [{'index':'1.1', 'slot_model': 'Mrv Blade A', 'slot_serial': 'saf31423'},
                                        {'index':'1.2', 'slot_model': 'Mrv Blade A', 'slot_serial': 'saf31423'}]
        :rtype: list
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.SLOT_TABLE).execute_command()
        result = self._parse_table(output)
        return result

    def port_table(self):
        """
        Port table
        :return: list of port data, [{'index':'1.1.1', 'port_model': 'Mrv port A', 'port_speed': '1Gb'},
                                        {'index':'1.2.1', 'port_model': 'Mrv port A', 'port_speed': '1Gb'},
                                        {'index':'1.2.2', 'port_model': 'Mrv port A', 'port_speed': '1Gb'}]
        :rtype: list
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.PORT_TABLE).execute_command()
        result = self._parse_table(output)
        return result

    def protocol_table(self):
        """
        Protocol table
        :return: 
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.PROTOCOL_TABLE).execute_command()
        result = self._parse_table(output)
        return result

    @staticmethod
    def _parse_table(data):
        """
        Parse table and build dict
        :param data: 
        :return: 
        """
        result = []
        line_output = data.split('\n')
        line_output.reverse()
        fields = AutoloadActions._split_string(line_output.pop())
        while line_output:
            values = AutoloadActions._split_string(line_output.pop())
            if len(values) == len(fields):
                result.append(dict(zip(fields, values)))
        return result

    @staticmethod
    def _split_string(string):
        return re.findall('"(.*?)"', string)
