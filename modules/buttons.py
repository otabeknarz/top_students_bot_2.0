from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)


class Buttons:
    def __init__(self):
        self.remove_keyboard = ReplyKeyboardRemove()

    @staticmethod
    def main_keyboard():
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📊 Natijalarim")]])


class InlineButtons:
    @staticmethod
    def get_join_channel_buttons(channels: dict) -> InlineKeyboardMarkup:
        inline_buttons = [
            [InlineKeyboardButton(text=channel_name, url=channel_link)]
            for channel_id, (channel_name, channel_link) in channels.items()
        ]
        inline_buttons.append(
            [
                InlineKeyboardButton(
                    text="✅ I've joined them all", callback_data="joined"
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=inline_buttons)
