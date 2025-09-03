import unittest
import socket, select
from tests.common import recvline, randletters

class TestNickDuplicate(unittest.TestCase):
    def test_nick_duplicate(self):
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s1.connect(('localhost', 6667))
            s2.connect(('localhost', 6667))
            nick = randletters(5)
            s1.sendall(b'NICK %s\r\n' % nick)
            self.assertEqual(recvline(s1), b':server 001 %s :Welcome\r\n' % nick,
                msg="O servidor não aceitou um apelido válido no primeiro cliente.")
            self.assertEqual(recvline(s1), b':server 422 %s :MOTD File is missing\r\n' % nick,
                msg="O servidor não enviou a mensagem de MOTD após registro do apelido no primeiro cliente.")
            s2.sendall(b'NICK %s\r\n' % nick)
            self.assertEqual(recvline(s2), b':server 433 * %s :Nickname is already in use\r\n' % nick,
                msg="O servidor permitiu o uso de apelido duplicado. Verifique se está bloqueando apelidos já em uso.")
            nick2 = randletters(6)
            s2.sendall(b'NICK %s\r\n' % nick2)
            self.assertEqual(recvline(s2), b':server 001 %s :Welcome\r\n' % nick2,
                msg="O servidor não aceitou um apelido válido no segundo cliente.")
            self.assertEqual(recvline(s2), b':server 422 %s :MOTD File is missing\r\n' % nick2,
                msg="O servidor não enviou a mensagem de MOTD após registro do apelido no segundo cliente.")
            s1.sendall(b'NICK %s\r\n' % nick2)
            self.assertEqual(recvline(s1), b':server 433 %s %s :Nickname is already in use\r\n' % (nick, nick2),
                msg="O servidor permitiu troca de apelido para um já em uso. Verifique se está bloqueando corretamente.")
            s2.sendall(b'NICK %s\r\n' % nick.upper())
            self.assertEqual(recvline(s2), b':server 433 %s %s :Nickname is already in use\r\n' % (nick2, nick.upper()),
                msg="O servidor permitiu troca de apelido para um já em uso (case insensitive).")
            newnick = randletters(7)
            s1.sendall(b'NICK %s\r\n' % newnick)
            self.assertEqual(recvline(s1), b':%s NICK %s\r\n' % (nick, newnick),
                msg="O servidor não permitiu troca para um apelido livre após registro.")
            r,_,_=select.select([s1,s2],[],[],0.1)
            self.assertEqual(r, [], msg="Não deve receber mais dados além das mensagens esperadas.")
        finally:
            s1.shutdown(socket.SHUT_WR)
            s2.shutdown(socket.SHUT_WR)
            s1.close()
            s2.close()

if __name__ == '__main__':
    unittest.main()
