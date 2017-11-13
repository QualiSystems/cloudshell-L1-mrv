#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.layer_one_driver_exception import LayerOneDriverException
from cloudshell.layer_one.core.response.response_info import ResourceDescriptionResponseInfo, GetStateIdResponseInfo, \
    AttributeValueResponseInfo
from mrv.autoload.resource_description import ResourceDescription
from mrv.cli.mrv_cli_handler import MrvCliHandler
from mrv.cli.mrv_command_modes import ConfigPortCommandMode, ConfigChassisCommandMode
from mrv.command_actions.autoload_actions import AutoloadActions
from mrv.command_actions.chassis_configuration_actions import ChassisConfigurationActions
from mrv.command_actions.mapping_actions import MappingActions
from mrv.command_actions.port_configuration_actions import PortConfigurationActions
from mrv.command_actions.system_actions import SystemActions
from mrv.helpers.address import Address
from mrv.helpers.table_helper import ChassisTableHelper, BladeTableHelper, PortTableHelper, PortProtocolTableHelper


class DriverCommands(DriverCommandsInterface):
    """
    MRV driver commands implementation
    """

    def __init__(self, logger):
        """
        :param logger: 
        """
        self._logger = logger
        self._cli_handler = MrvCliHandler(self._logger)
        self._ports_attributes_setters = {'Duplex': self._set_port_duplex,
                                          'Protocol': self._set_protocol,
                                          'Auto Negotiation': self._set_auto_neg}

    @property
    def _chassis_table(self):
        """Chassis data"""
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            return ChassisTableHelper(autoload_actions.chassis_table()).address_dict()

    @property
    def _slot_table(self):
        """Slot data"""
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            return BladeTableHelper(autoload_actions.slot_table()).address_dict()

    @property
    def _port_table(self):
        """Port data"""
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            return PortTableHelper(autoload_actions.port_table()).address_dict()

    @property
    def _port_protocol_table(self):
        """Port protocol data"""
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            return PortProtocolTableHelper(autoload_actions.protocol_table()).index_dict()

    def login(self, address, username, password):
        """
        Perform login operation on the device
        :param address: resource address, "192.168.42.240"
        :param username: username to login on the device
        :param password: password
        :return: None
        :raises Exception: if command failed
        Example:
            session = CliSession(address, username, password)
            session.connect()
        """
        self._cli_handler.define_session_attributes(address, username, password)
        with self._cli_handler.default_mode_service() as session:
            system_actions = SystemActions(session, self._logger)
            self._logger.info(system_actions.device_info())

    def get_state_id(self):
        """
        Check if CS synchronized with the device.
        :return: Synchronization ID, GetStateIdResponseInfo(-1) if not used
        :rtype: cloudshell.layer_one.core.response.response_info.GetStateIdResponseInfo
        :raises Exception: if command failed

        Example:
            state_id = self._state_flow.get_id()
            return GetStateIdResponseInfo(state_id)
        """
        return GetStateIdResponseInfo(self._chassis_table[Address(1)].get('nbsCmmcChassisName'))

    def set_state_id(self, state_id):
        """
        Set synchronization state id to the device, called after Autoload or SyncFomDevice commands
        :param state_id: synchronization ID
        :type state_id: str
        :return: None
        :raises Exception: if command failed

        Example:
            self._state_flow.set_id(state_id)
        """
        with self._cli_handler.config_mode_service() as session:
            detached_chassis_mode = ConfigChassisCommandMode.detached_instance('1', session.command_mode)
            with session.enter_mode(detached_chassis_mode) as chassis_configuration_session:
                chassis_configuration = ChassisConfigurationActions(chassis_configuration_session, self._logger)
                chassis_configuration.set_chassis_name(state_id)

    def map_bidi(self, src_port, dst_port):
        """
        Create a bidirectional connection between source and destination ports
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_port: dst port address, '192.168.42.240/1/22'
        :type dst_port: str
        :return: None
        :raises Exception: if command failed

        Example:
            self._map_flow.map_bidi(src_port, dst_port)
        """
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            mapping_actions.map_bidi(Address.from_cs_address(src_port).build_str(),
                                     Address.from_cs_address(dst_port).build_str())

    def map_uni(self, src_port, dst_ports):
        """
        Unidirectional mapping of two ports
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_ports: list of dst ports addresses, ['192.168.42.240/1/21', '192.168.42.240/1/22']
        :type dst_ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            self._map_flow.map_uni(src_port, dst_port)
        """
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            _src_port = Address.from_cs_address(src_port).build_str()
            _dst_ports = [Address.from_cs_address(port).build_str() for port in dst_ports]
            mapping_actions.map_uni(_src_port, _dst_ports)

    def get_resource_description(self, address):
        """
        Auto-load function to retrieve all information from the device
        :param address: resource address, '192.168.42.240'
        :type address: str
        :return: resource description
        :rtype: cloudshell.layer_one.core.response.response_info.ResourceDescriptionResponseInfo
        :raises cloudshell.layer_one.core.layer_one_driver_exception.LayerOneDriverException: Layer one exception.

        Example:

            from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
            from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
            from cloudshell.layer_one.core.response.resource_info.entities.port import Port

            chassis_resource_id = chassis_info.get_id()
            chassis_address = chassis_info.get_address()
            chassis_model_name = "{{ cookiecutter.model_name }} Chassis"
            chassis_serial_number = chassis_info.get_serial_number()
            chassis = Chassis(resource_id, address, model_name, serial_number)

            blade_resource_id = blade_info.get_id()
            blade_model_name = 'Generic L1 Module'
            blade_serial_number = blade_info.get_serial_number()
            blade.set_parent_resource(chassis)

            port_id = port_info.get_id()
            port_serial_number = port_info.get_serial_number()
            port = Port(port_id, 'Generic L1 Port', port_serial_number)
            port.set_parent_resource(blade)

            return ResourceDescriptionResponseInfo([chassis])
        """

        response_info = ResourceDescriptionResponseInfo(
            ResourceDescription(address, self._chassis_table, self._slot_table, self._port_table,
                                self._port_protocol_table).build())
        return response_info

    def map_clear(self, ports):
        """
        Remove simplex/multi-cast/duplex connection ending on the destination port
        :param ports: ports, ['192.168.42.240/1/21', '192.168.42.240/1/22']
        :type ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            for port in ports:
                self._map_flow.map_clear(port)
        """
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            _ports = [Address.from_cs_address(port).build_str() for port in ports]
            mapping_actions.map_clear(_ports)

    def map_clear_to(self, src_port, dst_ports):
        """
        Remove simplex/multi-cast/duplex connection ending on the destination port
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_ports: list of dst ports addresses, ['192.168.42.240/1/21', '192.168.42.240/1/22']
        :type dst_ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            self._map_flow.map_clear_to(src_port, dst_port)
        """
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            _src_port = Address.from_cs_address(src_port).build_str()
            _dst_ports = [Address.from_cs_address(port).build_str() for port in dst_ports]
            mapping_actions.map_clear_to(_src_port, _dst_ports)

    def get_attribute_value(self, cs_address, attribute_name):
        """
        Retrieve attribute value from the device
        :param cs_address: address, '192.168.42.240/1/21'
        :type cs_address: str
        :param attribute_name: attribute name, "Port Speed"
        :type attribute_name: str
        :return: attribute value
        :rtype: cloudshell.layer_one.core.response.response_info.AttributeValueResponseInfo
        :raises Exception: if command failed

        Example:
            value = self._attribute_flow.get(cs_address, attribute_name)
            return AttributeValueResponseInfo(value)
        """
        raise LayerOneDriverException(self.__class__.__name__, 'GetAttributeValue command is not supported')

    def set_attribute_value(self, cs_address, attribute_name, attribute_value):
        """
        Set attribute value to the device
        :param cs_address: address, '192.168.42.240/1/21'
        :type cs_address: str
        :param attribute_name: attribute name, "Port Speed"
        :type attribute_name: str
        :param attribute_value: value, "10000"
        :type attribute_value: str
        :return: attribute value
        :rtype: cloudshell.layer_one.core.response.response_info.AttributeValueResponseInfo
        :raises Exception: if command failed
        """
        address = Address.from_cs_address(cs_address)
        if address.is_chassis() or address.is_slot():
            raise LayerOneDriverException(self.__class__.__name__,
                                          'SetAttributeValue for Chassis or Slot/Blade is not supported')
        else:
            attribute_setter = self._ports_attributes_setters.get(attribute_name)
            if attribute_setter:
                attribute_setter(address, attribute_value)
            else:
                raise LayerOneDriverException(self.__class__.__name__,
                                              'SetAttributeValue is not supported for attribute {}'.format(
                                                  attribute_name))
            return AttributeValueResponseInfo(attribute_value)

    def _set_port_duplex(self, address, value):
        """
        Change duplex value for a specific port
        :param address:
        :param value:
        :return:
        """
        with self._cli_handler.config_mode_service() as session:
            detached_port_mode = ConfigPortCommandMode.detached_instance(address.build_str(), session.command_mode)
            with session.enter_mode(detached_port_mode) as config_port_session:
                port_configuration_actions = PortConfigurationActions(config_port_session, self._logger)
                if str(value) == '2':
                    duplex_value = 'half'
                else:
                    duplex_value = 'full'
                port_configuration_actions.set_port_duplex(duplex_value)

    def _set_protocol(self, address, value):
        """
        Change protocol value for a specific port
        :param address:
        :param value:
        :return:
        """
        pass

    def _set_auto_neg(self, address, value):
        """
        Change auto-negotiation value for a specific port
        :param address:
        :param value:
        :return:
        """
        with self._cli_handler.config_mode_service() as session:
            detached_port_mode = ConfigPortCommandMode.detached_instance(address.build_str(), session.command_mode)
            with session.enter_mode(detached_port_mode) as config_port_session:
                port_configuration_actions = PortConfigurationActions(config_port_session, self._logger)
                if re.match(r'[Ff]alse', value):
                    port_configuration_actions.set_auto_neg_off()
                else:
                    port_configuration_actions.set_auto_neg_on()

    def map_tap(self, src_port, dst_ports):
        return self.map_uni(src_port, dst_ports)

    def set_speed_manual(self, src_port, dst_port, speed, duplex):
        return NotImplemented

