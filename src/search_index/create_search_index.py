from yandex_cloud_ml_sdk.search_indexes import (
    StaticIndexChunkingStrategy,
    HybridSearchIndexType,
    ReciprocalRankFusionIndexCombinationStrategy,
)
import pandas as pd
from glob import glob


def get_token_count(model, filename):
    with open(filename, "r", encoding="utf8") as f:
        return len(model.tokenize(f.read()))


def get_file_len(filename):
    with open(filename, encoding="utf-8") as f:
        return len(f.read())


def create_search_index(sdk, model):
    # Подготовка данных
    files = [fn for fn in glob("data/*/*.md") if fn.count("/") == 2]
    d = [
        {
            "File": fn,
            "Tokens": get_token_count(model, fn),
            "Chars": get_file_len(fn),
            "Category": fn.split("/")[1],
        }
        for fn in files
    ]

    df = pd.DataFrame(d)
    df["Uploaded"] = df["File"].apply(lambda fn: upload_file(sdk, fn))

    # Создание индекса для wines
    wines_files = df[df["Category"] == "wines"]["Uploaded"]
    op = sdk.search_indexes.create_deferred(
        wines_files,
        index_type=HybridSearchIndexType(
            chunking_strategy=StaticIndexChunkingStrategy(
                max_chunk_size_tokens=1000, chunk_overlap_tokens=100
            ),
            combination_strategy=ReciprocalRankFusionIndexCombinationStrategy(),
        ),
    )
    index = op.wait()

    # Добавление regions
    regions_files = df[df["Category"] == "regions"]["Uploaded"]
    op = index.add_files_deferred(regions_files)
    op.wait()

    # Добавление таблицы food_wine
    with open("data/food_wine_table.md", encoding="utf-8") as f:
        food_wine = f.read()

    # Разбивка таблицы на чанки
    lines = food_wine.split("\n")
    header = lines[:2]
    chunk_size = 600 * 3
    chunks = []
    current_chunk = header.copy()

    for line in lines[2:]:
        current_chunk.append(line)
        if len("\n".join(current_chunk)) > chunk_size:
            chunks.append("\n".join(current_chunk))
            current_chunk = header.copy()

    if current_chunk != header:
        chunks.append("\n".join(current_chunk))

    # Загрузка чанков
    uploaded_chunks = []
    for chunk in chunks:
        chunk_id = sdk.files.upload_bytes(
            chunk.encode(),
            ttl_days=5,
            expiration_policy="static",
            mime_type="text/markdown",
        )
        uploaded_chunks.append(chunk_id)

    # Добавление чанков в индекс
    op = index.add_files_deferred(uploaded_chunks)
    op.wait()

    return index


def upload_file(sdk, filename):
    return sdk.files.upload(filename, ttl_days=1, expiration_policy="static")
