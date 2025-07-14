import os
import asyncio
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import ChatJoinRequest, Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FORCE_SUB_CHANNEL
from helper_func import is_subscribed, handle_force_sub, URL, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user, check_join_request, add_join_request, delete_all_join_requests, add_channels, get_channels, delete_all_channels

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass 
    check_user = await handle_force_sub(client, message)
    if not check_user: 
        return True 
    else:
        pass 
    text = message.text 
    if len(message.command) != 2:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Movies", url="https://t.me/Filmyfunda_movies"),
                    InlineKeyboardButton("TV shows", url="https://t.me/serials_funda"),
                    InlineKeyboardButton("🔒 Close", callback_data = "close")
                ]
            ]
        )
        await message.reply_photo(
            photo="https://ibb.co/h3crmyZ",
            caption = START_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else '@' + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id
    ),
    reply_markup=reply_markup,
    quote=True
)
        return
 
    else:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        for msg in messages:
            for msg in messages:
                if bool(CUSTOM_CAPTION) & bool(msg.document):
                    caption = CUSTOM_CAPTION.format(
                        previouscaption="" if not msg.caption else msg.caption.html,
                        filename=msg.document.file_name,
                        first_name=message.from_user.first_name
                    )
                else:
                    caption = "" if not msg.caption else msg.caption.html
                    
                    if DISABLE_CHANNEL_BUTTON:
                        reply_markup = msg.reply_markup
                    else:
                        from random import choice
                        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                        
                        channel_links = [
                            
                            ("colors kannada", "https://t.me/+J8vSpNYtE-k1Zjc1"),
                            ("zee kannada", "https://t.me/+ZVorkdJpLMk2NDU9"),
                            ("star suvarna", "https://t.me/+ksO3EEeMWRs3OWE9")
                        ]

    channel_name, channel_url = choice(channel_links)
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🔗 Join {channel_name}", url=channel_url)]
    ])


    try:
        await msg.copy(
            chat_id=message.from_user.id,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            protect_content=PROTECT_CONTENT
        )
        await asyncio.sleep(0.5)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await msg.copy(
            chat_id=message.from_user.id,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            protect_content=PROTECT_CONTENT
        )
    except Exception:
        pass
        return

#=====================================================================================##

WAIT_MSG = """"<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a replay to any telegram message with out any spaces.</code>"""

#=====================================================================================##

@Bot.on_message(filters.command("add_channel") & filters.user(ADMINS))
async def add_channels_handler(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: `/add_channel <channel_id1> <channel_id2> ...`")
        return

    # Parse channel IDs from the command
    channel_ids = message.command[1:]
    valid_ids = [channel_id.strip() for channel_id in channel_ids if channel_id.startswith("-100")]

    if not valid_ids:
        await message.reply("No valid Channel IDs found! Make sure they start with `-100`.")
        return

    try:
        # Overwrite existing IDs with the new ones
        add_channels(valid_ids)  # Synchronous function call
        await message.reply(f"Channel IDs `{', '.join(valid_ids)}` added successfully!")
    except Exception as e:
        await message.reply(f"Failed to add channels: {str(e)}")

@Bot.on_message(filters.command("get_channels") & filters.user(ADMINS))
async def get_channels_handler(client, message):
    try:
        channels = get_channels()  # Synchronous function call
        if not channels:
            await message.reply("No channels added yet.")
            return

        await message.reply(f"Channels: {', '.join(channels)}")
    except Exception as e:
        await message.reply(f"Failed to retrieve channels: {str(e)}")

@Bot.on_message(filters.command("delete_channels") & filters.user(ADMINS))
async def delete_channels_handler(client, message):
    try:
        # Remove all channels from the database
        delete_all_channels()  # Synchronous function call
        await message.reply("All channel IDs have been deleted!")
    except Exception as e:
        await message.reply(f"Failed to delete channels: {str(e)}")

@Bot.on_message(filters.command('delreq') & filters.private & filters.user(ADMINS))
async def del_req(client, message):
    delete_all_join_requests()    
    await message.reply("ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ")

# Define DEL_MSG and URL at the top of your script
DEL_MSG = {}
URL = {}

@Bot.on_chat_join_request(filters.group | filters.channel)
async def autoapprove(client: Client, message: ChatJoinRequest):
    user = message.from_user
    if not check_join_request(user.id, message.chat.id):
        add_join_request(user.id, message.chat.id)

    all_joined = True
    channels = get_channels()
    if not channels:
        channels = FORCE_SUB_CHANNEL
    for channel_id in channels:
        if not await is_subscribed(client, message, [channel_id]):
            all_joined = False
            break

    if all_joined:
        dl = DEL_MSG.get(user.id)
        if dl:
            await dl.delete()

        link = URL.get(user.id)
        if link:  # Ensure link is not None
            btn = [[InlineKeyboardButton("refresh", url=link)]]
            await client.send_message(
                chat_id=user.id,
                text="Click and continue your main process",
                reply_markup=InlineKeyboardMarkup(btn)
            )
        else:
            await client.send_message(
                chat_id=user.id,
                text="Click and continue your main process"
            )
@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(9)
        await msg.delete()
