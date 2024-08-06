# import pytest
# import os
# from unittest.mock import call
# from pyspark.sql.functions import *
# from pyspark.sql import SparkSession
# from notebooks.archive.test_utils import *
# from notebooks.local.utils.dbutils_local import DBUtilsLocal
# from ipynb.fs.defs.notebooks.nmis8.load_nmis_json import *


# def test_should_consume_multiple_files_from_multiple_directories(
#     mock_spark: SparkSession, mock_dbutils: DBUtilsLocal, read_dir, some_parquet
# ):
#     # GIVEN I have a read_dir1 that exists
#     read_dir1 = f"{read_dir}/1"
#     os.makedirs(read_dir1, exist_ok=True)
#     os.makedirs(f"{read_dir1}/unprocessed", exist_ok=True)
#     # GIVEN I have a read_dir2 that exists
#     read_dir2 = f"{read_dir}/2"
#     os.makedirs(read_dir2, exist_ok=True)
#     os.makedirs(f"{read_dir2}/unprocessed", exist_ok=True)
#     # GIVEN I have 2 json files in read_dir1/unprocessed with router data
#     # GIVEN I have 2 json files in read_dir2/unprocessed with switch data
#     data_files = [
#         make_file_json_data(read_dir1, [node_with_router_details()]),
#         make_file_json_data(read_dir1, [node_with_router_details()], "servername2"),
#         make_file_json_data(read_dir2, [node_with_switch_details()]),
#         make_file_json_data(read_dir2, [node_with_switch_details()], "servername2"),
#     ]

#     # WHEN I make a Json_Data_Loader pointed to our read_dir1 and read_dir2 and target
#     # WHEN I call load_files on that Json_Data_Loader
#     Json_Data_Loader(
#         mock_spark, mock_dbutils, [read_dir1, read_dir2], some_parquet
#     ).load_files()

#     # THEN the 4 json files in read_dir1/unprocessed and read_dir2/unprocessed
#     # should have been moved to to thier respective /processed directories
#     for data_file in data_files:
#         mock_dbutils.fs.mv.assert_any_call(
#             data_file["unprocessed"],
#             data_file["processed"],
#         )

#     # THEN there should be data in the target parquet table containing our router and switch information from the json files
#     df = mock_spark.read.parquet(some_parquet)
#     expected_row_count = 4
#     assert df.count() == expected_row_count


# def test_should_only_process_certain_node_types(
#     mock_spark: SparkSession, mock_dbutils: DBUtilsLocal, read_dir, some_parquet
# ):
#     # GIVEN I have a read_dir that exists
#     # GIVEN I have a json file in read_dir/unprocessed with a mix of data that should be processed and should not
#     make_file_json_data(
#         read_dir,
#         [node_with_router_details(), node_with_switch_details(), node_with_details()],
#     )

#     # WHEN I make a Json_Data_Loader pointed to our read_dir1 and read_dir2 and target
#     # WHEN I call load_files on that Json_Data_Loader
#     Json_Data_Loader(mock_spark, mock_dbutils, [read_dir], some_parquet).load_files()

#     # THEN there should be data in the target parquet table containing our router information
#     # from the json files, but NOT our unknown nodeType information
#     df = mock_spark.read.parquet(some_parquet)
#     expected_row_count = 2
#     assert df.count() == expected_row_count


# def test_should_process_files_of_correct_type(
#     mock_spark: SparkSession, mock_dbutils: DBUtilsLocal, read_dir, some_parquet
# ):
#     # GIVEN I have a read_dir that exists
#     # GIVEN 1 json file with router events data exists in our readDir/unprocessed
#     json_data_file = make_file_json_data(read_dir, [node_with_router_details()])

#     # GIVEN 1 non-json file exists in our read_dir/unprocessed
#     with open(f"{read_dir}/unprocessed/file3.txt", "w") as outfile:
#         outfile.write("Non Json Contents")

#     # WHEN I make a Json_Data_Loader pointed to our read_dir and target
#     # WHEN I call load_files on that Json_Data_Loader
#     Json_Data_Loader(mock_spark, mock_dbutils, [read_dir], some_parquet).load_files()

#     # THEN the json file in read_dir/unprocessed should have been moved to read_dir/processed
#     mock_dbutils.fs.mv.assert_any_call(
#         json_data_file["unprocessed"], json_data_file["processed"]
#     )

#     # THEN I should see that the non-json file was not moved to read_dir/processed
#     assert (
#         call(f"{read_dir}/unprocessed/file3.txt", f"{read_dir}/processed/file3.txt")
#         not in mock_dbutils.fs.mv.mock_calls
#     )


# def check_column_info(df, nodeType):
#     expected = {
#         "event_timestamp": frozen_time(),
#         "info.system.city": "Torrance",
#         "info.system.country": "United States",
#         "info.system.divison": "Ag & Turf",
#         "info.system.intfCollect": 46,
#         "info.system.intfTotal": "125",
#         "info.system.location": "Starfire Lab",
#         "info.system.location_id": "462",
#         "info.system.name": "torrisg-1-sc-us",
#         "info.system.nodeType": nodeType,
#         "info.system.region": "Region 4",
#         "info.system.serialNum": "FJC252714UY",
#         "info.system.state": "California",
#         "info.system.sysName": "torrisg-1-sc-us-system",
#         "info.system.sysObjectName": "ciscoCat9500FixedSwitchStack",
#         "info.system.sysUpTimeSec": 3555468,
#         "info.system.tier": "Tier 2",
#         "info.interface.1.collect": "false",
#         "info.interface.1.ifHighSpeed": "1000",
#         "info.interface.1.ifOperStatus": "down",
#         "info.interface.1.interface": "gigabitethernet0-0",
#         "info.interface.10.collect": "true",
#         "info.interface.10.ifHighSpeed": "2000",
#         "info.interface.10.ifOperStatus": "up",
#         "info.interface.10.interface": "tengigabitethernet1-0-2",
#         "info.status.FAN Status--1018.element": "GigabitEthernet1/1/1",
#         "info.status.FAN Status--1018.index": "1018",
#         "info.status.FAN Status--1018.event": "FAN Status",
#         "info.status.FAN Status--1018.status": "ok",
#         "info.status.FAN Status--1018.value": "100",
#         "info.status.FAN Status--1019.element": "Vlan75",
#         "info.status.FAN Status--1019.index": "1019",
#         "info.status.FAN Status--1019.event": "FAN Status",
#         "info.status.FAN Status--1019.status": "error",
#         "info.status.FAN Status--1019.value": "30",
#         "info.tempStatus.1012.TemperatureStateName": "normal",
#     }
#     for key, value in expected.items():
#         assert (
#             df.filter(col("info.system.nodeType") == nodeType)
#             .select(col(key).alias("val"))
#             .first()["val"]
#             == value
#         )


# def test_info_column_contents(
#     mock_spark: SparkSession, mock_dbutils: DBUtilsLocal, read_dir, some_parquet
# ):
#     # GIVEN I have a read_dir that exists
#     # GIVEN a json file with router events data exists in our read_dir/unprocessed
#     make_file_json_data(
#         read_dir, [node_with_router_details(), node_with_switch_details()]
#     )

#     # WHEN I make a Json_Data_Loader pointed to our read_dir and target_dir
#     # WHEN I call load_files on that Json_Data_Loader
#     Json_Data_Loader(mock_spark, mock_dbutils, [read_dir], some_parquet).load_files()

#     # THEN I should have a parquet table in my target_dir
#     df = mock_spark.read.parquet(some_parquet)

#     # THEN I should have an event_timestamp column with a timestamp based
#     # on the date in my file I gathered the data from.
#     # THEN I should have JSON schema data in the info column
#     check_column_info(df, "router")
#     check_column_info(df, "switch")
