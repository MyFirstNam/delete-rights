def hex_xor(hex1,hex2):  # 实现256位，数据间的异或
    return '{:064X}'.format(int(hex1,16) ^ int(hex2,16))

print()