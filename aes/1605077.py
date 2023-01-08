import time
from BitVector import *

Mixer = [
    [BitVector(hexstring="02"), BitVector(hexstring="03"), BitVector(hexstring="01"), BitVector(hexstring="01")],
    [BitVector(hexstring="01"), BitVector(hexstring="02"), BitVector(hexstring="03"), BitVector(hexstring="01")],
    [BitVector(hexstring="01"), BitVector(hexstring="01"), BitVector(hexstring="02"), BitVector(hexstring="03")],
    [BitVector(hexstring="03"), BitVector(hexstring="01"), BitVector(hexstring="01"), BitVector(hexstring="02")]
]
InvMixer = [
    [BitVector(hexstring="0E"), BitVector(hexstring="0B"), BitVector(hexstring="0D"), BitVector(hexstring="09")],
    [BitVector(hexstring="09"), BitVector(hexstring="0E"), BitVector(hexstring="0B"), BitVector(hexstring="0D")],
    [BitVector(hexstring="0D"), BitVector(hexstring="09"), BitVector(hexstring="0E"), BitVector(hexstring="0B")],
    [BitVector(hexstring="0B"), BitVector(hexstring="0D"), BitVector(hexstring="09"), BitVector(hexstring="0E")]
]
AES_modulus = BitVector(bitstring='100011011')

BLOCK_SIZE = 16

round_constant = "01"

SBox = ()
InvSBox = ()


def initialize_s_box():
    box = [i for i in range(0, 256)]
    box[0] = 0x63
    c = BitVector(intVal=0x63, size=8)
    for i in range(1, 256):
        b = BitVector(intVal=i, size=8).gf_MI(AES_modulus, 8)
        s = c ^ b ^ (b << 1) ^ (b << 1) ^ (b << 1) ^ (b << 1)
        box[i] = s.int_val()
    global SBox
    SBox = tuple(box)


def initialize_inverse_s_box():
    box = [0] * 256
    for i in range(0, 256):
        box[SBox[i]] = i
    global InvSBox
    InvSBox = tuple(box)


def transpose(matrix):
    matrix_t = []
    for i in range(0, BLOCK_SIZE//4):
        row = []
        for col in matrix:
            row.append(col[i])
        matrix_t.append(row)
    return matrix_t


def xor_hex_string(a, b):
    xor_value = int(a, 16) ^ int(b, 16)
    return '{:x}'.format(xor_value)


def multiply_finite(bv1, bv2):
    bv3 = bv1.gf_multiply_modular(bv2, AES_modulus, 8)
    return bv3.get_bitvector_in_hex()


def double_round():
    global round_constant
    bv1 = BitVector(hexstring="02")
    bv2 = BitVector(hexstring=round_constant)
    round_constant = multiply_finite(bv1, bv2)


def byte_substitution(byte):
    b = BitVector(hexstring=byte)
    int_val = b.intValue()
    s = SBox[int_val]
    s = BitVector(intVal=s, size=8)
    return s.get_bitvector_in_hex()


def inv_byte_substitution(byte):
    b = BitVector(hexstring=byte)
    int_val = b.intValue()
    s = InvSBox[int_val]
    s = BitVector(intVal=s, size=8)
    return s.get_bitvector_in_hex()


def g(w):
    w.append(w.pop(0))

    w = list(map(byte_substitution, w))

    global round_constant
    w[0] = xor_hex_string(round_constant, w[0])

    double_round()
    return w


def schedule_keys(key_string):
    key_list = list(map(lambda c: format(ord(c), "x"), list(key_string)))
    key_matrix = []
    for i in range(0, BLOCK_SIZE, BLOCK_SIZE//4):
        key_matrix.append(key_list[i:i + BLOCK_SIZE//4])
    keys_list = [key_matrix]

    for iteration in range(0, 10):
        g_value = g(key_matrix[BLOCK_SIZE//4 - 1].copy())
        next_key_matrix = [list(map(xor_hex_string, key_matrix[0], g_value))]
        for i in range(0, BLOCK_SIZE//4 - 1):
            next_key_matrix.append(list(map(xor_hex_string, key_matrix[i+1], next_key_matrix[i])))
        keys_list.append(next_key_matrix)
        key_matrix = next_key_matrix
    return keys_list


def row_col_multiply_sum(row, col):
    factors = list(map(lambda a, b: multiply_finite(a, BitVector(hexstring=b)), row, col))
    xor_sum = factors[0]
    for i in range(1, BLOCK_SIZE//4):
        xor_sum = xor_hex_string(xor_sum, factors[i])
    return xor_sum


def hex_list_to_col_major_matrix(hex_str_list):
    matrix = []
    for i in range(0, BLOCK_SIZE // 4):
        matrix.append(hex_str_list[i:BLOCK_SIZE:BLOCK_SIZE // 4])
    return matrix


def mix_columns(mixer, state_matrix):
    state_matrix = transpose(state_matrix)
    mix_column_matrix = []
    for i in range(0, BLOCK_SIZE // 4):
        row = []
        for j in range(0, BLOCK_SIZE // 4):
            row.append(row_col_multiply_sum(mixer[i], state_matrix[j]))
        mix_column_matrix.append(row)
    return mix_column_matrix


def encrypt(keys_list, hex_list):
    text_matrix = hex_list_to_col_major_matrix(hex_list)

    first_key_matrix = transpose(keys_list[0])
    state_matrix = list(map(lambda a, b: list(map(xor_hex_string, a, b)), text_matrix, first_key_matrix))

    for step in range(1, 11):
        state_matrix = list(map(lambda a: list(map(byte_substitution, a)), state_matrix))

        for i in range(0, BLOCK_SIZE//4):
            for j in range(0, i):
                m = state_matrix[i]
                m.append(m.pop(0))

        if step != 10:
            state_matrix = mix_columns(Mixer, state_matrix)

        round_key_matrix = transpose(keys_list[step])
        state_matrix = list(map(lambda a, b: list(map(xor_hex_string, a, b)), state_matrix, round_key_matrix))

    state_matrix = transpose(state_matrix)
    cipher_hex_value_list = []
    for row in state_matrix:
        cipher_hex_value_list += row
    return cipher_hex_value_list


def decrypt(keys_list, hex_list):
    keys_list.reverse()
    cipher_matrix = hex_list_to_col_major_matrix(hex_list)

    first_key_matrix = transpose(keys_list[0])
    state_matrix = list(map(lambda a, b: list(map(xor_hex_string, a, b)), cipher_matrix, first_key_matrix))

    for step in range(1, 11):
        for i in range(0, BLOCK_SIZE // 4):
            for j in range(0, i):
                m = state_matrix[i]
                m.insert(0, m.pop())

        state_matrix = list(map(lambda a: list(map(inv_byte_substitution, a)), state_matrix))

        round_key_matrix = transpose(keys_list[step])
        state_matrix = list(map(lambda a, b: list(map(xor_hex_string, a, b)), state_matrix, round_key_matrix))

        if step != 10:
            state_matrix = mix_columns(InvMixer, state_matrix)

    state_matrix = transpose(state_matrix)
    decipher_hex_value_list = []
    for row in state_matrix:
        decipher_hex_value_list += row
    return decipher_hex_value_list


def full_encrypt(input_hex_list, round_keys):
    output_hex_list = []
    start_time = time.time()
    for chunk in range(0, len(input_hex_list), BLOCK_SIZE):
        output_hex_list += encrypt(round_keys, input_hex_list[chunk:chunk + BLOCK_SIZE])
    end_time = time.time()
    return output_hex_list, end_time - start_time


def full_decrypt(input_hex_list, round_keys):
    output_hex_list = []
    start_time = time.time()
    for chunk in range(0, len(input_hex_list), BLOCK_SIZE):
        output_hex_list += decrypt(round_keys.copy(), input_hex_list[chunk:chunk + BLOCK_SIZE])
    end_time = time.time()
    return output_hex_list, end_time - start_time


if __name__ == '__main__':
    initialize_s_box()
    initialize_inverse_s_box()

    key = input("Insert 16 character key:\n")
    print()
    key = key.ljust(BLOCK_SIZE, "0")
    key = key[:BLOCK_SIZE]
    key_hex = "".join("{:02x}".format(ord(c)) for c in key)
    print("Key:")
    print(key + " [In ASCII]")
    print(key_hex + " [In HEX]")
    print()

    key_start_time = time.time()
    keys = schedule_keys(key)
    key_end_time = time.time()
    key_time = key_end_time - key_start_time

    option = int(input("Select an option:\n1. Text String 2. File\n"))

    if option == 1:
        plain_text = input("Enter some text:\n")
        print()
        print("Plain Text:")
        print(plain_text + " [In ASCII]")
        l_just_amount = BLOCK_SIZE - (len(plain_text) % BLOCK_SIZE)
        plain_text = plain_text.ljust(len(plain_text) + l_just_amount, "0")
        plain_text_hex_list = list(map(lambda c: format(ord(c), "x"), list(plain_text)))
        print("".join(plain_text_hex_list) + " [In HEX]")
        print()

        cipher_hex_list, encryption_time = full_encrypt(plain_text_hex_list, keys.copy())

        print("Cipher Text:")
        cipher = "".join(list(map(lambda x: chr(int(x, 16)), cipher_hex_list)))
        print(cipher + " [In ASCII]")
        print("".join(cipher_hex_list) + " [In HEX]")
        print()

        message_hex_list, decryption_time = full_decrypt(cipher_hex_list, keys.copy())

        print("Deciphered Text:")
        message = "".join(list(map(lambda x: chr(int(x, 16)), message_hex_list)))
        print(message[:-l_just_amount] + " [In ASCII]")
        print("".join(message_hex_list) + " [In HEX]")
        print()

        print("Execution time:")
        print("Key scheduling: ", key_time)
        print("Encryption: ", encryption_time)
        print("Decryption: ", decryption_time)

    elif option == 2:
        file_name = input("Enter a filename:\n")
        print()
        with open(file_name, "rb") as rf:
            file_data = []
            c = rf.read(1).hex()
            while c:
                file_data += c
                c = rf.read(1).hex()

            print("Input file: ")
            print("".join(file_data))
            print()

            l_just_amount = BLOCK_SIZE - (len(file_data) % BLOCK_SIZE)
            file_data += l_just_amount * ["30"]

            cipher_list, encryption_time = full_encrypt(file_data, keys.copy())
            print("Cipher: ")
            print("".join(cipher_list))
            print()

            with open("output_" + file_name, "wb") as wf:
                message_list, decryption_time = full_decrypt(cipher_list, keys.copy())

                message_list = message_list[:-l_just_amount]

                print("Output file: ")
                message_hex = "".join(message_list)
                print(message_hex)
                print()

                wf.write(bytes.fromhex(message_hex))

                print("Execution time:")
                print("Key scheduling: ", key_time)
                print("Encryption: ", encryption_time)
                print("Decryption: ", decryption_time)
            pass
        pass

    else:
        print("Invalid input.")
