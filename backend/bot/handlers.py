from aiogram import Router, types, F
from aiogram.filters import Command
from backend.bot.api_client import OpenIntelClient
from backend.config.settings import settings
from backend.database.session import async_session_maker
from backend.database.models import User
from sqlalchemy import select
import re

router = Router()
api_client = OpenIntelClient()

async def get_or_create_user(telegram_id: int) -> User:
    async with async_session_maker() as session:
        result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user with default 3 credits, or infinite if admin
            is_admin = telegram_id == settings.TELEGRAM_ADMIN_ID
            credits = 999999 if is_admin else 3
            user = User(
                telegram_id=telegram_id,
                credits=credits,
                is_superuser=is_admin
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
        return user

async def consume_credit(telegram_id: int) -> bool:
    async with async_session_maker() as session:
        result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
        user = result.scalar_one_or_none()
        
        if not user or user.credits <= 0:
            return False
            
        if not user.is_superuser:
            user.credits -= 1
            await session.commit()
            
        return True

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user = await get_or_create_user(message.from_user.id)
    
    welcome_text = (
        "🦅 *Welcome to OpenIntel OSINT Engine*\n\n"
        "Send me any target identifier to initiate a deep scan across global intelligence networks\.\n\n"
        "Supported formats:\n"
        "📧 Email\n"
        "📱 Phone Number\n"
        "🌐 IPv4 Address\n"
        "👤 Username\n\n"
        f"💳 *Your Credits:* {user.credits}"
    )
    await message.answer(welcome_text)

def detect_query_type(query: str) -> str:
    if "@" in query and "." in query:
        return "EMAIL"
    if re.match(r'^\+?[1-9]\d{1,14}$', query.replace(' ', '').replace('-', '')):
        return "PHONE"
    if re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', query):
        return "IP"
    return "USERNAME"

@router.message(F.text)
async def handle_search(message: types.Message):
    user = await get_or_create_user(message.from_user.id)
    
    if user.credits <= 0:
        await message.answer("❌ *Out of credits!*\n_Please contact support to top up your balance\._")
        return
        
    query = message.text.strip()
    query_type = detect_query_type(query)
    
    # 1. Send initial pending message
    wait_msg = await message.answer(f"⏳ *Initiating scan for {query_type}:* `{query}`\.\.\.\n_This may take a few moments\._")
    
    # Consume credit before running
    await consume_credit(message.from_user.id)
    
    try:
        # 2. Call backend API
        result = await api_client.execute_scan(query, query_type)
        
        # 3. Format and send result
        formatted_result = format_report(result, query)
        await wait_msg.edit_text(formatted_result, disable_web_page_preview=True)
        
    except Exception as e:
        await wait_msg.edit_text(f"❌ *Scan Failed*\n`{escape_md(str(e))}`")

def escape_md(text: str) -> str:
    """Escapes special characters for Telegram MarkdownV2"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def format_report(data: dict, target: str) -> str:
    """Formats the JSON result into a clean Telegram MarkdownV2 message"""
    status = data.get('status', 'COMPLETED')
    modules_run = data.get('modules_run', 0)
    
    report = f"🎯 *Target Report:* `{escape_md(target)}`\n"
    report += f"✅ *Status:* {escape_md(status)}\n"
    report += f"🔌 *Modules Queried:* {modules_run}\n\n"
    
    results = data.get('results', {})
    if not results:
        report += "🔍 _No intelligence found for this target\._"
        return report
        
    report += "🔎 *Intelligence Data:*\n"
    for module_name, module_data in results.items():
        clean_name = module_name.replace('_', ' ').title()
        report += f"\n*\[{escape_md(clean_name)}\]*\n"
        
        if isinstance(module_data, dict):
            for k, v in module_data.items():
                if v: 
                    report += f"• *{escape_md(k.title())}:* `{escape_md(str(v))}`\n"
        elif isinstance(module_data, list):
            for item in module_data:
                report += f"• `{escape_md(str(item))}`\n"
        else:
            report += f"• `{escape_md(str(module_data))}`\n"
            
    return report
