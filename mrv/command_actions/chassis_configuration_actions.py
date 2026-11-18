from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

import mrv.command_templates.chassis_configuration as command_template

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService


class ChassisConfigurationActions:
    """Chassis configuration actions."""

    def __init__(self, cli_service: CliService) -> None:
        self._cli_service = cli_service

    def set_chassis_name(self, chassis_name: str) -> str:
        """Set chassis name."""
        output = CommandTemplateExecutor(
            self._cli_service, command_template.SET_CHASSIS_NAME
        ).execute_command(chassis_name=chassis_name)
        return output
