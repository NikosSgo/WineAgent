import os
import json
from .create_search_index import create_search_index


def get_search_index(sdk, model, search_index_json: str):
    search_index = None

    if os.path.exists(search_index_json):
        try:
            with open(search_index_json, "r", encoding="utf-8") as file:
                search_index_id = json.load(file)

            if search_index_id:
                search_index = sdk.search_indexes.get(search_index_id)
                print(f"Используем существующий индекс: {search_index_id}")

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Ошибка чтения файла {search_index_json}: {e}")
            search_index = None

    if search_index is None:
        print("Создаем новый search index...")
        search_index = create_search_index(sdk, model)

        with open(search_index_json, "w", encoding="utf-8") as file:
            json.dump(search_index.id, file, ensure_ascii=False)
        print(f"Создан новый индекс: {search_index.id}")

    return search_index
