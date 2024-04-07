from models import *

class UaLanguage:
    def __init__(self):
        self.name = "AirDrop"
        self.token = 'USDT'
        self.language_name = "Українська"

    def home(self):
        return "Головне меню"

    def back(self):
        return "Назад"

    def profile(self):
        return "Профіль"

    def balance(self):
        return "Баланс"

    def my_sales(self):
        return "Мої покупки"

    def market(self):
        return "Магазин"

    def website(self):
        return "Наш сайт"

    def admin(self):
        return "Адміністратор"

    def choose_language(self):
        return "Оберіть мову / Please choose language"

    def ua(self):
        return 'UA 🇺🇦'

    def en(self):
        return "EN 🇬🇧"

    def home_menu(self):
        return "Ви в головному меню"

    def new_language_set(self):
        return f"Нову мову встановлено: {self.language_name}"

    def balance_view(self, user: User):
        return f"В даний момент ваш баланс: {user.balance} {self.token}"

    def not_insert(self):
        return "Не вказано"

    def deposit(self):
        return "Поповнити"

    def withdraw(self):
        return "Вивести"

    def profile_view(self, user: User):
        return f"""Вітаю, {user.first_name}

Ваш юзернейм: {user.username}
Ваша ел.адреса: {user.email if user.email else self.not_insert()}

Профіль створено: {user.created_at}
"""

    def change_email(self):
        return "Змінити ел.адресу"

    def insert_email(self):
        return "Введіть вашу ел.адресу"

    def incorrect_email(self):
        return "Введена не коректна адреса"

    def item_preview(self, item: Item):
        return f"""{item.name}

{item.description}

Price: <b>{item.price} {self.token}</b>"""

    def buy(self):
        return "Купити"

    def preview_purchase(self, item, purchase):
        return f"""Покупка №{purchase.id}

<b>{item.name}</b>

Ціна покупки: {item.price} {self.token}
Дата покупки: {purchase.created_at}
Статус: {purchase.status}"""

    def not_purchases(self):
        return "У вас ще немає покупок"


class EnLanguage(UaLanguage):
    def __init__(self):
        super().__init__()
        self.language_name = "English"

    def home(self):
        return "Home menu"

    def back(self):
        return "Back"

    def admin(self):
        return "Admin"

    def home_menu(self):
        return "Hello at home menu"

    def new_language_set(self):
        return f"New language set: {self.language_name}"


def get_language(language=1):
    if language == 1:
        language = UaLanguage()
    elif language == 2:
        language = EnLanguage()
    else:
        language = UaLanguage()
    return language
