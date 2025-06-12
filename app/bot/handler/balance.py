from telegram import Update,ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler,CallbackContext, CallbackQueryHandler
from api.repositories.user import UserRepository
from api.services.user import UserService
from api.services.wallet import WalletService
from api.repositories.wallet import WalletRepository
from api.models.wallet import Chain
from dotenv import load_dotenv
import os
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


async def balance_command(update: Update,
    context: ContextTypes.DEFAULT_TYPE)->None:
    """Handle the /balance command."""
    user = update.effective_user
    user_info = update.message.from_user
    user_service = await get_user_service()
    wallet_service = await get_wallet_service()
    
    try:
        user = await user_service.get_user(str(user.id))
        if not user:
            raise ValueError("User not Found in DB")
        wallets = await wallet_service.get_user_wallets(str(user.id),chain=Chain.SOLANA)
        address = wallets[0].address
        balance = await wallet_service.check_wallet_balance(address)
        print(balance);
        balance_message = (
                f"""
Thank you for using Obverse! Here's the current balance for your Solana wallet:

** Solana Address**:  
**Address**: `{address}` *(Tap to copy)*
Balance: `{balance}` SOL

Stay in control of your assets with Obverse. If you have any questions or need assistance, our support team is here to help!

Best regards,
The Obverse Team
"""
        )
        await update.message.reply_text(text=balance_message,parse_mode='markdown',disable_web_page_preview=True)
    except Exception as e :
        logger.error(f"Error in fund command for user {user.id}: {str(e)}")
        await update.message.reply_text(
            "⚠️ An error occurred while processing your request. Please try again later."
        )
        raise





