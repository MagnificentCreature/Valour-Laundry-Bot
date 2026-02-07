import logging
import os

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from image_generator import create_status_image
from models import Dryer, Washer

THREAD_ID = 2
WASHER_COUNT = 10
DRYER_COUNT = 10

last_message = None
machines = {
    "washer": [Washer(i) for i in range(WASHER_COUNT)],
    "dryer": [Dryer(i) for i in range(DRYER_COUNT)],
}
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def new_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the status of the washing machines"""
    global last_message

    last_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        message_thread_id=THREAD_ID,
        text=prepare_message(),
    )


async def edit_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edit a message in the forum topic"""
    global last_message

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=last_message.message_id,
        text=prepare_message(),
    )


async def send_image_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the status image to the chat."""
    photo = create_status_image(machines)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo,
        message_thread_id=THREAD_ID,
    )


async def set_availability(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Changes the value of my_value based on user input."""
    global machines

    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text(
                "Please provide a value. Usage: /set <washer/dryer> <index> <minutes>"
            )
            return

        machine_type, index, time_left = (
            args[0],
            int(args[1]) - 1,
            int(args[2]),
        )  # Convert the input to the desired type (e.g., int)

        machines[machine_type][index].set_time(time_left)

        # Send confirmation
        await update.message.reply_text(
            f"{machine_type.capitalize()} {index+1} time set to {time_left} min"
        )

    except Exception:
        await update.message.reply_text("Usage: /set <washer/dryer> <index> <minutes>")


def prepare_message():
    """Prepare the status message"""
    washers = [str(machine) for machine in machines["washer"]]
    dryers = [str(machine) for machine in machines["dryer"]]
    return "\n".join(washers) + "\n" + "\n".join(dryers)


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")

    application = ApplicationBuilder().token(TOKEN).build()

    show_status_handler = CommandHandler("status", new_status)
    edit_message_handler = CommandHandler("edit", edit_status)
    set_availability_handler = CommandHandler("set", set_availability)
    image_status_handler = CommandHandler("image", send_image_status)

    application.add_handler(show_status_handler)
    application.add_handler(edit_message_handler)
    application.add_handler(set_availability_handler)
    application.add_handler(image_status_handler)

    print("Bot is running...")
    application.run_polling()
