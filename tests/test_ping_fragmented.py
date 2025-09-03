import unittest
import socket, base64, select, os
from tests.common import recvline

class TestPingFragmented(unittest.TestCase):
    def test_ping_fragmented(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('localhost', 6667))

            # Verifica se o servidor lida corretamente com comando recebido em partes quebradas
            args = base64.b32encode(os.urandom(16))
            s.sendall(b'P')
            s.sendall(b'ING')
            s.sendall(b' %s' % args[:5])
            s.sendall(args[5:] + b'\r')
            s.sendall(b'\n')
            resposta = recvline(s)
            self.assertEqual(resposta, b':server PONG server :%s\r\n' % args,
                msg="O servidor não lida corretamente com comandos recebidos em partes quebradas. Verifique o buffer de leitura.")

            # Verifica se o servidor lida corretamente com mais de um comando recebido simultaneamente
            args1 = base64.b32encode(os.urandom(16))
            args2 = base64.b32encode(os.urandom(16))
            s.sendall(b'PING %s\r\nPING %s\r\n' % (args1, args2))
            self.assertEqual(recvline(s), b':server PONG server :%s\r\n' % args1)
            self.assertEqual(recvline(s), b':server PONG server :%s\r\n' % args2)

            # Verifica se o servidor lida corretamente com dados residuais em situação de múltiplos comandos
            args1 = base64.b32encode(os.urandom(16))
            args2 = base64.b32encode(os.urandom(16))
            args3 = base64.b32encode(os.urandom(16))
            s.sendall(b'PING %s\r\nPING %s\r\nPING %s' % (args1, args2, args3[:4]))
            self.assertEqual(recvline(s), b':server PONG server :%s\r\n' % args1)
            self.assertEqual(recvline(s), b':server PONG server :%s\r\n' % args2)
            r,_,_=select.select([s],[],[],0.1)
            self.assertEqual(r, [], msg="Não deve receber nada antes de completar o comando.")
            s.sendall(b'%s\r' % args3[4:])
            r,_,_=select.select([s],[],[],0.1)
            self.assertEqual(r, [], msg="Não deve receber nada antes de completar o comando.")
            s.sendall(b'\n')
            self.assertEqual(recvline(s), b':server PONG server :%s\r\n' % args3)

        finally:
            s.shutdown(socket.SHUT_WR)
            s.close()

if __name__ == '__main__':
    unittest.main()
