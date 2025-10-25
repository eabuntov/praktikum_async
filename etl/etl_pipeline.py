import logging
import os

from es_loader import ElasticLoader
from state_storage import RedisStorage
from pg_listener import PostgresListener
from etl_transformer import Transformer
from pg_extractor import PostgresExtractor

logging.basicConfig(level=logging.INFO)


class ETLPipeline:
    """ETL pipeline implementation for movies, genres, and people."""

    def __init__(self, extractor: PostgresExtractor, transformer: Transformer, loader: ElasticLoader):
        self.extractor = extractor
        self.transformer = transformer
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

        for rows in self.extractor.fetch_movies(time, ids, batch_size=batch_size):
            transformed = [self.transformer.transform_movie(r) for r in rows]
            self.loader.load_bulk(transformed, index="movies")
            self._update_state("movies", rows, transformed)

    def _process_genres(self, batch_size: int):
        """Fetch, transform, and load genre data."""
        logging.info("Starting genre ETL pipeline...")
        time = self.state.retrieve_state("genres_time")
        ids = self.state.retrieve_state("genres_ids")

        for rows in self.extractor.fetch_genres(time, ids, batch_size=batch_size):
            transformed = [self.transformer.transform_genre(r) for r in rows]
            self.loader.load_bulk(transformed, index="genres")
            self._update_state("genres", rows, transformed)

    def _process_people(self, batch_size: int):
        """Fetch, transform, and load person data."""
        logging.info("Starting people ETL pipeline...")
        time = self.state.retrieve_state("people_time")
        ids = self.state.retrieve_state("people_ids")

        for rows in self.extractor.fetch_people(time, ids, batch_size=batch_size):
            transformed = [self.transformer.transform_person(r) for r in rows]
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
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'port': os.environ.get('DB_PORT'),
    }

    extractor = PostgresExtractor(postgres_dsl)
    transformer = Transformer()
    loader = ElasticLoader(os.environ.get("ELK_URL"))
    pipeline = ETLPipeline(extractor, transformer, loader)
    pipeline.run(batch_size=int(os.environ.get("BATCH_SIZE", "100")))

    # Start listening for DB changes
    listener = PostgresListener(postgres_dsl)
    for change in listener.wait_for_changes():
        listener.handle_change(change)
