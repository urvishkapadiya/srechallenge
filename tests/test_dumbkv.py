import pytest
from dumbkv import DumbKV, PostgresDumbKV

@pytest.mark.usefixtures("database_location")
class TestDumbKV:
    @pytest.fixture(autouse=True)
    def setup_class(self, database_location):
        if 'postgres' in database_location:
            self.kv = PostgresDumbKV(database_location)
        else:
            self.kv = DumbKV(":memory:")
        self.kv.create_table()

    def test_set_get_delete(self):
        self.kv.set(1, "key1", "value1")
        assert self.kv.get(1, "key1") == "value1"
        self.kv.delete(1, "key1")

    def test_get_non_existent(self):
        with pytest.raises(Exception):
            self.kv.get(2, "key2")

    def test_set_existing_key(self):
        self.kv.set(3, "key1", "value1")
        with pytest.raises(Exception):
            self.kv.set(3, "key1", "value2")