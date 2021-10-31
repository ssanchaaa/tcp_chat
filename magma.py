import numpy as np

#переводим текст в биты
def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


#переводим биты в текст
def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').replace(b'\x00', b'').decode(encoding, errors) or '\0'


def separator(bits, count):
    mas = ([bits[i:i+count] for i in range(0, len(bits), count)])
    if len(mas[(len(mas))-1]) != count:
        for _ in range(count - len(mas[(len(mas))-1])):
           mas[len(mas)-1] = '0' + mas[len(mas)-1]
    #print(mas)
    return mas


def get_table():
    S = np.loadtxt("table.txt", int)
    return S


def get_key():
    # print("Введите систему счисления ключа: ")
    # s_sche = int(input())
    s_sche = 10
    #print("Введите ключ: ")
    a = "123456789"
    key = bin(int(a, s_sche))[2:].zfill(256)
    round_key = separator(key, 32)
    round_key = round_key*3+round_key[::-1]
    return key, round_key



#сложение по модулю 2^32 с раундовым ключом
def plus2v32(block, round_key):
    b = int(block, base=2) + int(round_key, base=2)
    if b.bit_length() > 32:
        b = bin(b)[2:]
        b = b[len(b) - 32:].zfill(32)
    else:
        b = bin(b)[2:].zfill(32)
    return b


#замена по блокам
def change(block, key):
    key8 = separator(key, 4)
    key8 = key8[::-1]
    result = ""
    for i in range(8):
        a = int(str(block[i][int(key8[i], base=2)]), base=10)
        a = int(bin(a)[2:], base=10)
        result = str(a).zfill(4) + result
    return result


#циклический сдвиг влево
def shift11(bits):
    return bits[11:]+bits[:11]


#функция f
def f(block, r_key):
    pls = plus2v32(block, r_key)
    cng = change(table, pls)
    sft = shift11(cng)
    return sft


def scrambler(txt):
    #print("Введите текст для шифрования: ")
    txt = text_to_bits(txt)
    mtxt = separator(txt, 64)
    result = ""
    for n1 in mtxt:
        n11 = separator(n1, 32)
        for q in range(32):
            helper = f(n11[1], round_key[q])
            n11[0] = bin(int(n11[0], 2) ^ int(helper, 2))[2:].zfill(32)
            if q != 31:
                n11[0], n11[1] = n11[1], n11[0]
            else:
                res = n11[0] + n11[1]
        result = result+res
    return result


def decoder(scram):
    result = ""
    mscrm = separator(scram, 64)
    r_key = round_key[::-1]
    for n1 in mscrm:
        n11 = separator(n1, 32)
        for q in range(32):
            helper = f(n11[1], r_key[q])
            n11[0] = bin(int(n11[0], 2) ^ int(helper, 2))[2:].zfill(32)
            if q != 31:
                n11[0], n11[1] = n11[1], n11[0]
            else:
                res = n11[0] + n11[1]
        result = result+res
    return result

key, round_key = get_key()
table = get_table()
f_scram = open("scram.txt", "w")
f_decode = open("decoderText.txt", "w")

def start():
    a = 1
    print('Введите "1" для шифрования или "2" для шифрования и дешифрования: ')
    while a == 1:
        command = input()
        if command == "1":
            scram = scrambler()
            f_scram.write(f"scram_bits: {scram.strip()}\n")
            a = 0
        elif command == "2":
            scram = scrambler()
            decode = decoder(scram)
            f_scram.write("scram_bits: ")
            f_scram.write(scram)
            f_decode.write("decoder_text: ")
            f_decode.write(text_from_bits(decode))
            a = 0
        else:
            print('Error. Введите "1" для шифрования или "2" для шифрования и дешифрования: ')


#start()

# a = scrambler("9089888786")
# print("scr = ", a)
# b = decoder(a)
# print("dcd = ", b)
# print(text_from_bits(b))


f_scram.close()
f_decode.close()