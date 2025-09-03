import socket, base64, select, os, re, sys

def recvline(s):
    buf = b''
    s.settimeout(2)
    try:
        while True:
            c = s.recv(1)
            if not c:
                break
            buf += c
            if c == b'\n':
                break
        return buf
    except socket.timeout:
        raise AssertionError("Timeout ao esperar resposta do servidor. Verifique se o servidor está enviando respostas corretamente.")
    finally:
        s.settimeout(None)

def recvcmd(s, cmd):
    s.settimeout(2)
    try:
        for _ in range(50):
            line = recvline(s)
            arr = line.split()
            if len(arr) >= 2 and arr[0].startswith(b':') and arr[1] == cmd:
                return line
        raise AssertionError(f"Timeout ou resposta inesperada ao esperar comando {cmd.decode()}. Verifique se o servidor está enviando a resposta correta.")
    finally:
        s.settimeout(None)

def randletters(n):
    res = b''
    while len(res) < n:
        res += re.sub(br'[^a-z]', b'', os.urandom(512))
    return res[:n]
