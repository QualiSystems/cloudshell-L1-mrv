#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime

from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.layer_one.core.driver_listener import DriverListener
from cloudshell.layer_one.core.helper.xml_logger import XMLLogger
from mrv.mrv_command_executor import MrvCommandExecutor

if __name__ == '__main__':

    driver_name = 'MRV_MCC'

    log_path = os.path.join(os.path.dirname(sys.argv[0]), '..', 'Logs')
    os.environ['LOG_PATH'] = log_path

    xml_file_name = driver_name + '--' + datetime.now().strftime('%d-%b-%Y--%H-%M-%S') + '.xml'
    xml_logger = XMLLogger(os.path.join(log_path, driver_name, xml_file_name))

    command_logger = get_qs_logger(log_group=driver_name,
                                   log_file_prefix=driver_name + '_commands', log_category='COMMANDS')

    command_executor = MrvCommandExecutor(command_logger)
    server = DriverListener(command_executor, xml_logger, command_logger)
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = None
    server.start_listening(port=port)
