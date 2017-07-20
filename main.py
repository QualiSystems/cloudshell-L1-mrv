import os
import sys

from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.layer_one.core.driver_listener import DriverListener
from mrv.mrv_command_executor import MrvCommandExecutor

if __name__ == '__main__':
    print 'Argument List: ', str(sys.argv)

    driver_name = 'MRV L1 Generic driver'

    # os.environ['LOG_PATH'] = os.path.join(os.path.dirname(sys.argv[0]), '..', 'Logs')
    xml_logger = get_qs_logger(log_group=driver_name,
                               log_file_prefix=driver_name + '_xml', log_category='XML')

    command_logger = get_qs_logger(log_group=driver_name,
                                   log_file_prefix=driver_name + '_commands', log_category='COMMANDS')

    command_executor = MrvCommandExecutor(command_logger)
    server = DriverListener(command_executor, xml_logger, command_logger)
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = None
    server.start_listening(port=port)
