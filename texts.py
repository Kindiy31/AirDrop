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

    def paste_photo_or_text(self):
        return "Відправте мені фото, відео або текст"

    def admin_menu(self):
        return "Ви в адміністративному меню"

    def mailing(self):
        return "Розсилка"

    def paste_caption(self):
        return "Введіть опис"

    def new_deposit(self, amount):
        return f"Ваш баланс поповнено на {amount} {self.token}"

    def insert_amount(self, path):
        if path == "deposit":
            path = "Поповнення"
        else:
            path = "Виводу"
        return f"Введіть суму {path}"

    def only_int(self):
        return "Введіть лише ціле число"

    def insert_hash(self):
        return "Введіть хеш транзакції"

    def insert_address(self):
        return "Введіть адресу на вивід"

    def transaction_modifided_before(self):
        return "Транзакція вже оброблена"

    def modifided_transaction(self, transaction: Transaction):
        msg = f"""Ваша транзакція №{transaction.id} {"не" if transaction.status == 3 else ''} прийнята"""
        if transaction.transaction_type == 1:
            if transaction.status == 3:
                msg += f"""
{transaction.amount} {self.token} були повернуті на баланс"""
        elif transaction.transaction_type == 0:
            if transaction.status == 2:
                msg += f"""
{transaction.amount} {self.token} були зараховані на баланс"""
        return msg


    def transaction_created(self, transaction: Transaction, is_admin=False):
        if is_admin:
            msg = f"""Транзакція № {transaction.id}

Сума: {transaction.amount}

"""
            if transaction.transaction_type == 0:
                msg += f"""Тип: Депозит
Хеш: {transaction.transaction_hash}
"""
            elif transaction.transaction_type == 1:
                msg += f"""Тип: Вивід
Адреса: {transaction.address}
"""
            elif transaction.transaction_type == 2:
                msg += f"""Тип: Покупка
ID предмету: {transaction.item_id}
"""
            msg += f"""
Дата створення: {transaction.created_at}
Статус: {"Створено" if transaction.status == 1 else "Прийнято" if transaction.status == 2 else "Відхилено" if transaction.status == 3 else "Невідомо"}"""
            return msg
        return f"""Транзакцію №{transaction.id} створено!

Очікуйте підтвердження адміністратора"""

    def confirm(self):
        return "Прийняти"

    def cancel(self):
        return "Відхилити"


class EnLanguage(UaLanguage):
    def __init__(self):
        super().__init__()
        self.language_name = "English"

    def home(self):
        return "Home menu"

    def back(self):
        return "Back"

    def profile(self):
        return "Profile"

    def balance(self):
        return "Balance"

    def my_sales(self):
        return "My purchases"

    def market(self):
        return "Market"

    def website(self):
        return "Our website"

    def admin(self):
        return "Admin"

    def choose_language(self):
        return "Choose language"

    def ua(self):
        return 'UA 🇺🇦'

    def en(self):
        return "EN 🇬🇧"

    def home_menu(self):
        return "You are in the main menu"

    def new_language_set(self):
        return f"New language set: {self.language_name}"

    def balance_view(self, user: User):
        return f"Your current balance: {user.balance} {self.token}"

    def not_insert(self):
        return "Not specified"

    def deposit(self):
        return "Deposit"

    def withdraw(self):
        return "Withdraw"

    def change_email(self):
        return "Change email"

    def insert_email(self):
        return "Enter your email"

    def incorrect_email(self):
        return "Incorrect email address"

    def item_preview(self, item: Item):
        return f"""{item.name}

{item.description}

Price: <b>{item.price} {self.token}</b>"""

    def buy(self):
        return "Buy"

    def preview_purchase(self, item, purchase):
        return f"""Purchase №{purchase.id}

<b>{item.name}</b>

Purchase price: {item.price} {self.token}
Purchase date: {purchase.created_at}
Status: {purchase.status}"""

    def not_purchases(self):
        return "You have no purchases yet"

    def paste_photo_or_text(self):
        return "Send me a photo, video or text"

    def admin_menu(self):
        return "You are in the admin menu"

    def mailing(self):
        return "Mailing"

    def paste_caption(self):
        return "Enter a caption"

    def new_deposit(self, amount):
        return f"Your balance has been replenished by {amount} {self.token}"

    def insert_amount(self, path):
        if path == "deposit":
            path = "Deposit"
        else:
            path = "Withdrawal"
        return f"Enter the amount of {path}"

    def only_int(self):
        return "Enter only an integer"

    def insert_hash(self):
        return "Enter the transaction hash"

    def insert_address(self):
        return "Enter the withdrawal address"

    def transaction_modifided_before(self):
        return "The transaction has already been processed"

    def modifided_transaction(self, transaction: Transaction):
        msg = f"""Your transaction №{transaction.id} {"not" if transaction.status == 3 else ''} accepted"""
        if transaction.transaction_type == 1:
            if transaction.status == 3:
                msg += f"""
{transaction.amount} {self.token} were returned to the balance"""
        elif transaction.transaction_type == 0:
            if transaction.status == 2:
                msg += f"""
{transaction.amount} {self.token} were credited to the balance"""
        return msg

    def transaction_created(self, transaction: Transaction, is_admin=False):
        if is_admin:
            msg = f"""Transaction № {transaction.id}

Amount: {transaction.amount}

"""
            if transaction.transaction_type == 0:
                msg += f"""Type: Deposit
Hash: {transaction.transaction_hash}
"""
            elif transaction.transaction_type == 1:
                msg += f"""Type: Withdrawal
Address: {transaction.address}
"""
            elif transaction.transaction_type == 2:
                msg += f"""Type: Purchase
Item ID: {transaction.item_id}
"""
            msg += f"""
Creation date: {transaction.created_at}
Status: {"Created" if transaction.status == 1 else "Accepted" if transaction.status == 2 else "Rejected" if transaction.status == 3 else "Unknown"}"""
            return msg
        return f"""Transaction №{transaction.id} created!

Waiting for administrator confirmation"""

    def confirm(self):
        return "Accept"

    def cancel(self):
        return "Reject"



def get_language(language=1):
    if language == 1:
        language = UaLanguage()
    elif language == 2:
        language = EnLanguage()
    else:
        language = UaLanguage()
    return language
