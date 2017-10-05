#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port
from mrv.helpers.address import Address


class ResourceDescription(object):
    """MRV resource description builder"""
    IGNORE_BLADES = ['EM316LNXNM-MCC']

    def __init__(self, address, chassis_table, slot_table, port_table, port_protocol_table):
        self._resource_address = address
        self._chassis_table = chassis_table
        self._slot_table = slot_table
        self._port_table = port_table
        self._port_protocol_table = port_protocol_table

        self._mapping_table = {}

    # Build Chassis
    def _build_chassis(self):
        """
        Build chassis using data from chassis table
        :return:
        """
        chassis_dict = {}
        for address, record in self._chassis_table.iteritems():
            serial_number = record.get('nbsCmmcChassisSerialNum')
            chassis = Chassis(address.index(), self._resource_address, 'Generic MRV Chassis', serial_number)
            chassis.set_model_name(record.get('nbsCmmcChassisModel'))
            chassis.set_serial_number(serial_number)
            chassis.set_os_version(None)
            chassis_dict[address] = chassis
        return chassis_dict

    # Build blades
    def _build_blades(self, chassis_dict):
        """
        Build blades using data from slot table
        :param chassis_dict:
        :return:
        """
        blades_dict = {}
        for address, record in self._slot_table.iteritems():
            blade_model = record.get('nbsCmmcSlotModel')
            serial_number = record.get('nbsCmmcSlotSerialNum')
            chassis = chassis_dict.get(address.get_chassis_address())
            if chassis and blade_model.lower() != 'n/a' and blade_model not in self.IGNORE_BLADES:
                blade = Blade(address.index(), 'Generic L1 Module', serial_number)
                blade.set_model_name(blade_model)
                blade.set_serial_number(serial_number)
                blades_dict[address] = blade
                blade.set_parent_resource(chassis)
        return blades_dict

    # Build ports
    @staticmethod
    def _port_mapping_address(data_dict):
        chassis_id = data_dict.get('nbsCmmcPortZoneChassisOper')
        if int(chassis_id) > 0:
            slot_id = data_dict.get('nbsCmmcPortZoneSlotOper')
            port_id = data_dict.get('nbsCmmcPortZoneIdOper')
            port_mapping_address = Address(chassis_id, slot_id, port_id)
        else:
            port_mapping_address = None
        return port_mapping_address

    def _set_port_attributes(self, port, record):
        """
        Set create attributes for a specific port
        :param port:
        :type port: cloudshell.layer_one.core.response.resource_info.entities.port.Port
        :param record:
        :type record: dict
        :return:
        """
        # Model Name attribute
        port.set_model_name(record.get('nbsCmmcPortName'))
        # Protocol type and value attributes
        proto_index = record.get('nbsCmmcPortProtoOper')
        if proto_index in self._port_protocol_table:
            port.set_protocol_value(self._port_protocol_table[proto_index].get('nbsCmmcSysProtoRate'))
            port.set_protocol_type_value(self._port_protocol_table[proto_index].get('nbsCmmcSysProtoFamily'))
        # Port duplex attribute
        port.set_duplex(re.sub(r'notsupported|n/a', '', record.get('nbsCmmcPortDuplex') or '', flags=re.IGNORECASE))
        # Auto negotiation attribute
        _auto_negotiation_value = re.sub(r'notsupported|n/a', '', record.get('nbsCmmcPortAutoNegotiation') or '',
                                         flags=re.IGNORECASE)
        if _auto_negotiation_value:
            port.set_auto_negotiation(re.match(r'on|true', _auto_negotiation_value, flags=re.IGNORECASE) is not None)
        # Port RxPower attribute
        port.set_rx_power(record.get('nbsCmmcPortRxPower'))
        # Port Tx Power attribute
        port.set_tx_power(record.get('nbsCmmcPortTxPower'))
        # Port speed attribute
        port.set_port_speed(record.get('nbsCmmcPortSpeed'))
        # port wavelength attribute
        port.set_wavelength(record.get('nbsCmmcPortWavelength'))

    def _build_ports(self, blades_dict):
        """
        Build port using data from port table
        :param blades_dict:
        :return:
        """
        ports_dict = {}
        for address, record in self._port_table.iteritems():
            blade = blades_dict.get(address.get_slot_address())
            if blade:
                serial_number = record.get('nbsCmmcPortSerialNumber')
                port = Port(address.index(), 'Generic L1 Port', serial_number)
                self._set_port_attributes(port, record)
                ports_dict[address] = port
                port_mapping_address = self._port_mapping_address(record)
                if port_mapping_address:
                    self._mapping_table[address] = port_mapping_address
                port.set_parent_resource(blade)
        return ports_dict

    # Mappings
    def _build_ports_mappings(self, ports_dict):
        for src_address, dst_address in self._mapping_table.iteritems():
            src_port = ports_dict.get(src_address)
            dst_port = ports_dict.get(dst_address)
            src_port.add_mapping(dst_port)

    def build(self):
        """
        Build autoload structure
        :return:
        """
        chassis_dict = self._build_chassis()
        blades_dict = self._build_blades(chassis_dict)
        ports_dict = self._build_ports(blades_dict)
        self._build_ports_mappings(ports_dict)
        return chassis_dict.values()
