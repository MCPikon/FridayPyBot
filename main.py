""" Friday Telegram Bot - Python 3.11.5 """

from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from secrets import token_urlsafe

TOKEN: Final = open("api-token", "r").read()
BOT_USERNAME: Final = "@fridayesp_bot"

# Functions
def generate_pass() -> str:
    return token_urlsafe(13)

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy Friday :)")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ayuda del bot (Aquí se mostrarán los comandos)")

async def pass_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_pass())

# Responses
def handle_response(text: str) -> str:
    lower_text: str = text.lower()
    if "hola" in lower_text:
        return "Hey"
    
    if "que tal" in lower_text:
        return "Muy Bien!!"

    if 'adios' in lower_text:
        return "Chaoo"
    
    return "No te he entendido... (Prueba a utilizar /help)"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User ({update.message.chat.id}) in {message_type}: \"{text}\"")

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print("Bot:", response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} causó un error {context.error}")

if __name__ == "__main__":
    print("Encendiendo Bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('pass', pass_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print("Buscando actualizaciones...")
    app.run_polling(poll_interval=3)
