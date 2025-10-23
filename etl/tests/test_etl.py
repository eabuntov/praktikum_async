def test_process_batch_transforms_rows(etl, fake_rows):
    actions = etl.process_batch(fake_rows)
    assert len(actions) == 2
    assert actions[0]["_id"] == "1"
    assert actions[0]["_index"] == "movies"
    assert "title" in actions[0]["_source"]
    assert actions[0]["_source"]["imdb_rating"] == 8.8


def test_run_once_calls_es_index(etl, mock_es, fake_rows):
    n = etl.run_once()
    assert n == len(fake_rows)
    assert mock_es.index.call_count == len(fake_rows)
    mock_es.index.assert_any_call(
        index="movies", id="1", document=fake_rows[0] | {"imdb_rating": fake_rows[0]["rating"]}
    )
