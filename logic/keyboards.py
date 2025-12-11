from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


home_page = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Uyni qoshish", callback_data="create_home")],
])


def create_home_markup_kb(home):
    keyboard = InlineKeyboardBuilder()
    for h in home:
        keyboard.add(InlineKeyboardButton(text=h.home_name,callback_data=f"home_{h.id}")) # h.id should be fine but not sure
    return keyboard.adjust(2).as_markup()

def create_back_button(nav: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"nav_{nav}")]
    ])
    return keyboard


def create_regions_markup_kb(regions_list: list, nav: str):
    keyboard = InlineKeyboardBuilder()
    for region in regions_list:
        keyboard.add(InlineKeyboardButton(text=region["name"],callback_data=f"state_{region['name']}"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Back", callback_data=f"nav_{nav}"))
    return keyboard.adjust(2).as_markup()


def create_state_regions_markup_kb(regions_list: list, nav: str, state_name):
    keyboard = InlineKeyboardBuilder()
    for region in regions_list:
        keyboard.add(InlineKeyboardButton(text=region["name"],callback_data=f"region_{region['name']}_{state_name}"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Back", callback_data=f"nav_{nav}"))
    return keyboard.adjust(2).as_markup()

def create_markap_kb(name, url):
    if name == "None" or url== "None":
        return None
    ads_channel = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, url=url)]
    ])
    return ads_channel