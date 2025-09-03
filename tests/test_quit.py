import unittest
import socket, os, re, select
from tests.common import recvline, recvcmd, randletters

class TestQuit(unittest.TestCase):
    def test_quit(self):
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
            s1.sendall(b'JOIN %s\r\n' % ch1)
            self.assertEqual(recvcmd(s1, b'JOIN'), b':%s JOIN :%s\r\n' % (nick1, ch1))
            s2.sendall(b'JOIN %s\r\n' % ch1)
            self.assertEqual(recvcmd(s2, b'JOIN'), b':%s JOIN :%s\r\n' % (nick2, ch1))
            s3.sendall(b'JOIN %s\r\n' % ch1)
            self.assertEqual(recvcmd(s3, b'JOIN'), b':%s JOIN :%s\r\n' % (nick3, ch1))
            s2.shutdown(socket.SHUT_WR)
            self.assertTrue(recvcmd(s1, b'QUIT').startswith(b':%s QUIT' % nick2))
            self.assertTrue(recvcmd(s3, b'QUIT').startswith(b':%s QUIT' % nick2))
            s3.shutdown(socket.SHUT_WR)
            self.assertTrue(recvcmd(s1, b'QUIT').startswith(b':%s QUIT' % nick3))
            s1.sendall(b'NICK %s\r\n' % nick2)
            self.assertEqual(recvline(s1), b':%s NICK %s\r\n' % (nick1, nick2))
            s1.sendall(b'NICK %s\r\n' % nick3)
            self.assertEqual(recvline(s1), b':%s NICK %s\r\n' % (nick2, nick3))
            r,_,_=select.select([s1],[],[],0.1)
            self.assertEqual(r, [], msg="Não deve receber nada além do que foi verificado.")
        finally:
            s1.shutdown(socket.SHUT_WR)
            s1.close()
            s2.close()
            s3.close()

if __name__ == '__main__':
    unittest.main()
