#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.layer_one.core.command_executor import CommandExecutor, CommandResponseManager
from mrv.cli.mrv_cli_handler import MrvCliHandler
from mrv.response.mrv_response_info import GetStateIdResponseInfo, AttributeValueResponseInfo
from mrv_driver_commands import MrvDriverCommands


class MrvCommandExecutor(CommandExecutor):
    def __init__(self, logger):
        super(MrvCommandExecutor, self).__init__(logger)
        self._cli_handler = MrvCliHandler(logger)
        self._registered_commands.update({'GetStateId': self.get_state_id_executor,
                                          'SetStateId': self.set_state_id_executor,
                                          'GetAttributeValue': self.get_attribute_value_executor,
                                          'SetAttributeValue': self.set_attribute_value_executor})

    def _driver_instance(self):
        return MrvDriverCommands(self._cli_handler, self._logger)

    def get_state_id_executor(self, command_request, driver_instance):
        """
        :param command_request:
        :type command_request: cloudshell.layer_one.core.entities.command.Command
        :param driver_instance
        :type driver_instance: cloudshell.layer_one.core.driver_commands_interface.DriverCommandsInterface
        :return:
        :rtype: CommandResponse
        """
        with CommandResponseManager(command_request, self._logger) as command_response:
            command_response.response_info = GetStateIdResponseInfo(self._state_id)
        return command_response

    def set_state_id_executor(self, command_request, driver_instance):
        """
        :param command_request:
        :type command_request: cloudshell.layer_one.core.entities.command.Command
        :param driver_instance
        :type driver_instance: cloudshell.layer_one.core.driver_commands_interface.DriverCommandsInterface
        :return:
        :rtype: CommandResponse
        """
        self._state_id = command_request.command_params.get('StateId')[0]
        with CommandResponseManager(command_request, self._logger) as command_response:
            pass
        return command_response

    def get_attribute_value_executor(self, command_request, driver_instance):
        """
        :param command_request:
        :type command_request: cloudshell.layer_one.core.entities.command.Command
        :param driver_instance
        :type driver_instance: cloudshell.layer_one.core.driver_commands_interface.DriverCommandsInterface
        :return:
        :rtype: CommandResponse
        """
        self._state_id = command_request.command_params.get('Attribute')[0]
        with CommandResponseManager(command_request, self._logger) as command_response:
            command_response.response_info = AttributeValueResponseInfo('NA')
        return command_response

    def set_attribute_value_executor(self, command_request, driver_instance):
        """
        :param command_request:
        :type command_request: cloudshell.layer_one.core.entities.command.Command
        :param driver_instance
        :type driver_instance: cloudshell.layer_one.core.driver_commands_interface.DriverCommandsInterface
        :return:
        :rtype: CommandResponse
        """
        attribute_name = command_request.command_params.get('Attribute')[0]
        attribute_value = command_request.command_params.get('Value')[0]
        with CommandResponseManager(command_request, self._logger) as command_response:
            command_response.response_info = AttributeValueResponseInfo(attribute_value)
        return command_response
