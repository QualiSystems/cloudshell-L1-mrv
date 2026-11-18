from __future__ import annotations

from abc import ABC, abstractmethod

from mrv.helpers.address import Address


class TableHelper(ABC):
    """Associate addresses instances with table data."""

    def __init__(self, table):
        self._table = table

    @staticmethod
    @abstractmethod
    def build_address(record):
        """Address for a specific entity."""
        pass

    def address_dict(self):
        """Build dict of data with Address of entity as key."""
        new_table = {}
        for record in self._table:
            address = self.build_address(record)
            new_table[address] = record
        return new_table


class ChassisTableHelper(TableHelper):
    @staticmethod
    def build_address(record):
        """Chassis address."""
        index = record.get("nbsCmmcChassisIndex") or record.get("Index")
        return Address(index)


class BladeTableHelper(TableHelper):
    @staticmethod
    def build_address(record):
        """Blade address."""
        chassis_index = record.get("nbsCmmcSlotChassisIndex") or record.get(
            "ChassisIndex"
        )
        slot_index = record.get("nbsCmmcSlotIndex") or record.get("Index")
        return Address(chassis_index, slot_index)


class PortTableHelper(TableHelper):
    @staticmethod
    def build_address(record):
        """Port address."""
        chassis_index = record.get("nbsCmmcPortChassisIndex") or record.get(
            "ChassisIndex"
        )
        slot_index = record.get("nbsCmmcPortSlotIndex") or record.get("SlotIndex")
        index = record.get("nbsCmmcPortIndex") or record.get("Index")
        return Address(chassis_index, slot_index, index)


class PortProtocolTableHelper:
    """Build protocol table."""

    def __init__(self, protocol_table):
        self._protocol_table = protocol_table

    def index_dict(self):
        index_dict = {}
        for record in self._protocol_table:
            index_dict[
                record.get("nbsCmmcSysProtoIndex") or record.get("Index")
            ] = record
        return index_dict
