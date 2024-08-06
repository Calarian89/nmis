# import uuid
# import json
# from datetime import datetime
# from pyspark.sql.functions import *

# frozen_time_string = "20230612010203"


# def frozen_time() -> datetime:
#     return datetime(2023, 6, 12, 1, 2, 3)


# def generate_cookie_matcher(key, value):
#     def cookie_matcher(request):
#         return (
#             key,
#             value,
#         ) in request._cookies.get_dict().items()

#     return cookie_matcher


# def node_with_no_details():
#     return {"node_id": str(uuid.uuid4()), "info": {}}


# def node_with_details(nodeType="unknown"):
#     node = node_with_no_details()
#     node["info"] = {
#         "system": {
#             "city": "Torrance",
#             "country": "United States",
#             "divison": "Ag & Turf",
#             "intfCollect": 46,
#             "intfTotal": "125",
#             "location": "Starfire Lab",
#             "location_id": "462",
#             "name": "torrisg-1-sc-us",
#             "nodedown": "false",
#             "nodeType": nodeType,
#             "region": "Region 4",
#             "serialNum": "FJC252714UY",
#             "state": "California",
#             "snmpdown": "true",
#             "sysName": "torrisg-1-sc-us-system",
#             "sysObjectName": "ciscoCat9500FixedSwitchStack",
#             "sysUpTimeSec": 3555468,
#             "tier": "Tier 2",
#         },
#         "interface": {
#             "1": {
#                 "collect": "false",
#                 "ifHighSpeed": "1000",
#                 "ifOperStatus": "down",
#                 "interface": "gigabitethernet0-0",
#             },
#             "10": {
#                 "collect": "true",
#                 "ifHighSpeed": "2000",
#                 "ifOperStatus": "up",
#                 "interface": "tengigabitethernet1-0-2",
#             },
#         },
#         "status": {
#             "FAN Status--1018": {
#                 "element": "GigabitEthernet1/1/1",
#                 "event": "FAN Status",
#                 "index": "1018",
#                 "status": "ok",
#                 "value": "100",
#             },
#             "FAN Status--1019": {
#                 "element": "Vlan75",
#                 "event": "FAN Status",
#                 "index": "1019",
#                 "status": "error",
#                 "value": "30",
#             },
#         },
#         "tempStatus": {
#             "1012": {
#                 "TemperatureStateName": "normal",
#                 "TemperatureStatusDescr": "Switch 1 - Inlet Temp Sensor, GREEN ",
#                 "ciscoEnvMonTemperatureStatusDescr": "1012",
#                 "index": "1012",
#                 "tempValue": "100",
#             },
#         },
#     }
#     return node


# def node_with_router_details():
#     return node_with_details("router")


# def node_with_switch_details():
#     return node_with_details("switch")


# def make_file_json_data(dir: str, data: any, servername: str = "servername1") -> str:
#     name = f"{dir}/unprocessed/{servername}-{frozen_time_string}.json"
#     with open(name, "w") as outfile:
#         json.dump(data, outfile)
#     return {
#         "unprocessed": name,
#         "processed": f"{dir}/processed/{servername}-{frozen_time_string}.json",
#     }
