import os
from dotenv import load_dotenv
from yandex_cloud_ml_sdk import YCloudML

load_dotenv()


class Agent:
    def __init__(self) -> None:
        folder_id = os.getenv("folder_id")
        auth = os.getenv("api_key")
        if folder_id is None:
            raise ValueError("folder id enviroment variable is required")
        if auth is None:
            raise ValueError("api_key enviroment variable is required")
        self._sdk = YCloudML(folder_id=folder_id, auth=auth)
        self._model = self._sdk.models.completions("yandexgpt", model_version="rc")

    def ask_question(self):
        try:
            question = input("Введите вопрос: ")
            print(self._model.run(question).text)
        except Exception as e:
            print(f"Error: {e}")
