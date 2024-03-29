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

    # dataTransferPath = [
    #       {"from": "b1000", "to": "b1001"},
    #       {"from": "b1000", "to": "b1003"},
    #       {"from": "b1001", "to": "b1002"},
    #       {"from": "b1003", "to": "b1004"}
    # ]

    dataTransferPath = [
          {"from": "b1000", "to": "b1001"},
          {"from": "b1001", "to": "b1002"},
          {"from": "b1002", "to": "b1003"},
          {"from": "b1003", "to": "b1004"}
    ]


    return dataTransferPath

if __name__ == "__main__":
    centerroute.run(host='127.0.0.1', port=20099, debug=True)

    # dataTransferPath = [
    #     {"from": "b1000", "to": "b1001"},
    #     {"from": "b1001", "to": "b1002"},
    #     {"from": "b1002", "to": "b1003"},
    #     {"from": "b1003", "to": "b1004"},
    #     {"from": "b1004", "to": "b1005"},
    #     {"from": "b1005", "to": "b1006"},
    #     {"from": "b1006", "to": "b1007"},
    #     {"from": "b1007", "to": "b1008"},
    #     {"from": "b1008", "to": "b1009"},
    #     {"from": "b1009", "to": "b1010"},
    #     {"from": "b1010", "to": "b1011"},
    #     {"from": "b1011", "to": "b1012"},
    #     {"from": "b1012", "to": "b1013"},
    #     {"from": "b1013", "to": "b1014"},
    #     {"from": "b1014", "to": "b1015"},
    #     {"from": "b1015", "to": "b1016"},
    #     {"from": "b1016", "to": "b1017"},
    #     {"from": "b1017", "to": "b1018"},
    #     {"from": "b1018", "to": "b1019"},
    #     {"from": "b1019", "to": "b1020"},
    #     {"from": "b1020", "to": "b1021"},
    #     {"from": "b1021", "to": "b1022"},
    #     {"from": "b1022", "to": "b1023"},
    #     {"from": "b1023", "to": "b1024"},
    #     {"from": "b1024", "to": "b1025"},
    #     {"from": "b1025", "to": "b1026"},
    #     {"from": "b1026", "to": "b1027"},
    #     {"from": "b1027", "to": "b1028"},
    #     {"from": "b1028", "to": "b1029"},
    #     {"from": "b1029", "to": "b1030"},
    #     {"from": "b1030", "to": "b1031"},
    #     {"from": "b1031", "to": "b1032"},
    #     {"from": "b1032", "to": "b1033"},
    #     {"from": "b1033", "to": "b1034"},
    #     {"from": "b1034", "to": "b1035"},
    #     {"from": "b1035", "to": "b1036"},
    #     {"from": "b1036", "to": "b1037"},
    #     {"from": "b1037", "to": "b1038"},
    #     {"from": "b1038", "to": "b1039"},
    #     {"from": "b1039", "to": "b1040"},
    #     {"from": "b1040", "to": "b1041"},
    #     {"from": "b1041", "to": "b1042"},
    #     {"from": "b1042", "to": "b1043"},
    #     {"from": "b1043", "to": "b1044"},
    #     {"from": "b1044", "to": "b1045"},
    #     {"from": "b1045", "to": "b1046"},
    #     {"from": "b1046", "to": "b1047"},
    #     {"from": "b1047", "to": "b1048"},
    #     {"from": "b1048", "to": "b1049"},
    #     {"from": "b1049", "to": "b1050"},
    #     {"from": "b1050", "to": "b1051"},
    #     {"from": "b1051", "to": "b1052"},
    #     {"from": "b1052", "to": "b1053"},
    #     {"from": "b1053", "to": "b1054"},
    #     {"from": "b1054", "to": "b1055"},
    #     {"from": "b1055", "to": "b1056"},
    #     {"from": "b1056", "to": "b1057"},
    #     {"from": "b1057", "to": "b1058"},
    #     {"from": "b1058", "to": "b1059"},
    #     {"from": "b1059", "to": "b1060"},
    #     {"from": "b1060", "to": "b1061"},
    #     {"from": "b1061", "to": "b1062"},
    #     {"from": "b1062", "to": "b1063"},
    #     {"from": "b1063", "to": "b1064"},
    #     {"from": "b1064", "to": "b1065"},
    #     {"from": "b1065", "to": "b1066"},
    #     {"from": "b1066", "to": "b1067"},
    #     {"from": "b1067", "to": "b1068"},
    #     {"from": "b1068", "to": "b1069"},
    #     {"from": "b1069", "to": "b1070"},
    #     {"from": "b1070", "to": "b1071"},
    #     {"from": "b1071", "to": "b1072"},
    #     {"from": "b1072", "to": "b1073"},
    #     {"from": "b1073", "to": "b1074"},
    #     {"from": "b1074", "to": "b1075"},
    #     {"from": "b1075", "to": "b1076"},
    #     {"from": "b1076", "to": "b1077"},
    #     {"from": "b1077", "to": "b1078"},
    #     {"from": "b1078", "to": "b1079"},
    #     {"from": "b1079", "to": "b1080"},
    #     {"from": "b1080", "to": "b1081"},
    #     {"from": "b1081", "to": "b1082"},
    #     {"from": "b1082", "to": "b1083"},
    #     {"from": "b1083", "to": "b1084"},
    #     {"from": "b1084", "to": "b1085"},
    #     {"from": "b1085", "to": "b1086"},
    #     {"from": "b1086", "to": "b1087"},
    #     {"from": "b1087", "to": "b1088"},
    #     {"from": "b1088", "to": "b1089"},
    #     {"from": "b1089", "to": "b1090"},
    #     {"from": "b1090", "to": "b1091"},
    #     {"from": "b1091", "to": "b1092"},
    #     {"from": "b1092", "to": "b1093"},
    #     {"from": "b1093", "to": "b1094"},
    #     {"from": "b1094", "to": "b1095"},
    #     {"from": "b1095", "to": "b1096"},
    #     {"from": "b1096", "to": "b1097"}
    # ]