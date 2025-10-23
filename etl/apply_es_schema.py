import os
import json
import requests
import logging


def apply_elastic_schema(index_name: str):
    """
    Применить схему из json-файла к индексу в ES
    :param index_name: Имя индекса
    :return:
    """
    with open(os.getenv("SCHEMA_FILE"), "r", encoding="utf-8") as f:
        schema_text = f.read().strip()

    schema_json = json.loads(schema_text)

    resp = requests.put(f"{os.getenv("ELK_URL")}/{index_name}", json=schema_json)
    if resp.ok:
        logging.info(f"✅ Index '{index_name}' created.")
    elif resp.status_code == 400 and 'resource_already_exists_exception' in resp.text:
        logging.warning(f"ℹ️  Index '{index_name}' already exists. Skipping.")
    else:
        logging.error(f"Failed to create index: {resp.status_code} {resp.text}")
        resp.raise_for_status()
