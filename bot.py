import typing

import aiogram
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputTextMessageContent,
)

from db.storage import UserStorage, User


class AskMessageToSend(StatesGroup):
    message = State()
    confirmation = State()


def get_user_full_name(user: User) -> str:
    user_full_name = user.first_name
    if user.second_name is not None:
        user_full_name += " " + user.second_name
    return user_full_name


class TG_Bot:
    def __init__(self, bot_token: str, user_storage: UserStorage):
        self._user_storage: UserStorage = user_storage
        self._bot: aiogram.Bot = aiogram.Bot(
            token=bot_token, default=DefaultBotProperties(parse_mode="HTML")
        )
        self._storage: MemoryStorage = MemoryStorage()
        self._dispatcher: aiogram.Dispatcher = aiogram.Dispatcher(storage=self._storage)
        self._create_keyboards()

    async def init(self):
        self._init_handler()

    async def start(self):
        print("Bot has started")
        await self._dispatcher.start_polling(self._bot)

    async def _show_menu(self, message: aiogram.types.Message, user: User):
        await message.answer("Добро пожаловать", reply_markup=self._menu_keyboard_user)

    async def _show_recipents(self, inline_query: InlineQuery):
        results = []
        all_users = await self._user_storage.get_all_members()

        for user in all_users:
            user_full_name = get_user_full_name(user)
            results.append(
                InlineQueryResultArticle(
                    id=str(user.id),
                    title=user_full_name,
                    input_message_content=InputTextMessageContent(
                        message_text=f"Написать <a href='tg://user?id={user.id}'>{user_full_name}</a>",
                        parse_mode="HTML",
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="Написать",
                                    callback_data=f"write {user.id}",
                                )
                            ]
                        ],
                        resize_keyboard=True,
                    ),
                )
            )

        await inline_query.answer(results, is_personal=True, cache_time=10)

    async def _ask_message_to_send(self, call: CallbackQuery, state: FSMContext):
        await self._bot.send_message(call.from_user.id, "Введите сообщение:")
        await state.set_state(AskMessageToSend.message)
        await state.update_data(recipient_id=call.data.split()[1])

    async def _verificate_message_to_send(
        self, message: aiogram.types.Message, state: FSMContext
    ):
        if message.content_type != aiogram.types.ContentType.TEXT:
            await message.reply(
                "К отправке принимаются только текстовые сообщения",
                reply_markup=self._cancel_keyboard,
            )
            return

        checked_text = message.text + "\n\nпроверено"

        await state.update_data(message=checked_text)
        await state.set_state(AskMessageToSend.confirmation)
        await message.answer(
            "Подтвердите отправку измененного сообщения по кнопке ниже:",
        )
        await message.answer(
            checked_text,
            reply_markup=self._message_confirming_keyboard,
        )

    async def _send_message(self, call: CallbackQuery, state: FSMContext):
        await call.message.edit_reply_markup()
        state_data = await state.get_data()
        recipient_id = state_data["recipient_id"]
        message = state_data["message"]

        await self._bot.send_message(recipient_id, message)

        user = await self._user_storage.get_by_id(int(recipient_id))
        user_full_name = get_user_full_name(user)
        await call.message.answer(
            f"Сообщение успешно отправлено пользователю {user_full_name}",
            reply_markup=self._to_menu_keyboard_user,
        )
        await state.clear()

    async def _cancel(self, call: CallbackQuery, state: FSMContext):
        if state is not None:
            await state.clear()
            await call.answer("Возвращение в меню")
        await self._bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id
        )
        user = await self._user_storage.get_by_id(call.from_user.id)
        await self._show_menu(call.message, user)

    def _init_handler(self):
        self._dispatcher.message.register(
            self._user_middleware(self._show_menu), Command(commands=["start", "menu"])
        )
        self._dispatcher.message.register(
            self._user_middleware(self._show_menu), aiogram.F.text == "Menu"
        )
        self._dispatcher.inline_query.register(
            self._show_recipents, aiogram.F.query == "list"
        )
        self._dispatcher.callback_query.register(
            self._ask_message_to_send, aiogram.F.data.startswith("write")
        )
        self._dispatcher.message.register(
            self._verificate_message_to_send, AskMessageToSend.message
        )
        self._dispatcher.callback_query.register(
            self._send_message,
            aiogram.F.data.startswith("send"),
            AskMessageToSend.confirmation,
        )
        self._dispatcher.callback_query.register(
            self._cancel, aiogram.F.data == "cancel"
        )

    def _user_middleware(self, func: typing.Callable) -> typing.Callable:
        async def wrapper(message: aiogram.types.Message, *args, **kwargs):
            user = await self._user_storage.get_by_id(message.chat.id)
            if user is None:
                user = User(
                    id=message.chat.id,
                    role=User.USER,
                    first_name=message.from_user.first_name,
                    second_name=message.from_user.last_name,
                )
                await self._user_storage.create(user)

            if user.role != User.BLOCKED:
                await func(message, user)

        return wrapper

    def _create_keyboards(self):
        self._menu_keyboard_user = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Выбрать получателя",
                        switch_inline_query_current_chat="list",
                    )
                ]
            ],
            resize_keyboard=True,
        )
        self._to_menu_keyboard_user = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Menu")]],
            resize_keyboard=True,
        )
        self._message_confirming_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Отправить",
                        callback_data="send",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Отмена",
                        callback_data="cancel",
                    )
                ],
            ],
            resize_keyboard=True,
        )
        self._cancel_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="ОТМЕНА", callback_data="cancel")]
            ],
            resize_keyboard=True,
        )
