#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.layer_one_driver_exception import LayerOneDriverException
from cloudshell.layer_one.core.response.response_info import ResourceDescriptionResponseInfo
from mrv.autoload.mrv_attributes import MRVChassisAttributes, MRVPortAttributes, MRVSlotAttributes
from mrv.autoload.resource_description import ResourceDescription
from mrv.command_actions.autoload_actions import AutoloadActions
from mrv.command_actions.chassis_configuration_actions import ChassisConfigurationActions
from mrv.command_actions.mapping_actions import MappingActions
from mrv.command_actions.system_actions import SystemActions
from mrv.helpers.address import Address
from mrv.helpers.table_helper import ChassisTableHelper, BladeTableHelper, PortTableHelper, PortProtocolTableHelper
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

    @property
    def _chassis_table(self):
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            return ChassisTableHelper(autoload_actions.chassis_table()).address_dict()

    @property
    def _slot_table(self):
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            return BladeTableHelper(autoload_actions.slot_table()).address_dict()

    @property
    def _port_table(self):
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            return PortTableHelper(autoload_actions.port_table()).address_dict()

    @property
    def _port_protocol_table(self):
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            return PortProtocolTableHelper(autoload_actions.protocol_table()).index_dict()

    def get_state_id(self):
        return GetStateIdResponseInfo(self._chassis_table[Address(1)].get('nbsCmmcChassisName'))

    def set_state_id(self, state_id):
        with self._cli_handler.config_chassis_mode_service() as session:
            chassis_configuration = ChassisConfigurationActions(session, self._logger)
            chassis_configuration.set_chassis_name(state_id)

    def map_bidi(self, src_port, dst_port):
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            mapping_actions.map_bidi(Address.from_cs_address(src_port).build_str(),
                                     Address.from_cs_address(dst_port).build_str())

    def map_uni(self, src_port, dst_port):
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            mapping_actions.map_uni(Address.from_cs_address(src_port).build_str(),
                                    Address.from_cs_address(dst_port).build_str())

    def get_resource_description(self, address):
        response_info = ResourceDescriptionResponseInfo(
            ResourceDescription(address, self._chassis_table, self._slot_table, self._port_table, self._port_protocol_table).build())
        return response_info

    def map_clear(self, ports):
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            _ports = [Address.from_cs_address(port).build_str() for port in ports]
            mapping_actions.map_clear(_ports)

    def login(self, address, username, password):
        self._cli_handler.define_session_attributes(address, username, password)
        with self._cli_handler.default_mode_service() as session:
            system_actions = SystemActions(session, self._logger)
            self._logger.info(system_actions.device_info())

    def map_clear_to(self, src_port, dst_port):
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            mapping_actions.map_clear_to(Address.from_cs_address(src_port).build_str(),
                                         Address.from_cs_address(dst_port).build_str())

    def get_attribute_value(self, cs_address, attribute_name):
        address = Address.from_cs_address(cs_address)
        if address.is_chassis():
            attributes = MRVChassisAttributes(self._chassis_table)
        elif address.is_slot():
            attributes = MRVSlotAttributes(self._slot_table)
        elif address.is_port():
            attributes = MRVPortAttributes(self._port_table, self._port_protocol_table)
        else:
            raise LayerOneDriverException(self.__class__.__name__, 'Incorrect address, {}'.format(address))
        return AttributeValueResponseInfo(attributes.get_attribute(attribute_name, address).value)

    def set_attribute_value(self, address, attribute_name, attribute_value):
        return AttributeValueResponseInfo(attribute_value)
