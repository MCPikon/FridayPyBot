""" Friday Telegram Bot - Python 3.11.5 """

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import config
import logging
import coloredlogs
import locale
from datetime import datetime
from secrets import token_urlsafe
from random import sample, choice
from imgurpython import ImgurClient

# Imgur API Client
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
    images_list = imgur_client.get_album_images("NbhcNZo")
    image = choice(images_list)
    return image.link


def get_random_video_meme_link() -> str:
    videos_list = imgur_client.get_album_images("c2YLLz3")
    video = choice(videos_list)
    return video.link


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"¡Hola {update.effective_user.username}! Soy Friday, para saber que puedo hacer usa /help")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Ayuda del bot:\n"\
            "/pass - Genera una contraseña aleatoria\n"\
            "/passphrase - Genera una contraseña de frases aleatoria\n"\
            "/meme - Envía un meme aleatorio de una colección del bot\n"\
            "/vidmeme - Envía un videomeme aleatorio de una colección del bot"
    await update.message.reply_text(text)


async def pass_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown_v2(f"```{generate_pass()}```")


async def passphrase_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown_v2(f"```{generate_passphrase()}```")


async def random_memes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_photo(get_random_meme_link())
    except:
        await update.message.reply_photo("static\errors\error_img.png", 
                                         caption="Ha ocurrido un error obteniendo el meme de la colección <b>(Por favor intentalo más tarde)</b>",
                                         parse_mode=ParseMode.HTML)


async def random_video_memes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_video(get_random_video_meme_link())
    except:
        await update.message.reply_video("static\errors\error_vid.mp4",
                                         caption="Ha ocurrido un error obteniendo el vídeo de la colección <b>(Por favor intentalo más tarde)</b>",
                                         parse_mode=ParseMode.HTML)


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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_type: str = update.message.chat.type
    text: str = update.message.text

    logging.info("User (%s) in %s: \"%s\"" % (update.message.chat.id, message_type, text))

    if message_type == "group":
        if config.BOT_USERNAME in text:
            new_text: str = text.replace(config.BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    logging.info("Bot: %s" % response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Update %s causó un error %s" % (update, context.error))


def main() -> None:
    ''' Main function (Starts the bot, set all handlers and polls it) '''
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


if __name__ == "__main__":
    main()
