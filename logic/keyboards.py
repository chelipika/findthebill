from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder



def create_home_markup_kb(home,tgId):
    keyboard = InlineKeyboardBuilder()
    for h in home:
        keyboard.add(InlineKeyboardButton(text=h,callback_data=f"home_{tgId}_{h}"))
    return keyboard.adjust(2).as_markup()

def create_back_button(nav: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"nav_{nav}")]
    ])
    return keyboard


def create_markap_kb(name, url):
    if name == "None" or url== "None":
        return None
    ads_channel = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, url=url)]
    ])
    return ads_channel