#(©).CodeXBotz




import os
import logging
from logging.handlers import RotatingFileHandler



#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7843566779:AAEl-zXJWjOutYhvafCAA1gxkKJKEwnORhg")

#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "977080"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "0c20c4265501492a1513f91755acd42b")

#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002399526012"))

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "5898875558"))

#Database 
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://abcd:abcd@cluster0.aymuk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "filesharexbot")

#force sub channel id, if you want enable force sub
#FORCE_SUB_CHANNEL = int(os.environ.get("FORCE_SUB_CHANNEL", "-1001601560776"))

FORCE_SUB_CHANNEL = list(map(int, [id.strip() for id in os.environ.get("FORCE_SUB_CHANNEL", "-1002421873890").split(",")]))

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

#start message
START_MSG = os.environ.get("START_MESSAGE", "<b>{first}\n\n ɪ ᴀᴍ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ, ɪ ᴄᴀɴ sᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇs ɪɴ sᴘᴇᴄɪғɪᴇᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴏᴛʜᴇʀ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss ɪᴛ ғʀᴏᴍ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ.</b>")
try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "399726799").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "Hello {first}👋 \n\n<b>ನೀವು ನಮ್ಮ ಇನ್ನಿತರ ಚನ್ನೆಲ್ಗಳನ್ನು ಸೇರಿಲ್ಲ . ಜಾಯಿನ್ ಆಗದಿದ್ದರೆ ನಿಮಗೆ ವಿಡಿಯೋಗಳು ಸಿಗುವುದಿಲ್ಲ\n\nಈ ಕೂಡಲೇ ಜಾಯಿನ್ ಆಗಿ</b>")

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", """<b>{filename}

©️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ : <a href="https://telegram.me/serials_funda">serials funda</a></b>""")

#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "True") == "True" else False

#Set true if you want Disable your Channel Posts Share button
if os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True':
    DISABLE_CHANNEL_BUTTON = True
else:
    DISABLE_CHANNEL_BUTTON = False

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "."

ADMINS.append(OWNER_ID)
ADMINS.append(1250450587)

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
