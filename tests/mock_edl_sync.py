import time
from pyspark.sql import SparkSession

"""
Process made to mimic the EDL's background sync process that runs in databricks. It typically monitors tables in the edl_stage DB
for having a tblproperty of edl_state = edl_ready. It will then try and sync the data in that table with the corrosponding edl DB table.
This process will result in the edl_state of that table being set to edl_success or edl_failure. If success, it will delete the table shortly
after.

This mock is used for testing, and will follow the happy path of the process above. Changing from edl_ready to edl_success on first pass,
then deleting tables already in edl_success on subsequent passes.  It will only monitor tables names you give it.

Intended to be used in a lambda in conjunction with concurrent.futures.ThreadPoolExecutor.
EXAMPLE:
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    executor.submit(lambda: mock_edl_sync_process(mock_spark, temp_db, [table.name for table in router_tables()]))
    tested_future = executor.submit(my_process_i_am_testing)
for future in concurrent.futures.as_completed([tested_future]):
        future.result()
"""

process_name = "mock_edl_sync_process"


def mock_edl_sync_process(
    mock_spark: SparkSession,
    database_name: str,
    table_names: list[str],
    wait_seconds=1.5,
    max_wait_seconds=10,
):
    time_elapased = 0
    while True:
        for table in table_names:
            table_name = f"{database_name}.{table}"
            try:
                props = mock_spark.sql(f"SHOW TBLPROPERTIES {table_name}")
                state = props.filter((props.key == "edl_state")).first()["value"]
                if state == "edl_ready":
                    print(
                        f"{process_name}: changing {table_name} from edl_ready to edl_success"
                    )
                    mock_spark.sql(
                        f"ALTER TABLE {table_name} SET TBLPROPERTIES ('edl_state' = 'edl_success') "
                    )
                if state == "edl_success":
                    print(
                        f"{process_name}: deleting {table_name} since it was already in edl_success"
                    )
                    mock_spark.sql(f"DROP TABLE {table_name}")
            except:
                print(
                    f"{process_name}: doing nothing since {table_name} does not exist"
                )
        time_elapased += wait_seconds
        if time_elapased > max_wait_seconds:
            return
        time.sleep(wait_seconds)
