from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import logging
from backend.config.settings import settings
from backend.bot.handlers import router

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Bot and Dispatcher
    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
    )
    dp = Dispatcher()
    
    # Include routers
    dp.include_router(router)
    
    # Start polling
    logging.info("Starting OpenIntel Telegram Bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
