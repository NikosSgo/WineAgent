import os
from typing import Dict, Optional

import telebot
from dotenv import load_dotenv
from yandex_cloud_ml_sdk import YCloudML

from agent.Agent import Agent
from function_calls import (
    SearchWinePriceList,
    Handover,
    AddToCart,
    ShowCart,
    ClearCart
)
from search_index.get_search_index import get_search_index

# Константы
MODEL_NAME = "yandexgpt"
MODEL_VERSION = "rc"
SEARCH_INDEX_FILE = "search_index.json"
THREAD_TTL_DAYS = 1
EXPIRATION_POLICY = "static"


class TelegramBot:
    """Класс для управления Telegram ботом."""

    def __init__(self):
        load_dotenv()
        self._validate_environment()

        self.folder_id = os.getenv("FOLDER_ID")
        self.api_key = os.getenv("API_KEY")
        self.telegram_token = os.getenv("TG_TOKEN")

        self.sdk = YCloudML(folder_id=self.folder_id, auth=self.api_key)
        self.model = self.sdk.models.completions(
            MODEL_NAME, model_version=MODEL_VERSION)
        self.index = get_search_index(self.sdk, self.model, SEARCH_INDEX_FILE)

        self.bot = telebot.TeleBot(self.telegram_token)
        self.threads: Dict[int, any] = {}

        self._setup_agent()
        self._setup_handlers()

    def _validate_environment(self) -> None:
        """Проверяет наличие необходимых переменных окружения."""
        required_vars = ["FOLDER_ID", "API_KEY", "TG_TOKEN"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(f"Missing environment variables: {
                             ', '.join(missing_vars)}")

    def _setup_agent(self) -> None:
        """Настраивает агента сомелье."""
        instruction = """
        Ты - опытный сомелье, в задачу которого входит отвечать на вопросы пользователя про вина
        и рекомендовать лучшие вина к еде, а также искать вина в прайс-листе нашего магазина. 
        Посмотри на всю имеющуюся в твоем распоряжении информацию
        и выдай одну или несколько лучших рекомендаций.
        Если вопрос касается конкретных вин или цены, то вызови функцию SearchWinePriceList.
        Для передачи управления оператору - вызови функцию Handover. Для добавления вина в корзину
        используй AddToCart. Для просмотра корзины: ShowCart. Если нужно очистить корзину: ClearCart. 
        Все названия вин, цветов, кислотности пиши на русском языке.
        Если что-то непонятно, то лучше уточни информацию у пользователя.
        """

        self.wine_agent = Agent(
            model=self.model,
            sdk=self.sdk,
            instruction=instruction,
            search_index=self.index,
            tools=[SearchWinePriceList, Handover,
                   AddToCart, ShowCart, ClearCart],
        )

    def _setup_handlers(self) -> None:
        """Настраивает обработчики сообщений."""
        @self.bot.message_handler(commands=["start"])
        def start_handler(message):
            self._handle_message(message, is_start=True)

        @self.bot.message_handler(func=lambda message: True)
        def message_handler(message):
            self._handle_message(message, is_start=False)

    def _get_thread(self, chat_id: int):
        """Получает или создает тред для чата."""
        if chat_id in self.threads:
            return self.threads[chat_id]

        thread = self.sdk.threads.create(
            ttl_days=THREAD_TTL_DAYS,
            expiration_policy=EXPIRATION_POLICY
        )
        print(f"New thread {thread.id} created for chat {chat_id}")
        self.threads[chat_id] = thread
        return thread

    def _handle_message(self, message, is_start: bool = False) -> None:
        """Обрабатывает входящее сообщение."""
        try:
            thread = self._get_thread(message.chat.id)
            print(f"Processing message on thread {
                  thread.id}, msg={message.text}")

            response = self.wine_agent(message.text, thread=thread)
            self.bot.send_message(message.chat.id, response)

        except Exception as e:
            error_message = "Извините, произошла ошибка. Попробуйте позже."
            print(f"Error processing message: {e}")
            self.bot.send_message(message.chat.id, error_message)

    def run(self) -> None:
        """Запускает бота."""
        print("Бот готов к работе")
        try:
            self.bot.polling(none_stop=True)
        except KeyboardInterrupt:
            print("Бот остановлен пользователем")
        except Exception as e:
            print(f"Ошибка при работе бота: {e}")


def main():
    """Основная функция запуска приложения."""
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        print(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    main()
