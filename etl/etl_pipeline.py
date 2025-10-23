import logging
import os

from es_loader import ElasticLoader
from state_storage import RedisStorage
from pg_listener import PostgresListener
from etl_transformer import Transformer
from pg_extractor import PostgresExtractor

logging.basicConfig(level=logging.INFO)

class ETLPipeline:
    """Реализация пайплайна в целом"""

    def __init__(self, extractor: PostgresExtractor, transformer: Transformer, loader: ElasticLoader):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader
        self.state = RedisStorage()

    def run(self, batch_size: int):
        """Запускаем передачу данных"""
        time = self.state.retrieve_state("time")
        ids = self.state.retrieve_state("ids")
        for rows in self.extractor.fetch_movies(time, ids, batch_size=batch_size):
            transformed = [self.transformer.transform(r) for r in rows]
            self.loader.load_bulk(transformed)
            logging.info(rows[-1])
            self.state.save_state("time", rows[-1]["created"])
            self.state.save_state("ids", [row["id"] for row in transformed])
            logging.info(f"Загружено {len(transformed)} записей в Elasticsearch")



if __name__ == "__main__":
    # точка входа сервиса
    postgres_dsl = {'dbname': os.environ.get('DB_NAME'),
           'user': os.environ.get('DB_USER'), 
           'password': os.environ.get('DB_PASSWORD'), 
           'host': os.environ.get('DB_HOST'), 
           'port': os.environ.get('DB_PORT')}

    # Пересылаем весь объем данных
    extractor = PostgresExtractor(postgres_dsl)
    transformer = Transformer()
    loader = ElasticLoader(os.environ.get("ELK_URL"), os.environ.get("ELK_INDEX"))
    pipeline = ETLPipeline(extractor, transformer, loader)
    pipeline.run(batch_size=int(os.environ.get("BATCH_SIZE", "100")))

    # Начинаем отслеживать изменения
    listener = PostgresListener(postgres_dsl)
    for change in listener.wait_for_changes():
        listener.handle_change(change)