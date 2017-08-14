from xml.etree.ElementTree import Element

from cloudshell.layer_one.core.response.response_info import ResponseInfo


class GetStateIdResponseInfo(ResponseInfo):
    ATTRIBUTE_NAME = 'StateId'

    def __init__(self, state_id):
        self._state_id = state_id

    def build_xml_node(self):
        response_info_node = self._build_response_info_node()
        response_info_node.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        response_info_node.attrib['xsi:type'] = "StateInfo"
        attribute_node = Element(self.ATTRIBUTE_NAME)
        attribute_node.text = self._state_id
        response_info_node.append(attribute_node)
        return response_info_node


class AttributeValueResponseInfo(ResponseInfo):
    ATTRIBUTE_NAME = 'Value'

    def __init__(self, value):
        self._value = value if value else 'NA'

    def build_xml_node(self):
        response_info_node = self._build_response_info_node()
        response_info_node.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        response_info_node.attrib['xsi:type'] = "AttributeInfoResponse"
        attribute_node = Element(self.ATTRIBUTE_NAME)
        attribute_node.text = self._value
        response_info_node.append(attribute_node)
        return response_info_node
