from pydantic import BaseModel, Field
import pandas as pd

pl = pd.read_excel("data/wine-price.xlsx")

pl.columns = ["Id", "Name", "Country", "Price", "WHPrice", "etc"]

acid_map = {"СХ": "Сухое", "СЛ": "Сладкое", "ПСХ": "Полусухое", "ПСЛ": "Полусладкое"}
pl["Acidity"] = pl["Name"].apply(
    lambda x: acid_map.get(x.split()[-1].replace("КР", ""), "")
)
pl["Acidity"].value_counts()


pl["Color"] = pl["Name"].apply(
    lambda x: (
        "Красное" if (x.split()[-1].startswith("КР") or x.split()[-2] == "КР") else ""
    )
)
pl["Color"].value_counts()


country_map = {
    "IT": "Италия",
    "FR": "Франция",
    "ES": "Испания",
    "RU": "Россия",
    "PT": "Португалия",
    "AR": "Армения",
    "CL": "Чили",
    "AU": "Австрия",
    "GE": "Грузия",
    "ZA": "ЮАР",
    "US": "США",
    "NZ": "Новая Зеландия",
    "DE": "Германия",
    "AT": "Австрия",
    "IL": "Израиль",
    "BG": "Болгария",
    "GR": "Греция",
}

revmap = {v.lower(): k for k, v in country_map.items()}


def find_wines(req):
    x = pl.copy()
    if req.country and req.country.lower() in revmap.keys():
        x = x[x["Country"] == revmap[req.country.lower()]]
    if req.acidity:
        x = x[x["Acidity"] == req.acidity.capitalize()]
    if req.color:
        x = x[x["Color"] == req.color.capitalize()]
    if req.name:
        x = x[x["Name"].apply(lambda x: req.name.lower() in x.lower())]
    if req.sort_order and len(x) > 0:
        if req.sort_order == "cheapest":
            x = x.sort_values(by="Price")
        elif req.sort_order == "most expensive":
            x = x.sort_values(by="Price", ascending=False)
        else:
            pass
    if x is None or len(x) == 0:
        return "Подходящих вин не найдено"
    return "Вот какие вина были найдены:\n" + "\n".join(
        [
            f"{z['Name']} ({country_map.get(z['Country'], 'Неизвестно')}) - {
                z['Price']
            }"
            for _, z in x.head(10).iterrows()
        ]
    )


class SearchWinePriceList(BaseModel):
    """Эта функция позволяет искать вина в прайс-листе по одному или нескольким параметрам."""

    name: str = Field(description="Название вина", default=None)
    country: str = Field(description="Страна", default=None)
    acidity: str = Field(
        description="Кислотность (сухое, полусухое, сладкое, полусладкое)", default=None
    )
    color: str = Field(description="Цвет вина (красное, белое, розовое)", default=None)
    sort_order: str = Field(
        description="Порядок выдачи (most expensive, cheapest, random, average)",
        default=None,
    )
    what_to_return: str = Field(
        description="Что вернуть (wine info или price)", default=None
    )

    def process(self, thread):
        return find_wines(self)
