from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis


class ResourceInfoBuilder(object):
    def __init__(self, address, chassis_table, slot_table, port_table):
        self._address = address
        self._chassis_table = chassis_table
        self._slot_table = slot_table
        self._port_table = port_table

        self._chassis = {}

        """{'nbsCmmcChassisEnablePortChangeTraps': 'on', 'nbsCmmcChassisEnableLINTraps': 'on',
            'nbsCmmcChassisModel': 'NC316-288PMC-4X', 'nbsCmmcChassisPS3Status': 'bad',
            'nbsCmmcChassisResetAllModules': 'notSupported', 'nbsCmmcChassisPowerStatus': 'sufficient',
            'nbsCmmcChassisFan3Status': 'good', 'nbsCmmcChassisCountersState': 'notSupported',
            'nbsCmmcChassisTemperatureMin': '5', 'nbsCmmcChassisEnableSwitchoverTraps': 'on',
            'nbsCmmcChassisPS2Status': 'good', 'nbsCmmcChassisLoopbackTimeout': '0',
            'nbsCmmcChassisFan5Status': 'bad', 'nbsCmmcChassisObjectId': '', 'nbsCmmcChassisLoader': '4294967295',
            'nbsCmmcChassisNVAreaAdmin': '4294967295', 'nbsCmmcChassisFirmwareLoad': '',
            'nbsCmmcChassisPS1Status': 'good', 'nbsCmmcChassisPortInfoBitMap': '',
            'nbsCmmcChassisNumberOfSlots': '10', 'nbsCmmcChassisFan1Status': 'good',
            'nbsCmmcChassisTemperature': '35', 'nbsCmmcChassisNumberOfPortsBitMap': '',
            'nbsCmmcChassisFan4Status': 'good', 'nbsCmmcChassisPS4Status': 'bad',
            'nbsCmmcChassisFace': '7c:70:72:6f:74:3a:65:74:68:65:72:7c:74:65:6d:70:3a:2d:32:31:34:37:34:38:33:36:34:38:7c:70:73:31:3a:36:7c:70:73:32:3a:36:7c:70:73:33:3a:36:7c:70:73:34:3a:36:7c',
            'nbsCmmcChassisSerialNum': '033007AT78W6', 'nbsCmmcChassisEnablePortTraps': 'on',
            'nbsCmmcChassisEnablePortDiagsTraps': 'on', 'nbsCmmcChassisSlotListBitMap': '',
            'nbsCmmcChassisEnableModuleSpecificTraps': 'on', 'nbsCmmcChassisFan2Status': 'good',
            'nbsCmmcChassisCrossConnect': 'operating', 'nbsCmmcChassisIfIndex': '100000',
            'nbsCmmcChassisFan8Status': 'bad', 'nbsCmmcChassisIndex': '1', 'nbsCmmcChassisNVAreaOper': '4294967295',
            'nbsCmmcChassisEnableChassisTraps': 'on', 'nbsCmmcChassisFan7Status': 'bad',
            'nbsCmmcChassisNVAreaBanks': '0', 'nbsCmmcChassisType': 'bu82',
            'nbsCmmcChassisEnableLoopbackTraps': 'on', 'nbsCmmcChassisHardwareRevision': '2, Firmware: 0x1a',
            'nbsCmmcChassisName': '636357620834532313', 'nbsCmmcChassisFan6Status': 'bad',
            'nbsCmmcChassisFirmwareCaps': '00', 'nbsCmmcChassisEnableLinkTraps': 'on',
            'nbsCmmcChassisEnableAutoReset': 'notSupported', 'nbsCmmcChassisTemperatureLimit': '45',
            'nbsCmmcChassisEnableSlotChangeTraps': 'on'}"""

    def _build_chassis(self):
        for record in self._chassis_table:
            index = record.get('nbsCmmcChassisIndex')
            model = record.get('nbsCmmcChassisModel')
            serial = record.get('nbsCmmcChassisSerialNum')
            chassis = Chassis(index, self._address, model, serial)
            self._chassis[index] = chassis

    def get__info(self):
        self._build_chassis()
        return self._chassis
