from abc import ABCMeta, abstractmethod

from mrv.helpers.address import Address


class TableHelper(object):
    """Associate addresses instances with table data"""
    __metaclass__ = ABCMeta

    def __init__(self, table):
        self._table = table

    @staticmethod
    @abstractmethod
    def build_address(record):
        """
        Address for a specific entity
        :param record:
        :return:
        """
        pass

    def address_dict(self):
        """
        Build dict of data with Address of entity as key
        :return: 
        """
        new_table = {}
        for record in self._table:
            address = self.build_address(record)
            new_table[address] = record
        return new_table


class ChassisTableHelper(TableHelper):
    @staticmethod
    def build_address(record):
        """
        Chassis address
        :param record:
        :return:
        """
        index = record.get('nbsCmmcChassisIndex') or record.get('Index')
        return Address(index)


class BladeTableHelper(TableHelper):
    @staticmethod
    def build_address(record):
        """
        Blade address
        :param record:
        :return:
        """
        chassis_index = record.get('nbsCmmcSlotChassisIndex') or record.get('ChassisIndex')
        slot_index = record.get('nbsCmmcSlotIndex') or record.get('Index')
        return Address(chassis_index, slot_index)


class PortTableHelper(TableHelper):
    @staticmethod
    def build_address(record):
        """
        Port address
        :param record:
        :return:
        """
        chassis_index = record.get('nbsCmmcPortChassisIndex') or record.get('ChassisIndex')
        slot_index = record.get('nbsCmmcPortSlotIndex') or record.get('SlotIndex')
        index = record.get('nbsCmmcPortIndex') or record.get('Index')
        return Address(chassis_index, slot_index,
                       index)


class PortProtocolTableHelper(object):
    """
    Build protocol table
    """
    def __init__(self, protocol_table):
        self._protocol_table = protocol_table

    def index_dict(self):
        index_dict = {}
        for record in self._protocol_table:
            index_dict[record.get('nbsCmmcSysProtoIndex') or record.get('Index')] = record
        return index_dict
