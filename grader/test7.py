#!/usr/bin/env python3
import socket, base64, select, os, re, sys
def recvline(s):
    buf = b''
    while True:
        c = s.recv(1)
        buf += c
        if c == b'' or c == b'\n':
            return buf

def recvcmd(s, cmd):
    while True:
        line = recvline(s)
        arr = line.split()
        if len(arr) >= 2 and arr[0].startswith(b':') and arr[1] == cmd:
            return line

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

# Os clientes entram em 3 canais
ch1 = b'#'+randletters(8)
ch2 = b'#'+randletters(8)
ch3 = b'#'+randletters(8)
s1.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s1, b'JOIN') == b':%s JOIN :%s\r\n' % (nick1, ch1)
s1.sendall(b'JOIN %s\r\n' % ch2)
assert recvcmd(s1, b'JOIN') == b':%s JOIN :%s\r\n' % (nick1, ch2)
s1.sendall(b'JOIN %s\r\n' % ch3)
assert recvcmd(s1, b'JOIN') == b':%s JOIN :%s\r\n' % (nick1, ch3)
s2.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s2, b'JOIN') == b':%s JOIN :%s\r\n' % (nick2, ch1)
s2.sendall(b'JOIN %s\r\n' % ch2)
assert recvcmd(s2, b'JOIN') == b':%s JOIN :%s\r\n' % (nick2, ch2)
s2.sendall(b'JOIN %s\r\n' % ch3)
assert recvcmd(s2, b'JOIN') == b':%s JOIN :%s\r\n' % (nick2, ch3)
s3.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s3, b'JOIN') == b':%s JOIN :%s\r\n' % (nick3, ch1)
s3.sendall(b'JOIN %s\r\n' % ch2)
assert recvcmd(s3, b'JOIN') == b':%s JOIN :%s\r\n' % (nick3, ch2)
s3.sendall(b'JOIN %s\r\n' % ch3)
assert recvcmd(s3, b'JOIN') == b':%s JOIN :%s\r\n' % (nick3, ch3)

# Os clientes saem de canais e cada um fica apenas em um
s1.sendall(b'PART %s\r\n' % ch2)
assert recvcmd(s1, b'PART') == b':%s PART %s\r\n' % (nick1, ch2)
assert recvcmd(s2, b'PART') == b':%s PART %s\r\n' % (nick1, ch2)
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick1, ch2)
s1.sendall(b'PART %s :mensagem de saida deve ser ignorada\r\n' % ch3)
assert recvcmd(s1, b'PART') == b':%s PART %s\r\n' % (nick1, ch3)
assert recvcmd(s2, b'PART') == b':%s PART %s\r\n' % (nick1, ch3)
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick1, ch3)
s2.sendall(b'PART %s\r\n' % ch1)
assert recvcmd(s1, b'PART') == b':%s PART %s\r\n' % (nick2, ch1)
assert recvcmd(s2, b'PART') == b':%s PART %s\r\n' % (nick2, ch1)
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick2, ch1)
s2.sendall(b'PART %s\r\n' % ch3)
assert recvcmd(s2, b'PART') == b':%s PART %s\r\n' % (nick2, ch3)
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick2, ch3)
s3.sendall(b'PART %s\r\n' % ch1)
assert recvcmd(s1, b'PART') == b':%s PART %s\r\n' % (nick3, ch1)
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick3, ch1)
s3.sendall(b'PART %s\r\n' % ch2)
assert recvcmd(s2, b'PART') == b':%s PART %s\r\n' % (nick3, ch2)
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick3, ch2)


# Cada cliente manda uma mensagem
msg1 = base64.b64encode(os.urandom(32))
s1.sendall(b'PRIVMSG %s :%s\r\n' % (ch1, msg1))
msg2 = base64.b64encode(os.urandom(32))
s2.sendall(b'PRIVMSG %s :%s\r\n' % (ch2, msg2))
msg3 = base64.b64encode(os.urandom(32))
s3.sendall(b'PRIVMSG %s :%s\r\n' % (ch3, msg3))

r,_,_=select.select([s1,s2,s3],[],[],0.1)
assert r == []  # ninguém deveria receber as mensagens enviadas

s1.shutdown(socket.SHUT_WR)
s2.shutdown(socket.SHUT_WR)
s3.shutdown(socket.SHUT_WR)
