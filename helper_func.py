import base64
import re
import logging
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, ChatAdminRequired
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database.database import get_channels, check_join_request, add_join_request, delete_all_join_requests
from config import FORCE_SUB_CHANNEL, ADMINS

DEL_MSG = {}
URL = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def handle_force_sub(client, message):
    # Developer plz don't remove credit @sahid_malik
    unjoined_channels = []  
    invite_links = []

    channels = get_channels()
    if not channels:
        channels = FORCE_SUB_CHANNEL

    for channel_id in channels:
        if not await is_subscribed(client, message, [channel_id]):
            try:
                invite_link = await client.create_chat_invite_link(
                    channel_id, creates_join_request=True
                )
                invite_links.append(invite_link.invite_link)
                unjoined_channels.append(channel_id)
            except ChatAdminRequired:
                logger.error(f"Make sure Bot is admin in channel: {channel_id}")
                return False

    if not unjoined_channels:
        return True

    btn = []
    for idx, invite_link in enumerate(invite_links):
        btn.append([InlineKeyboardButton(f"ಈ ಚಾನೆಲ್ ಜಾಯಿನ್ ಆಗಿ {idx + 1} ♂️", url=invite_link)])

    try:
        link = f"https://t.me/{client.username}?start={message.command[1]}"
    except Exception as e:
        link = f"https://t.me/{client.username}?start=subscribe"

    btn.append([InlineKeyboardButton("ಮುಂದುವರಿಯಲು ಕ್ಲಿಕ್ ಮಾಡಿ ♂️", url=link)])

    # Define your message text
    message_text = "📢 ಹೊಸ ಅಪ್‌ಡೇಟ್!\n\n" \
                   "👉 ಮೊದಲು ಕೆಳಗೆ ಕೊಟ್ಟಿರುವ ಮೊದಲನೇ ಬಟನ್ ಅನ್ನು ಒತ್ತಿ ಚಾನೆಲ್ ಜಾಯಿನ್ ಆಗಿ.\n\n" \
                   "ರಿಕ್ವೈಸ್ಟ್ ಕಲಿಸಿದ ನಂತರ ಅದರ ಕೆಳಗೆ ಕೊಟ್ಟಿರುವ ಬಟನ್ ಒತ್ತಿ\n\n\n" \
                   "ನೀವು ಚಾನೆಲ್ ಜಾಯಿನ್ ಆಗದೆ ಇದ್ದಲ್ಲಿ ನಿಮಗೆ ವಿಡಿಯೋ ಸಿಗುವುದಿಲ್ಲ."

    # Send message with buttons
    await message.reply_text(
        text=message_text,
        reply_markup=InlineKeyboardMarkup(btn),
        disable_web_page_preview=True
    )
    URL[message.from_user.id] = link
    m = await client.send_message(
        chat_id=message.from_user.id,
        #text="Join update channel",
        #reply_markup=InlineKeyboardMarkup(btn),
        #parse_mode=ParseMode.HTML
    )

    DEL_MSG[message.from_user.id] = m
    return False

async def is_subscribed(bot, query, FSUB_CHANNELS): 
    # Developer plz don't remove credit @sahid_malik
    try:
        for channel in FSUB_CHANNELS:  # Iterate over each channel
            # Check if there is a join request in the current channel
            join_request_exists = check_join_request(user_id=query.from_user.id, chat_id=int(channel))

            if join_request_exists:
                continue  # If join request exists, move to the next channel

            try:
                # Check if the user is a member of the current channel
                user = await bot.get_chat_member(int(channel), query.from_user.id)
            except UserNotParticipant:
                return False  # If the user is not a participant in any one channel, return False
            except Exception as e:
                logger.exception(e)
                return False  # Return False if any other error occurs

            # If the user is banned ('kicked'), return False
            if user.status == 'kicked':
                return False

    except Exception as e:
        logger.exception(e)
        return False  # In case of any other error, return False

    return True  # If the user is subscribed to all channels, return True

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.strip("=") # links generated before this commit will be having = sign, hence striping them to handle padding errors.
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern,message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    else:
        return 0

def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time
