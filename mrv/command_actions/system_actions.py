from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

import mrv.command_templates.system as command_template

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService


class SystemActions:
    """System actions."""

    def __init__(self, cli_service: CliService) -> None:
        self._cli_service = cli_service

    def device_info(self) -> str:
        """Device info."""
        output = CommandTemplateExecutor(
            self._cli_service, command_template.DEVICE_INFO
        ).execute_command()
        return output
