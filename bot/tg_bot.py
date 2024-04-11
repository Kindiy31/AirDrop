import re
import sys
import asyncio
import logging
from aiogram import types
from aiogram.types import ContentType
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.client.bot import DefaultBotProperties
from bot.keyboards import Keyboards, get_language

sys.path.append('..')

import config
from database import Database


db = Database()
form_router = Router()
kb = Keyboards()
bot = Bot(token=config.TOKEN,
          default=DefaultBotProperties(parse_mode='HTML'))


class States(StatesGroup):
    email = State()
    mailing = State()
    deposit = State()
    withdraw = State()


def get_name_with_link(user=None, user_username=None, user_name=None):
    if user:
        user_name = user.get('first_name')
        user_username = user.get('username')
    if user_username:
        user_name = f'<a href="t.me/{user_username}">{user_name}</a>'
    return user_name


class HandlerUser:
    def __init__(self, id_user, state=None, call=None, message=None):
        self.state = state
        self.message = message
        self.id_user = id_user
        self.language = get_language()
        self.user = None
        self.kb = Keyboards()
        self.call = call
        if self.call:
            self.states = self.call.data.split('_')
        else:
            self.states = None

    async def connect(self):
        self.user = await db.take_users(id_user=self.id_user)
        if self.user:
            self.language = get_language(language=self.user.language)
            self.kb = Keyboards(language=self.user.language)
            if not self.user.language:
                if self.call:
                    if self.states[0] != "language":
                        return True
                else:
                    return True

    async def handler_start(self):
        if not self.user:
            await db.register(message=self.message)
            await self.connect()
        if self.user:
            if not self.user.language:
                await self.send_choose_language()
            else:
                await self.starting_bot()

    async def starting_bot(self, is_edit=None, old_call=None):
        if not old_call:
            data = await self.state.get_data()
            old_call = data.get('msg_to_change')
        if old_call:
            self.call = old_call
        await self.clear_old_message()
        await self.state.clear()
        if not is_edit:
            await bot.send_message(self.id_user, self.language.home_menu(),
                                   reply_markup=self.kb.home(user=self.user))
        else:
            if is_edit:
                await self.edit_via_call(text=self.language.home_menu(),
                                         reply_markup=self.kb.home(user=self.user),
                                         old_call=old_call)

    async def send_choose_language(self):
        await bot.send_message(self.id_user, self.language.choose_language(),
                               reply_markup=self.kb.choose_language())

    async def start_mailing(self):
        msg = await bot.send_message(self.id_user, self.language.paste_photo_or_text(),
                                     reply_markup=self.kb.back())
        msgs_to_delete = [msg.message_id,]
        await self.state.update_data(
            msgs_to_delete=msgs_to_delete
        )
        await self.state.set_state(States.mailing)

    async def finish_mailing(self):
        data = await self.state.get_data()
        content_type = data.get('content_type')
        users = await db.take_users()
        if content_type == ContentType.TEXT:
            for user in users:
                await bot.send_message(user.id, data.get('text'))
        elif content_type == ContentType.PHOTO:
            await self.append_msgs_to_delete(self.message.message_id)
            if self.message.content_type == ContentType.TEXT:
                for user in users:
                    await bot.send_photo(user.id, data.get('file_id'),
                                         caption=self.message.text)
        elif content_type == ContentType.VIDEO:
            await self.append_msgs_to_delete(self.message.message_id)
            if self.message.content_type == ContentType.TEXT:
                for user in users:
                    await bot.send_video(user.id, data.get('file_id'),
                                         caption=self.message.text)
        await self.starting_bot(is_edit=data.get('msg_to_change'))

    async def append_msgs_to_delete(self, message_id):
        data = await self.state.get_data()
        msgs_to_delete = data.get('msgs_to_delete')
        if not msgs_to_delete:
            msgs_to_delete = []
        msgs_to_delete.append(message_id)
        await self.state.update_data(
            msgs_to_delete=msgs_to_delete
        )

    async def get_fist_mail(self):
        await self.append_msgs_to_delete(self.message.message_id)
        if self.message.content_type == ContentType.TEXT:
            await self.state.update_data(
                content_type=self.message.content_type,
                text=self.message.text
            )
            await self.finish_mailing()
        elif self.message.content_type == ContentType.PHOTO or self.message.content_type == ContentType.VIDEO:
            await self.state.update_data(
                content_type=self.message.content_type,
                file_id=self.message.photo[-1].file_id if self.message.content_type == ContentType.PHOTO
                else self.message.video.file_id
            )
            msg = await bot.send_message(self.id_user, self.language.paste_caption(),
                                         reply_markup=self.kb.back())
            await self.append_msgs_to_delete(msg.message_id)

    async def callback_manager(self):
        if self.states:
            first_state = self.states[0]
            if first_state == "language":
                await self.set_language()
            elif first_state == "home" or first_state == "back":
                await self.starting_bot(is_edit=True)
            elif first_state == "balance":
                await self.balance_callback()
            elif first_state == "profile":
                await self.profile_callback()
            elif first_state == "market":
                await self.market_callback()
            elif first_state == "mySales":
                await self.my_sales_callback()
            elif first_state == "admin":
                await self.admin_wrapper()

    async def admin_wrapper(self):
        if self.user.is_admin:
            if len(self.states) == 1:
                await self.start_admin()
            elif len(self.states) >= 2:
                if self.states[1] == "mailing":
                    await self.state.update_data(
                        msg_to_change=self.call
                    )
                    await self.start_mailing()
                elif self.states[1] == "transaction":
                    await self.transaction_modify_admin()

    async def transaction_modify_admin(self):
        if len(self.states) == 4:
            id_transaction = int(self.states[2])
            modify_type = self.states[3]
            transaction = await db.take_transactions(id_transaction=id_transaction)
            if transaction.status == 1:
                transaction = await db.modify_transaction(transaction=transaction, modify_type=modify_type)
                creator = await db.take_users(id_user=transaction.user_id)
                await bot.send_message(creator.id, get_language(language=creator.language).modifided_transaction(transaction=transaction))
                await self.edit_via_call(text=self.language.transaction_created(transaction=transaction, is_admin=True))
            else:
                await self.edit_via_call(text=self.language.transaction_created(transaction=transaction, is_admin=True))
                await bot.send_message(self.id_user, self.language.transaction_modifided_before())

    async def start_admin(self):
        if self.user.is_admin:
            await self.edit_via_call(text=self.language.admin_menu(),
                                     reply_markup=self.kb.admin())

    async def my_sales_callback(self):
        purchases = await db.take_purchases(id_user=self.id_user)
        msgs_to_delete = []
        if purchases:
            for purchase in purchases:
                id_item = purchase.item_id
                item = await db.take_items(id_item=id_item)
                msg = await bot.send_photo(self.id_user, item.image_url,
                                           caption=self.language.preview_purchase(item=item, purchase=purchase),
                                           reply_markup=self.kb.back())
                msgs_to_delete.append(msg.message_id)
        else:
            msg = await bot.send_message(self.id_user, self.language.not_purchases(),
                                         reply_markup=self.kb.back())
            msgs_to_delete.append(msg.message_id)
        await self.state.update_data(
            msgs_to_delete=msgs_to_delete,
            msg_to_change=self.call
        )

    async def market_callback(self):
        if len(self.states) == 1:
            items = await db.take_items()
            data = await self.state.get_data()
            msgs_to_delete = data.get('msgs_to_delete')
            if not msgs_to_delete:
                msgs_to_delete = []
            for item in items:
                msg = await bot.send_photo(self.id_user, item.image_url,
                                           caption=self.language.item_preview(item=item),
                                           reply_markup=self.kb.item(item_id=item.id))
                msgs_to_delete.append(msg.message_id)
            msg_to_change = self.call
            await self.state.update_data(
                msgs_to_delete=msgs_to_delete,
                msg_to_change=msg_to_change
            )
        elif len(self.states) == 3:
            if self.states[1] == "buy":
                item_id = int(self.states[2])
                item = await db.take_items(id_item=item_id)
                if float(self.user.balance) < float(item.price):
                    msg = await bot.send_message(self.id_user, self.language.not_enough_money(user=self.user),
                                                 reply_markup=self.kb.back())
                else:
                    purchase = await db.buy_item(id_user=self.id_user, id_item=item_id)
                    item = await db.take_items(id_item=item_id)
                    await self.starting_bot(is_edit=True)
                    msg = await bot.send_photo(self.id_user, item.image_url,
                                               caption=self.language.preview_purchase(item=item, purchase=purchase),
                                               reply_markup=self.kb.back())
                await self.state.update_data(
                    msgs_to_delete=[msg.message_id, ],
                )

    async def balance_callback(self):
        if len(self.states) == 1:
            await self.edit_via_call(text=self.language.balance_view(user=self.user),
                                     reply_markup=self.kb.balance())
        elif len(self.states) == 2:
            if self.states[1] == "deposit" or self.states[1] == "withdraw":
                if self.states[1] == "deposit":
                    await self.state.set_state(States.deposit)
                    transaction_type = 0
                else:
                    await self.state.set_state(States.withdraw)
                    transaction_type = 1
                await self.state.update_data(
                    starting=True,
                    transaction_type=transaction_type
                )
                await self.transaction_creating_wrapper()

    async def transaction_creating_wrapper(self):
        data = await self.state.get_data()
        transaction_type = data.get('transaction_type')
        amount = data.get('amount')
        starting = data.get('starting')
        if starting:
            msg = await bot.send_message(self.id_user, self.language.insert_amount(path=self.states[1]),
                                         reply_markup=self.kb.back())
            await self.append_msgs_to_delete(message_id=msg.message_id)
            await self.state.update_data(
                starting=False
            )
        elif not amount:
            amount = self.message.text
            if amount.isdigit():
                if transaction_type == 1 and float(self.user.balance) < float(amount):
                    msg = await bot.send_message(self.id_user, self.language.not_enough_money(user=self.user),
                                                 reply_markup=self.kb.back())
                    await self.append_msgs_to_delete(message_id=msg.message_id)
                    return
                await self.state.update_data(
                    amount=amount
                )
                if transaction_type == 0:
                    transaction_hash = data.get('transaction_hash')
                    if not transaction_hash:
                        msg = await bot.send_message(self.id_user, self.language.insert_hash(),
                                                     reply_markup=self.kb.back())
                        await self.append_msgs_to_delete(message_id=msg.message_id)

                elif transaction_type == 1:
                    address = data.get('address')
                    if not address:
                        msg = await bot.send_message(self.id_user, self.language.insert_address(),
                                                     reply_markup=self.kb.back())
                        await self.append_msgs_to_delete(message_id=msg.message_id)
            else:
                msg = await bot.send_message(self.id_user, self.language.only_int(),
                                             reply_markup=self.kb.back())
                await self.append_msgs_to_delete(message_id=msg.message_id)
        else:
            if transaction_type == 0:
                transaction_hash = self.message.text
                await self.state.update_data(
                    transaction_hash=transaction_hash,
                    transaction_type=transaction_type
                )
            elif transaction_type == 1:
                address = self.message.text
                await self.state.update_data(
                    address=address,
                    transaction_type=transaction_type
                )
            await self.finish_creating_transaction()

    async def finish_creating_transaction(self):
        data = await self.state.get_data()
        transaction_type = data.get('transaction_type')
        amount = data.get('amount')
        transaction_hash = None
        address = None
        item_id = None
        if transaction_type == 0:
            transaction_hash = data.get('transaction_hash')
        elif transaction_type == 1:
            address = data.get('address')
        elif transaction_type == 2:
            item_id = data.get('item_id')
        transaction = await db.create_transaction(
            transaction_type=transaction_type,
            transaction_hash=transaction_hash,
            address=address,
            amount=amount,
            item_id=item_id,
            user_id=self.id_user
        )
        await bot.send_message(self.id_user, self.language.transaction_created(transaction=transaction))
        admins = await db.take_admins()
        print(admins)
        for admin in admins:
            await bot.send_message(admin.id, self.language.transaction_created(transaction=transaction, is_admin=True),
                                   reply_markup=self.kb.modify_transaction(id_transaction=transaction.id))
        await self.starting_bot()

    async def clear_old_message(self):
        data = await self.state.get_data()
        msgs_to_delete = data.get('msgs_to_delete')
        if msgs_to_delete:
            for msg_id in msgs_to_delete:
                await self.delete_message(msg_id=msg_id)

    async def profile_callback(self):
        if len(self.states) == 1:
            await self.edit_via_call(text=self.language.profile_view(user=self.user),
                                     reply_markup=self.kb.profile())
        elif len(self.states) == 2:
            msg = await bot.send_message(self.id_user, self.language.insert_email(),
                                         reply_markup=self.kb.back())
            print(msg)
            await self.state.update_data(msgs_to_delete=[msg.message_id, ], msg_to_change=self.call)
            await self.state.set_state(States.email)

    async def get_email(self):
        email = self.message.text
        is_valid = await self.is_valid_email(email=email)
        data = await self.state.get_data()
        if is_valid:
            await db.set_email(email=email, id_user=self.id_user)
            msg_to_change = data.get('msg_to_change')
            await self.clear_old_message()
            await self.delete_message(msg_id=self.message.message_id)
            await self.connect()
            await self.edit_via_call(text=self.language.profile_view(user=self.user),
                                     reply_markup=self.kb.profile(),
                                     old_call=msg_to_change)
        else:
            msg = await bot.send_message(self.id_user, self.language.incorrect_email(),
                                         reply_markup=self.kb.back())
            msgs_to_delete = data.get('msgs_to_delete')
            if msgs_to_delete:
                msgs_to_delete.append(msg.message_id)
                msgs_to_delete.append(self.message.message_id)
            else:
                msgs_to_delete = [self.message.message_id, msg.message_id]
            self.state.update_data(msgs_to_delete=msgs_to_delete)

    async def edit_via_call(self, text=None, reply_markup=None, chat_id=None, message_id=None, old_call=None):
        if old_call:
            self.call = old_call
        if not chat_id:
            chat_id = self.call.message.chat.id
        if not message_id:
            message_id = self.call.message.message_id
        if not text:
            text = self.call.message.text
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup
            )
        except:
            pass

    async def delete_message(self, msg_id):
        try:
            await bot.delete_message(chat_id=self.id_user, message_id=msg_id)
        except:
            pass

    async def set_language(self):
        language = self.states[1]
        if language == 'en':
            language_code = 2
        elif language == 'ua':
            language_code = 1
        else:
            language_code = 1
        await db.set_language(language_code=language_code, id_user=self.id_user)
        await self.connect()
        await self.edit_via_call(text=self.language.new_language_set(), reply_markup=self.kb.go_to_home_menu())

    @staticmethod
    async def is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    async def add_balance(self, amount):
        await bot.send_message(self.id_user, self.language.new_deposit(amount=amount))


# Хендлер на команду /start
@form_router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    handler = HandlerUser(id_user=message.from_user.id, message=message, state=state)
    nothing_language = await handler.connect()
    if nothing_language:
        await handler.send_choose_language()
    else:
        await handler.handler_start()


@form_router.callback_query()
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    handler = HandlerUser(id_user=callback_query.from_user.id, call=callback_query, state=state)
    nothing_language = await handler.connect()
    if nothing_language:
        await handler.send_choose_language()
    else:
        await handler.callback_manager()


@form_router.message(States.email)
async def get_email(message: types.Message, state: FSMContext):
    handler = HandlerUser(id_user=message.from_user.id, message=message, state=state)
    nothing_language = await handler.connect()
    if nothing_language:
        await handler.send_choose_language()
    else:
        await handler.get_email()


@form_router.message(States.mailing)
async def get_email(message: types.Message, state: FSMContext):
    handler = HandlerUser(id_user=message.from_user.id, message=message, state=state)
    nothing_language = await handler.connect()
    if nothing_language:
        await handler.send_choose_language()
    else:
        data = await state.get_data()
        content_type = data.get('content_type')
        if content_type:
            await handler.finish_mailing()
        else:
            await handler.get_fist_mail()

@form_router.message(States.deposit)
@form_router.message(States.withdraw)
async def transaction_wrapper(message: types.Message, state: FSMContext):
    handler = HandlerUser(id_user=message.from_user.id, message=message, state=state)
    nothing_language = await handler.connect()
    if nothing_language:
        await handler.send_choose_language()
    else:
        await handler.transaction_creating_wrapper()



async def main():
    await db.connect()
    # await db.add_item(
    #     name="Grass",
    #     description="Grass is the underlying infrastructure that powers AI models. By installing the Grass",
    #     price=150,
    #     image_url="https://app.airdrop-hunter.site/images/grass_logo_updated.png"
    # )
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
