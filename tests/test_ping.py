import unittest
import socket, base64, os
from tests.common import recvline

class TestPing(unittest.TestCase):
    def test_ping(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('localhost', 6667))
            for i in range(16):
                args = base64.b32encode(os.urandom(16))
                s.sendall(b'PING %s\r\n' % args)
                resposta = recvline(s)
                self.assertEqual(resposta, b':server PONG server :%s\r\n' % args,
                    msg=f"O servidor não respondeu corretamente ao comando PING. Verifique se está formatando a resposta corretamente e usando o payload recebido.")
        finally:
            s.shutdown(socket.SHUT_RDWR)
            s.close()

if __name__ == '__main__':
    unittest.main()
