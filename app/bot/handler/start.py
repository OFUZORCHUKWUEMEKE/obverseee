import os
from telegram import Update,ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler,CallbackContext, CallbackQueryHandler
from api.repositories.user import UserRepository
from api.services.user import UserService
from api.services.wallet import WalletService
from api.repositories.wallet import WalletRepository
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

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle the /start command."""
    user = update.effective_user
    user_info = update.message.from_user

    user_service = await get_user_service()
    wallet_service = await get_wallet_service()
    
    try:
        existing_user = await user_service.get_user(str(user.id))
        # print(existing_user)    
        welcome_message = (
            f"👋 Hello {user_info.first_name}, Welcome to Obverse!\n\n"
            "Obverse is a Stablecoin Payment management agent that helps businesses/Individuals "
            "collect fiat payments through links and QR codes.\n"
            "Use the menu below to get started or type /help for more information."
        )
        
        if not existing_user:
            # Create new user if doesn't exist
            user_created = await user_service.create_user(
                str(user.id),
                username=user.username,
            )
            # user_created = await user_service.get_user(str(user.id))
            # print(user_created)
            # Create default wallet for new user
            wallets = await wallet_service.get_user_wallets(str(user_created.id))
            print(f"wallets",wallets)
            if not wallets:
                # wallets = await wallet_service.get_user_wallets(str(user_created.id))
                new_wallet = await wallet_service.create_solana_wallet(str(user_created.id))
                # logger.info("Created new Solana wallet for user")
                await user_service.add_wallet_to_user(str(user.id), wallet_id=new_wallet.id)
                welcome_message += "\n\nA new Solana wallet has been created for you!"
        
        # Send welcome message to all users
        await update.message.reply_text(welcome_message)
        
        # Log user interaction
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
    except Exception as e:
        logger.error(f"Error in start command for user {user.id}: {str(e)}")
        await update.message.reply_text(
            "⚠️ An error occurred while processing your request. Please try again later."
        )
        raise