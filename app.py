import logging
import os

from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ApplicationBuilder, Updater, CommandHandler, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv

from fast_style_transfer.evaluate import style_photo
from cartoon_gan.cartoonize import cartoonize_image
from arbitrary_style_transfer.style_transfer import transfer_style

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)


SELECTING_STYLE = 1
WAITING_IMAGE = 2

START_TEXT = r"""Hi, I'm style bot\. I can apply different styles to your photo, cartoonize it using CartoonGan or transfer style from one photo to another\.
To proceed, click a button with a style below and send an image\.

Commands:
/start or /help \- display this message
`style` \- select style and apply it to image \(`style` is one of `Udnie`, `Scream`, `La Muse`, `Rain Princess`, `Wave`, `Wreck`\)
/details \- show some details about used neural nets
/transfer\_style \- same as pressing `Transfer Style`

Have fun 😎"""

DETAILS_TEXT = """[CartoonGan page on TensorflowHub](https://tfhub.dev/sayakpaul/lite-model/cartoongan/dr/1)
[Fast Style Transfer github page](https://github.com/lengstrom/fast-style-transfer)
[Magenta Arbitrary image stylization page on TensorflowHub](https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2)"""

STYLE_BUTTON_TO_STYLE = {
    "La Muse": "la_muse",
    "Rain Princess": "rain_princess",
    "Udnie": "udnie",
    "Scream": "scream",
    "Wave": "wave",
    "Wreck": "wreck"
}


def get_style_keyboard() -> InlineKeyboardMarkup:
    """Generate an inline keyboard layout with available styles"""
    keyboard = [
        [
            KeyboardButton("Udnie"),
            KeyboardButton("Scream"),
            KeyboardButton("Rain Princess"),
        ],
        [
            KeyboardButton("La Muse"),
            KeyboardButton("Wave"),
            KeyboardButton("Wreck"),
        ],
        [
            KeyboardButton("Cartoonize using CartoonGan")
        ],
        [
            KeyboardButton("Transfer Style")
        ],
        [
            KeyboardButton("/help"),
            KeyboardButton("/details")
        ],
    ]
    return ReplyKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a start message with available styles and transition to style selection state"""
    await update.message.reply_text(
        START_TEXT,
        reply_markup=get_style_keyboard(),
        parse_mode='MarkdownV2'
    )
    return SELECTING_STYLE


async def details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        DETAILS_TEXT,
        parse_mode='MarkdownV2'
    )


async def select_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get the selected style and transition to waiting for image state"""
    style = update.message.text
    context.user_data['style'] = style
    if style == "Cartoonize using CartoonGan":
        reply = "Please send an image to cartoonize."
    elif style == "Transfer Style":
        reply = "Please send an image to which you want apply style and than style image."
    else:
        reply = f"You have selected {style} style. Please send an image to convert."
    await update.message.reply_text(reply)
    return WAITING_IMAGE


async def receive_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the received image and send back the converted image"""
    user_id = str(update.message.from_user.id)
    style = context.user_data.get('style')
    if not style:
        await update.message.reply_text("Please select a style first.")
        return SELECTING_STYLE
    
    photo_file = await update.message.photo[-1].get_file()

    content_image_path = context.user_data.get('content_image_path')
    if style == "Transfer Style" and not content_image_path:
        content_image_path = f"images_to_style/{user_id}_content.jpg"
        context.user_data['content_image_path'] = content_image_path
        await photo_file.download_to_drive(content_image_path)
        await update.message.reply_text("Please send style image.")
        return WAITING_IMAGE

    await photo_file.download_to_drive(f"images_to_style/{user_id}.jpg")

    if style == "Cartoonize using CartoonGan":
        converted_image = cartoonize_image(f"images_to_style/{user_id}.jpg")
    elif style == "Transfer Style":
        converted_image = transfer_style(content_image_path, f"images_to_style/{user_id}.jpg")
        context.user_data['content_image_path'] = None
    else:
        converted_image = style_photo(STYLE_BUTTON_TO_STYLE[style], f"images_to_style/{user_id}.jpg")

    await update.message.reply_photo(photo=open(converted_image, 'rb'))
    return SELECTING_STYLE


async def transfer_style_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['style'] = "Transfer Style"
    print("\n\nIN transfer handler\n\n")
    reply = "Please send an image to which you want apply style and than style image."
    await update.message.reply_text(reply)
    return WAITING_IMAGE


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)


def main() -> None:
    """Run the bot"""

    load_dotenv()

    app = ApplicationBuilder().token(os.environ["TG_BOT_TOKEN"]).build()


    # Add conversation handler with states and handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler("transfer_style", transfer_style_handler)],
        states={
            SELECTING_STYLE: [MessageHandler(filters.Regex(r'^(Udnie|Scream|Rain Princess|La Muse|Wave|Wreck|Cartoonize using CartoonGan|Transfer Style)$'), select_style)],
            WAITING_IMAGE: [MessageHandler(filters.PHOTO, receive_image)]
        },
        fallbacks=[CommandHandler('start', start), CommandHandler("transfer_style", transfer_style_handler)],
    )

    # Add handlers to the dispatcher
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("details", details))
    app.add_handler(CommandHandler("help", start))
    app.add_error_handler(error_handler)

    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()
