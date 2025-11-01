import logging
import sys
sys.path.append("/opt")
from config.config import settings
from es_loader import ElasticLoader
from state_storage import RedisStorage
from pg_listener import PostgresListener
from etl_transformer import TransformerFactory
from pg_extractor import PostgresExtractor

logging.basicConfig(level=logging.INFO)


class ETLPipeline:
    """ETL pipeline implementation for movies, genres, and people."""

    def __init__(self, extractor: PostgresExtractor, loader: ElasticLoader):
        self.extractor = extractor
        self.loader = loader
        self.state = RedisStorage()

    def run(self, batch_size: int):
        """Runs the full ETL process for all entity types."""
        self._process_movies(batch_size)
        self._process_genres(batch_size)
        self._process_people(batch_size)

    def _process_movies(self, batch_size: int):
        """Fetch, transform, and load movie data."""
        logging.info("Starting movie ETL pipeline...")
        time = self.state.retrieve_state("movies_time")
        ids = self.state.retrieve_state("movies_ids")
        transformer = TransformerFactory.get("movie")
        for rows in self.extractor.fetch_movies(time, ids, batch_size=batch_size):
            transformed = [transformer.transform(r) for r in rows]
            self.loader.load_bulk(transformed, index="movies")
            self._update_state("movies", rows, transformed)

    def _process_genres(self, batch_size: int):
        """Fetch, transform, and load genre data."""
        logging.info("Starting genre ETL pipeline...")
        time = self.state.retrieve_state("genres_time")
        ids = self.state.retrieve_state("genres_ids")
        transformer = TransformerFactory.get("genre")
        for rows in self.extractor.fetch_genres(time, ids, batch_size=batch_size):
            transformed = [transformer.transform(r) for r in rows]
            self.loader.load_bulk(transformed, index="genres")
            self._update_state("genres", rows, transformed)

    def _process_people(self, batch_size: int):
        """Fetch, transform, and load person data."""
        logging.info("Starting people ETL pipeline...")
        time = self.state.retrieve_state("people_time")
        ids = self.state.retrieve_state("people_ids")
        transformer = TransformerFactory.get("person")
        for rows in self.extractor.fetch_people(time, ids, batch_size=batch_size):
            transformed = [transformer.transform(r) for r in rows]
            self.loader.load_bulk(transformed, index="persons")
            self._update_state("persons", rows, transformed)

    def _update_state(self, entity: str, rows: list[dict], transformed: list[dict]):
        """Save latest batch state for entity."""
        if not rows:
            return
        self.state.save_state(f"{entity}_time", rows[-1].get("updated") or rows[-1].get("created"))
        self.state.save_state(f"{entity}_ids", [row["id"] for row in transformed])
        logging.info(f"Loaded {len(transformed)} {entity} records into Elasticsearch")


if __name__ == "__main__":
    # Entry point
    postgres_dsl = {
        'dbname': settings.db_name,
        'user': settings.db_user,
        'password': settings.db_password,
        'host': settings.db_host,
        'port': settings.db_port,
    }

    extractor = PostgresExtractor(postgres_dsl)
    loader = ElasticLoader()
    pipeline = ETLPipeline(extractor, loader)
    pipeline.run(batch_size=int(settings.batch_size))

    # Start listening for DB changes
    listener = PostgresListener(postgres_dsl)
    for change in listener.wait_for_changes():
        listener.handle_change(change)
