from telegram import Update,ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler,CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
from api.repositories.user import UserRepository
from api.services.user import UserService
from api.services.wallet import WalletService
from api.repositories.wallet import WalletRepository
from api.services.swap import JupiterSwap
from api.models.wallet import Chain
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

SELECTING_OPTION, WAITING_FOR_INPUT,CONFIRM = range(3)

async def get_user_service():
    # Assuming you have access to user_repository here
    user_repository = UserRepository()  # You'll need to create this
    return UserService(user_repository)  # Return an INSTANCE, not the class

async def get_wallet_service():
    wallet_repository = WalletRepository()
    return WalletService(wallet_repository)

async def buy_command(update: Update,
    context: ContextTypes.DEFAULT_TYPE)->None:
    """
    Handle the /balance command.
    Buy Stablecoin USDT / USDC
    """
    # user = update.effective_user
    # user_info = update.message.from_user
    # user_service = await get_user_service()
    # wallet_service = await get_wallet_service()
    # swap = JupiterSwap()
    keyboard = [
        [InlineKeyboardButton("USDT", callback_data="usdt")],
        [InlineKeyboardButton("USDC", callback_data="usdc")],
        [InlineKeyboardButton("PYUSD", callback_data="pyusd")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
    return SELECTING_OPTION

async def button_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    selected_option = query.data
    context.user_data["selected_option"] = selected_option

    await query.edit_message_text(f"Please enter your {selected_option.replace('_','')}:")
    return WAITING_FOR_INPUT

    # try:
    #     user = await user_service.get_user(str(user.id))
    #     if not user:
    #         raise ValueError("User not Found in DB")
    #     wallets = await wallet_service.get_user_wallets(str(user.id),chain=Chain.SOLANA)
    #     address = wallets[0].address
    #     sol_mint = swap.tokens["SOL"]
    #     bal =  swap.get_token_balance(address,sol_mint)


#         if bal == 0.0 :
#             balance_message = (
#                 f"""
# 💰 Your current balance is insufficient for this transaction. Please deposit /fund to proceed. 🔄

# Best regards,
# The Obverse Team ✨
#                     """
#             )
#             await update.message.reply_text(text=balance_message,parse_mode='markdown',disable_web_page_preview=True)

        # await update.message.reply_text(text=balance_message,parse_mode='markdown',disable_web_page_preview=True)
    # except Exception as e:
    #     logger.error(f"Error in fund command for user {user.id}: {str(e)}")
    #     await update.message.reply_text(
    #         "⚠️ An error occurred while processing your request. Please try again later."
    #     )
    #     raise




