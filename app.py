import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, FSInputFile

from modules import functions
from modules import settings
from modules.buttons import Buttons, InlineButtons
from modules.filters import TextEqualsFilter

load_dotenv()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

buttons = Buttons()
inline_buttons = InlineButtons()

photo = FSInputFile("top-students.jpg")
get_welcome_text = (
    lambda name, join_link: f"""
🚀 <strong>{name}</strong> is inviting you to "TOP Students" marathon 2.0
Have you heard about liberal arts colleges? What differentiates them from universities? How can you win 100% scholarships to study at them?
Our marathon speakers - full-ride scholarship students at Colby, Amherst, and Haverford college - will share their journeys of admissions and all you need to know about these schools in our marathon.

❕ How to join:

- register and invite 3 of your friends to the marathon 

🎁 We are also giving out 6 consultations for free:

- 3 consultations to the participants who invited the most number of their friends 
- during the webinars, you can donate. Everyday the person to donate the most amount of money will also receive a consultation. (All the money donated will  be given to a charity)

🗓 Dates: June 27, 28, 29

🔽Join:

https://t.me/top_students_bot?start={join_link}
"""
)


async def check_is_subscribed(chat_id, user_id) -> bool:
    try:
        status = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return status.status != "left"
    except Exception as e:
        logger.error(e)
        return False


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_json = {
        "id": message.from_user.id,
        "username": message.from_user.username or message.from_user.id,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name or "",
    }
    response = functions.post_request(url=settings.USERS_API, json=user_json)

    if response.ok:
        parts = message.text.strip().split(maxsplit=1)
        await functions.handle_start_with_invitation(
            bot=bot, message=message, parts=parts
        )

    subscription_statuses = {True: {}, False: {}}
    for channel_id, (channel_name, channel_link) in settings.CHANNELS_IDs.items():
        status = await check_is_subscribed(channel_id, message.from_user.id)
        subscription_statuses[status].update({channel_id: (channel_name, channel_link)})

    if subscription_statuses.get(False):
        unjoined_channels_inline_buttons = inline_buttons.get_join_channel_buttons(
            subscription_statuses.get(False)
        )
        await message.answer(
            "birinchi ushbu kanallarga ulanib oling",
            reply_markup=unjoined_channels_inline_buttons,
        )
        return

    if not response.ok:
        response = functions.get_request(
            url=f"{settings.USERS_API}{message.from_user.id}/"
        )

    json_response = response.json()
    await message.answer_photo(
        photo=photo,
        caption=get_welcome_text(
            (
                f"@{message.chat.username}"
                if message.chat.username
                else message.chat.full_name
            ),
            json_response.get("invitation_token"),
        ),
        reply_markup=buttons.main_keyboard(),
    )


@dp.message(TextEqualsFilter("📊 Natijalarim"))
async def my_stats_handler(message: Message) -> None:
    response = functions.get_request(url=f"{settings.USERS_API}{message.from_user.id}/")
    if response.ok:
        json_response = response.json()
        await message.answer(
            f"Siz {len(json_response.get('invitations'))} ta do'stingizni taklif qilgansiz",
            reply_markup=buttons.main_keyboard(),
        )
    else:
        await message.answer(
            "Qandaydir muammo yuz berdi biz bilan bog'laning (skringshotlarni yuborishni unutmang @otabke_narz)",
            reply_markup=buttons.remove_keyboard,
        )


@dp.callback_query()
async def all_callback_handler(callback: CallbackQuery) -> None:
    query = callback.data

    if query == "joined":
        subscription_statuses = {True: {}, False: {}}
        for channel_id, (channel_name, channel_link) in settings.CHANNELS_IDs.items():
            status = await check_is_subscribed(channel_id, callback.message.chat.id)
            subscription_statuses[status].update(
                {channel_id: (channel_name, channel_link)}
            )

        if subscription_statuses.get(False):
            unjoined_channels_inline_buttons = inline_buttons.get_join_channel_buttons(
                subscription_statuses.get(False)
            )
            await callback.message.delete()
            await asyncio.sleep(0.5)
            await callback.message.answer(
                "birinchi ushbu kanallarga ulanib oling",
                reply_markup=unjoined_channels_inline_buttons,
            )

        else:
            response = functions.get_request(
                url=f"{settings.USERS_API}{callback.message.chat.id}/"
            )
            if not response.ok:
                response = functions.get_request(
                    url=f"{settings.USERS_API}{callback.message.chat.id}/"
                )

            json_response = response.json()
            await callback.message.answer_photo(
                photo=photo,
                caption=get_welcome_text(
                    (
                        f"@{callback.message.chat.username}"
                        if callback.message.chat.username
                        else callback.message.chat.full_name
                    ),
                    json_response.get("invitation_token"),
                ),
                reply_markup=buttons.main_keyboard(),
            )


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
