import os
import json
import requests
import logging


def apply_elastic_schemas():
    """
    Применяем json-схем: movies, genres, и persons.
    """

    elk_url = os.getenv("ELK_URL")
    schema_path = os.getenv("SCHEMA_FILE")
    indices = ["movies", "genres", "persons"]

    # Load schema

    for index_name in indices:
        try:
            with open(f"es_schemas/{index_name}_schema.json", "r", encoding="utf-8") as f:
                schema_json = json.load(f)
        except FileNotFoundError as e:
            logging.error(f"❌ Failed to load schema file '{schema_path}': {e}")
            raise
        try:
            resp = requests.put(f"{elk_url}/{index_name}", json=schema_json)

            if resp.ok:
                logging.info(f"✅ Index '{index_name}' created successfully.")
            elif resp.status_code == 400 and "resource_already_exists_exception" in resp.text:
                logging.warning(f"ℹ️ Index '{index_name}' already exists. Skipping.")
            else:
                logging.error(f"❌ Failed to create index '{index_name}': {resp.status_code} {resp.text}")
                resp.raise_for_status()

        except requests.exceptions.RequestException as e:
            logging.error(f"🚫 Request error while creating index '{index_name}': {e}")
        except Exception as e:
            logging.exception(f"💥 Unexpected error while applying schema to '{index_name}': {e}")
