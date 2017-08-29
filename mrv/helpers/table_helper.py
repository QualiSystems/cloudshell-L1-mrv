from abc import ABCMeta, abstractmethod

from mrv.helpers.address import Address


class TableHelper(object):
    __metaclass__ = ABCMeta

    def __init__(self, table):
        self._table = table

    @staticmethod
    @abstractmethod
    def build_address(record):
        pass

    def address_dict(self):
        new_table = {}
        for record in self._table:
            address = self.build_address(record)
            new_table[address] = record
        return new_table


class ChassisTableHelper(TableHelper):
    @staticmethod
    def build_address(record):
        return Address(record.get('nbsCmmcChassisIndex'))


class BladeTableHelper(TableHelper):
    @staticmethod
    def build_address(record):
        return Address(record.get('nbsCmmcSlotChassisIndex'), record.get('nbsCmmcSlotIndex'))


class PortTableHelper(TableHelper):
    @staticmethod
    def build_address(record):
        return Address(record.get('nbsCmmcPortChassisIndex'), record.get('nbsCmmcPortSlotIndex'),
                       record.get('nbsCmmcPortIndex'))


class PortProtocolTableHelper(object):
    def __init__(self, protocol_table):
        self._protocol_table = protocol_table

    def index_dict(self):
        index_dict = {}
        for record in self._protocol_table:
            index_dict[record.get('nbsCmmcSysProtoIndex')] = record
        return index_dict
