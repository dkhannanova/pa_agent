def catalog_search(query: str) -> list[dict]:
    items = [
        {"name": "conversion", "description": "Конверсия click→purchase"},
        {"name": "retention_d7", "description": "Retention D7"},
    ]
    q = query.lower()
    return [x for x in items if q in x["name"] or q in x["description"].lower()]
