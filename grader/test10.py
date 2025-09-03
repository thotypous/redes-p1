#!/usr/bin/env python3
import socket, base64, select, os, re, sys
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

s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.connect(('localhost', 6667))
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.connect(('localhost', 6667))
s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s3.connect(('localhost', 6667))

# Loga os clientes no servidor
nick1 = randletters(8)
s1.sendall(b'NICK %s\r\n' % nick1)
assert recvline(s1) == b':server 001 %s :Welcome\r\n' % nick1
assert recvline(s1) == b':server 422 %s :MOTD File is missing\r\n' % nick1
nick2 = randletters(8)
s2.sendall(b'NICK %s\r\n' % nick2)
assert recvline(s2) == b':server 001 %s :Welcome\r\n' % nick2
assert recvline(s2) == b':server 422 %s :MOTD File is missing\r\n' % nick2
nick3 = randletters(8)
s3.sendall(b'NICK %s\r\n' % nick3)
assert recvline(s3) == b':server 001 %s :Welcome\r\n' % nick3
assert recvline(s3) == b':server 422 %s :MOTD File is missing\r\n' % nick3

ch1 = b'#'+randletters(8)
s1.sendall(b'JOIN %s\r\n' % ch1)
assert recvline(s1) == b':%s JOIN :%s\r\n' % (nick1, ch1)
assert recvline(s1).strip() == b':server 353 %s = %s :%s' % (nick1, ch1, nick1)
assert recvline(s1) == b':server 366 %s %s :End of /NAMES list.\r\n' % (nick1, ch1)

# Quando o cliente2 entrar, o nome do cliente1 também tem que estar na lista
s2.sendall(b'JOIN %s\r\n' % ch1)
assert recvline(s1) == b':%s JOIN :%s\r\n' % (nick2, ch1)
assert recvline(s2) == b':%s JOIN :%s\r\n' % (nick2, ch1)
assert recvline(s2).strip() == b':server 353 %s = %s :%s' % (nick2, ch1, b' '.join(sorted([nick1, nick2])))
assert recvline(s2) == b':server 366 %s %s :End of /NAMES list.\r\n' % (nick2, ch1)

# Quando o cliente1 sair, o cliente2 deve ser notificado
s1.shutdown(socket.SHUT_WR)
assert recvline(s2).startswith(b':%s QUIT' % nick1)

# Quando o cliente3 entrar, o nome do cliente2 também tem que estar na lista
s3.sendall(b'JOIN %s\r\n' % ch1)
assert recvline(s2) == b':%s JOIN :%s\r\n' % (nick3, ch1)
assert recvline(s3) == b':%s JOIN :%s\r\n' % (nick3, ch1)
assert recvline(s3).strip() == b':server 353 %s = %s :%s' % (nick3, ch1, b' '.join(sorted([nick2, nick3])))
assert recvline(s3) == b':server 366 %s %s :End of /NAMES list.\r\n' % (nick3, ch1)

r,_,_=select.select([s2,s3],[],[],0.1)
assert r == []  # não deve receber nada além do que foi verificado até o momento

s2.shutdown(socket.SHUT_WR)
s3.shutdown(socket.SHUT_WR)
