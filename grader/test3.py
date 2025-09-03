#!/usr/bin/env python3
import socket, base64, select, os, re
def recvline(s):
    buf = b''
    while True:
        c = s.recv(1)
        buf += c
        if c == b'' or c == b'\n':
            return buf

def randletters(n):
    res = b''
    while len(res) < n: 
        res += re.sub(br'[^a-z]', b'', os.urandom(512))
    return res[:n]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 6667))

# Verifica se o servidor nega nicks contendo caracteres especiais
nick = b'0' + randletters(7)
s.sendall(b'NIC')
s.sendall(b'K %s' % nick[:2])
s.sendall(b'%s\r\n' % nick[2:])
assert recvline(s) == b':server 432 * %s :Erroneous nickname\r\n' % nick

nick = randletters(3) + b':' + randletters(3)
s.sendall(b'NICK %s\r\n' % nick)
assert recvline(s) == b':server 432 * %s :Erroneous nickname\r\n' % nick

# Verifica se o servidor aceita um nick contendo apenas caracteres permitidos
nick = randletters(8)
s.sendall(b'NICK %s\r\n' % nick)
assert recvline(s) == b':server 001 %s :Welcome\r\n' % nick
assert recvline(s) == b':server 422 %s :MOTD File is missing\r\n' % nick

r,_,_=select.select([s],[],[],0.1)
assert r == []  # não é pra receber mais nada além disso

s.shutdown(socket.SHUT_RDWR)
