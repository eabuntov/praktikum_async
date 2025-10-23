from typing import Generator, Any

from sqlparse.utils import offset

from db_routines import get_db_cursor
from etl_transformer import Transformer


class PostgresExtractor:
    """Адаптер для выбора данных из БД."""

    def __init__(self, dsl: dict):
        self.dsn = dsl
        self.transformer = Transformer()

    def fetch_movies(self, last_time: str,
                     last_ids: list, batch_size: int) -> Generator[list[dict[str, Any]], None, None]:
        """
        Выгрузка данных батчами
        :param last_ids: идентификаторы записей, отправленных в прошлый раз
        :param last_time: Последнее полученное время создания фильма
        :param batch_size: размер батча
        :return: список словарей
        """
        if not last_ids:
            last_ids = []
        if not last_time:
            last_time = "1970-01-01 00:00:00+00:00"
        offset = 0
        with get_db_cursor(self.dsn) as cur, \
                open("sql/movies_select.sql", "r", encoding="utf-8") as query_file:
            condition = f" AND fw.id NOT IN ('{'\', \''.join(last_ids)}')" if last_ids else ""
            query = query_file.read().replace("{}", condition)
            cur.execute(query,
                        (last_time, str(batch_size), str(offset)))
            while rows := cur.fetchall():
                yield rows
                offset += len(rows)
                cur.execute(query,
                            (last_time, str(batch_size), str(offset)))


    def fetch_film(self, film_id: str) -> dict[str, Any]:
        """
        Выгрузка отдельного фильма
        :param film_id: идентификатор
        :return: словарь с данными
        """
        with get_db_cursor(self.dsn) as cur, open("sql/film_select.sql", "r", encoding="utf-8") as query_file:
            cur.execute(query_file.read(), (film_id,))
            return cur.fetchone()
