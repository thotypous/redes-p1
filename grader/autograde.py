#!/usr/bin/env python3
import os
import signal
import json
import subprocess
import time


def main():
    tests_weight = 10*[1]
    scores = {}

    if os.path.exists('./compilar'):
        print('Chamando ./compilar')
        os.chmod('./compilar', 0o755)
        os.system('./compilar')

    for i, weight in enumerate(tests_weight):
        testno = i + 1
        os.chmod('./servidor', 0o755)
        pid = os.spawnlp(os.P_NOWAIT, './servidor', './servidor')
        print('\nServidor executando no pid=%d' % pid)
        time.sleep(1)

        test = 'test%d' % testno
        scores[test] = 0

        print('Teste #%d' % testno)
        timeout = 5
        p = subprocess.Popen('grader/%s.py' % test)
        try:
            if p.wait(timeout=timeout) == 0:
                scores[test] = weight
                print('OK')
        except subprocess.TimeoutExpired:
            print('%s: TIMEOUT (%.3f s)' % (test, timeout))
            os.kill(p.pid, signal.SIGINT)

        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)

    print(json.dumps({'scores':scores}))


if __name__ == '__main__':
    main()
