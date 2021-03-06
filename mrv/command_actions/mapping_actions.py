#!/usr/bin/python
# -*- coding: utf-8 -*-

import mrv.command_templates.mapping as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor


class MappingActions(object):
    def __init__(self, cli_service, logger):
        """
        Mapping actions
        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def map_bidi(self, src_port, dst_port):
        """
        Bidirectional mapping
        :param src_port: 
        :param dst_port: 
        :return: 
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.MAP_BIDI).execute_command(
            src_port=src_port, dst_port=dst_port)
        return output

    def map_uni(self, src_port, dst_ports):
        """
        Unidirectional mapping
        :param src_port: 
        :param dst_ports:
        :return: 
        """
        executor = CommandTemplateExecutor(self._cli_service, command_template.MAP_UNI)
        output = ''
        for dst_port in dst_ports:
            output += executor.execute_command(src_port=src_port, dst_port=dst_port)
        return output

    def map_clear(self, ports):
        """
        Clear bidirectional mapping
        :param ports: 
        :return: 
        """
        output = ""
        executor = CommandTemplateExecutor(self._cli_service, command_template.MAP_CLEAR)
        for port in ports:
            output += executor.execute_command(port=port)
        return output

    def map_clear_to(self, src_port, dst_ports):
        """
        Clear unidirectional mapping
        :param src_port: 
        :param dst_ports
        :return: 
        """
        executor = CommandTemplateExecutor(self._cli_service, command_template.MAP_CLEAR_TO)
        output = ''
        for dst_port in dst_ports:
            output += executor.execute_command(src_port=src_port, dst_port=dst_port)
        return output
