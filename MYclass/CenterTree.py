from flask import Flask, request, jsonify, Blueprint
import json
import datetime
import pprint
# 辅助函数
def print_with_timestamp(message):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

centerroute = Flask(__name__)
@centerroute.route("/tree/postx/endpointx", methods=['POST'])
# POST格式为JSON格式
def intentionAly():
    data = request.json
    data = json.loads(data)
    print_with_timestamp(data)

    dataTransferPath = [
          {"from": "b1000", "to": "b1001"},
          {"from": "b1000", "to": "b1003"},
          {"from": "b1001", "to": "b1002"},
          {"from": "b1003", "to": "b1004"}
    ]

    # dataTransferPath = [
    #       {"from": "b1000", "to": "b1003"},
    #       {"from": "b1002", "to": "b1000"},
    #       {"from": "b1002", "to": "b1001"},
    #       {"from": "b1001", "to": "b1004"}
    # ]
    # dataTransferPath = [
    #     {"from": "b1000", "to": "b1001"},
    #     {"from": "b1000", "to": "b1002"},
    #     {"from": "b1000", "to": "b1003"},
    #     {"from": "b1000", "to": "b1004"},
    #     {"from": "b1000", "to": "b1005"},
    #     {"from": "b1000", "to": "b1006"},
    #     {"from": "b1000", "to": "b1007"},
    #     {"from": "b1000", "to": "b1008"},
    #     {"from": "b1000", "to": "b1009"},
    #     {"from": "b1001", "to": "b1010"},
    #     {"from": "b1001", "to": "b1011"},
    #     {"from": "b1001", "to": "b1012"},
    #     {"from": "b1001", "to": "b1013"},
    #     {"from": "b1001", "to": "b1014"},
    #     {"from": "b1001", "to": "b1015"},
    #     {"from": "b1001", "to": "b1016"},
    #     {"from": "b1001", "to": "b1017"},
    #     {"from": "b1001", "to": "b1018"},
    #     {"from": "b1001", "to": "b1019"},
    #     {"from": "b1002", "to": "b1020"},
    #     {"from": "b1002", "to": "b1021"},
    #     {"from": "b1002", "to": "b1022"},
    #     {"from": "b1002", "to": "b1023"},
    #     {"from": "b1002", "to": "b1024"},
    #     {"from": "b1002", "to": "b1025"},
    #     {"from": "b1002", "to": "b1026"},
    #     {"from": "b1002", "to": "b1027"},
    #     {"from": "b1002", "to": "b1028"},
    #     {"from": "b1002", "to": "b1029"},
    #     {"from": "b1003", "to": "b1030"},
    #     {"from": "b1003", "to": "b1031"},
    #     {"from": "b1003", "to": "b1032"},
    #     {"from": "b1003", "to": "b1033"},
    #     {"from": "b1003", "to": "b1034"},
    #     {"from": "b1003", "to": "b1035"},
    #     {"from": "b1003", "to": "b1036"},
    #     {"from": "b1003", "to": "b1037"},
    #     {"from": "b1003", "to": "b1038"},
    #     {"from": "b1003", "to": "b1039"},
    #     {"from": "b1004", "to": "b1040"},
    #     {"from": "b1004", "to": "b1041"},
    #     {"from": "b1004", "to": "b1042"},
    #     {"from": "b1004", "to": "b1043"},
    #     {"from": "b1004", "to": "b1044"},
    #     {"from": "b1004", "to": "b1045"},
    #     {"from": "b1004", "to": "b1046"},
    #     {"from": "b1004", "to": "b1047"},
    #     {"from": "b1004", "to": "b1048"},
    #     {"from": "b1004", "to": "b1049"},
    #     {"from": "b1005", "to": "b1050"},
    #     {"from": "b1005", "to": "b1051"},
    #     {"from": "b1005", "to": "b1052"},
    #     {"from": "b1005", "to": "b1053"},
    #     {"from": "b1005", "to": "b1054"},
    #     {"from": "b1005", "to": "b1055"},
    #     {"from": "b1005", "to": "b1056"},
    #     {"from": "b1005", "to": "b1057"},
    #     {"from": "b1005", "to": "b1058"},
    #     {"from": "b1005", "to": "b1059"},
    #     {"from": "b1006", "to": "b1060"},
    #     {"from": "b1006", "to": "b1061"},
    #     {"from": "b1006", "to": "b1062"},
    #     {"from": "b1006", "to": "b1063"},
    #     {"from": "b1006", "to": "b1064"},
    #     {"from": "b1006", "to": "b1065"},
    #     {"from": "b1006", "to": "b1066"},
    #     {"from": "b1006", "to": "b1067"},
    #     {"from": "b1006", "to": "b1068"},
    #     {"from": "b1006", "to": "b1069"},
    #     {"from": "b1007", "to": "b1070"},
    #     {"from": "b1007", "to": "b1071"},
    #     {"from": "b1007", "to": "b1072"},
    #     {"from": "b1007", "to": "b1073"},
    #     {"from": "b1007", "to": "b1074"},
    #     {"from": "b1007", "to": "b1075"},
    #     {"from": "b1007", "to": "b1076"},
    #     {"from": "b1007", "to": "b1077"},
    #     {"from": "b1007", "to": "b1078"},
    #     {"from": "b1007", "to": "b1079"},
    #     {"from": "b1008", "to": "b1080"},
    #     {"from": "b1008", "to": "b1081"},
    #     {"from": "b1008", "to": "b1082"},
    #     {"from": "b1008", "to": "b1083"},
    #     {"from": "b1008", "to": "b1084"},
    #     {"from": "b1008", "to": "b1085"},
    #     {"from": "b1008", "to": "b1086"},
    #     {"from": "b1008", "to": "b1087"},
    #     {"from": "b1008", "to": "b1088"},
    #     {"from": "b1008", "to": "b1089"},
    #     {"from": "b1009", "to": "b1090"},
    #     {"from": "b1009", "to": "b1091"},
    #     {"from": "b1009", "to": "b1092"},
    #     {"from": "b1009", "to": "b1093"},
    #     {"from": "b1009", "to": "b1094"},
    #     {"from": "b1009", "to": "b1095"},
    #     {"from": "b1009", "to": "b1096"},
    #     {"from": "b1009", "to": "b1097"},
    #     {"from": "b1009", "to": "b1098"},
    #     {"from": "b1009", "to": "b1099"}
    # ]
    return dataTransferPath

if __name__ == "__main__":
    centerroute.run(host='127.0.0.1', port=20099, debug=True)