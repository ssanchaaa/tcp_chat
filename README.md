Ассинхронный tcp-чат на threading. Работает нa localhost

# Как запустить
```Bash
mkdir ~/ssanchaaa-tcpchat
cd ~/ssanchaaa-tcpchat
git clone git@github.com:ssanchaaa/tcp_chat.git
cd tcp-chat
./install_requirements.sh
./start_server.sh
```
В отдельном окне терминала:
```Bash
cd ~/ssanchaaa-tcpchat/tcp-chat
./start_client.sh
```

# Файлы
- serverA.py - код сервера
- clientA.py - код клиента
- magma.py - код алгоритма magma для шифрования паролей пользователей

- pass.txt - файл с логинами и паролями пользователей
- last10msg.txt - файл, в который сохраняются послднии сообщния из чата 
- table.txt - таблица для алгоритма магма
