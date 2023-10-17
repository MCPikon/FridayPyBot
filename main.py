""" Friday Telegram Bot - Python 3.11.5 """

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config

import logging
import coloredlogs
import locale
from datetime import datetime
from secrets import token_urlsafe
from random import sample, choice

from imgurpython import ImgurClient

# Imgur Client
imgur_client = ImgurClient(config.CLIENT_ID, config.CLIENT_SECRET, config.ACCESS_TOKEN, config.REFRESH_TOKEN)

# Logs
coloredlogs.install()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Set the local time
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Functions
def generate_pass() -> str:
    return token_urlsafe(13)


def generate_passphrase() -> str:
    num_words = 12
    with open("wordlist.txt", 'r') as file:
        words = file.read().splitlines()

    passphrase = "-".join(sample(words, num_words))
    return passphrase


def get_random_meme_link() -> str:
    try:
        images_list = imgur_client.get_album_images("NbhcNZo")
        image = choice(images_list)
        return image.link
    except:
        return "static\errors\error_img.png"


def get_random_video_meme_link() -> str:
    try:
        videos_list = imgur_client.get_album_images("c2YLLz3")
        video = choice(videos_list)
        return video.link
    except:
        return "static\errors\error_vid.mp4"


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy Friday, para saber que puedo hacer usa /help")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """Ayuda del bot:
            \n/pass - Genera una contraseña aleatoria
            \n/passphrase - Genera una contraseña de frases aleatoria
            \n/meme - Envía un meme aleatorio de una colección del bot
            \n/vidmeme - Envía un videomeme aleatorio de una colección del bot
           """
    await update.message.reply_text(text)


async def pass_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown_v2(f"```{generate_pass()}```")


async def passphrase_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown_v2(f"```{generate_passphrase()}```")


async def random_memes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(get_random_meme_link())


async def random_video_memes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_video(get_random_video_meme_link())


# Responses
def handle_response(text: str) -> str:
    lower_text: str = text.lower()
    if "hola" in lower_text:
        return "Hey"

    if "que tal" in lower_text:
        return "Muy Bien!!"

    if "adios" in lower_text:
        return "Chaoo"
    
    if "¿que día es hoy?" in lower_text:
        return f"Hoy es {str(datetime.utcnow().strftime('%A %d'))}"
    
    if "¿que hora es?" in lower_text:
        return f"Son las {str(datetime.utcnow().strftime('%H:%M'))}"

    return "No te he entendido... (Prueba a utilizar /help)"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    logging.info(f"User ({update.message.chat.id}) in {message_type}: \"{text}\"")

    if message_type == "group":
        if config.BOT_USERNAME in text:
            new_text: str = text.replace(config.BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    logging.info(f"Bot: {response}")
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Update {update} causó un error {context.error}")


if __name__ == "__main__":
    app = Application.builder().token(config.BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('pass', pass_command))
    app.add_handler(CommandHandler('passphrase', passphrase_command))
    app.add_handler(CommandHandler('meme', random_memes_command))
    app.add_handler(CommandHandler('vidmeme', random_video_memes_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    app.run_polling(poll_interval=3.0, read_timeout=30)
