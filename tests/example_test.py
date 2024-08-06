def test_should_validate_fixtures(test_run_id: str, temp_db: str, temp_dir: str):
    assert len(test_run_id) > 0
    assert len(temp_db) > 0
    assert len(temp_dir) > 0
