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

s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.connect(('localhost', 6667))
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.connect(('localhost', 6667))

# Loga ambos os clientes no servidor
nick1 = randletters(7)
s1.sendall(b'NICK %s\r\n' % nick1)
assert recvline(s1) == b':server 001 %s :Welcome\r\n' % nick1
assert recvline(s1) == b':server 422 %s :MOTD File is missing\r\n' % nick1
nick2 = randletters(6)
s2.sendall(b'NICK %s\r\n' % nick2)
assert recvline(s2) == b':server 001 %s :Welcome\r\n' % nick2
assert recvline(s2) == b':server 422 %s :MOTD File is missing\r\n' % nick2

# Verifica se o cliente2 recebe mensagem enviada pelo cliente1
msg = base64.b64encode(os.urandom(32))
s1.sendall(b'PRIVMSG %s :%s\r\n' % (nick2, msg))
assert recvline(s2) == b':%s PRIVMSG %s :%s\r\n' % (nick1, nick2, msg)

# Verifica se o cliente1 recebe mensagem enviada pelo cliente2
msg = base64.b64encode(os.urandom(32))
s2.sendall(b'PRIVMSG %s :%s\r\n' % (nick1, msg))
assert recvline(s1) == b':%s PRIVMSG %s :%s\r\n' % (nick2, nick1, msg)

# Se o cliente1 trocar de nick, ele não deve mais receber mensagens enviadas ao nick antigo
nick1new = randletters(8)
s1.sendall(b'NICK %s\r\n' % nick1new)
assert recvline(s1) == b':%s NICK %s\r\n' % (nick1, nick1new)
msg = base64.b64encode(os.urandom(32))
s2.sendall(b'PRIVMSG %s :%s\r\n' % (nick1, msg))

# Se o cliente1 trocar de nick, ele não deve mais receber mensagens enviadas ao nick antigo
nick2new = randletters(8)
s2.sendall(b'NICK %s\r\n' % nick2new)
assert recvline(s2) == b':%s NICK %s\r\n' % (nick2, nick2new)
msg = base64.b64encode(os.urandom(32))
s1.sendall(b'PRIVMSG %s :%s\r\n' % (nick2, msg))

nick1, nick2 = nick1new, nick2new

# Verifica se o cliente2 recebe mensagem enviada pelo cliente1 após a troca de nick
msg = base64.b64encode(os.urandom(32))
s1.sendall(b'PRIVMSG %s :%s\r\n' % (nick2.upper(), msg))
assert recvline(s2) in {
        b':%s PRIVMSG %s :%s\r\n' % (nick1, nick2, msg),
        b':%s PRIVMSG %s :%s\r\n' % (nick1, nick2.upper(), msg)
    }

# Verifica se o cliente1 recebe mensagem enviada pelo cliente2 após a troca de nick
msg = base64.b64encode(os.urandom(32))
s2.sendall(b'PRIVMSG %s :%s\r\n' % (nick1.upper(), msg))
assert recvline(s1) in {
        b':%s PRIVMSG %s :%s\r\n' % (nick2, nick1, msg),
        b':%s PRIVMSG %s :%s\r\n' % (nick2, nick1.upper(), msg)
    }

r,_,_=select.select([s1,s2],[],[],0.1)
assert r == []  # não é pra receber mais nada além do que foi verificado

s1.shutdown(socket.SHUT_WR)
s2.shutdown(socket.SHUT_WR)
