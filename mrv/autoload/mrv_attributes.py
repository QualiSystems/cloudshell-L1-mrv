from cloudshell.layer_one.core.response.resource_info.entities.attributes import StringAttribute


class MRVAttributes(object):
    def __init__(self, resource_table, defined_attributes):
        self._resource_table = resource_table
        self._defined_attributes = defined_attributes

    def get_attribute(self, attribute_name, address):
        """
        Attribute by name
        :param attribute_name: 
        :param address: 
        :return:
        :rtype: cloudshell.layer_one.core.response.resource_info.entities.base.Attribute
        """
        if attribute_name in self._defined_attributes:
            return self._defined_attributes[attribute_name](address)
        raise Exception(self.__class__.__name__, 'Attribute {} is not defined'.format(attribute_name))

    def get_attributes(self, address):
        attributes = []
        for attribute_name in self._defined_attributes:
            attribute = self.get_attribute(attribute_name, address)
            if attribute.value != attribute.DEFAULT_VALUE:
                attributes.append(attribute)
        return attributes


class MRVChassisAttributes(MRVAttributes):
    MODEL_NAME = 'Model Name'
    SERIAL_NUMBER = 'Serial Number'
    OS_VERSION = 'OS Version'

    def __init__(self, resource_table):
        super(MRVChassisAttributes, self).__init__(resource_table, {self.MODEL_NAME: self.model_name,
                                                                    self.SERIAL_NUMBER: self.serial_number,
                                                                    self.OS_VERSION: self.os_version})

    def model_name(self, address):
        value = self._resource_table.get(address).get('nbsCmmcChassisModel')
        return StringAttribute(self.MODEL_NAME, value or StringAttribute.DEFAULT_VALUE)

    def serial_number(self, address):
        value = self._resource_table.get(address).get('nbsCmmcChassisSerialNum')
        return StringAttribute(self.SERIAL_NUMBER, value or StringAttribute.DEFAULT_VALUE)

    def os_version(self, address):
        # value = self._resource_table.get(address).get('nbsCmmcChassisSerialNum')
        value = None
        return StringAttribute(self.SERIAL_NUMBER, value or StringAttribute.DEFAULT_VALUE)


class MRVSlotAttributes(MRVAttributes):
    MODEL_NAME = 'Model Name'
    SERIAL_NUMBER = 'Serial Number'

    def __init__(self, resource_table):
        super(MRVSlotAttributes, self).__init__(resource_table, {self.MODEL_NAME: self.model_name,
                                                                 self.SERIAL_NUMBER: self.serial_number})

    def model_name(self, address):
        value = self._resource_table.get(address).get('nbsCmmcSlotModel')
        return StringAttribute(self.MODEL_NAME, value or StringAttribute.DEFAULT_VALUE)

    def serial_number(self, address):
        value = self._resource_table.get(address).get('nbsCmmcSlotSerialNum')
        return StringAttribute(self.SERIAL_NUMBER, value or StringAttribute.DEFAULT_VALUE)


class MRVPortAttributes(MRVAttributes):
    MODEL_NAME = 'Model Name'
    PROTOCOL_VALUE = 'Protocol Value'
    PROTOCOL_TYPE_VALUE = 'Protocol Type Value'
    DUPLEX = 'Duplex'

    def __init__(self, resource_table):
        super(MRVPortAttributes, self).__init__(resource_table, {})
