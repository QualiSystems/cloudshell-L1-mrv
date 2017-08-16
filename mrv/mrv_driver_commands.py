#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.layer_one_driver_exception import LayerOneDriverException
from cloudshell.layer_one.core.response.response_info import ResourceDescriptionResponseInfo
from mrv.autoload.resource_description import ResourceDescription
from mrv.command_actions.autoload_actions import AutoloadActions
from mrv.command_actions.mapping_actions import MappingActions
from mrv.command_actions.system_actions import SystemActions
from mrv.response.mrv_response_info import AttributeValueResponseInfo, GetStateIdResponseInfo


class MrvDriverCommands(DriverCommandsInterface):
    def __init__(self, cli_handler, logger):
        """
        :param cli_handler: 
        :type cli_handler: mrv.cli.mrv_cli_handler.MrvCliHandler
        :param logger: 
        """
        self._cli_handler = cli_handler
        self._logger = logger

    @staticmethod
    def _address_list(raw_address):
        return re.sub(r'\d+.\d+.\d+.\d+', '1', raw_address).split('/')

    @staticmethod
    def _reformat_address(raw_address):
        return '.'.join(MrvDriverCommands._address_list(raw_address))

    @property
    def _chassis_table(self):
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            return autoload_actions.chassis_table()

    @property
    def _slot_table(self):
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            return autoload_actions.slot_table()

    @property
    def _port_table(self):
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            return autoload_actions.port_table()

    def get_state_id(self):
        return GetStateIdResponseInfo(self._chassis_table[0].get('nbsCmmcChassisName'))

    def map_bidi(self, src_port, dst_port):
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            mapping_actions.map_bidi(self._reformat_address(src_port), self._reformat_address(dst_port))

    def map_uni(self, src_port, dst_port):
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            mapping_actions.map_uni(self._reformat_address(src_port), self._reformat_address(dst_port))

    def get_resource_description(self, address):
        response_info = ResourceDescriptionResponseInfo(
            ResourceDescription(address, self._chassis_table, self._slot_table, self._port_table).build())
        return response_info

    def map_clear(self, ports):
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            _ports = [self._reformat_address(port) for port in ports]
            mapping_actions.map_clear(_ports)

    def login(self, address, username, password):
        self._cli_handler.define_session_attributes(address, username, password)
        with self._cli_handler.default_mode_service() as session:
            system_actions = SystemActions(session, self._logger)
            self._logger.info(system_actions.device_info())

    def map_clear_to(self, src_port, dst_port):
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            mapping_actions.map_clear_to(self._reformat_address(src_port), self._reformat_address(dst_port))

    def get_attribute_value(self, address, attribute_name):
        address_list = self._address_list(address)
        if len(address_list) == 1:
            value = self._get_chassis_attribute(self._reformat_address(address), attribute_name)
        elif len(address_list) == 2:
            value = self._get_blade_attribute(self._reformat_address(address), attribute_name)
        elif len(address_list) == 3:
            value = self._get_port_attribute(self._reformat_address(address), attribute_name)
        else:
            raise LayerOneDriverException(self.__class__.__name__, 'Incorrect address, {}'.format(address))
        return AttributeValueResponseInfo(value)

    def set_attribute_value(self, address, attribute_name, attribute_value):
        return AttributeValueResponseInfo(attribute_value)

    def _get_chassis_attribute(self, address, attribute_name):
        chassis_attribute_table = {'serial number': 'nbsCmmcChassisSerialNum'}
        attribute_key = chassis_attribute_table.get(attribute_name.lower())
        if attribute_key is None:
            value = None
        else:
            chassis_table = self._chassis_table_by_address(self._chassis_table)
            if address in chassis_table:
                value = chassis_table[address].get(attribute_key)
            else:
                value = None
        return value

    def _get_blade_attribute(self, address, attribute_name):
        pass

    def _get_port_attribute(self, address, attribute_name):
        pass

    @staticmethod
    def _chassis_table_by_address(chassis_table):
        new_table = {}
        for record in chassis_table:
            new_table[record.get('nbsCmmcChassisIndex')] = record
        return new_table
