import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram import InputMediaPhoto, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import mqtt_helper
from image_generator import create_status_image
from models import Dryer, Washer

THREAD_ID = 2
WASHER_COUNT = 10
DRYER_COUNT = 10

application = None
bot_loop = None
last_message = None
machines = {
    "washer": [Washer(i) for i in range(WASHER_COUNT)],
    "dryer": [Dryer(i) for i in range(DRYER_COUNT)],
}
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def prepare_message():
    """Prepare the status message"""
    washers = [str(machine) for machine in machines["washer"]]
    dryers = [str(machine) for machine in machines["dryer"]]
    zipped = list(zip(washers, dryers))
    return (
        "`"
        + "\n"
        + "\n".join([f"{washer:10} {dryer:10}" for washer, dryer in zipped])
        + "`"
    )


async def new_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the status of the washing machines"""
    global last_message

    photo = create_status_image(machines)

    last_message = await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        caption=prepare_message(),
        photo=photo,
        message_thread_id=THREAD_ID,
        parse_mode="MarkdownV2",
    )


async def start_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the status of the washing machines"""

    photo = create_status_image(machines)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        caption=prepare_message(),
        photo=photo,
        parse_mode="MarkdownV2",
    )


async def update_status_message(bot, chat_id, message_id):
    photo = create_status_image(machines)
    await bot.edit_message_media(
        chat_id=chat_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=photo, caption=prepare_message(), parse_mode="MarkdownV2"
        ),
    )


async def update_message():
    """Updates the Telegram message with the latest status."""
    if last_message:
        try:
            await update_status_message(
                application.bot, last_message.chat.id, last_message.message_id
            )
        except Exception as e:
            logging.error(f"Error updating message: {e}")


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


def update_processing(input, machine_type, machine_index):
    if machines[machine_type][machine_index].get_time() > 0:
        return
    machines[machine_type][machine_index].set_time(input)


def on_mqtt_message(client, userdata, msg):
    """Handle incoming MQTT messages to update machine status."""
    try:
        parts = msg.topic.split("/")
        if len(parts) < 3:
            return

        machine_type = parts[1]  # "washer" or "dryer"
        index = int(parts[2]) - 1  # Convert 1-based index to 0-based
        payload = msg.payload.decode("utf-8")

        if machine_type in machines and 0 <= index < len(machines[machine_type]):
            # Determine time left
            if payload.upper() == "F":  # F for finished
                minutes = 0
            elif payload.isdigit():
                minutes = int(payload)
            else:
                return  # Ignore invalid payloads

            # Update the machine state
            update_processing(minutes, machine_type, index)
            logging.info(f"MQTT Update: {machine_type} {index+1} -> {minutes} min")

            print("HERE")
            if bot_loop:
                if last_message:
                    asyncio.run_coroutine_threadsafe(update_message(), bot_loop)
                else:
                    asyncio.run_coroutine_threadsafe(new_status(), bot_loop)

    except Exception as e:
        logging.error(f"MQTT Error processing message: {e}")


async def countdown_timer():
    """Background task to decrease machine time every minute."""
    while True:
        await asyncio.sleep(30)
        # await asyncio.sleep(60)
        has_changes = False
        for machine_list in machines.values():
            for machine in machine_list:
                if machine.tick():
                    has_changes = True

        if has_changes:
            await update_message()


async def post_init(app):
    global bot_loop
    bot_loop = asyncio.get_running_loop()
    app.create_task(countdown_timer())


# Removed edit status command, it was used for debugging
async def edit_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edit a message in the forum topic"""
    global last_message
    if last_message:
        await update_status_message(
            context.bot, update.effective_chat.id, last_message.message_id
        )


def pybot_init(token):
    global application
    application = ApplicationBuilder().token(token).post_init(post_init).build()

    show_status_handler = CommandHandler("status", new_status)
    set_availability_handler = CommandHandler("set", set_availability)
    edit_status_handler = CommandHandler("edit", edit_status)
    start_handler = CommandHandler("start", start_reply)

    application.add_handler(show_status_handler)
    application.add_handler(set_availability_handler)
    application.add_handler(edit_status_handler)
    application.add_handler(start_handler)

    application.run_polling()


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    BROKER_URL = os.getenv("MQTT_SERVER")
    USERNAME = os.getenv("MQTT_USER")
    PASSWORD = os.getenv("MQTT_PASS")

    mqtt_helper.mqtt_init(BROKER_URL, USERNAME, PASSWORD, on_mqtt_message)
    pybot_init(TOKEN)
