from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

import mrv.command_templates.autoload as command_template

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService


class AutoloadActions:
    """Autoload actions."""

    def __init__(self, cli_service: CliService) -> None:
        self._cli_service = cli_service

    def chassis_table(self) -> list[dict[str, str]]:
        """Chassis table.

        result - [{"index": "1", "model": "MRV Chassis", "serial": "1ndsKsf"}, ]
        """
        output = CommandTemplateExecutor(
            self._cli_service, command_template.CHASSIS_TABLE
        ).execute_command()
        result = self._parse_table(output)
        return result

    def slot_table(self) -> list[dict[str, str]]:
        """Slot table.

        result example - [
                            {
                                "index":"1.1",
                                "slot_model": "Mrv Blade A",
                                "slot_serial": "saf31423"
                            },
                        ]
        """
        output = CommandTemplateExecutor(
            self._cli_service, command_template.SLOT_TABLE
        ).execute_command()
        result = self._parse_table(output)
        return result

    def port_table(self) -> list[dict[str, str]]:
        """Port table.

        result example - [
                            {
                                "index":"1.1.1",
                                "port_model": "Mrv port A",
                                "port_speed": "1Gb"
                            },
                        ]
        """
        output = CommandTemplateExecutor(
            self._cli_service, command_template.PORT_TABLE
        ).execute_command()
        result = self._parse_table(output)
        return result

    def protocol_table(self) -> list[dict[str, str]]:
        """Protocol table."""
        output = CommandTemplateExecutor(
            self._cli_service, command_template.PROTOCOL_TABLE
        ).execute_command()
        result = self._parse_table(output)
        return result

    @staticmethod
    def _parse_table(data: str) -> list[dict[str, str]]:
        """Parse table and build dict."""
        result = []
        line_output = data.split("\n")
        line_output.reverse()
        fields = AutoloadActions._split_string(line_output.pop())
        while line_output:
            values = AutoloadActions._split_string(line_output.pop())
            if len(values) == len(fields):
                result.append(dict(zip(fields, values)))
        return result

    @staticmethod
    def _split_string(string: str) -> list[str]:
        return re.findall('"(.*?)"', string)
