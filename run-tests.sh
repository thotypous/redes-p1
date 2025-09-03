#!/bin/sh
# Executa todos os testes, subindo o servidor em background para cada teste
set -e
chmod +x servidor
i=1
for test in test_ping test_ping_fragmented test_nick_validation test_nick_duplicate test_privmsg test_join test_part test_quit test_names test_disconnect; do
    fuser -k 6667/tcp || true
    echo "Executando $test (Passo $i)"
    ./servidor &
    SERVIDOR_PID=$!
    sleep 0.2
    python3 -m unittest tests.$test
    kill $SERVIDOR_PID
    sleep 0.2
    i=$((i + 1))
done
