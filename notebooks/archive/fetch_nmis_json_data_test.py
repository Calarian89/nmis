# import pytest
# import json
# import os
# from notebooks.local.utils.dbutils_local import dbutils
# from datetime import datetime
# from unittest.mock import Mock, call
# from notebooks.archive.test_utils import generate_cookie_matcher, frozen_time
# from ipynb.fs.defs.notebooks.nmis8.fetch_nmis_json_data import ServerInfo, DataRetriever

# # Mocking out current time
# # It did not like me mocking datetime.now. Just replace the wrapper function instead.
# DataRetriever.now = frozen_time


# def test_construct_data_retriever_with_secrets(mock_dbutils):
#     data_retriever = DataRetriever([], "", "", mock_dbutils)

#     assert data_retriever.api_id == "nmis_api_id_value"
#     assert data_retriever.api_pwd == "nmis_api_pwd_value"


# def test_process_all_servers(mock_dbutils, requests_mock):
#     # Mocking out auth call and response
#     requests_mock.register_uri(
#         "POST",
#         "https://test.co/api/data/omk/opCharts/login?username=nmis_api_id_value&password=nmis_api_pwd_value",
#         status_code=200,
#         cookies={"auth_cookie": "auth_cookie_value"},
#     )

#     #  Mocking out data call and response
#     requests_mock.register_uri(
#         "GET",
#         'https://test.co/api/data/en/omk/opCharts/v1/nodes?query=["config.nodeType","router"]&properties=["info."]',
#         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
#         status_code=200,
#         json=[{"key": "value"}],
#     )

#     requests_mock.register_uri(
#         "GET",
#         "https://test.co/api/data/en/omk/opCharts/v1/nodes?query=switch",
#         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
#         status_code=200,
#         json=[{"key": "value2"}],
#     )

#     # Invoke logic
#     DataRetriever(
#         [
#             ServerInfo("test_server", "https://test.co/api/data"),
#             ServerInfo("test_server2", "https://test.co/api/data", "query=switch"),
#         ],
#         "/mnt/some_path/unprocessed",
#         'query=["config.nodeType","router"]&properties=["info."]',
#         mock_dbutils,
#     ).process_all_servers()

#     # Assert that file should have been written with specific name and contents
#     mock_dbutils.fs.put.assert_has_calls(
#         [
#             call(
#                 "/mnt/some_path/unprocessed/test_server-20230612010203.json",
#                 '[{"key": "value"}]',
#             ),
#             call(
#                 "/mnt/some_path/unprocessed/test_server2-20230612010203.json",
#                 '[{"key": "value2"}]',
#             ),
#         ]
#     )


# # def test_continue_when_auth_call_fails(mock_dbutils, requests_mock):
# #     # GIVEN auth call to server1 fails
# #     requests_mock.register_uri(
# #         "POST",
# #         "https://test.co/should_fail/omk/opCharts/login",
# #         status_code=503,
# #     )
# #     # GIVEN auth call to server2 succeeds
# #     requests_mock.register_uri(
# #         "POST",
# #         "https://test.co/api/data/omk/opCharts/login",
# #         status_code=200,
# #         cookies={"auth_cookie": "auth_cookie_value"},
# #     )
# #     # GIVEN data call to server2 succeeds
# #     requests_mock.register_uri(
# #         "GET",
# #         "https://test.co/api/data/en/omk/opCharts/v1/nodes",
# #         status_code=200,
# #         json=[{"key": "value"}],
# #     )

# # WHEN I make a data retriever for server1 and server2
# # WHEN I call to process all servers using that data retriever
# # THEN it should throw an exception
# # with pytest.raises(Exception, match="Failed to process one or more servers."):
# #     DataRetriever(
# #         [
# #             ServerInfo("test_server", "https://test.co/should_fail"),
# #             ServerInfo("test_server2", "https://test.co/api/data"),
# #         ],
# #         "/mnt/some_path/unprocessed",
# #         "query=query",
# #         mock_dbutils,
# #     ).process_all_servers()

# # # THEN I should see that server2 processed successfully.
# # mock_dbutils.fs.put.assert_called_once_with(
# #     "/mnt/some_path/unprocessed/test_server2-20230612010203.json",
# #     '[{"key": "value"}]',
# # )


# # def test_continue_when_data_call_fails(mock_dbutils, requests_mock):
# #     # GIVEN auth call to server1 succeeds
# #     requests_mock.register_uri(
# #         "POST",
# #         "https://test.co/should_fail/omk/opCharts/login",
# #         status_code=200,
# #         cookies={"auth_cookie": "auth_cookie_value"},
# #     )
# #     # GIVEN auth call to server2 succeeds
# #     requests_mock.register_uri(
# #         "POST",
# #         "https://test.co/api/data/omk/opCharts/login",
# #         status_code=200,
# #         cookies={"auth_cookie": "auth_cookie_value"},
# #     )
# #     # GIVEN data call for server1 fails
# #     requests_mock.register_uri(
# #         "GET",
# #         "https://test.co/should_fail/en/omk/opCharts/v1/nodes",
# #         status_code=503,
# #     )
# #     # GIVEN data call for server2 succeeds
# #     requests_mock.register_uri(
# #         "GET",
# #         "https://test.co/api/data/en/omk/opCharts/v1/nodes",
# #         status_code=200,
# #         json=[{"key": "value"}],
# #     )

# # WHEN I make a data retriever for server1 and server2
# # WHEN I call to process all servers using that data retriever
# # THEN it should throw an exception
# # with pytest.raises(Exception, match="Failed to process one or more servers."):
# #     DataRetriever(
# #         [
# #             ServerInfo("test_server", "https://test.co/should_fail"),
# #             ServerInfo("test_server2", "https://test.co/api/data"),
# #         ],
# #         "/mnt/some_path/unprocessed",
# #         "query=query",
# #         mock_dbutils,
# #     ).process_all_servers()

# # # THEN I should see that server2 processed successfully.
# # mock_dbutils.fs.put.assert_called_once_with(
# #     "/mnt/some_path/unprocessed/test_server2-20230612010203.json",
# #     '[{"key": "value"}]',
# # )


# def test_process_individual_node_ids(mock_dbutils, requests_mock, read_dir):
#     # By mocking we replace the write functionality of dbutils so we can write our test data locally.
#     mock_dbutils.fs.put = dbutils.fs.put
#     # GIVEN auth call to server_1 succeeds
#     requests_mock.register_uri(
#         "POST",
#         "http://server_1/omk/opCharts/login",
#         status_code=200,
#         cookies={"auth_cookie": "auth_cookie_value"},
#     )
#     # GIVEN auth call to server_2 succeeds
#     requests_mock.register_uri(
#         "POST",
#         "http://server_2/omk/opCharts/login",
#         status_code=200,
#         cookies={"auth_cookie": "auth_cookie_value"},
#     )
#     # GIVEN data call to server_1 to get node_ids succeeds
#     requests_mock.register_uri(
#         "GET",
#         "http://server_1/en/omk/opCharts/v1/nodes",
#         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
#         status_code=200,
#         json=["node_1", "node_2"],
#     )
#     # GIVEN data call to server_2 to get node_ids succeeds
#     requests_mock.register_uri(
#         "GET",
#         "http://server_2/en/omk/opCharts/v1/nodes",
#         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
#         status_code=200,
#         json=["node_3", "node_4"],
#     )
#     # GIVEN data call to node_1 succeeds
#     requests_mock.register_uri(
#         "GET",
#         "http://server_1/en/omk/opCharts/v1/nodes/node_1",
#         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
#         status_code=200,
#         json={"node_id": "server_1_node"},
#     )
#     # GIVEN data call to node_2 succeeds
#     requests_mock.register_uri(
#         "GET",
#         "http://server_1/en/omk/opCharts/v1/nodes/node_2",
#         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
#         status_code=200,
#         json={"node_id": "server_1_node"},
#     )
#     # GIVEN data call to node_3 succeeds
#     requests_mock.register_uri(
#         "GET",
#         "http://server_2/en/omk/opCharts/v1/nodes/node_3",
#         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
#         status_code=200,
#         json={"node_id": "server_2_node"},
#     )
#     # GIVEN data call to node_4 succeeds
#     requests_mock.register_uri(
#         "GET",
#         "http://server_2/en/omk/opCharts/v1/nodes/node_4",
#         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
#         status_code=200,
#         json={"node_id": "server_2_node"},
#     )
#     # WHEN I make a data retriever for server1 and server2
#     # WHEN I call to process all individual nodes using that data retriever
#     data_retriever = DataRetriever(
#         [
#             ServerInfo("server_1", "http://server_1"),
#             ServerInfo("server_2", "http://server_2"),
#         ],
#         f"{read_dir}/unprocessed/node_ids",
#         "query=query",
#         mock_dbutils,
#         should_process_individual_node_ids=True,
#         individual_target_dir=f"{read_dir}/unprocessed",
#     )
#     data_retriever.process_all_servers()

#     # THEN I should see that server 1 has a file that contains all the node_ids data
#     with open(f"{read_dir}/unprocessed/server_1-20230612010203.json", "r") as file:
#         assert (
#             file.read()
#             == '[{"node_id": "server_1_node"}, {"node_id": "server_1_node"}]'
#         )

#     # THEN I should see that server 2 has a file that contains all the node_ids data
#     with open(f"{read_dir}/unprocessed/server_2-20230612010203.json", "r") as file:
#         assert (
#             file.read()
#             == '[{"node_id": "server_2_node"}, {"node_id": "server_2_node"}]'
#         )


# # def test_process_individual_node_ids_should_continue_on_error(
# #     mock_dbutils, requests_mock, read_dir
# # ):
# #     # By mocking we replace the write functionality of dbutils so we can write our test data locally.
# #     mock_dbutils.fs.put = dbutils.fs.put
# #     mock_dbutils.fs.rm = dbutils.fs.rm
# #     # GIVEN auth call to server_1 succeeds
# #     requests_mock.register_uri(
# #         "POST",
# #         "http://server_1/omk/opCharts/login",
# #         status_code=200,
# #         cookies={"auth_cookie": "auth_cookie_value"},
# #     )
# #     # GIVEN auth call to server_2 succeeds
# #     requests_mock.register_uri(
# #         "POST",
# #         "http://server_2/omk/opCharts/login",
# #         status_code=200,
# #         cookies={"auth_cookie": "auth_cookie_value"},
# #     )
# #     # GIVEN data call to server_1 to get node_ids succeeds
# #     requests_mock.register_uri(
# #         "GET",
# #         "http://server_1/en/omk/opCharts/v1/nodes",
# #         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
# #         status_code=200,
# #         json=["node_1", "node_2"],
# #     )
# #     # GIVEN data call to server_2 to get node_ids succeeds
# #     requests_mock.register_uri(
# #         "GET",
# #         "http://server_2/en/omk/opCharts/v1/nodes",
# #         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
# #         status_code=200,
# #         json=["node_3", "node_4"],
# #     )
# #     # GIVEN data call to node_1 succeeds
# #     requests_mock.register_uri(
# #         "GET",
# #         "http://server_1/en/omk/opCharts/v1/nodes/node_1",
# #         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
# #         status_code=200,
# #         json={"node_id": "server_1_node"},
# #     )
# #     # GIVEN data call to node_2 fails
# #     requests_mock.register_uri(
# #         "GET",
# #         "http://server_1/en/omk/opCharts/v1/nodes/node_2",
# #         status_code=503,
# #     )
# #     # GIVEN data call to node_3 succeeds
# #     requests_mock.register_uri(
# #         "GET",
# #         "http://server_2/en/omk/opCharts/v1/nodes/node_3",
# #         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
# #         status_code=200,
# #         json={"node_id": "server_2_node"},
# #     )
# #     # GIVEN data call to node_4 succeeds
# #     requests_mock.register_uri(
# #         "GET",
# #         "http://server_2/en/omk/opCharts/v1/nodes/node_4",
# #         additional_matcher=generate_cookie_matcher("auth_cookie", "auth_cookie_value"),
# #         status_code=200,
# #         json={"node_id": "server_2_node"},
# #     )
# #     # WHEN I make a data retriever for server1 and server2
# #     # WHEN I call to process all individual nodes using that data retriever
# #     data_retriever = DataRetriever(
# #         [
# #             ServerInfo("server_1", "http://server_1"),
# #             ServerInfo("server_2", "http://server_2"),
# #         ],
# #         f"{read_dir}/unprocessed/node_ids",
# #         "query=query",
# #         mock_dbutils,
# #         should_process_individual_node_ids=True,
# #         individual_target_dir=f"{read_dir}/unprocessed",
# #     )

# #     # THEN it should throw an exception
# #     with pytest.raises(Exception, match="Failed to process one or more servers."):
# #         data_retriever.process_all_servers()

# #     # THEN I should see that there are no more files containing just node id arrays left in the target_dir
# #     assert os.listdir(f"{read_dir}/unprocessed/node_ids") == []

# #     # THEN I should see that server 1 has a file that contains all the node_ids data from the successful calls
# #     with open(f"{read_dir}/unprocessed/server_1-20230612010203.json", "r") as file:
# #         assert file.read() == '[{"node_id": "server_1_node"}]'

# #     # THEN I should see that server 2 has a file that contains all the node_ids data since they all were successful
# #     with open(f"{read_dir}/unprocessed/server_2-20230612010203.json", "r") as file:
# #         assert (
# #             file.read()
# #             == '[{"node_id": "server_2_node"}, {"node_id": "server_2_node"}]'
# #         )
