import pytest

@pytest.fixture(scope="session")
def api_base_url():
    # Docker DNS resolves the service name "api" to its container IP
    return "http://fastapi_app:8000"
