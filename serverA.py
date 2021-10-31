import select, socket, datetime, threading, re
from magma import scrambler as scrm, decoder as dcdr, text_from_bits as t_f_b

print('Для выключения сервера нажмите Ctrl+C.')
sock = socket.socket()
sock.bind(('', 5050))
sock.listen(10) 
sock.setblocking(0)

inputs = [sock]  # сокеты, которые будем читать
outputs = []  # сокеты, в которые надо писать
messages ={} # здесь будем хранить сообщения для сокетов
names ={} # здесь будем хранить имена для сокетов
lstMsg = [] # здесь будут последние 10 сообщений, выводимые при авторизации 
iterLstMsg = 0 # для проверки количества сообщений

def last10msgUpd(msg):
    global lstMsg
    global iterLstMsg 
    if iterLstMsg >= 10:
        lstMsg.pop(0)
        lstMsg.append(msg)
    else:
        lstMsg.append(msg)
    iterLstMsg = iterLstMsg + 1
    

def last10msgSend(connection):
    global lstMsg
    msgStr = "\n".join(lstMsg)
    connection.send(msgStr.encode("utf-8"))


def registration(connection, nAme, passwd):
    a = "a"
    
    #try:
    if a == "a":
        with open("pass.txt", "r") as f:
            for line in f:
                match = re.search(r"([A-z0-9_]+)(\^\$\@)([A-z0-9_]+)", line)
                if match[1] == nAme:
                    print("Есть такой логин")
                    connection.send("^$@existsLog".encode("utf-8"))
                    return 0
        
        with open("pass.txt", "a") as f:
            f.write(f"\n{nAme}^$@{hex(int(scrm(passwd), 2))[2:]}")
        connection.send(f"^$@goodAuth".encode('utf-8'))
        if nAme not in names.values():
            names[connection] = nAme
        last10msgSend(connection)
        return 1
    #except:
       # print("some error")
        #return 0
    
    
def log_in(connection, nAme, passwd):
    fLog = 0
       
    try:
        with open("pass.txt", "r") as f:
            for line in f:
                match = re.search(r"([A-z0-9_]+)(\^\$\@)([A-z0-9_]+)", line)
                if match[1] == nAme:
                    fLog = 1
                    if match[3] == hex(int(scrm(passwd), 2))[2:]:
                        if nAme not in names.values():
                            names[connection] = nAme
                            print(f'name "{names.get(connection, "unnamed")}" saved')
                            connection.send("^$@goodLog_in".encode("utf-8"))
                            last10msgSend(connection)
                            return 1
                        else:
                            connection.send("^$@alredExistLog".encode("utf-8"))
                            return 0
                        
    except:
        print("no file pass.txt")
        return 0
        
    if fLog == 0:
        connection.send("^$@incLog".encode("utf-8"))
    else:
        connection.send("^$@incPass".encode("utf-8"))
    return 0
        

def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


def clear_resource(resource):
    """
    Метод очистки ресурсов использования сокета
    """
    if resource in outputs:
        outputs.remove(resource)
    if resource in inputs:
        inputs.remove(resource)
    try:
        resource.close()
    except:
        pass
    if resource in messages:
        del messages[resource]
        
    if resource in names:
        del names[resource]

    print('closing connection ' + str(resource))


print('\nОжидание подключения...')
while True:
    # вызов `select.select` который проверяет сокеты в 
    # списках: `inputs`, `outputs` и по готовности, хотя бы
    # одного - возвращает списки: `reads`, `send`, `excepts`
    name = "unnamed"
    try:
        reads, send, excepts = select.select(inputs, outputs, inputs)
    except ValueError:
        for i in inputs:
            if i.fileno() == -1:
                clear_resource(i)
        for i in outputs:
            if i.fileno() == -1:
                clear_resource(i)
            
    # Далее проверяются эти списки, и принимаются 
    # решения в зависимости от назначения списка

    # список READS - сокеты, готовые к чтению
    for conn in reads:
        if conn == sock:
            # если это серверный сокет, то пришел новый
            # клиент, принимаем подключение
            new_conn, client_addr = conn.accept()
            print('Успешное подключение!')
            # устанавливаем неблокирующий сокет
            new_conn.setblocking(0)
            # поместим новый сокет в очередь 
            # на прослушивание
            inputs.append(new_conn)

            
        else:
            # если это НЕ серверный сокет, то 
            # клиент хочет что-то сказать
            data = ""
            try:
                data = conn.recv(1024)
                if data[:8].decode("utf-8") == "@$^name=":
                    msg = re.search(r"(\@\$\^name=)([A-z0-9_]+)(\@\$\^pass=)([A-z0-9_]+)", data.decode("utf-8"))
                    nAme = msg[2]
                    passwd = msg[4]
                    a = log_in(conn, nAme, passwd)
                    if a == 0:
                        continue
                        
                elif data[:8].decode("utf-8") == "@$^auth=":
                    msg = re.search(r"(\@\$\^auth=)([A-z0-9_]+)(\@\$\^pass=)([A-z0-9_]+)", data.decode("utf-8"))
                    nAme = msg[2]
                    passwd = msg[4]
                    a = registration(conn, nAme, passwd)
                    if a == 0:
                        continue
                
            except:
                print("fffffffffffffffffffffffffffff")
                
            if data:
                # если сокет прочитался и есть сообщение 
                # то кладебудем сообщение в словарь, где 
                # ключом т сокет клиента
                print(f"getting data: {data.decode('utf-8')}")
                messages[conn] = [data]
                msggg = messages.get(conn, "&&&")
                

                if data[:8].decode("utf-8") == "@$^name=":
                    last10msgUpd("server: " + msg[2] + " подключился")
                elif data[:8].decode("utf-8") == "@$^auth=":
                    last10msgUpd("server: " + msg[2] + " зарегистрирован")
                else:
                    last10msgUpd(str(datetime.datetime.now().time()) + " " + data.decode('utf-8'))

                for i in list(messages):
                    if i == conn:
                        continue
                # если есть сообщения - то переводим  
                    try:
                        if data[:8].decode("utf-8") == "@$^name=":
                            i.send(f"server: {msg[2]} подключился".encode('utf-8'))
                        elif data[:8].decode("utf-8") == "@$^auth=":
                            i.send(f"server: {msg[2]} зарегистрирован".encode('utf-8'))
                        else:
                            i.send(f"{datetime.datetime.now().time()} {data.decode('utf-8')}".encode("utf-8"))
                    except:
                        print("some problem with connect")
                        clear_resource(i)
                        clear_resource(conn)
                # добавляем соединение клиента в очередь 
                # на готовность к приему сообщений от сервера
                if conn not in outputs:
                    outputs.append(conn)
            
            else:
                last10msgUpd('server: '+(names.get(conn, "unnamed"))+ ' отключился')
                for i in list(messages):
                    if i == conn:
                        continue
                # если есть сообщения - то переводим 
                # его в верхний регистр и отсылаем
                    try:
                        i.send(f'server: {(names.get(conn, "unnamed"))} отключился'.encode("utf-8"))
                    except:
                        names.pop(conn)
                print(f'{conn} отключился...')
                # если сообщений нет, то клиент
                # закрыл соединение или отвалился 
                # удаляем его сокет из всех очередей
                clear_resource(conn)
                # закрываем сокет как положено, тем 
                # самым очищаем используемые ресурсы
                # удаляем сообщения для данного сокета

    # список SEND - сокеты, готовые принять сообщение


    # список EXCEPTS - сокеты, в которых произошла ошибка
    for conn in excepts:
        print(f'{conn} отвалился...')
        # удаляем сокет с ошибкой из всех очередей
        inputs.remove(conn)
        if conn in outputs:
            outputs.remove(conn)
        # закрываем сокет как положено, тем 
        # самым очищаем используемые ресурсы
        conn.close()
        # удаляем сообщения для данного сокета
        del messages[conn]