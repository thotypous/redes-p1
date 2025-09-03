#!/usr/bin/env python3
import socket, base64, os
def recvline(s):
    buf = b''
    while True:
        c = s.recv(1)
        buf += c
        if c == b'' or c == b'\n':
            return buf
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 6667))
for i in range(16):
    # Verifica se o servidor responde a PING
    args = base64.b32encode(os.urandom(16))
    s.sendall(b'PING %s\r\n' % args)
    assert recvline(s) == b':server PONG server :%s\r\n' % args
s.shutdown(socket.SHUT_RDWR)
