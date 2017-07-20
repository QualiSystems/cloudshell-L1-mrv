from cloudshell.layer_one.core.command_executor import CommandExecutor
from mrv.cli.mrv_cli_handler import MrvCliHandler
from mrv_driver_commands import MrvDriverCommands


class MrvCommandExecutor(CommandExecutor):
    def __init__(self, logger):
        super(MrvCommandExecutor, self).__init__(logger)
        self._cli_handler = MrvCliHandler(logger)

    def _driver_instance(self):
        return MrvDriverCommands(self._cli_handler, self._logger)
