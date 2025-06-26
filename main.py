import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    filters, ContextTypes
)

# Bot & Admin
BOT_TOKEN = "7842020009:AAE9-fS_mX5u5OWb5yp_8WZqnZofUsoyLQ0"
ADMIN_ID = 5343691376

# Conversation States
BGMI_UID, IGN, POP_QUANTITY, SCREENSHOT, UPI_PAYMENT = range(5)

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"👋 Welcome to BGMI Pop Order Bot\nUsername: @{user.username or 'unknown'}"
    buttons = [
        [KeyboardButton("📥 Pop Order")],
        [KeyboardButton("💰 Pay"), KeyboardButton("📊 Status")],
        [KeyboardButton("🆘 Help")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Handle text buttons
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Pop Order" in text:
        await update.message.reply_text("📌 Step 1: Please enter your BGMI UID:")
        return BGMI_UID
    elif "Pay" in text:
        await update.message.reply_text("💰 Please send your payment screenshot here.")
        return SCREENSHOT
    elif "Status" in text:
        await update.message.reply_text("📊 Our admin will update your status soon.")
    elif "Help" in text:
        await update.message.reply_text("🆘 For support contact: @TRxROHIT")

# Step 1: BGMI UID
async def bgmi_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['uid'] = update.message.text
    await update.message.reply_text("✅ Step 2: Enter your IGN (in-game name):")
    return IGN

# Step 2: IGN
async def ign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ign'] = update.message.text
    await update.message.reply_text("🔢 Step 3: Enter POP Quantity (e.g., 1, 2, 3):")
    return POP_QUANTITY

# Step 3: Pop Quantity
async def pop_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['pop_qty'] = update.message.text
    await update.message.reply_text("📸 Step 4: Please upload your payment screenshot:")
    return SCREENSHOT

# Step 4: Screenshot
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['screenshot'] = update.message.photo[-1].file_id
    await update.message.reply_text("🕐 Step 5: Pop Time is fixed at 30 minutes.")

    await update.message.reply_text("💳 Step 6: Enter your UPI ID or payment method used:")
    return UPI_PAYMENT

# Step 5: UPI Details
async def upi_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['upi'] = update.message.text

    # Send all info to admin
    data = context.user_data
    msg = (
        "📥 New POP Order Received\n"
        f"👤 UID: {data['uid']}\n"
        f"🎮 IGN: {data['ign']}\n"
        f"🔢 Pop Qty: {data['pop_qty']}\n"
        f"💳 UPI Info: {data['upi']}\n"
        f"🕒 Time: 30 Min Pop\n"
        f"👀 From: @{update.effective_user.username or 'unknown'}"
    )

    # Forward screenshot and message
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=data['screenshot'], caption=msg)
    await update.message.reply_text("✅ Your order has been submitted and sent to admin.")
    return ConversationHandler.END

# Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Pop order canceled.")
    return ConversationHandler.END

# Command Handlers
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🆘 For help, contact @TRxROHIT")

async def pay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Send your payment screenshot to confirm your order.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Status will be updated by admin soon.")

# Main App
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Conversation handler for pop order
conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("poporder", button_handler),
        MessageHandler(filters.Regex("Pop Order"), button_handler)
    ],
    states={
        BGMI_UID: [MessageHandler(filters.TEXT, bgmi_uid)],
        IGN: [MessageHandler(filters.TEXT, ign)],
        POP_QUANTITY: [MessageHandler(filters.TEXT, pop_quantity)],
        SCREENSHOT: [MessageHandler(filters.PHOTO, screenshot)],
        UPI_PAYMENT: [MessageHandler(filters.TEXT, upi_payment)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("pay", pay_command))
app.add_handler(CommandHandler("status", status_command))
app.add_handler(CommandHandler("poporder", button_handler))
app.add_handler(MessageHandler(filters.TEXT, button_handler))
app.add_handler(conv_handler)

# Run the bot
if __name__ == "__main__":
    app.run_polling()
