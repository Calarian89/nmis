import pytest
import uuid
import os
import shutil
from pyspark.sql import SparkSession
from unittest.mock import Mock
from notebooks.local.utils.dbutils_local import DBUtilsLocal, dbutils
from notebooks.local.utils.spark_local import get_spark_session


@pytest.fixture(autouse=True, scope="session")
def test_run_id() -> str:
    id = str(uuid.uuid4())
    print(f"Generated unique ID for this test session: {id}")
    return id


@pytest.fixture
def mock_dbutils() -> DBUtilsLocal:
    # Leverage the local version of DBUtils to use any non-destructive logic.
    mock_dbutils = Mock()
    mock_dbutils.secrets = dbutils.secrets
    mock_dbutils.fs.ls = dbutils.fs.ls
    mock_dbutils.fs.head = dbutils.fs.head
    return mock_dbutils


@pytest.fixture(scope="session")
def mock_spark(test_run_id: str) -> SparkSession:
    print(f"Creating spark session for tests: {test_run_id}")
    spark = get_spark_session(test_run_id)
    yield spark
    print(f"Tearing down spark session: {test_run_id}")
    spark.catalog.clearCache()
    spark.stop()


@pytest.fixture()
def temp_db(mock_spark: SparkSession) -> str:
    dbname = "temp_db"
    mock_spark.sql(f"CREATE DATABASE IF NOT EXISTS {dbname}")
    yield dbname
    mock_spark.sql(f"DROP DATABASE {dbname} CASCADE")


@pytest.fixture()
def temp_dir(test_run_id: str) -> str:
    print(f"Creating temp directory for testing: {test_run_id}")
    dir = f"./{test_run_id}"
    os.mkdir(dir)
    yield dir
    print(f"Deleting temp directory for testing: {test_run_id}")
    shutil.rmtree(dir)
