from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

import mrv.command_templates.port_configuration as command_template

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService


class PortConfigurationActions:
    """Port configuration actions."""

    def __init__(self, cli_service: CliService) -> None:
        self._cli_service = cli_service

    def set_port_duplex(self, duplex_value: str) -> str:
        """Set port duplex."""
        output = CommandTemplateExecutor(
            self._cli_service, command_template.SET_DUPLEX
        ).execute_command(duplex_value=duplex_value)
        return output

    def set_auto_neg_on(self) -> str:
        """Set port auto-negotiation ON."""
        output = CommandTemplateExecutor(
            self._cli_service, command_template.AUTO_NEG_ON
        ).execute_command()
        return output

    def set_auto_neg_off(self) -> str:
        """Set port auto-negotiation OFF."""
        output = CommandTemplateExecutor(
            self._cli_service, command_template.AUTO_NEG_OFF
        ).execute_command()
        return output
