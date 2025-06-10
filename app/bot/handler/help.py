import os
from telegram import Update,ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler,CallbackContext, CallbackQueryHandler
import logging

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = (
        "🤖 *Available Commands*\n\n"
        "/start - Start the bot and show main menu\n"
        "/help - Show this help message\n"
        "/buy -  Buy stablecoins easily\n"
        "/fund - Add funds to your wallet address\n"
        "/payment - Create a Payment Link\n"
        "/AgentMode - Talk to Obverse Agent\n"
        "/balance - Check your current wallet balance\n\n"
        "💡 You can also use the inline buttons for easier navigation!"
    )
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown'
    )