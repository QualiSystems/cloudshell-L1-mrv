from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.response.response_info import ResourceDescriptionResponseInfo
from mrv.autoload.resource_description import ResourceDescription
from mrv.command_actions.autoload_actions import AutoloadActions
from mrv.command_actions.system_actions import SystemActions


class MrvDriverCommands(DriverCommandsInterface):
    def __init__(self, cli_handler, logger):
        """
        :param cli_handler: 
        :type cli_handler: mrv.cli.mrv_cli_handler.MrvCliHandler
        :param logger: 
        """
        self._cli_handler = cli_handler
        self._logger = logger

    def map_bidi(self, src_port, dst_port):
        pass

    def get_resource_description(self, address):
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            chassis_table = autoload_actions.chassis_table()
            slot_table = autoload_actions.slot_table()
            port_table = autoload_actions.port_table()
            response_info = ResourceDescriptionResponseInfo(
                ResourceDescription(address, chassis_table, slot_table, port_table).build())
        return response_info

    def map_clear(self, src_port, dst_port):
        pass

    def login(self, address, username, password):
        self._cli_handler.define_session_attributes(address, username, password)
        with self._cli_handler.default_mode_service() as session:
            system_actions = SystemActions(session, self._logger)
            self._logger.info(system_actions.device_info())

    def map_clear_to(self, src_port, dst_port):
        pass