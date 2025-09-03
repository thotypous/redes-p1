import unittest
import socket, os, re, select
from tests.common import recvline, randletters

class TestDisconnect(unittest.TestCase):
    def test_disconnect(self):
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
            self.assertEqual(recvline(s1), b':%s JOIN :%s\r\n' % (nick1, ch1))
            self.assertEqual(recvline(s1).strip(), b':server 353 %s = %s :%s' % (nick1, ch1, nick1))
            self.assertEqual(recvline(s1), b':server 366 %s %s :End of /NAMES list.\r\n' % (nick1, ch1))
            s2.sendall(b'JOIN %s\r\n' % ch1)
            self.assertEqual(recvline(s1), b':%s JOIN :%s\r\n' % (nick2, ch1))
            self.assertEqual(recvline(s2), b':%s JOIN :%s\r\n' % (nick2, ch1))
            self.assertEqual(recvline(s2).strip(), b':server 353 %s = %s :%s' % (nick2, ch1, b' '.join(sorted([nick1, nick2]))))
            self.assertEqual(recvline(s2), b':server 366 %s %s :End of /NAMES list.\r\n' % (nick2, ch1))
            s1.shutdown(socket.SHUT_WR)
            self.assertTrue(recvline(s2).startswith(b':%s QUIT' % nick1))
            s3.sendall(b'JOIN %s\r\n' % ch1)
            self.assertEqual(recvline(s2), b':%s JOIN :%s\r\n' % (nick3, ch1))
            self.assertEqual(recvline(s3), b':%s JOIN :%s\r\n' % (nick3, ch1))
            self.assertEqual(recvline(s3).strip(), b':server 353 %s = %s :%s' % (nick3, ch1, b' '.join(sorted([nick2, nick3]))))
            self.assertEqual(recvline(s3), b':server 366 %s %s :End of /NAMES list.\r\n' % (nick3, ch1))
            r,_,_=select.select([s2,s3],[],[],0.1)
            self.assertEqual(r, [], msg="Não deve receber nada além do que foi verificado.")
        finally:
            s2.shutdown(socket.SHUT_WR)
            s3.shutdown(socket.SHUT_WR)
            s1.close()
            s2.close()
            s3.close()

if __name__ == '__main__':
    unittest.main()
