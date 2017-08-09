#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.layer_one.core.layer_one_driver_exception import LayerOneDriverException


class L1CliHandler(object):
    def __init__(self, logger, session_type=None):
        self._logger = logger
        self._session_type = session_type
        self._cli = CLI(session_pool=SessionPoolManager(max_pool_size=1))

        self._host = None
        self._port = None
        self._username = None
        self._password = None

    def _ssh_session(self):
        return SSHSession(self._host, self._username, self._password, self._port)

    def _telnet_session(self):
        return TelnetSession(self._host, self._username, self._password, self._port)

    def _new_sessions(self):
        if self._session_type and self._session_type.lower() == SSHSession.SESSION_TYPE.lower():
            new_sessions = self._ssh_session()
        elif self._session_type and self._session_type.lower() == TelnetSession.SESSION_TYPE.lower():
            new_sessions = self._telnet_session()
        else:
            new_sessions = [self._ssh_session(), self._telnet_session()]
        return new_sessions

    def define_session_attributes(self, address, username, password):
        """
        Define session attributes
        :param address: 
        :type address: str
        :param username: 
        :param password: 
        :return: 
        """

        address_list = address.split(':')
        if len(address_list) == 2:
            self._host, self._port = address_list
        else:
            self._host = address
        self._username = username
        self._password = password

    def get_cli_service(self, command_mode):
        """
        Create new cli service or get it from pool
        :param command_mode: 
        :return: 
        """
        if not self._host or not self._username or not self._password:
            raise LayerOneDriverException(self.__class__.__name__,
                                          "Cli Attributes is not defined, call Login command first")
        return self._cli.get_session(self._new_sessions(), command_mode, self._logger)
