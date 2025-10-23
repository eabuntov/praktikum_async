from typing import Any


class Transformer:
    """Преобразователь данных SQL в схему Elasticsearch"""

    ROLE_MAP = {
        "director": "directors",
        "actor": "actors",
        "writer": "writers",
    }

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        """
        Трансформация отдельной денормализованной строки в словарь для ES
        :param row: данные из БД
        :return: данные для ES
        """
        persons = row.get("persons") or []
        grouped = {"directors": [], "actors": [], "writers": []}

        for p in persons:
            role = p.get("role")
            if role in self.ROLE_MAP:
                grouped[self.ROLE_MAP[role]].append({
                    "id": str(p["id"]),
                    "name": p["name"],
                })

        return {
            "id": str(row["id"]),
            "imdb_rating": float(row["imdb_rating"]) if row["imdb_rating"] else None,
            "genres": row["genres"] or [],
            "title": row["title"],
            "description": row["description"],
            "directors_names": [p["name"] for p in grouped["directors"]],
            "actors_names": [p["name"] for p in grouped["actors"]],
            "writers_names": [p["name"] for p in grouped["writers"]],
            "directors": grouped["directors"],
            "actors": grouped["actors"],
            "writers": grouped["writers"],
        }