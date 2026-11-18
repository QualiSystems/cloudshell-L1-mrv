from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

import mrv.command_templates.mapping as command_template

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService


class MappingActions:
    def __init__(self, cli_service: CliService) -> None:
        self._cli_service = cli_service

    def map_bidi(self, src_port: str, dst_port: str) -> str:
        """Bidirectional mapping."""
        output = CommandTemplateExecutor(
            self._cli_service, command_template.MAP_BIDI
        ).execute_command(src_port=src_port, dst_port=dst_port)
        return output

    def map_uni(self, src_port: str, dst_ports: list[str]) -> str:
        """Unidirectional mapping."""
        executor = CommandTemplateExecutor(self._cli_service, command_template.MAP_UNI)
        output = ""
        for dst_port in dst_ports:
            output += executor.execute_command(src_port=src_port, dst_port=dst_port)
        return output

    def map_clear(self, ports: list[str]) -> str:
        """Clear bidirectional mapping."""
        output = ""
        executor = CommandTemplateExecutor(
            self._cli_service, command_template.MAP_CLEAR
        )
        for port in ports:
            output += executor.execute_command(port=port)
        return output

    def map_clear_to(self, src_port: str, dst_ports: list[str]) -> str:
        """Clear unidirectional mapping."""
        executor = CommandTemplateExecutor(
            self._cli_service, command_template.MAP_CLEAR_TO
        )
        output = ""
        for dst_port in dst_ports:
            output += executor.execute_command(src_port=src_port, dst_port=dst_port)
        return output
