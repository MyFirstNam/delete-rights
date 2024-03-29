block_size = 32
def padPKCS7(x):  # 负责增加填充，k为8
    ch = block_size - (len(x) % block_size)
    return x + bytes([ch] * ch)


def unpadPKCS7(s):  # 该函数负责对解密后的明文去填充
    i = s[-1]
    if i == 0 or s[-i:] != bytes([i] * i):
        return s
    return s[0:-i]

if __name__ == '__main__':
    s = padPKCS7(b'b1000')
    print(s)
    s = unpadPKCS7(s)
    print(s.decode())

