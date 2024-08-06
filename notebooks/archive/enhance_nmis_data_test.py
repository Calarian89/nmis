# import pytest
# from ipynb.fs.defs.notebooks.nmis8.enhance_nmis_data import *
# from ipynb.fs.defs.notebooks.nmis8.load_nmis_json import Json_Data_Loader
# from notebooks.local.utils.dbutils_local import DBUtilsLocal
# from pyspark.sql import SparkSession
# from pyspark.sql.functions import *
# from pyspark.sql.types import *
# from notebooks.archive.test_utils import *

# prod_events_table = "prod_events_table"


# def given_parquet_data(
#     data: List[Any], mock_spark, mock_dbutils, read_dir, some_parquet
# ):
#     make_file_json_data(read_dir, data)

#     Json_Data_Loader(mock_spark, mock_dbutils, [read_dir], some_parquet).load_files()


# # def test_enhance_data(
# #     mock_spark: SparkSession,
# #     mock_dbutils: DBUtilsLocal,
# #     read_dir: str,
# #     some_parquet: str,
# #     temp_db: str,
# # ):
# #     router_node = node_with_router_details()
# #     #  GIVEN routers data exists in a parquet table
# #     given_parquet_data([router_node], mock_spark, mock_dbutils, read_dir, some_parquet)

# #     # WHEN I make an Nmis_Data_Enhancer pointed to that parquet
# #     enhancer = Nmis_Data_Enhancer(
# #         mock_spark,
# #         some_parquet,
# #         None,  # Don't provide a target dir since local spark does not like saving tables to a path,
# #         f"{temp_db}.{prod_events_table}",
# #         db_name=temp_db,
# #     )
# #     enhancer.enhance()

# #     # Then the tables shouold be created
# #     events = mock_spark.read.table(f"{temp_db}.nmis_device_events")
# #     statuses = mock_spark.read.table(f"{temp_db}.nmis_device_event_statuses")
# #     interfaces = mock_spark.read.table(f"{temp_db}.nmis_device_event_interfaces")
# #     temps = mock_spark.read.table(f"{temp_db}.nmis_device_event_temperatures")
# #     locations = mock_spark.read.table(f"{temp_db}.device_locations")

# #     # THEN I should see that all the tables have the correct number of records.
# #     assert events.count() == 1
# #     assert statuses.count() == 2
# #     assert interfaces.count() == 2
# #     assert temps.count() == 1
# #     assert locations.count() == 1

# #     # THEN I should see that events has the proper data
# #     record = events.first()
# #     assert record["event_id"] != None
# #     assert record["event_timestamp"] == frozen_time()
# #     assert record["node_id"] == router_node["node_id"]
# #     assert record["device_type"] == "router"
# #     assert record["device_name"] == "torrisg-1-sc-us"
# #     assert record["system_name"] == "torrisg-1-sc-us-system"
# #     assert record["uptime_seconds"] == 3555468
# #     assert record["serial_number"] == "FJC252714UY"
# #     assert record["model"] == "ciscoCat9500FixedSwitchStack"
# #     assert record["total_device_interfaces"] == 125
# #     assert record["SNMP_enabled_interface_amount"] == 46
# #     assert record["location_id"] == 462
# #     assert record["tier"] == "Tier 2"
# #     assert record["division"] == "Ag & Turf"
# #     assert record["node_down_state"] == "false"
# #     assert record["SNMP_state"] == "true"

# #     # THEN I should see that locations has the proper data
# #     record = locations.first()
# #     assert record["location_id"] == 462
# #     assert record["location"] == "Starfire Lab"
# #     assert record["city"] == "Torrance"
# #     assert record["state"] == "California"
# #     assert record["country"] == "United States"
# #     assert record["region"] == "Region 4"
# #     assert record["timestamp"] == frozen_time()

# #     # THEN I should see that statuses has the proper data
# #     record = statuses.filter(statuses.index == "1018").first()
# #     assert record["event_id"] == events.first()["event_id"]
# #     assert record["type"] == "FAN Status"
# #     assert record["element"] == "GigabitEthernet1/1/1"
# #     assert record["index"] == "1018"
# #     assert record["status"] == "ok"
# #     assert record["value"] == 100
# #     record = statuses.filter(statuses.index == "1019").first()
# #     assert record["event_id"] == events.first()["event_id"]
# #     assert record["type"] == "FAN Status"
# #     assert record["element"] == "Vlan75"
# #     assert record["index"] == "1019"
# #     assert record["status"] == "error"
# #     assert record["value"] == 30

# #     # THEN I should see that interfaces has the proper data
# #     record = interfaces.filter(interfaces.interface_id == "1").first()
# #     assert record["event_id"] == events.first()["event_id"]
# #     assert record["interface_id"] == "1"
# #     assert record["name"] == "gigabitethernet0-0"
# #     assert record["status"] == "down"
# #     assert record["SNMP_enabled"] == False
# #     assert record["speed_in_mbs"] == 1000
# #     record = interfaces.filter(interfaces.interface_id == "10").first()
# #     assert record["event_id"] == events.first()["event_id"]
# #     assert record["interface_id"] == "10"
# #     assert record["name"] == "tengigabitethernet1-0-2"
# #     assert record["status"] == "up"
# #     assert record["SNMP_enabled"] == True
# #     assert record["speed_in_mbs"] == 2000

# #     # THEN I should see that temperatures has the proper data
# #     record = temps.first()
# #     assert record["event_id"] == events.first()["event_id"]
# #     assert record["state"] == "normal"
# #     assert record["sensor"] == "1012"


# def test_router_edl_table_properties(
#     mock_spark: SparkSession,
#     mock_dbutils: DBUtilsLocal,
#     read_dir: str,
#     some_parquet: str,
#     temp_db: str,
# ):
#     # GIVEN data exists in a parquet table
#     given_parquet_data(
#         [node_with_router_details()], mock_spark, mock_dbutils, read_dir, some_parquet
#     )

#     # WHEN I make an Nmis_Data_Enhancer pointed to that parquet
#     enhancer = Nmis_Data_Enhancer(
#         mock_spark,
#         some_parquet,
#         None,  # Don't provide a target dir since local spark does not like saving tables to a path,
#         f"{temp_db}.{prod_events_table}",
#         db_name=temp_db,
#     )
#     enhancer.enhance()

#     # THEN I should see that all tables have the tblproperties they need to be synced with the EDL
#     for table in tables():
#         props = mock_spark.sql(f"SHOW TBLPROPERTIES {temp_db}.{table.name}")
#         assert props.filter((props.key == "edl_state")).first()["value"] == "edl_ready"
#         assert (
#             props.filter((props.key == "edl_datatype")).first()["value"]
#             == "com.deere.enterprise.datalake.enhance.nmis_device_events_enhance"
#         )
#         assert (
#             props.filter((props.key == "edl_representation")).first()["value"]
#             == table.schema_env
#         )


# def test_should_only_process_new_records(
#     mock_spark: SparkSession,
#     mock_dbutils: DBUtilsLocal,
#     read_dir: str,
#     some_parquet: str,
#     temp_db: str,
# ):
#     # GIVEN device data exists in a parquet table
#     given_parquet_data(
#         [node_with_router_details()], mock_spark, mock_dbutils, read_dir, some_parquet
#     )

#     # GIVEN the prod events table is already populated with data that is newer than the current device parquet data
#     prod_events_df = mock_spark.createDataFrame(
#         [[frozen_time()]],
#         schema=StructType([StructField("event_timestamp", TimestampType())]),
#     )
#     prod_events_df.write.saveAsTable(f"{temp_db}.{prod_events_table}")

#     # WHEN I make an Nmis_Data_Enhancer pointed to that parquet and prod event table
#     enhancer = Nmis_Data_Enhancer(
#         mock_spark,
#         some_parquet,
#         None,  # Don't provide a target dir since local spark does not like saving tables to a path,
#         f"{temp_db}.{prod_events_table}",
#         db_name=temp_db,
#     )
#     enhancer.enhance()

#     # THEN I should see that all tables are empty since there were no new records to process
#     for table in tables():
#         assert mock_spark.read.table(f"{temp_db}.{table.name}").count() == 0
