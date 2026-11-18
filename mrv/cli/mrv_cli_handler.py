from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.service.command_mode_helper import CommandModeHelper

from mrv.cli.l1_cli_handler import L1CliHandler
from mrv.cli.mrv_command_modes import ConfigCommandMode, DefaultCommandMode

if TYPE_CHECKING:
    from cloudshell.cli.service.session_pool_context_manager import (
        SessionPoolContextManager,
    )


class MrvCliHandler(L1CliHandler):
    def __init__(self) -> None:
        super().__init__()
        self.modes = CommandModeHelper.create_command_mode()

    @property
    def _default_mode(self) -> DefaultCommandMode:
        return self.modes[DefaultCommandMode]

    @property
    def _config_mode(self) -> ConfigCommandMode:
        return self.modes[ConfigCommandMode]

    def default_mode_service(self) -> SessionPoolContextManager:
        """Default mode session."""
        return self.get_cli_service(self._default_mode)

    def config_mode_service(self) -> SessionPoolContextManager:
        """Config mode session."""
        return self.get_cli_service(self._config_mode)
