import unittest
import socket, os, re, base64, select
from tests.common import recvline, recvcmd, randletters

class TestJoin(unittest.TestCase):
    def test_join(self):
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s1.connect(('localhost', 6667))
            s2.connect(('localhost', 6667))
            s3.connect(('localhost', 6667))
            nick1 = randletters(8)
            s1.sendall(b'NICK %s\r\n' % nick1)
            self.assertEqual(recvline(s1), b':server 001 %s :Welcome\r\n' % nick1)
            self.assertEqual(recvline(s1), b':server 422 %s :MOTD File is missing\r\n' % nick1)
            nick2 = randletters(8)
            s2.sendall(b'NICK %s\r\n' % nick2)
            self.assertEqual(recvline(s2), b':server 001 %s :Welcome\r\n' % nick2)
            self.assertEqual(recvline(s2), b':server 422 %s :MOTD File is missing\r\n' % nick2)
            nick3 = randletters(8)
            s3.sendall(b'NICK %s\r\n' % nick3)
            self.assertEqual(recvline(s3), b':server 001 %s :Welcome\r\n' % nick3)
            self.assertEqual(recvline(s3), b':server 422 %s :MOTD File is missing\r\n' % nick3)
            ch1 = b'#'+randletters(8)
            ch2 = b'#'+randletters(8)
            s1.sendall(b'JOIN %s\r\n' % ch1)
            self.assertEqual(recvcmd(s1, b'JOIN'), b':%s JOIN :%s\r\n' % (nick1, ch1),
                msg="O servidor não enviou JOIN corretamente para o cliente 1.")
            s1.sendall(b'JOIN %s\r\n' % ch2)
            self.assertEqual(recvcmd(s1, b'JOIN'), b':%s JOIN :%s\r\n' % (nick1, ch2),
                msg="O servidor não enviou JOIN corretamente para o cliente 1 no segundo canal.")
            s2.sendall(b'JOIN %s\r\n' % ch1)
            self.assertEqual(recvcmd(s2, b'JOIN'), b':%s JOIN :%s\r\n' % (nick2, ch1),
                msg="O servidor não enviou JOIN corretamente para o cliente 2.")
            s2.sendall(b'JOIN %s\r\n' % ch2)
            self.assertEqual(recvcmd(s2, b'JOIN'), b':%s JOIN :%s\r\n' % (nick2, ch2),
                msg="O servidor não enviou JOIN corretamente para o cliente 2 no segundo canal.")
            s3.sendall(b'JOIN %s\r\n' % ch1)
            self.assertEqual(recvcmd(s3, b'JOIN'), b':%s JOIN :%s\r\n' % (nick3, ch1),
                msg="O servidor não enviou JOIN corretamente para o cliente 3.")
            msg1 = base64.b64encode(os.urandom(32))
            s1.sendall(b'PRIVMSG %s :%s\r\n' % (ch1, msg1))
            self.assertEqual(recvcmd(s2, b'PRIVMSG'), b':%s PRIVMSG %s :%s\r\n' % (nick1, ch1, msg1),
                msg="O servidor não entregou a mensagem do canal ao cliente 2.")
            self.assertEqual(recvcmd(s3, b'PRIVMSG'), b':%s PRIVMSG %s :%s\r\n' % (nick1, ch1, msg1),
                msg="O servidor não entregou a mensagem do canal ao cliente 3.")
            msg2 = base64.b64encode(os.urandom(32))
            s2.sendall(b'PRIVMSG %s :%s\r\n' % (ch2, msg2))
            self.assertEqual(recvcmd(s1, b'PRIVMSG'), b':%s PRIVMSG %s :%s\r\n' % (nick2, ch2, msg2),
                msg="O servidor não entregou a mensagem do canal ao cliente 1.")
            msg3 = base64.b64encode(os.urandom(32))
            s3.sendall(b'PRIVMSG %s :%s\r\n' % (ch1.upper(), msg3))
            received1 = recvcmd(s1, b'PRIVMSG')
            self.assertIn(received1, {
                b':%s PRIVMSG %s :%s\r\n' % (nick3, ch1, msg3),
                b':%s PRIVMSG %s :%s\r\n' % (nick3, ch1.upper(), msg3)
            }, msg="O servidor não entregou a mensagem do canal ao cliente 1 (case insensitive).")
            received2 = recvcmd(s2, b'PRIVMSG')
            self.assertIn(received2, {
                b':%s PRIVMSG %s :%s\r\n' % (nick3, ch1, msg3),
                b':%s PRIVMSG %s :%s\r\n' % (nick3, ch1.upper(), msg3)
            }, msg="O servidor não entregou a mensagem do canal ao cliente 2 (case insensitive).")
            r,_,_=select.select([s1,s2,s3],[],[],0.1)
            self.assertEqual(r, [], msg="Não deve receber mais dados além das mensagens esperadas.")
        finally:
            s1.shutdown(socket.SHUT_WR)
            s2.shutdown(socket.SHUT_WR)
            s3.shutdown(socket.SHUT_WR)
            s1.close()
            s2.close()
            s3.close()

if __name__ == '__main__':
    unittest.main()
