import asyncio
from config import TOKEN
from aiogram import Bot, Dispatcher
from logic.handlers import router
from database.models import async_main

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    await async_main()
    print("Starting bot polling...")
    dp.include_router(router=router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")