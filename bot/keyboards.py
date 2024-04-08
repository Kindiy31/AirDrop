import json
import config
from texts import get_language
from aiogram import types
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


class Keyboards:
    def __init__(self, language=1):
        self.language = get_language(language=language)

    def generate_reply_markup(self, buttons, home=None, back=None):
        buttons_list = []
        for row in buttons:
            if row:
                if len(row) != 1:
                    buttons_list.append([KeyboardButton(text=text) for text in row])
                else:
                    buttons_list.append([KeyboardButton(text=row[0])])
        if home:
            buttons_list.append(
                [
                    KeyboardButton(text=self.language.home())
                ]
            )
        if back:
            buttons_list.append(
                [
                    KeyboardButton(text=self.language.back())
                ]
            )
        markup = types.ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)
        return markup

    def generate_inline_markup(self, buttons, back=None):
        buttons_list = []
        for data in buttons:
            row = []
            for button in data:
                name = button.get('name')
                if 'callback' in button:
                    callback = button.get('callback')
                    row.append(InlineKeyboardButton(text=name, callback_data=callback))
                elif 'webapp' in button:
                    webapp = WebAppInfo(url=button.get('webapp'))
                    row.append(InlineKeyboardButton(text=name, web_app=webapp))
                elif 'url' in button:
                    url = button.get('url')
                    row.append(InlineKeyboardButton(text=name, url=url))
            if row:
                buttons_list.append(row)
        if back is True:
            buttons_list.append([InlineKeyboardButton(text=self.language.back(), callback_data="home")])
        elif back:
            buttons_list.append([InlineKeyboardButton(text=self.language.back(), callback_data=back)])
        markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=buttons_list)
        return markup

    def home(self, user):
        buttons = [
            [
                {
                    "name": self.language.profile(),
                    "callback": 'profile'
                },
                {
                    "name": self.language.balance(),
                    "callback": 'balance'
                }
            ],
            [
                {
                    "name": self.language.my_sales(),
                    "callback": 'mySales'
                },
                {
                    "name": self.language.market(),
                    "callback": 'market'
                }
            ],
            [
                {
                    "name": self.language.website(),
                    "webapp": config.my_url
                }
            ]
        ]
        if user.is_admin:
            buttons.append(
                [
                    {
                        "name": self.language.admin(),
                        "callback": 'admin'
                    }
                ]
            )
        markup = self.generate_inline_markup(buttons=buttons)
        return markup

    def item(self, item_id):
        buttons = [
            [
                {
                    "name": self.language.buy(),
                    "callback": f"market_buy_{item_id}"
                }
            ]
        ]
        markup = self.generate_inline_markup(buttons=buttons, back=True)
        return markup

    def admin(self):
        buttons = [
            [
                {
                    "name": self.language.mailing(),
                    "callback": "admin_mailing"
                }
            ]
        ]
        markup = self.generate_inline_markup(buttons=buttons, back=True)
        return markup

    def go_to_home_menu(self):
        buttons = [
            [
                {
                    "name": self.language.home(),
                    "callback": "home"
                }
            ]
        ]
        markup = self.generate_inline_markup(buttons=buttons)
        return markup

    def choose_language(self):
        buttons = [
            [
                {
                    "name": self.language.ua(),
                    "callback": "language_ru"
                },
                {
                    "name": self.language.en(),
                    "callback": "language_en"
                }
            ]
        ]
        markup = self.generate_inline_markup(buttons=buttons)
        return markup

    def balance(self):
        buttons = [
            [
                {
                    "name": self.language.deposit(),
                    "callback": "balance_deposit"
                },
                {
                    "name": self.language.withdraw(),
                    "callback": "balance_withdraw"
                }
            ]
        ]
        markup = self.generate_inline_markup(buttons=buttons, back=True)
        return markup

    def profile(self):
        buttons = [
            [
                {
                    "name": self.language.change_email(),
                    "callback": "profile_email"
                }
            ]
        ]
        markup = self.generate_inline_markup(buttons=buttons, back=True)
        return markup

    def back(self):
        buttons = [
            [
            ]
        ]
        markup = self.generate_inline_markup(buttons=buttons, back=True)
        return markup
