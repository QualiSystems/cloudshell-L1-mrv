#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port
from mrv.autoload.mrv_attributes import MRVChassisAttributes, MRVSlotAttributes, MRVPortAttributes
from mrv.helpers.address import Address


class ResourceDescription(object):
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
        chassis_dict = {}
        chassis_attributes = MRVChassisAttributes(self._chassis_table)
        for address, record in self._chassis_table.iteritems():
            model_name = 'Generic MRV Chassis'
            serial_number = chassis_attributes.serial_number(address).value
            chassis = Chassis(address.index(), self._resource_address, model_name, serial_number)
            chassis.attributes = chassis_attributes.get_attributes(address)
            chassis_dict[address] = chassis
        return chassis_dict

    # Build blades
    def _build_blades(self, chassis_dict):
        blades_dict = {}
        slots_attributes = MRVSlotAttributes(self._slot_table)
        for address, record in self._slot_table.iteritems():
            model_name = 'Generic L1 Module'
            blade_model = slots_attributes.model_name(address).value
            serial_number = slots_attributes.serial_number(address).value
            if blade_model.lower() != 'n/a' and blade_model not in self.IGNORE_BLADES:
                blade = Blade(address.index(), model_name, serial_number)
                blade.attributes = MRVSlotAttributes(self._slot_table).get_attributes(address)
                blades_dict[address] = blade
                chassis = chassis_dict.get(address.get_chassis_address())
                if chassis:
                    blade.set_parent_resource(chassis)
        return blades_dict

    # Build ports
    @staticmethod
    def _port_mapping_address(data_dict):
        chassis_id = data_dict.get('nbsCmmcPortZoneChassisOper')
        if int(chassis_id) > 0:
            slot_id = data_dict.get('nbsCmmcPortZoneSlotOper')
            port_id = data_dict.get('nbsCmmcPortZoneIdOper')
            port_mapping_key = Address(chassis_id, slot_id, port_id)
        else:
            port_mapping_key = None
        return port_mapping_key

    def _build_ports(self, blades_dict):
        ports_dict = {}
        ports_attributes = MRVPortAttributes(self._port_table, self._port_protocol_table)
        for address, record in self._port_table.iteritems():
            blade = blades_dict.get(address.get_slot_address())
            if blade:
                serial_number = record.get('nbsCmmcPortSerialNumber')
                model_name = 'Generic L1 Port'
                port = Port(address.index(), model_name, serial_number)
                port.attributes = ports_attributes.get_attributes(address)
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
        chassis_dict = self._build_chassis()
        blades_dict = self._build_blades(chassis_dict)
        ports_dict = self._build_ports(blades_dict)
        self._build_ports_mappings(ports_dict)
        return chassis_dict.values()
