import pandas
import InfoTransCenter

# 用于产生随机字符串
import secrets

file_name = ""

df = pandas.read_excel(file_name)

processor = InfoTransCenter.InfoTransCenter(
    host="127.0.0.1",
    user="root",
    port=3306,
    password="rootroot",
    database="InfoTransCenter"
)

for index, row in df:
    from_bus_id = row[""]  # todo
    to_bus_id = row[""]  # todo
    # 产生随机数作为 info_id
    info_id_len = 32  # 16字节
    info_id = secrets.token_bytes(info_id_len).hex()
    processor.insert_record(info_id, from_bus_id, to_bus_id)
df.close()
