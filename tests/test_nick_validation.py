import unittest
import socket, os, re, select
from tests.common import recvline, randletters

class TestNickValidation(unittest.TestCase):
    def test_nick_invalid(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('localhost', 6667))
            nick = b'0' + randletters(7)
            s.sendall(b'NIC')
            s.sendall(b'K %s' % nick[:2])
            s.sendall(b'%s\r\n' % nick[2:])
            resposta = recvline(s)
            self.assertEqual(resposta, b':server 432 * %s :Erroneous nickname\r\n' % nick,
                msg="O servidor aceitou um apelido inválido. Verifique a validação do apelido.")
        finally:
            s.close()

    def test_nick_special_char(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('localhost', 6667))
            nick = randletters(3) + b':' + randletters(3)
            s.sendall(b'NICK %s\r\n' % nick)
            resposta = recvline(s)
            self.assertEqual(resposta, b':server 432 * %s :Erroneous nickname\r\n' % nick,
                msg="O servidor aceitou um apelido com caractere especial. Verifique a validação do apelido.")
        finally:
            s.close()

    def test_nick_valid(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('localhost', 6667))
            nick = randletters(8)
            s.sendall(b'NICK %s\r\n' % nick)
            resposta1 = recvline(s)
            resposta2 = recvline(s)
            self.assertEqual(resposta1, b':server 001 %s :Welcome\r\n' % nick,
                msg="O servidor não aceitou um apelido válido. Verifique a lógica de registro.")
            self.assertEqual(resposta2, b':server 422 %s :MOTD File is missing\r\n' % nick,
                msg="O servidor não enviou a mensagem de MOTD após registro do apelido.")
            r,_,_=select.select([s],[],[],0.1)
            self.assertEqual(r, [], msg="Não deve receber mais dados além das mensagens esperadas.")
        finally:
            s.close()

if __name__ == '__main__':
    unittest.main()
