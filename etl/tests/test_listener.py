import json
from unittest.mock import MagicMock, patch
from ..etl import PostgresListener

def test_listener_yields_payload(monkeypatch):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.notifies = [MagicMock(payload=json.dumps({"id": "123"}))]
    mock_conn.closed = 0

    with patch("listener.connect_and_listen", return_value=(mock_conn, mock_cur)):
        listener = PostgresListener(dsn={}, channel="test")
        gen = listener.wait_for_changes(timeout=0)
        result = next(gen)
        assert result == {"id": "123"}


def test_listener_reconnects_on_error(monkeypatch):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.closed = 1  # simulate broken connection

    mock_reconnect = MagicMock(return_value=(mock_conn, mock_cur))
    monkeypatch.setattr("listener.connect_and_listen", mock_reconnect)

    listener = PostgresListener(dsn={}, channel="test")
    gen = listener.wait_for_changes(timeout=0)

    # First iteration triggers reconnect
    try:
        next(gen)
    except StopIteration:
        pass

    mock_reconnect.assert_called()
