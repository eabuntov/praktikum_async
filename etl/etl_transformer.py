from typing import Any


class Transformer:
    """Преобразователь данных SQL в схему Elasticsearch."""

    ROLE_MAP = {
        "director": "directors",
        "actor": "actors",
        "writer": "writers",
    }

    def transform_movie(self, row: dict[str, Any]) -> dict[str, Any]:
        """
        Трансформация отдельной денормализованной строки фильма в документ Elasticsearch.
        """
        persons = row.get("persons") or []
        genres = row.get("genres") or []
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
            "rating": float(row["rating"]) if row["rating"] else None,
            "genres": row["genres"] or [],
            "title": row["title"],
            "type": row["type"],
            "description": row["description"],
            "directors_names": [p["name"] for p in grouped["directors"]],
            "actors_names": [p["name"] for p in grouped["actors"]],
            "writers_names": [p["name"] for p in grouped["writers"]],
            "directors": grouped["directors"],
            "actors": grouped["actors"],
            "writers": grouped["writers"],
        }

    def transform_genre(self, row: dict[str, Any]) -> dict[str, Any]:
        """
        Трансформация строки жанра в документ Elasticsearch.
        """
        return {
            "id": str(row["id"]),
            "name": row.get("name"),
            "description": row.get("description"),
            "created": row.get("created"),
            "modified": row.get("modified"),
        }

    def transform_person(self, row: dict[str, Any]) -> dict[str, Any]:
        """
        Трансформация строки человека в документ Elasticsearch.
        """
        return {
            "id": str(row["id"]),
            "full_name": row.get("full_name"),
            "created": row.get("created"),
            "modified": row.get("modified"),
        }
