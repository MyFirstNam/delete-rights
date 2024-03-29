import os
def busid_to_secret(busid):
    line_index = int(busid[2:])+1
    # 获取当前文件的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 设置相对于当前文件的路径
    config_folder = os.path.join(current_dir, '../../../', 'Resource')
    config_file = 'secret_key'

    # 组合并规范化路径
    config_path = os.path.normpath(os.path.join(config_folder, config_file))

    with open(config_path, "r") as f:
        for i in range(line_index):
            line = f.readline()
    return line[6:-1]

def busid_to_IBBE_secret(busid):
    line_index = int(busid[2:])+1

    # 获取当前文件的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 设置相对于当前文件的路径
    config_folder = os.path.join(current_dir, '../../../', 'Resource/IBBE_params')
    config_file = 'IBBE_secret_key.txt'

    # 组合并规范化路径
    config_path = os.path.normpath(os.path.join(config_folder, config_file))

    with open(config_path, "r") as f:
        for i in range(line_index):
            line = f.readline()
    return line.replace('\n','')

if __name__ == '__main__':
     print(busid_to_IBBE_secret('b1000'))
     print(busid_to_secret("b1000"))


