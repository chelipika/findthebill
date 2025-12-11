

from config import TOKEN, CHANNEL_ID
import database.requests as rq


import requests
import json
from datetime import datetime


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

async def create_header(authToken):
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
    "User-Agent": "V2266A"}
    return headers

# API Endpoints
urlElectrocity = "/api/v1/electricity/AccountRefresh"
urlWater = "/api/v1/cold_water/AccountRefresh"
urlProfile = "/api/v1/accounts/Profile"
urlHomeList = "/api/v1/home/HomeList"
urlRegion = "/api/v1/common/DistrictList?region="
urlCountry = "/api/v1/common/RegionList?uz"
urlElectrocityAccountSearch = "/api/v1/electricity/AccountSearch"
urlSendSMSLoginIn = "/api/v1/verification/RequestOTP"
urlSendCodeSMS = "/api/v1/verification/SubmitOTP"
urLGetAuthToken = "/api/v1/accounts/Login"
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
    phone_number = State()
    sms_code = State()



class GroupMsg(StatesGroup):
    img = State()
    audio = State()
    txt = State()
    inline_link_name = State()
    inline_link_link = State()
    

class Gen(StatesGroup):
    wait = State()
async def format_utility_info(data: dict) -> str:
    """
    Takes a JSON dictionary of utility data and returns a formatted string.
    """
    
    # 1. Helper function to format money (e.g., 172749.63 -> 172 749.63)
    def money_fmt(value):
        try:
            val = float(value)
            return f"{val:,.2f}".replace(",", " ")
        except (ValueError, TypeError):
            return value

    # 2. Parse and format dates
    try:
        # Parse '2025-12-06T00:00:00' -> '06.12.2025'
        read_date = datetime.fromisoformat(data.get('last_readings_date', '')).strftime('%d.%m.%Y')
    except ValueError:
        read_date = data.get('last_readings_date', '')

    try:
        # Parse updated_at (handling the 'Z' if present)
        updated_raw = data.get('updated_at', '').replace('Z', '+00:00')
        updated_time = datetime.fromisoformat(updated_raw).strftime('%d.%m.%Y %H:%M')
    except ValueError:
        updated_time = data.get('updated_at', '')

    # 3. Get Analytics data safely
    analytics = data.get('analytics', {})

    # 4. Build the text message
    text = (
        f"<b>🧾 Hisob raqam ma'lumotlari:</b>\n"
        f"🆔 <b>Hisob raqam:</b> <code>{data.get('account_number')}</code>\n\n"
        
        f"💰 <b>Joriy Balans:</b> {money_fmt(data.get('balance', 0))} so'm\n"
        f"⚡️ <b>Bu oydagi iste'mol:</b> {data.get('usage_this_month')} birlik\n\n"
        
        f"📊 <b>Ko'rsatkichlar:</b>\n"
        f"• Oxirgi ko'rsatkich: {money_fmt(data.get('last_readings_value', 0))}\n"
        f"• Olingan sana: {read_date}\n\n"
        
        f"💵 <b>Hisob-kitob (Analitika):</b>\n"
        f"• Bu oy uchun: {money_fmt(analytics.get('this_month', 0))} so'm\n"
        f"• O'tgan oy uchun: {money_fmt(analytics.get('previous_month', 0))} so'm\n\n"
        
        f"🔄 <i>Ma'lumot yangilangan vaqt: {updated_time}</i>"
    )

    return text
def save_json_test(json_file):
    with open("test.json", "w", encoding="utf=8") as file:
        json.dump(json_file, file,indent=4)
async def get_existing_account_info(auth_token, tg_id):
    headers = await create_header(auth_token)
    response = requests.get(url=f"{url}{urlHomeList}", headers=headers)
    data = response.json()
    home_name = data[0]['address']
    elec_id = data[0]['electricity']['account']['id']
    natural_gas_id = data[0]['natural_gas']['account']['id']
    cold_water_id = data[0]['cold_water']['account']['id']
    garbage_id = data[0]['garbage']['account']['id']
    await rq.set_homeList(tgId=tg_id, homeName=home_name, elec_id=elec_id, natural_gas_id=natural_gas_id, cold_water_id=cold_water_id, garbage_id=garbage_id)
    text = f'''
    💻I.F.O: {data[0]['owner_full_name']}
    🏡Manzil: {data[0]['address']}
    🔥Tabiy gaz: {data[0]['natural_gas']['account']['balance']}
    ⚡Electro energiya: {data[0]['electricity']['account']['balance']}
    🚰Sovuq suv: {data[0]['cold_water']['account']['balance']}
    🚮Chiqqindi: {data[0]['garbage']['account']['balance']}
'''
    return text
async def get_SMS_phone(phone_number):
    data = {
    "purpose": "login",
    "address": phone_number,
    "client_secret": "Gy3LsrqYGQbXpklBsGKJQdv1xPJJbrIv"
    }
    response = requests.post(url=f"{url}{urlSendSMSLoginIn}",json=data)
    return response.json()

async def login_by_SMS(sussion, code):
    data = sussion
    payload = {
    "session": data,
    "otp": code,
    "client_secret": "Gy3LsrqYGQbXpklBsGKJQdv1xPJJbrIv"
    }
    response = requests.post(url=f"{url}{urlSendCodeSMS}",json=payload)
    return response.json()
async def get_auth_TOKEN(session):
    data = {
    "session_data": {
        "device_id": "db60f8ab597f89d1",
        "platform": "ANDROID",
        "device_os": "ANDROID",
        "device_model": "Samsung SM-A536E",
        "lang": "uz",
        "app_version": "2.0.9"
    },
    "verification_data": {
        "session": session,
        "client_secret": "Gy3LsrqYGQbXpklBsGKJQdv1xPJJbrIv"
    }
    }
    response = requests.post(url=f"{url}{urLGetAuthToken}", json=data)
    jsonData = response.json()
    authToken = jsonData['access']
    return authToken 
async def electricity_user_account_refresh(userElecInId):
    data = {
    "id": f"{userElecInId}" # id of water account
    }
    response = requests.post(url=f"{url}{urlElectrocity}", headers=headers, json=data)
    with open("test.json", "w") as file:
        json.dump(response.json(), file, indent=4)
    return response.json()
async def user_get_electricity_id(electricityGovId, districtId):
    data = {
    "search_by": "ACCOUNT_NUMBER",
    "search_value": f"{electricityGovId}",
    "district": f"{districtId}"
    }
    response = requests.post(url=f"{url}{urlElectrocityAccountSearch}", headers=headers, json=data)
    return response.json()

async def parse_user_bill_id(data):
    return data[0]["id"]

async def get_state_info(data: list):
    return data["id"], data["name"], data["natural_gas_id"], data["electricity_id"]


async def get_bill_electrocity(electroId):
    response = requests.get(url=f"{url}{urlHomeList}", headers=headers)
    return str(response.text)



async def get_country_regions():
    response = requests.get(url=f"{url}{urlCountry}",headers=headers)
    data = response.json()

    #DEBUGING AND TESTING
    # with open("test.json", "w") as file:
    #     json.dump(data, file, indent=4)
    # for region in data:
    #     print(region["name"])

    return data

async def get_state_regions(state_id):
    response = requests.get(url=f"{url}{urlRegion}{state_id}&uz", headers=headers)
    data = response.json()

    # DEBUGING AND TESTING
    # with open("test.json", "w") as file:
    #     json.dump(data, file, indent=4)
    # for region in data:
    #     print(region["name"])

    return data



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
    user_token = await rq.get_user_auth_token(user_id)
    if user_token != None:
        user_token = str(user_token)
        home_names_of_user = await rq.get_user_homes(user_id)
        home_names_of_user = list(home_names_of_user)
        if home_names_of_user != []:
            reply_markup = kb.create_home_markup_kb(home_names_of_user)
        else:
            reply_markup = kb.home_page
        await message.answer("Salom, bu bot bilan kop narsa qilsangiz boladi", reply_markup=reply_markup)
    else:
        await state.set_state(Ids.phone_number)
        await message.answer("Accountga kirish uchun,Telefon nomerizni kiritng:\nMasalan:+998991234567")



@router.message(Ids.phone_number)
async def handle_user_phoneNumber(message: Message, state: FSMContext):
    sms_send = await get_SMS_phone(message.text)
    await state.update_data(session = sms_send['session'])
    await state.set_state(Ids.sms_code)
    await message.answer("Sizning telefon nomerizga SMS kod uborildi, uni kiriting:")


@router.message(Ids.sms_code)
async def handle_sms_code(message: Message, state: FSMContext):
    sms_code = message.text
    session = await state.get_data()
    session = session.get("session")
    response_json = await login_by_SMS(sussion=session, code=sms_code)
    login_message = await message.answer("LOGIN QILINDI🎆")
    authToken_from_request = await get_auth_TOKEN(session=session)
    await rq.set_user_auth_token(authToken_from_request, message.from_user.id)
    print("TOKEN DBga Kiritldi")
    inform_message = await login_message.edit_text("Saqlangan uyniy teleon nomeriz bilan kidirilmoqta.🔎")
    text = await get_existing_account_info(auth_token=authToken_from_request, tg_id=message.from_user.id)
    await inform_message.edit_text(text)


@router.callback_query(F.data == "create_home")
async def create_home(callback: CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.set_state(Ids.homeName)
    await callback.message.answer("Uyni nomini kiriting (Masalan: Uy1, Asaka kvartira va hokazo)")

@router.message(Ids.homeName)
async def get_home_name(message: Message, state: FSMContext):
    await state.update_data(homeName=message.text)
    await rq.set_home_name(tg_id=message.from_user.id, home_name=message.text)
    await state.clear()
    await rq.set_home_name(message.from_user.id, message.text)

    await message.answer(f"Uyingiz {message.text} sahlandi,Nima qilmoqchisiz?:")




@router.message(Ids.electricity_id)
async def get_electricity_id(message: Message, state: FSMContext):
    context_data = await state.get_data()
    
    
    user_input = message.text
    saved_district_id = context_data.get("district_id")
    saved_target_home_id = context_data.get("target_home_id")
    add_elec_to_db = await rq.set_electricity_id(saved_target_home_id,electricity_id=user_input)
    if add_elec_to_db:
        pass
    else:
        print("ERROR ELEC ID IS NOT SAVED")
    user_info_backend = await user_get_electricity_id(user_input, saved_district_id) 
    print(user_info_backend) # 
    tmp_message = await message.answer("Ma'lumotlar qabul qilindi.")
    user_bill_data_backend = await electricity_user_account_refresh(user_info_backend[0]["id"])
    # print(user_bill_data_backend)
    await tmp_message.edit_text("Ma'lumotlarni jonatilyabti.")
    readable_text = await format_utility_info(user_bill_data_backend)
    await tmp_message.edit_text(readable_text, parse_mode="HTML")
    await state.clear()

@router.message(Command("profile"))
async def profile(message: Message):
    home_name = await rq.get_home_name(tg_id=message.from_user.id)
    await message.answer(f"Sizning uyingiz nomi: {await rq.get_home_name(tg_id=message.from_user.id)}\nSizning elektr energiya hisoblagich ID si: {await rq.get_electricity_id(home_name=home_name)}")

@router.message(Command("region"))
async def regions_test(message: Message):
    data = await get_country_regions()
    reply_markup = kb.create_regions_markup_kb(data,"main")
    await message.answer("Chose your region",reply_markup=reply_markup)



@router.message(Command("homes"))
async def homes(message: Message):
    user_id = message.from_user.id
    home_names_of_user = await rq.get_home_name(user_id)
    reply_markup = kb.create_home_markup_kb(home_names_of_user, user_id)
    await message.answer("Salom, bu bot bilan kop narsa qilsangiz boladi", reply_markup=reply_markup)




@router.callback_query(F.data.startswith("state_"))
async def get_state_regions_query(callback :CallbackQuery):
    parts = callback.data.split("_")
    await callback.answer(parts[1])
    data = await get_country_regions()
    for state in data:
        if parts[1] == state["name"]:
            id, name, elecId, gasId = await get_state_info(state)
            data = await get_state_regions(id)
            reply_markup = kb.create_state_regions_markup_kb(data,"countryRegions", name)
            await callback.message.edit_text("Viloyatingizni tanglang",reply_markup=reply_markup)

@router.callback_query(F.data.startswith("region_"))
async def fill_regions_elecId_query(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    await callback.answer(parts[1])
    country_states = await get_country_regions()
    for state_item in country_states:
        if parts[2] == state_item["name"]:
            id, name, gasId, elecId = await get_state_info(state_item)
            break
    data = await get_state_regions(id)
    
    for region_item in data:
        if parts[1] == region_item["name"]:
            
            if region_item['electricity_id'] == None:
                elec_prefix = elecId
            else:
                elec_prefix = f"{elecId}{region_item['electricity_id']}"

            if region_item['natural_gas_id'] == None:
                gas_prefix = gasId
            else:
                gas_prefix = f"{gasId}{region_item['natural_gas_id']}"
            
            await callback.message.edit_text(
                f"Sizning Electrik regioningiz: {region_item['name']}\n\n"
                f"Bu regioni Electrik tarmoq boshlanish IDsi: {elec_prefix}\n\n"
                f"Bu regioni Gaz tarmoq boshlanish IDsi: {gas_prefix}"
            )
            
            await state.update_data(
                district_id=region_item['id'], 
                region_elec_id=region_item['electricity_id'],
                region_gas_id=region_item['natural_gas_id']
            )
            
            await state.set_state(Ids.electricity_id)
            
            await callback.message.answer(
                f"Agarda siz Electrik ID ulamoqchi bolsez elec_ID kiriting...\n\n"
                f"Agarda siz Gaz ID ulamoqchi bolsez gas_ID kiriting..."
            )
            # Break the loop once found to prevent unnecessary iterations
            break





@router.callback_query(F.data=="add_elec_id_manually")
async def manual_add_elec_id(callback:CallbackQuery):
    data = await get_country_regions()
    reply_markup = kb.create_regions_markup_kb(data,"main")
    await callback.message.edit_text(f"Chose your region",reply_markup=reply_markup)

@router.callback_query(F.data.startswith("home_"))
async def unique_home_handler(callback:CallbackQuery, state: FSMContext):
    await callback.answer()
    home_id = callback.data.split("_")[1]
    await state.update_data(target_home_id=home_id)

    
@router.callback_query(F.data.startswith("nav"))
async def user_navigation_query(callback: CallbackQuery):
    await callback.answer()


    raw_nav_data = callback.data
    parts_nav = raw_nav_data.split("_")


    match parts_nav[1]:
        case "homes":
                user_id = callback.from_user.id
                home_names_of_user = await rq.get_home_name(user_id)
                reply_markup = kb.create_home_markup_kb(home_names_of_user, user_id)
                try:
                    await callback.message.edit_text(text=f"Salom, bu bot bilan kop narsa qilsangiz boladi", reply_markup=reply_markup)
                except Exception:
                    # Ignore if content hasn't changed
                    pass
        case "countryRegions":
            data = await get_country_regions()
            reply_markup = kb.create_regions_markup_kb(data,"main")
            await callback.message.edit_text("Viloyatingizni tanglang",reply_markup=reply_markup)
        case "main":
            await callback.message.edit_text("Salom")

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
