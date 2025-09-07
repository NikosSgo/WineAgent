from pydantic import BaseModel, Field


class Handover(BaseModel):
    """Эта функция позволяет передать диалог человеку-оператору поддержки"""

    reason: str = Field(
        description="Причина для вызова оператора", default="не указана"
    )

    def process(self, thread):
        return f"Я побежала вызывать оператора, ваш {
            thread.id=}, причина: {self.reason}"
