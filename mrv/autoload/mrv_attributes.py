class ChassisAttributes(object):
    def __init__(self, chassis_table):
        self._chassis_table = chassis_table

        self._attributes = {'Model Name': self.model_name,
                            'Serial Number': self.serial_number}

    def model_name(self, address):
        return self._chassis_table.get(address).get('nbsCmmcChassisModel')

    def serial_number(self, address):
        return self._chassis_table.get(address).get('nbsCmmcChassisSerialNum')
