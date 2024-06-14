import typing

import aiogram
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputTextMessageContent,
)

from config_reader import config
from db.storage import UserStorage, User


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
            user_full_name = user.first_name
            if user.second_name is not None:
                user_full_name += " " + user.second_name
            results.append(
                InlineQueryResultArticle(
                    id=str(user.id),
                    title=user_full_name,
                    thumb_url=user.user_pic,
                    thumb_height=100,
                    thumb_width=100,
                    input_message_content=InputTextMessageContent(
                        message_text=f"Написать {user_full_name} <a href='{user.user_pic}'>&#8205</a>",
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

    def _user_middleware(self, func: typing.Callable) -> typing.Callable:
        async def wrapper(message: aiogram.types.Message, *args, **kwargs):
            user = await self._user_storage.get_by_id(message.chat.id)
            if user is None:
                user_pic = None
                user_pics = await message.from_user.get_profile_photos(limit=1)
                if user_pics.photos:
                    user_pic = user_pics.photos[0][0].file_id
                    # user_pic_file = await self._bot.get_file(user_pic)
                    # user_pic_file_path = user_pic_file.file_path
                    # user_pic = f"https://api.telegram.org/file/bot{config.tgbot_api_key.get_secret_value()}/{user_pic_file_path}"

                user = User(
                    id=message.chat.id,
                    role=User.USER,
                    first_name=message.from_user.first_name,
                    second_name=message.from_user.last_name,
                    user_pic=user_pic,
                )
                await self._user_storage.create(user)

            if user.role != User.BLOCKED:
                await func(message, user)

        return wrapper

    def _admin_required(self, func: typing.Callable) -> typing.Callable:
        async def wrapper(message: aiogram.types.Message, user: User, *args, **kwargs):
            if user.role == User.ADMIN:
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
