from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import get_all_users, ban_user, remove_ban, get_ban_status, get_banned_users
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, MessageTooLong
from config import ADMINS

async def banned_users(_, __, message: Message):
    ban = await get_ban_status(message.from_user.id)
    
    return ban['is_banned'] if ban else False

banned_user = filters.create(banned_users)


@Client.on_message(filters.private & banned_user & filters.incoming)
async def ban_reply(bot, message):
    ban = await get_ban_status(message.from_user.id)
    
    if ban['is_banned']:
        await message.reply(f'Sorry Dude, You are Banned from using Me. \nBan Reason: {ban["ban_reason"]}')
        
@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_banned_users(bot, message):
    sts = await message.reply('Getting List Of Banned Users...')
    
    users = await get_banned_users()
    
    if not users:
        return await raju.edit_text("No users are currently banned.")

    out = "Banned Users Saved In DB Are:\n\n"
    for user in users:
        out += f"<a href='tg://user?id={user['_id']}'>{user['name']}</a> (Banned User)\n"
    
    try:
        await sts.edit_text(out)
    except MessageTooLong:
        with open('banned_users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('banned_users.txt', caption="List Of Banned Users")
        

@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Provide a user id / username')
    
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    
    try:
        chat = int(chat)
    except:
        pass
    
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("Invalid user, make sure I have met them before.")
    
    user = await get_ban_status(k.id)
    if user['is_banned']:
        return await message.reply(f"{k.mention} is already banned\nReason: {user['ban_reason']}")
    
    await ban_user(k.id, k.first_name, reason)
    await message.reply(f"Successfully banned {k.mention}")


@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Provide a user id / username')
    
    r = message.text.split(None)
    chat = message.command[1]
    
    try:
        chat = int(chat)
    except:
        pass
    
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("Invalid user, make sure I have met them before.")
    
    user = await get_ban_status(k.id)
    if not user['is_banned']:
        return await message.reply(f"{k.mention} is not banned.")
    

    await remove_ban(k.id)
    await message.reply(f"Successfully unbanned {k.mention}")
    
