import pytest
from unittest.mock import MagicMock
from elasticsearch import Elasticsearch
from ..etl import ETLProcessor

@pytest.fixture
def fake_rows():
    return [
        {"id": "1", "title": "Inception", "rating": 8.8, "description": "Dreams"},
        {"id": "2", "title": "Matrix", "rating": 8.7},
    ]

@pytest.fixture
def mock_db_reader(fake_rows):
    """Simulated DB reader that returns rows once."""
    mock = MagicMock()
    mock.fetch_batch.return_value = fake_rows
    return mock

@pytest.fixture
def mock_es():
    """Mock Elasticsearch client."""
    mock = MagicMock(spec=Elasticsearch)
    return mock

@pytest.fixture
def etl(mock_db_reader, mock_es):
    return ETLProcessor(mock_db_reader, mock_es, index_name="movies")
