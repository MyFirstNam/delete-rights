import subprocess
# from multiprocessing import Process
# import os
# os.environ["PATH"] = "/home/dengx/.conda/envs/deng_delete/bin:" + os.environ["PATH"]
# 定义参数列表
parameter_list = [
    ['b1001', '20001'],
    ['b1002', '20002'],
    ['b1003', '20003'],
    ['b1004', '20004'],
    ['b1005', '20005'],
    ['b1006', '20006'],
    ['b1007', '20007'],
    ['b1008', '20008'],
    ['b1009', '20009'],
    ['b1010', '20010'],
    ['b1011', '20011'],
    ['b1012', '20012'],
    ['b1013', '20013'],
    ['b1014', '20014'],
    ['b1015', '20015'],
    ['b1016', '20016'],
    ['b1017', '20017'],
    ['b1018', '20018'],
    ['b1019', '20019'],
    ['b1020', '20020'],
    ['b1021', '20021'],
    ['b1022', '20022'],
    ['b1023', '20023'],
    ['b1024', '20024'],
    ['b1025', '20025'],
    ['b1026', '20026'],
    ['b1027', '20027'],
    ['b1028', '20028'],
    ['b1029', '20029'],
    ['b1030', '20030'],
    ['b1031', '20031'],
    ['b1032', '20032'],
    ['b1033', '20033'],
    ['b1034', '20034'],
    ['b1035', '20035'],
    ['b1036', '20036'],
    ['b1037', '20037'],
    ['b1038', '20038'],
    ['b1039', '20039'],
    ['b1040', '20040'],
    ['b1041', '20041'],
    ['b1042', '20042'],
    ['b1043', '20043'],
    ['b1044', '20044'],
    ['b1045', '20045'],
    ['b1046', '20046'],
    ['b1047', '20047'],
    ['b1048', '20048'],
    ['b1049', '20049'],
    ['b1050', '20050'],
    ['b1051', '20051'],
    ['b1052', '20052'],
    ['b1053', '20053'],
    ['b1054', '20054'],
    ['b1055', '20055'],
    ['b1056', '20056'],
    ['b1057', '20057'],
    ['b1058', '20058'],
    ['b1059', '20059'],
    ['b1060', '20060'],
    ['b1061', '20061'],
    ['b1062', '20062'],
    ['b1063', '20063'],
    ['b1064', '20064'],
    ['b1065', '20065'],
    ['b1066', '20066'],
    ['b1067', '20067'],
    ['b1068', '20068'],
    ['b1069', '20069'],
    ['b1070', '20070'],
    ['b1071', '20071'],
    ['b1072', '20072'],
    ['b1073', '20073'],
    ['b1074', '20074'],
    ['b1075', '20075'],
    ['b1076', '20076'],
    ['b1077', '20077'],
    ['b1078', '20078'],
    ['b1079', '20079'],
    ['b1080', '20080'],
    ['b1081', '20081'],
    ['b1082', '20082'],
    ['b1083', '20083'],
    ['b1084', '20084'],
    ['b1085', '20085'],
    ['b1086', '20086'],
    ['b1087', '20087'],
    ['b1088', '20088'],
    ['b1089', '20089'],
    ['b1090', '20090'],
    ['b1091', '20091'],
    ['b1092', '20092'],
    ['b1093', '20093'],
    ['b1094', '20094'],
    ['b1095', '20095'],
    ['b1096', '20096'],
    ['b1097', '20097'],
    ['b1098', '20098'],
    ['b1099', '20099'],
]

#创建一个空的进程列表
processes = []

# 循环启动脚本
for params in parameter_list:
    cmd = ["python", "/home/dengx/deng_delete2_6/MYclass/route_bus1.py"] + params
    process = subprocess.Popen(cmd, executable="/home/dengx/.conda/envs/deng_delete/bin/python3")
    processes.append(process)
# 等待所有进程完成
for process in processes:
    process.wait()



# def run_subprocess(params):
#     cmd = ["python", "/home/dengx/deng_delete2_6/MYclass/route_bus1.py"] + params
#     subprocess.Popen(cmd, executable="/home/dengx/.conda/envs/deng_delete/bin/python3").wait()
#
#
# if __name__ == "__main__":
#     processes = []
#
#     for params in parameter_list:
#         process = Process(target=run_subprocess, args=(params,))
#         processes.append(process)
#         process.start()
#
#     for process in processes:
#         process.join()

#/home/dengx/.conda/envs/deng_delete/bin/python3    D:\Python\Interpret\Scripts\python.exe
#/home/dengx/deng_delete2_6/MYclass/

#     ['b1001', '20001'],
#     ['b1002', '20002'],
#      ['b1003', '20003'],
#     # ['b1004', '20004'],
#     # ['b1005', '20005'],
#     # ['b1006', '20006'],
#     # ['b1007', '20007'],
#     # ['b1008', '20008'],
#     # ['b1009', '20009'],
#     # ['b1010', '20010'],
#     # ['b1011', '20011'],
#     # ['b1012', '20012'],
#     # ['b1013', '20013'],
#     # ['b1014', '20014'],
#     # ['b1015', '20015'],
#     # ['b1016', '20016'],
#     # ['b1017', '20017'],
#     # ['b1018', '20018'],
#     # ['b1019', '20019'],
#     # ['b1020', '20020'],
#     # ['b1021', '20021'],
#     # ['b1022', '20022'],
#     # ['b1023', '20023'],
#     # ['b1024', '20024'],
#     # ['b1025', '20025'],
#     # ['b1026', '20026'],
#     # ['b1027', '20027'],
#     # ['b1028', '20028'],
#     # ['b1029', '20029'],
#     # ['b1030', '20030'],
#     # ['b1031', '20031'],
#     # ['b1032', '20032'],
#     # ['b1033', '20033'],
#     # ['b1034', '20034'],
#     # ['b1035', '20035'],
#     # ['b1036', '20036'],
#     # ['b1037', '20037'],
#     # ['b1038', '20038'],
#     # ['b1039', '20039'],
#     # ['b1040', '20040'],
#     # ['b1041', '20041'],
#     # ['b1042', '20042'],
#     # ['b1043', '20043'],
#     # ['b1044', '20044'],
#     # ['b1045', '20045'],
#     # ['b1046', '20046'],
#     # ['b1047', '20047'],
#     # ['b1048', '20048'],
#     # ['b1049', '20049'],
#     # ['b1050', '20050'],
#     # ['b1051', '20051'],
#     # ['b1052', '20052'],
#     # ['b1053', '20053'],
#     # ['b1054', '20054'],
#     # ['b1055', '20055'],
#     # ['b1056', '20056'],
#     # ['b1057', '20057'],
#     # ['b1058', '20058'],
#     # ['b1059', '20059'],
#     # ['b1060', '20060'],
#     # ['b1061', '20061'],
#     # ['b1062', '20062'],
#     # ['b1063', '20063'],
#     # ['b1064', '20064'],
#     # ['b1065', '20065'],
#     # ['b1066', '20066'],
#     # ['b1067', '20067'],
#     # ['b1068', '20068'],
#     # ['b1069', '20069'],
#     # ['b1070', '20070'],
#     # ['b1071', '20071'],
#     # ['b1072', '20072'],
#     # ['b1073', '20073'],
#     # ['b1074', '20074'],
#     # ['b1075', '20075'],
#     # ['b1076', '20076'],
#     # ['b1077', '20077'],
#     # ['b1078', '20078'],
#     # ['b1079', '20079'],
#     # ['b1080', '20080'],
#     # ['b1081', '20081'],
#     # ['b1082', '20082'],
#     # ['b1083', '20083'],
#     # ['b1084', '20084'],
#     # ['b1085', '20085'],
#     # ['b1086', '20086'],
#     # ['b1087', '20087'],
#     # ['b1088', '20088'],
#     # ['b1089', '20089'],
#     # ['b1090', '20090'],
#     # ['b1091', '20091'],
#     # ['b1092', '20092'],
#     # ['b1093', '20093'],
#     # ['b1094', '20094'],
#     # ['b1095', '20095'],
#     # ['b1096', '20096'],
#     # ['b1097', '20097'],
#     # ['b1098', '20098'],
#     # ['b1099', '20099'],
# ]