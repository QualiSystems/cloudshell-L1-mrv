import re


class Address(object):
    CHASSIS_LENGTH = 1
    SLOT_LENGTH = 2
    PORT_LENGTH = 3

    def __init__(self, *address_indexes):
        if 0 < len(address_indexes) < 4:
            self._address_indexes = address_indexes
        else:
            raise Exception(self.__class__.__name__, 'Incorrect address')

    def build_str(self):
        return '.'.join(self._address_indexes)

    def get_chassis_address(self):
        return Address(*self._address_indexes[:self.CHASSIS_LENGTH])

    def get_slot_address(self):
        return Address(*self._address_indexes[:self.SLOT_LENGTH])

    def get_port_address(self):
        return Address(*self._address_indexes[:self.PORT_LENGTH])

    def is_chassis(self):
        return len(self._address_indexes) == self.CHASSIS_LENGTH

    def is_slot(self):
        return len(self._address_indexes) == self.SLOT_LENGTH

    def is_port(self):
        return len(self._address_indexes) == self.PORT_LENGTH

    def index(self):
        return self._address_indexes[-1]

    @staticmethod
    def from_mrv_address(raw_address):
        """
        Build address from string address, like '1.2.3'
        :param raw_address: 
        :return: 
        """
        return Address(*raw_address.split('.'))

    @staticmethod
    def from_cs_address(raw_address):
        """
        Build address from string address, like '10.0.1.1/2/3'
        :param raw_address: 
        :return: 
        """
        return Address(*re.sub(r'\d+.\d+.\d+.\d+', '1', raw_address).split('/'))

    def __eq__(self, other):
        """
        :param other:
        :type other: Address
        :return: 
        """
        return self._address_indexes == other._address_indexes

    def __hash__(self):
        return self._address_indexes.__hash__()

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return 'Address: ' + self.build_str()

    def __repr__(self):
        return self.__str__()
