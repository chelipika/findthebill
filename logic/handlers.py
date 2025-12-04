

from config import TOKEN, CHANNEL_ID, authToken
import database.requests as rq


import requests
from datetime import datetime, timedelta
from collections import defaultdict


from aiogram import F, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery, FSInputFile, ChatJoinRequest
from aiogram.exceptions import TelegramBadRequest
from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated



bot = Bot(token=TOKEN)
import logic.keyboards as kb

url = "https://hgt-backend.io"
headers = {
    "accept-encoding": "gzip",
    "accept-language": "uz",
    "app-version": "2.0.9",
    "authorization": f"Bearer {authToken}",
    "Content-Type": "application/json",
    "device-id": "08af41804260b4ef",
    "device-name": "vivo V2266A",
    "device-type": "ANDROID",
    "host": "hgt-backend.io",
    "User-Agent": "V2266A"
}


# API Endpoints
urlElectrocity = "/api/v1/electricity/AccountRefresh"
urlWater = "/api/v1/cold_water/AccountRefresh"
urlProfile = "/api/v1/accounts/Profile"
urlHomeList = "/api/v1/home/HomeList"
newURL = url+"/api/v1/regions"


class AdvMsg(StatesGroup):
    img = State()
    audio = State()
    txt = State()
    inline_link_name = State()
    inline_link_link = State()
    

class Ids(StatesGroup):
    homeName = State()
    electricity_id = State()



class GroupMsg(StatesGroup):
    img = State()
    audio = State()
    txt = State()
    inline_link_name = State()
    inline_link_link = State()
    

class Gen(StatesGroup):
    wait = State()
    
async def get_homes_content(tgId):
    home_names = await rq.get_all_home_names()
    reply_markup = kb.create_home_markup_kb(home_names, tgId)
    return reply_markup, home_names


router = Router()

@router.channel_post()
async def forward_channel_post(message: Message):
    """Forwards messages from the channel to a all users in bot, the channel you created to accept the requests 
    will be the target channel(posts from this channel will be listened and forwarded to all users)."""
    for user in await rq.get_all_user_ids():
        try:
            await bot.forward_message(from_chat_id=CHANNEL_ID,chat_id=user, message_id=message.message_id)
        except Exception as e:
            await message.answer(f"Unexpected error: {e}")
        

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await rq.set_user(tg_id=user_id)
    await state.set_state(Ids.homeName)
    await message.answer("Uyni nomini kiriting (Masalan: Uy1, Asaka kvartira va hokazo)")

@router.message(Ids.homeName)
async def get_home_name(message: Message, state: FSMContext):
    await state.update_data(homeName=message.text)
    await rq.set_home_name(tg_id=message.from_user.id, home_name=message.text)
    await state.set_state(Ids.electricity_id)
    await message.answer("Elektr energiya hisoblagich ID sini kiriting")




@router.message(Ids.electricity_id)
async def get_electricity_id(message: Message, state: FSMContext):
    await state.update_data(electricity_id=message.text)
    data = await state.get_data()
    await rq.set_electricity_id(home_name=data['homeName'],electricity_id=message.text)
    await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz!")
    await message.answer(f"Sizning uyingiz nomi: {data['homeName']}\nSizning elektr energiya hisoblagich ID si: {data['electricity_id']}")
    await state.clear()

@router.message(Command("profile"))
async def profile(message: Message):
    home_name = await rq.get_home_name(tg_id=message.from_user.id)
    await message.answer(f"Sizning uyingiz nomi: {await rq.get_home_name(tg_id=message.from_user.id)}\nSizning elektr energiya hisoblagich ID si: {await rq.get_electricity_id(home_name=home_name)}")

@router.message(Command("homes"))
async def homes(message: Message):
    reply_markup, home_names = get_homes_content(message.from_user.id)
    await message.answer("Ro'yxatdagi barcha uylar nomlari:\n" + "\n".join(home_names), reply_markup=reply_markup)


@router.callback_query(F.data.startswith("home_"))
async def unique_home_handler(callback:CallbackQuery):
    await callback.answer()
    raw_data = callback.data
    parts = raw_data.split("_")
    user_electricity_id = await rq.get_electricity_id(parts[2])
    await callback.message.edit_text(f"Sizning {parts[2]} Electrick ID raqami: {user_electricity_id}",reply_markup=kb.create_back_button("homes"))

@router.callback_query(F.data.startswith("nav"))
async def user_navigation_query(callback: CallbackQuery):
    await callback.answer()


    raw_nav_data = callback.data
    parts_nav = raw_nav_data.split("_")


    match parts_nav[1]:
        case "homes":
                user_id = callback.from_user.id
                reply_markup, home_names = await get_homes_content(user_id)
                try:
                    await callback.message.edit_text(text=f"Sizning uylaringinz: {home_names}", reply_markup=reply_markup)
                except Exception:
                    # Ignore if content hasn't changed
                    pass


@router.message(Command("narrator")) #// /narrator 123456, all users will recieve 123456
async def narrator(message: Message, command: CommandObject):
    for user in await rq.get_all_user_ids():
        await bot.send_message(chat_id=user, text=command.args)

    
@router.message(Command("send_to_all_users"))
async def start_send_to_all(message: Message, state: FSMContext):
    await state.set_state(AdvMsg.img)
    await message.answer("send your img🖼️")


@router.message(AdvMsg.img)
async def ads_img(message: Message, state: FSMContext):
    photo_data = { "photo": message.photo }  # Ensure it's in dictionary format
    await state.update_data(img=message.photo[-1].file_id)
    await state.set_state(AdvMsg.txt)
    await message.answer("send your text🗄️")

@router.message(AdvMsg.txt)
async def ads_txt(message: Message, state: FSMContext):
    await state.update_data(txt=message.text)
    await state.set_state(AdvMsg.inline_link_name)
    await message.answer("send your inline_link name📛")

@router.message(AdvMsg.inline_link_name)
async def ads_lk_name(message: Message, state: FSMContext):
    await state.update_data(inline_link_name=message.text)
    await state.set_state(AdvMsg.inline_link_link)
    await message.answer("send your inline_link LINK🔗")

@router.message(AdvMsg.inline_link_link)
async def ads_final(message: Message, state: FSMContext):
    await state.update_data(inline_link_link=message.text)
    data = await state.get_data()
    new_inline_kb = kb.create_markap_kb(name=data['inline_link_name'], url=data['inline_link_link'])
    if new_inline_kb == None:
        for user in await rq.get_all_user_ids():
            if data['img']:
                await bot.send_photo(chat_id=user, photo=data['img'],caption=data['txt'])
            elif data['audio']:
                await bot.send_voice(chat_id=user, voice=data['audio'], caption=data["txt"])

    else:
        for user in await rq.get_all_user_ids():
            if data['img']:
                await bot.send_photo(chat_id=user, photo=data['img'],caption=data['txt'], reply_markup=new_inline_kb)
            elif data['audio']:
                await bot.send_voice(chat_id=user, voice=data['audio'], caption=data["txt"], reply_markup=new_inline_kb)


    await state.clear()



@router.message(Command("send_to_all_groups"))
async def start_send_to_all_GroupMsg(message: Message, state: FSMContext):
    await state.set_state(GroupMsg.img)
    await message.answer("send your img🖼️")


@router.message(GroupMsg.img)
async def ads_img_GroupMsg(message: Message, state: FSMContext):
    photo_data = { "photo": message.photo }  # Ensure it's in dictionary format
    await state.update_data(img=message.photo[-1].file_id)
    await state.set_state(GroupMsg.txt)
    await message.answer("send your text🗄️")

@router.message(GroupMsg.txt)
async def ads_txtGroupMsg(message: Message, state: FSMContext):
    await state.update_data(txt=message.text)
    await state.set_state(GroupMsg.inline_link_name)
    await message.answer("send your inline_link name📛")

@router.message(GroupMsg.inline_link_name)
async def ads_lk_nameGroupMsg(message: Message, state: FSMContext):
    await state.update_data(inline_link_name=message.text)
    await state.set_state(GroupMsg.inline_link_link)
    await message.answer("send your inline_link LINK🔗")

@router.message(GroupMsg.inline_link_link)
async def ads_finalGroupMsg(message: Message, state: FSMContext):
    await state.update_data(inline_link_link=message.text)
    data = await state.get_data()
    new_inline_kb = kb.create_markap_kb(name=data['inline_link_name'], url=data['inline_link_link'])
    if new_inline_kb == None:
        for user in await rq.get_all_groups_ids():
            if data['img']:
                await bot.send_photo(chat_id=user, photo=data['img'],caption=data['txt'])
            elif data['audio']:
                await bot.send_voice(chat_id=user, voice=data['audio'], caption=data["txt"])

    else:
        for user in await rq.get_all_groups_ids():
            if data['img']:
                await bot.send_photo(chat_id=user, photo=data['img'],caption=data['txt'], reply_markup=new_inline_kb)
            elif data['audio']:
                await bot.send_voice(chat_id=user, voice=data['audio'], caption=data["txt"], reply_markup=new_inline_kb)


    await state.clear()


@router.message(Gen.wait)
async def stop_flood(message: Message):
    await message.answer("Wait one requests at a time \nПодождите ваш запрос генерируется.")
