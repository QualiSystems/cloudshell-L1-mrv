from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port


class ResourceDescription(object):
    def __init__(self, address, chassis_table, slot_table, port_table):
        self._address = address
        self._chassis_table = chassis_table
        self._slot_table = slot_table
        self._port_table = port_table

        self._mapping_table = {}

    # Build Chassis
    @staticmethod
    def _chassis_key(chassis_id):
        return '{}'.format(chassis_id)

    def _build_chassis(self):
        chassis_dict = {}
        for record in self._chassis_table:
            index = record.get('nbsCmmcChassisIndex')
            model_name = record.get('nbsCmmcChassisModel')
            serial_number = record.get('nbsCmmcChassisSerialNum')
            chassis = Chassis(index, self._address, model_name, serial_number)
            chassis_dict[self._chassis_key(index)] = chassis
        return chassis_dict

    # Build blades
    @staticmethod
    def _blade_key(chassis_id, blade_id):
        return '{0}.{1}'.format(chassis_id, blade_id)

    def _build_blades(self, chassis_dict):
        blades_dict = {}
        for record in self._slot_table:
            chassis_index = record.get('nbsCmmcSlotChassisIndex')
            blade_index = record.get('nbsCmmcSlotIndex')
            model_name = record.get('nbsCmmcSlotModel')
            serial_number = record.get('nbsCmmcSlotSerialNum')
            if model_name.lower() != 'n/a':
                blade = Blade(blade_index, model_name, serial_number)
                blades_dict[self._blade_key(chassis_index, blade_index)] = blade
                chassis = chassis_dict.get(self._chassis_key(chassis_index))
                if chassis:
                    blade.set_parent_resource(chassis)
        return blades_dict

    # Build ports
    @staticmethod
    def _port_key(chassis_id, slot_id, port_id):
        return '{0}.{1}.{2}'.format(chassis_id, slot_id, port_id)

    def _port_mapping_key(self, data_dict):
        chassis_id = data_dict.get('nbsCmmcPortZoneChassisOper')
        if int(chassis_id) > 0:
            slot_id = data_dict.get('nbsCmmcPortZoneSlotOper')
            port_id = data_dict.get('nbsCmmcPortZoneIdOper')
            port_mapping_key = self._port_key(chassis_id, slot_id, port_id)
        else:
            port_mapping_key = None
        return port_mapping_key

    def _build_ports(self, blades_dict):
        ports_dict = {}
        for record in self._port_table:
            chassis_index = record.get('nbsCmmcPortChassisIndex')
            blade_index = record.get('nbsCmmcPortSlotIndex')
            port_index = record.get('nbsCmmcPortIndex')
            blade = blades_dict.get(self._blade_key(chassis_index, blade_index))
            if blade:
                serial_number = record.get('nbsCmmcPortSerialNumber')
                port = Port(port_index, 'Port {}'.format(blade.model_name), serial_number)
                port_key = self._port_key(chassis_index, blade_index, port_index)
                ports_dict[port_key] = port
                port_mapping_key = self._port_mapping_key(record)
                if port_mapping_key:
                    self._mapping_table[port_key] = port_mapping_key
                port.set_parent_resource(blade)
        return ports_dict

    # Mappings
    def _build_ports_mappings(self, ports_dict):
        for src_key, dst_key in self._mapping_table.iteritems():
            src_port = ports_dict.get(src_key)
            dst_port = ports_dict.get(dst_key)
            src_port.add_mapping(dst_port)

    def build(self):
        chassis_dict = self._build_chassis()
        blades_dict = self._build_blades(chassis_dict)
        ports_dict = self._build_ports(blades_dict)
        self._build_ports_mappings(ports_dict)
        return chassis_dict.values()
