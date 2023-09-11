from __future__ import annotations

import re
from typing import TYPE_CHECKING, Callable

from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.helper.logger import get_l1_logger
from cloudshell.layer_one.core.layer_one_driver_exception import LayerOneDriverException
from cloudshell.layer_one.core.response.response_info import (
    AttributeValueResponseInfo,
    GetStateIdResponseInfo,
    ResourceDescriptionResponseInfo,
)

from mrv.autoload.resource_description import ResourceDescription
from mrv.cli.mrv_cli_handler import MrvCliHandler
from mrv.cli.mrv_command_modes import ConfigChassisCommandMode, ConfigPortCommandMode

# from mrv.cli.simulator.cli_simulator import CLISimulator
from mrv.command_actions.autoload_actions import AutoloadActions
from mrv.command_actions.chassis_configuration_actions import (
    ChassisConfigurationActions,
)
from mrv.command_actions.mapping_actions import MappingActions
from mrv.command_actions.port_configuration_actions import PortConfigurationActions
from mrv.command_actions.system_actions import SystemActions
from mrv.helpers.address import Address
from mrv.helpers.table_helper import (
    BladeTableHelper,
    ChassisTableHelper,
    PortProtocolTableHelper,
    PortTableHelper,
)

if TYPE_CHECKING:
    from cloudshell.layer_one.core.helper.runtime_configuration import (
        RuntimeConfiguration,
    )

logger = get_l1_logger(name=__name__)


class DriverCommands(DriverCommandsInterface):
    """MRV driver commands implementation."""

    def __init__(self, runtime_config: RuntimeConfiguration) -> None:
        self._runtime_config = runtime_config
        self._cli_handler = MrvCliHandler()
        # self._cli_handler = CLISimulator(
        #     "test",
        #     os.path.join(
        #         os.path.dirname(os.path.abspath(__file__)), "cli", "simulator", "data"
        #     )
        # )
        self._ports_attributes_setters: dict[str, Callable] = {
            "Duplex": self._set_port_duplex,
            "Protocol": self._set_protocol,
            "Auto Negotiation": self._set_auto_neg,
        }

    @property
    def _chassis_table(self):
        """Chassis data."""
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session)
            return ChassisTableHelper(autoload_actions.chassis_table()).address_dict()

    @property
    def _slot_table(self):
        """Slot data."""
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session)
            return BladeTableHelper(autoload_actions.slot_table()).address_dict()

    @property
    def _port_table(self):
        """Port data."""
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session)
            return PortTableHelper(autoload_actions.port_table()).address_dict()

    @property
    def _port_protocol_table(self):
        """Port protocol data."""
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session)
            return PortProtocolTableHelper(
                autoload_actions.protocol_table()
            ).index_dict()

    def login(self, address: str, username: str, password: str) -> None:
        """Perform login operation on the device."""
        self._cli_handler.define_session_attributes(address, username, password)
        with self._cli_handler.default_mode_service() as session:
            system_actions = SystemActions(session)
            logger.info(system_actions.device_info())

    def get_resource_description(self, address: str) -> ResourceDescriptionResponseInfo:
        """Auto-load function to retrieve all information from the device."""
        response_info = ResourceDescriptionResponseInfo(
            ResourceDescription(
                address,
                self._chassis_table,
                self._slot_table,
                self._port_table,
                self._port_protocol_table,
            ).build()
        )
        return response_info

    def get_state_id(self) -> GetStateIdResponseInfo:
        """Check if CS synchronized with the device."""
        response_data = self._chassis_table[Address(1)].get("nbsCmmcChassisName")
        if not response_data:
            response_data = -1
        return GetStateIdResponseInfo(response_data)

    def set_state_id(self, state_id: str) -> None:
        """Set synchronization state id to the device.

        Called after Autoload or SyncFomDevice commands
        """
        with self._cli_handler.config_mode_service() as session:
            detached_chassis_mode = ConfigChassisCommandMode.detached_instance(
                "1", session.command_mode
            )
            with session.enter_mode(detached_chassis_mode) as chassis_config_session:
                chassis_config = ChassisConfigurationActions(chassis_config_session)
                chassis_config.set_chassis_name(state_id)

    def map_bidi(self, src_port: str, dst_port: str) -> None:
        """Create a bidirectional connection between source and destination ports."""
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session)
            try:
                mapping_actions.map_bidi(
                    Address.from_cs_address(src_port).build_str(),
                    Address.from_cs_address(dst_port).build_str(),
                )
            except CommandExecutionException:
                logger.debug("Using an old address format")
                mapping_actions.map_bidi(
                    Address.from_cs_address(src_port).build_str_no_dot(),
                    Address.from_cs_address(dst_port).build_str_no_dot(),
                )

    def map_uni(self, src_port: str, dst_ports: list[str]) -> None:
        """Unidirectional mapping of two ports."""
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session)
            _src_port = Address.from_cs_address(src_port).build_str()
            _dst_ports = [
                Address.from_cs_address(port).build_str() for port in dst_ports
            ]
            mapping_actions.map_uni(_src_port, _dst_ports)

    def map_clear(self, ports: list[str]) -> None:
        """Remove simplex/duplex connection ending on the destination port."""
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session)
            _ports = [Address.from_cs_address(port).build_str() for port in ports]
            mapping_actions.map_clear(_ports)

    def map_clear_to(self, src_port: str, dst_ports: list[str]) -> None:
        """Remove simplex/duplex connection ending on the destination port."""
        with self._cli_handler.config_mode_service() as session:
            mapping_actions = MappingActions(session)
            _src_port = Address.from_cs_address(src_port).build_str()
            _dst_ports = [
                Address.from_cs_address(port).build_str() for port in dst_ports
            ]
            mapping_actions.map_clear_to(_src_port, _dst_ports)

    def get_attribute_value(self, cs_address: str, attribute_name: str) -> None:
        """Retrieve attribute value from the device."""
        raise LayerOneDriverException("GetAttributeValue command is not supported")

    def set_attribute_value(
        self, cs_address: str, attribute_name: str, attribute_value: str
    ) -> AttributeValueResponseInfo:
        """Set attribute value to the device."""
        address = Address.from_cs_address(cs_address)
        if address.is_chassis() or address.is_slot():
            raise LayerOneDriverException(
                "SetAttributeValue for Chassis or Slot/Blade is not supported"
            )
        else:
            attribute_setter = self._ports_attributes_setters.get(attribute_name)
            if attribute_setter:
                attribute_setter(address, attribute_value)
            else:
                raise LayerOneDriverException(
                    f"SetAttributeValue is not supported for attribute {attribute_name}"
                )
            return AttributeValueResponseInfo(attribute_value)

    def _set_port_duplex(self, address: Address, value: str):
        """Change duplex value for a specific port."""
        with self._cli_handler.config_mode_service() as session:
            detached_port_mode = ConfigPortCommandMode.detached_instance(
                address.build_str(), session.command_mode
            )
            with session.enter_mode(detached_port_mode) as config_port_session:
                port_config_actions = PortConfigurationActions(config_port_session)
                if str(value) == "2":
                    duplex_value = "half"
                else:
                    duplex_value = "full"
                port_config_actions.set_port_duplex(duplex_value)

    def _set_protocol(self, address: Address, value: str) -> None:
        """Change protocol value for a specific port."""
        pass

    def _set_auto_neg(self, address: Address, value: str) -> None:
        """Change auto-negotiation value for a specific port."""
        with self._cli_handler.config_mode_service() as session:
            detached_port_mode = ConfigPortCommandMode.detached_instance(
                address.build_str(), session.command_mode
            )
            with session.enter_mode(detached_port_mode) as config_port_session:
                port_config_actions = PortConfigurationActions(config_port_session)
                if re.match(r"[Ff]alse", value):
                    port_config_actions.set_auto_neg_off()
                else:
                    port_config_actions.set_auto_neg_on()

    def map_tap(self, src_port: str, dst_ports: list[str]) -> None:
        return self.map_uni(src_port, dst_ports)

    def set_speed_manual(
        self, src_port: str, dst_port: str, speed: str, duplex: str
    ) -> None:
        raise NotImplementedError
