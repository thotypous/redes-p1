#!/usr/bin/env python3
import socket, base64, select, os
def recvline(s):
    buf = b''
    while True:
        c = s.recv(1)
        buf += c
        if c == b'' or c == b'\n':
            return buf

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 6667))

# Verifica se o servidor lida corretamente com comando recebido em partes quebradas
args = base64.b32encode(os.urandom(16))
s.sendall(b'P')
s.sendall(b'ING')
s.sendall(b' %s' % args[:5])
s.sendall(args[5:] + b'\r')
s.sendall(b'\n')
assert recvline(s) == b':server PONG server :%s\r\n' % args

# Verifica se o servidor lida corretamente com mais de um comando recebido simultaneamente
args1 = base64.b32encode(os.urandom(16))
args2 = base64.b32encode(os.urandom(16))
s.sendall(b'PING %s\r\nPING %s\r\n' % (args1, args2))
assert recvline(s) == b':server PONG server :%s\r\n' % args1
assert recvline(s) == b':server PONG server :%s\r\n' % args2

# Verifica se o servidor lida corretamente com dados residuais em situação de múltiplos comandos
args1 = base64.b32encode(os.urandom(16))
args2 = base64.b32encode(os.urandom(16))
args3 = base64.b32encode(os.urandom(16))
s.sendall(b'PING %s\r\nPING %s\r\nPING %s' % (args1, args2, args3[:4]))
assert recvline(s) == b':server PONG server :%s\r\n' % args1
assert recvline(s) == b':server PONG server :%s\r\n' % args2
r,_,_=select.select([s],[],[],0.1)
assert r == []  # não deve receber nada antes de completar o comando
s.sendall(b'%s\r' % args3[4:])
r,_,_=select.select([s],[],[],0.1)
assert r == []  # não deve receber nada antes de completar o comando
s.sendall(b'\n')
assert recvline(s) == b':server PONG server :%s\r\n' % args3

s.shutdown(socket.SHUT_WR)
