import unittest
import socket, base64, os, select
from tests.common import recvline, randletters

class TestPrivmsg(unittest.TestCase):
    def test_privmsg(self):
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s1.connect(('localhost', 6667))
            s2.connect(('localhost', 6667))
            nick1 = randletters(7)
            s1.sendall(b'NICK %s\r\n' % nick1)
            self.assertEqual(recvline(s1), b':server 001 %s :Welcome\r\n' % nick1,
                msg="O servidor não aceitou apelido válido para o cliente 1.")
            self.assertEqual(recvline(s1), b':server 422 %s :MOTD File is missing\r\n' % nick1)
            nick2 = randletters(6)
            s2.sendall(b'NICK %s\r\n' % nick2)
            self.assertEqual(recvline(s2), b':server 001 %s :Welcome\r\n' % nick2,
                msg="O servidor não aceitou apelido válido para o cliente 2.")
            self.assertEqual(recvline(s2), b':server 422 %s :MOTD File is missing\r\n' % nick2)
            msg = base64.b64encode(os.urandom(32))
            s1.sendall(b'PRIVMSG %s :%s\r\n' % (nick2, msg))
            self.assertEqual(recvline(s2), b':%s PRIVMSG %s :%s\r\n' % (nick1, nick2, msg),
                msg="O servidor não entregou a mensagem privada ao destinatário.")
            msg = base64.b64encode(os.urandom(32))
            s2.sendall(b'PRIVMSG %s :%s\r\n' % (nick1, msg))
            self.assertEqual(recvline(s1), b':%s PRIVMSG %s :%s\r\n' % (nick2, nick1, msg),
                msg="O servidor não entregou a mensagem privada ao destinatário.")
            nick1new = randletters(8)
            s1.sendall(b'NICK %s\r\n' % nick1new)
            self.assertEqual(recvline(s1), b':%s NICK %s\r\n' % (nick1, nick1new),
                msg="O servidor não permitiu troca de apelido para o cliente 1.")
            msg = base64.b64encode(os.urandom(32))
            s2.sendall(b'PRIVMSG %s :%s\r\n' % (nick1, msg))
            # Mensagem não deve ser entregue ao nick antigo
            nick2new = randletters(8)
            s2.sendall(b'NICK %s\r\n' % nick2new)
            self.assertEqual(recvline(s2), b':%s NICK %s\r\n' % (nick2, nick2new),
                msg="O servidor não permitiu troca de apelido para o cliente 2.")
            msg = base64.b64encode(os.urandom(32))
            s1.sendall(b'PRIVMSG %s :%s\r\n' % (nick2, msg))
            # Mensagem não deve ser entregue ao nick antigo
            nick1, nick2 = nick1new, nick2new
            msg = base64.b64encode(os.urandom(32))
            s1.sendall(b'PRIVMSG %s :%s\r\n' % (nick2.upper(), msg))
            received = recvline(s2)
            self.assertIn(received, {
                b':%s PRIVMSG %s :%s\r\n' % (nick1, nick2, msg),
                b':%s PRIVMSG %s :%s\r\n' % (nick1, nick2.upper(), msg)
            }, msg="O servidor não entregou a mensagem privada após troca de nick (case insensitive).")
            msg = base64.b64encode(os.urandom(32))
            s2.sendall(b'PRIVMSG %s :%s\r\n' % (nick1.upper(), msg))
            received = recvline(s1)
            self.assertIn(received, {
                b':%s PRIVMSG %s :%s\r\n' % (nick2, nick1, msg),
                b':%s PRIVMSG %s :%s\r\n' % (nick2, nick1.upper(), msg)
            }, msg="O servidor não entregou a mensagem privada após troca de nick (case insensitive).")
            r,_,_=select.select([s1,s2],[],[],0.1)
            self.assertEqual(r, [], msg="Não deve receber mais dados além das mensagens esperadas.")
        finally:
            s1.shutdown(socket.SHUT_WR)
            s2.shutdown(socket.SHUT_WR)
            s1.close()
            s2.close()

if __name__ == '__main__':
    unittest.main()
