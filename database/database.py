import pymongo, os
from config import DB_URI, DB_NAME


dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]


user_data = database['users']
join_request = database['join_requests']
channels_collection = database['channels']  # Collection for storing channel IDs

# Channel-related functions
def add_channels(channel_ids):
    """Overwrite all channel IDs in the database."""
    channels_collection.update_one(
        {"type": "channels_list"},  # Ensure all IDs are stored under one document
        {"$set": {"channels": channel_ids}},  # Replace the list with new IDs
        upsert=True
    )

def delete_all_channels():
    """Delete all channel IDs from the database."""
    channels_collection.delete_one({"type": "channels_list"})

def get_channels():
    """Retrieve the channel IDs list."""
    data = channels_collection.find_one({"type": "channels_list"})
    return data.get("channels", []) if data else []

# Join request-related functions
def add_join_request(user_id, chat_id):
    """Add a join request to the database."""
    join_request_data = {
        "user_id": user_id,
        "chat_id": chat_id
    }
    join_request.insert_one(join_request_data)

def check_join_request(user_id, chat_id):
    """Check if the user has a join request in the database."""
    result = join_request.find_one({"user_id": user_id, "chat_id": chat_id})
    return True if result else False

def delete_all_join_requests():
    """Delete all join requests from the database."""
    join_request.delete_many({})


async def present_user(user_id : int):
    found = user_data.find_one({'_id': user_id})
    if found:
        return True
    else:
        return False

async def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})
    return

async def full_userbase():
    user_docs = user_data.find()
    user_ids = []
    for doc in user_docs:
        user_ids.append(doc['_id'])
        
    return user_ids

async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
    return

async def get_all_users():
    user_docs = user_data.find()
    users = []
    async for doc in user_docs:
        users.append({
            'id': doc['_id'],
            'name': doc.get('name', 'Unknown'),  # Get user's name or 'Unknown'
            'ban_status': {
                'is_banned': doc.get('is_banned', False),
                'ban_reason': doc.get('ban_reason', None)
            }
        })
    return users
async def get_ban_status(user_id: int):
    user = user_data.find_one({'_id': user_id})
    if user and user.get('is_banned'):
        return {'is_banned': True, 'ban_reason': user.get('ban_reason')}
    return {'is_banned': False, 'ban_reason': None}
async def ban_user(user_id: int, name: str, reason: str):
    user_data.update_one(
        {'_id': user_id},
        {
            '$set': {
                'is_banned': True,
                'ban_reason': reason,
                'name': name  # Store the user's name when banning
            }
        },
        upsert=True
    )
async def remove_ban(user_id: int):
    user_data.update_one(
        {'_id': user_id},
        {
            '$set': {
                'is_banned': False,
                'ban_reason': None
            }
        }
    )
async def get_banned_users():
    banned_users_cursor = user_data.find({"is_banned": True})
    
    banned_users = []
    async for user in banned_users_cursor:
        banned_users.append(user)

    return banned_users
