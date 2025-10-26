import logging
import time
from typing import Any

import requests
from elasticsearch import Elasticsearch, helpers

from apply_es_schemas import apply_elastic_schemas
from config.config import settings


class ElasticLoader:
    """Загрузка, обновление и удаление данных в Elasticsearch."""

    @staticmethod
    def wait_for_elasticsearch():
        logging.info("⏳ Ждем загрузки Elasticsearch..")
        while True:
            try:
                r = requests.get(f"{settings.elk_url}/_cluster/health",
                                 params={"wait_for_status": "yellow", "timeout": "1s"})
                if r.ok and r.json().get("status") in ("yellow", "green"):
                    logging.info("✅ Elasticsearch готов.")
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)

    def __init__(self, es_host: str):
        ElasticLoader.wait_for_elasticsearch()
        self.es = Elasticsearch([es_host])
        apply_elastic_schemas()

    def load_bulk(self, docs: list[dict[str, Any]], index: str):
        """Загружает (вставляет или заменяет) документы в Elasticsearch."""
        logging.info("Загрузка данных в Elasticsearch...")
        actions = [
            {
                "_op_type": "index",  # replaces if exists
                "_index": index,
                "_id": doc["id"],
                "_source": doc,
            }
            for doc in docs
        ]
        helpers.bulk(self.es, actions)
        logging.info(f"Загружено {len(actions)} сущностей")


    def update(self, doc: dict[str, Any]):
        """Частичное обновление документов в Elasticsearch."""
        logging.info(f"Обновление документа {doc["id"]} в Elasticsearch...")
        self.es.update(self.index, doc=doc)


    def delete(self, doc_id: str):
        """Удаляет документы из Elasticsearch по их ID."""
        logging.info(f"Удаление документа {doc_id}  из индекса {self.index}...")
        self.es.delete(self.index, doc_id)