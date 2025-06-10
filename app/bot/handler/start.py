import os
from telegram import Update,ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler,CallbackContext, CallbackQueryHandler
from ...api.services.user import UserService
import logging

logger = logging.getLogger(__name__)

def get_wallet_service():
    return UserService


async def start_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_info = update.message.from_user
    telegram_user = update.effective_user # Extract user details
    """Handle the /start command."""
    user = update.effective_user
    
    # Log user interaction
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    welcome_message = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to our Obverse! I'm here to help you with various tasks.\n"
        "Use the menu below to get started or type /help for more information."
    )
    
    await update.message.reply_text(
        welcome_message,
    )