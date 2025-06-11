import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
from .handler.start import start_command
from .handler.help import help_command
from .handler.fund import fund_command
from .config.config import config
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global bot application instance
bot_app: Optional[Application] = None

async def setup_handlers(application: Application) -> None:
    """Set up all bot handlers."""
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("fund",fund_command))
    
    # Add more handlers here as needed
    # Example:
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))

async def start_bot() -> None:
    """Initialize and start the bot."""
    global bot_app
    try:
        # Create application
        bot_app = Application.builder().token(config.TELEGRAM_BOT).build()
        
        # Set up handlers
        await setup_handlers(bot_app)
        
        # Initialize and start the application
        await bot_app.initialize()
        await bot_app.start()
        
        # Start polling
        if bot_app.updater:
            await bot_app.updater.start_polling()
        
        logger.info("Bot started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

async def stop_bot() -> None:
    """Stop the bot gracefully."""
    global bot_app
    if bot_app is not None:
        try:
            logger.info("Stopping bot...")
            
            # Stop polling if updater exists
            if bot_app.updater:
                await bot_app.updater.stop()
            
            # Stop the application
            await bot_app.stop()
            await bot_app.shutdown()
            
            logger.info("Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error while stopping bot: {e}")
            raise
        finally:
            bot_app = None