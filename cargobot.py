import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# ===== CONFIG =====
ADMIN_ID = 1042437313
BOT_TOKEN = '8252580479:AAH7KG7hYPSB2osGUHtN3PEVY7aA5n3ajrU'  # <-- tokenni ENV dan o‘qiymiz
API_URL = "https://toocars.tj/api/trackcode"
BASE_URL = 'https://cargobot-istaravshan.up.railway.app'

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variableni o‘rnating!")

# ===== UI =====
def get_custom_keyboard():
    custom_keyboard = [
        ["Тафтиши трек код"],
        ["Нархнома::"],
        ["Алока бо администратор"],
        ["Адреси карго!!"],
        ["Молҳои маъншуда!!"]
    ]
    return ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Салом! Ман боти ҷустуҷӯи кодҳои трек ҳастам.",
        reply_markup=get_custom_keyboard()
    )

async def send_address_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    image_path = os.path.join(os.getcwd(), "statics", "cargo_address_image.jpg")
    try:
        with open(image_path, "rb") as photo:
            # MarkdownV2 ni vaqtincha ishlatmaymiz — escape xatolariga yo‘l qo‘ymaslik uchun
            caption = (
                "🏢 Манзили карго: Istaravshan cargo\n"
                "Istaravshan cargo\n"
                "15157940200\n"
                "浙江省金华市义乌市\n"
                "福田街道兴港小区 77幢2单元1楼库房\n"
                "Istaravshan (ном ва номер телефон)"
            )
            await update.message.reply_photo(photo=photo, caption=caption)
    except Exception as e:
        await update.message.reply_text(f"❌ Error in sending photo: {str(e)}")

async def search_track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    track_code = update.message.text.strip()
    try:
        payload = {"trackcode": track_code}
        headers = {"Content-Type": "application/json"}
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}

        if resp.status_code == 200 and "message" in data:
            await update.message.reply_text(f"✅ {data['message']}")
        else:
            await update.message.reply_text(
                f"🔍 Барои шумо бо код трек: ({track_code}) бор дар анбори мо намеёбад!"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Хато рух дод: {str(e)}")

async def show_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pricing_info = (
        "Нархномаи мо ⤵️⤵️⤵️\n"
        "Қабули борҳо аз 0.5кг ҳисоб карда мешавад.\n"
        "Аз 0.1–0.5 кг → 1.5$\n"
        "Аз 0.51–1 кг → 3$\n"
        "1 куб → 300$ ҳисоб карда мешавад\n"
    )
    await update.message.reply_text(pricing_info)

async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()

    if text == "Тафтиши трек код":
        context.user_data['search_mode'] = True
        await update.message.reply_text("🔍 Лутфан, код трекро ворид намоед:")
    elif text == "Нархнома::":
        context.user_data['search_mode'] = False
        await show_pricing(update, context)
    elif text == "Алока бо администратор":
        context.user_data['search_mode'] = False
        await update.message.reply_text("📞 WhatsApp: 985639009, 945553322, @istaravshan_cargo_official")
    elif text == "Адреси карго!!":
        context.user_data['search_mode'] = False
        await send_address_image(update, context)
    elif text == "Молҳои маъншуда!!":
        context.user_data['search_mode'] = False
        await update.message.reply_text(
            "КАРГОИ МО ИН НАМУДИ БОРХОРО КАБУЛ НАМЕКУНАД!\n\n"
            "• Ашёҳои шишагӣ\n"
            "• Яроқ ва ашёҳои ҳарбӣ\n"
            "• Маводҳои хатарнок\n"
            "• Маводҳои наркотикӣ ва психотропӣ\n"
            "• Ҳайвонот ва растаниҳо\n"
            "• Маводҳои порнографӣ\n"
            "• Маҳсулотҳои хӯрока ва тиббӣ\n"
            "• Пул ва ҳуҷҷатҳои қалбакӣ\n"
        )
    else:
        await search_track(update, context)

# ===== ENTRYPOINT =====
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_press))

    print("Polling mode.")
    app.run_polling(
        poll_interval=2.0,
        timeout=30,
        allowed_updates=None,
        drop_pending_updates=True
    )
