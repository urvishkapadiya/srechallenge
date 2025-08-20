import pytest

def pytest_addoption(parser):
    parser.addoption("--database-location", default=":memory:", help="Set database location")

@pytest.fixture
def database_location(request):
    return request.config.getoption("--database-location")