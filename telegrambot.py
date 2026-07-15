import asyncio
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.network.connection import ConnectionTcpMTProxyAbridged
import json
import os
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

API_ID = 
API_HASH = ''
BOT_TOKEN = ''

PROXY = ('127.0.0.1', 1080, '19d86b347a0d530861475ee6568fba83')
CURRENT_STATUS_FILE = "current_status.json"

client = TelegramClient(
    'bot_session',
    API_ID,
    API_HASH,
    connection=ConnectionTcpMTProxyAbridged,
    proxy=PROXY
)

def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def get_time_remaining(end_time):
    now = datetime.now().timestamp()
    remaining = end_time - now
    
    if remaining <= 0:
        return "Finished", 0
    elif remaining < 60:
        return f"{int(remaining)}s", int(remaining)
    elif remaining < 3600:
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        return f"{minutes}m {seconds}s", int(remaining)
    else:
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        return f"{hours}h {minutes}m", int(remaining)

def get_current_broadcast():
    if not os.path.exists(CURRENT_STATUS_FILE):
        return None
    
    try:
        with open(CURRENT_STATUS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data.get('is_playing', False):
            return None
        
        return data
    except Exception as e:
        logger.error(f"Error reading status: {e}")
        return None

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond(
        "This is an information Telegram bot for the 'shpaklevka tv' channel.\n"
        "If this bot is working, the channel is running!\n\n"
        "Available commands:\n"
        "/start - Show this message\n"
        "/now - What's currently on air\n"
        "/req - Suggest a program"
    )
    logger.info(f"User {event.sender_id} started the bot")

@client.on(events.NewMessage(pattern='/now'))
async def now_handler(event):
    data = get_current_broadcast()
    
    if not data:
        await event.respond(
            "Channel is not on air or information is unavailable.\n"
            "Try again later."
        )
        return
    
    display_name = data.get('display_name', 'Unknown')
    description = data.get('description', '')
    category = data.get('category', 'Uncategorized')
    age_rating = data.get('age_rating', 0)
    duration = data.get('duration', 0)
    start_time = data.get('start_time', 0)
    end_time = data.get('end_time', 0)
    
    time_left_str, remaining_seconds = get_time_remaining(end_time) if end_time > 0 else ("-", 0)
    
    if start_time > 0:
        start_dt = datetime.fromtimestamp(start_time)
        start_str = start_dt.strftime("%H:%M:%S")
        end_dt = datetime.fromtimestamp(start_time + duration)
        end_str = end_dt.strftime("%H:%M:%S")
    else:
        start_str = "-"
        end_str = "-"
    
    age_label = f"{age_rating}+" if age_rating > 0 else "0+"
    
    message = (
        f"Currently on air\n"
        f"{'=' * 30}\n\n"
        f"{display_name}\n"
        f"{description}\n\n"
        f"Age rating: {age_label}\n"
        f"Duration: {format_duration(duration)}\n"
        f"Remaining: {time_left_str}\n"
        f"Start: {start_str}\n"
        f"End: {end_str}\n\n"
        f"{'=' * 30}\n"
    )
    
    cover_path = data.get('cover', '')
    full_cover_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), cover_path) if cover_path else None
    
    if cover_path and os.path.exists(full_cover_path):
        try:
            await event.respond(file=full_cover_path)
            await event.respond(message)
            logger.info(f"Sent photo and text for {display_name}")
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            await event.respond(message)
    else:
        await event.respond(message)
        logger.info(f"Sent text for {display_name}")

@client.on(events.NewMessage(pattern='/req'))
async def req_handler(event):
    await event.respond(
        "Suggest a program\n\n"
        "Want to suggest your program for broadcast?\n"
        "Write here: @stepaandgddev"
    )
    logger.info(f"User {event.sender_id} requested program proposal")

@client.on(events.NewMessage(pattern=r'^/'))
async def unknown_command_handler(event):
    known_commands = ['/start', '/now', '/req', '/help']
    if event.text.split()[0] not in known_commands:
        await event.respond(
            "Unknown command.\n\n"
            "Available commands:\n"
            "/start - Start\n"
            "/now - What's currently on air\n"
            "/req - Suggest a program"
        )

async def main():
    logger.info("Starting bot with MTPROTO proxy...")
    logger.info(f"Proxy: {PROXY[0]}:{PROXY[1]}")
    logger.info(f"Secret: {PROXY[2][:8]}...")
    try:
        await client.start(bot_token=BOT_TOKEN)
        logger.info("Bot successfully started!")

        me = await client.get_me()
        logger.info(f"Bot ready! @{me.username}")
        logger.info("Press Ctrl+C to stop.")

        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")