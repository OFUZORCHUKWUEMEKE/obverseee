import os
from telegram import Update,ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler,CallbackContext, CallbackQueryHandler
# from ...api.services.user import UserService
from ...api.repositories.user import UserRepository
from ...api.services.user import UserService
from ...api.services.wallet import WalletService
from fastapi import Fastapi,Depends
import logging

logger = logging.getLogger(__name__)

async def get_user_service():
    return UserService

async def get_wallet_service():
    return WalletService


async def start_command(update:Update,context:ContextTypes.DEFAULT_TYPE,user_service:UserService=Depends(get_user_service),wallet_service:WalletService=Depends(get_wallet_service)):
    user_info = update.message.from_user
    telegram_user = update.effective_user # Extract user details
    """Handle the /start command."""
    user = update.effective_user
    exixting_user = await user_service.get_user(str(user.id))
    if existing_user:
        await update.message.reply_text(
            f"Hello! {user_info.first_name} , Welcome to Obverse\n"
            f"Obverse is a Stablecoin Payment management agent that helps businesses / Individuals collect fiat payments through links and QRcodes\n"
        )
    user_created = await user_service.create_user(
            str(user.id),
            username=user.username,
            )
    wallets = await wallet_service.get_user_wallets(str(user_created.id))
    if not wallets:
        new_wallet = await wallet_service.create_solana_wallet(str(user_created.id))
        await user_service.add_wallet_to_user(str(user.id),new_wallet.id)
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