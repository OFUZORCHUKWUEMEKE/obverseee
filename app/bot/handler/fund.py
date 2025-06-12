import os
from telegram import Update,ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler,CallbackContext, CallbackQueryHandler
from api.repositories.user import UserRepository
from api.services.user import UserService
from api.services.wallet import WalletService
from api.repositories.wallet import WalletRepository
from api.models.wallet import Chain
from dotenv import load_dotenv
from fastapi import FastAPI,Depends
import logging

load_dotenv()

logger = logging.getLogger(__name__)

async def get_user_service():
    # Assuming you have access to user_repository here
    user_repository = UserRepository()  # You'll need to create this
    return UserService(user_repository)  # Return an INSTANCE, not the class

async def get_wallet_service():
    wallet_repository = WalletRepository()
    return WalletService(wallet_repository)

async def fund_command( update: Update,
    context: ContextTypes.DEFAULT_TYPE)->None:
    """Handle the /fund command."""
    user = update.effective_user
    user_info = update.message.from_user
    user_service = await get_user_service()
    wallet_service = await get_wallet_service()

    try:
        existing_user = await user_service.get_user(str(user.id))
        if existing_user:
            wallets = await wallet_service.get_user_wallets(str(existing_user.id),chain=Chain.SOLANA)
            address = wallets[0].address
            fund_message = (
                 f"""
Ready to fund your Obverse wallet? Follow these simple steps to deposit SOL:

1. **Copy Your Solana Address**:  
**Address**: `{address}` *(Tap to copy)*

2. **Send SOL**: Use an external wallet like Binance, Coinbase, or Phantom to transfer SOL to this address.

Need help? Visit our support page at https://obverse.app/support or reach out to our team!

Happy trading,  
The Obverse Team
"""
            )
            await update.message.reply_text(text=fund_message,parse_mode='markdown',disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error in start command for user {user.id}: {str(e)}")
        await update.message.reply_text(
            "⚠️ An error occurred while processing your request. Please try again later."
        )
        raise

