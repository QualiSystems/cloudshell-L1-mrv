from __future__ import annotations

import re


class Address:
    """MRV address entity."""

    CHASSIS_LENGTH = 1
    SLOT_LENGTH = 2
    PORT_LENGTH = 3

    def __init__(self, *address_indexes) -> None:
        if 0 < len(address_indexes) < 4:
            self._address_indexes = tuple(str(i) for i in address_indexes)
        else:
            raise Exception("Incorrect address")

    def build_str(self) -> str:
        """Build address str."""
        return ".".join(self._address_indexes)

    def build_str_no_dot(self) -> str:
        """Build address."""
        return "".join(self._address_indexes[:2]) + str(
            self._address_indexes[-1]
        ).zfill(2)

    def get_chassis_address(self) -> Address:
        """Related Chassis address."""
        return Address(*self._address_indexes[: self.CHASSIS_LENGTH])

    def get_slot_address(self) -> Address:
        """Related slot address."""
        return Address(*self._address_indexes[: self.SLOT_LENGTH])

    def get_port_address(self) -> Address:
        """Related port address."""
        return Address(*self._address_indexes[: self.PORT_LENGTH])

    def is_chassis(self) -> bool:
        """Check if address is chassis address."""
        return len(self._address_indexes) == self.CHASSIS_LENGTH

    def is_slot(self) -> bool:
        """Check if address is slot address."""
        return len(self._address_indexes) == self.SLOT_LENGTH

    def is_port(self) -> bool:
        """Check if address is port address."""
        return len(self._address_indexes) == self.PORT_LENGTH

    def index(self) -> str:
        """Entity index."""
        return self._address_indexes[-1]

    @staticmethod
    def from_mrv_address(raw_address: str) -> Address:
        """Build address from string address, like "1.2.3"."""
        return Address(*raw_address.split("."))

    @staticmethod
    def from_cs_address(raw_address: str) -> Address:
        """Build address from string address, like "10.0.1.1/2/3"."""
        return Address(*re.sub(r"\d+.\d+.\d+.\d+", "1", raw_address).split("/"))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Address):
            return NotImplemented
        return self._address_indexes == other._address_indexes

    def __hash__(self):
        return self._address_indexes.__hash__()

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Address):
            return NotImplemented
        return not self == other

    def __str__(self) -> str:
        return self.build_str()

    def __repr__(self) -> str:
        return self.__str__()
