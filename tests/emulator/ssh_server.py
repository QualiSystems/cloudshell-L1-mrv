"""SSH front-end for MrvDevice. One device state shared by all sessions.

python -m tests.emulator.ssh_server --port 2222 --transcript out.txt [--config-password]
    [--legacy-address] [--legacy-ssh]

Every received line is appended to --transcript as it arrives, so a test can diff
the exact command stream two drivers sent.
"""

from __future__ import annotations

import argparse
import re
import socket
import threading

import paramiko

from tests.emulator.mrv_device import MrvDevice

USER = "admin"

LEGACY_KEX = ("diffie-hellman-group1-sha1",)
LEGACY_CIPHERS = ("aes128-cbc", "3des-cbc")
LEGACY_MACS = ("hmac-sha1",)


class _Auth(paramiko.ServerInterface):
    def __init__(self, password: str):
        self._password = password

    def check_auth_password(self, username, password):
        if username == USER and password == self._password:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):
        return (
            paramiko.OPEN_SUCCEEDED
            if kind == "session"
            else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
        )

    def check_channel_pty_request(self, *args):
        return True

    def check_channel_shell_request(self, channel):
        return True


def _serve_channel(
    chan, device: MrvDevice, lock: threading.Lock, transcript: str, telnet=False
):
    """chan: paramiko channel or plain socket (same sendall/recv interface)."""
    device = device.new_session()
    if telnet:
        device.login_stage = "username"
    chan.sendall(f"\r\nMRV MCC emulator\r\n{device.prompt}".encode())
    buf = b""
    skip_lf = False  # a "\r" already ended the line; drop the "\n" of a split "\r\n"
    while True:
        data = chan.recv(4096)
        if not data:
            break
        if telnet:
            data = re.sub(rb"\xff[\xfb-\xfe].|\xff[\xf0-\xfa]", b"", data)  # IAC
        buf += data
        while True:
            if skip_lf and buf[:1] == b"\n":
                buf = buf[1:]
            skip_lf = False
            m = re.search(rb"\r\n|\r|\n", buf)
            if not m:
                break
            raw, buf = buf[: m.start()], buf[m.end() :]
            skip_lf = m.group() == b"\r"
            line = raw.decode(errors="replace")
            with lock:
                secret = device.secret_input
                out = device.handle(line)
                with open(transcript, "a", encoding="utf-8") as f:
                    f.write(("<password>" if secret else line) + "\n")
                echo = "" if secret else line
                body = f"{echo}\r\n" + (
                    out.replace("\n", "\r\n") + "\r\n" if out else ""
                )
                chan.sendall((body + device.prompt).encode())
    chan.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--transcript", required=True)
    p.add_argument("--password", default="admin")
    p.add_argument("--config-password", action="store_true")
    p.add_argument("--legacy-address", action="store_true")
    p.add_argument("--legacy-ssh", action="store_true")
    p.add_argument("--telnet", action="store_true", help="serve telnet instead of SSH")
    a = p.parse_args()

    device = MrvDevice(a.password, a.config_password, a.legacy_address)
    lock = threading.Lock()
    host_key = paramiko.RSAKey.generate(2048)
    open(a.transcript, "w").close()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", a.port))
    sock.listen(10)

    def client(conn):
        if a.telnet:
            _serve_channel(conn, device, lock, a.transcript, telnet=True)
            return
        t = paramiko.Transport(conn)
        if a.legacy_ssh:
            so = t.get_security_options()
            so.kex = LEGACY_KEX
            so.ciphers = LEGACY_CIPHERS
            so.digests = LEGACY_MACS
            so.key_types = ("ssh-rsa",)
        t.add_server_key(host_key)
        t.start_server(server=_Auth(a.password))
        chan = t.accept(30)
        if chan is not None:
            _serve_channel(chan, device, lock, a.transcript)

    while True:
        conn, _ = sock.accept()
        threading.Thread(target=client, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
