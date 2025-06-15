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
from .handler.balance import balance_command
from .handler.buy import start_transaction, cancel_transaction, amount_received,timeout_handler,transaction_confirmed,currency_selected,CHOOSE_CURRENCY,INPUT_AMOUNT,CONFIRM_TRANSACTION
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
    application.add_handler(CommandHandler("balance",balance_command))
    # application.add_handler(CommandHandler("buy",buy_command))
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('buy', start_transaction)],
        states={
            CHOOSE_CURRENCY: [
                CallbackQueryHandler(currency_selected, pattern='^(USDC|USDT|PYUSD)$')
            ],
            INPUT_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, amount_received)
            ],
            CONFIRM_TRANSACTION: [
                CallbackQueryHandler(transaction_confirmed, pattern='^(confirm|cancel)$')
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_transaction),
            MessageHandler(filters.ALL, timeout_handler)
        ],
        conversation_timeout=300,  # 5 minutes timeout
        name="transaction_conversation",
    )
    application.add_handler(conversation_handler)
    
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