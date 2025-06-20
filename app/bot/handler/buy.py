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
# Define conversation states
CHOOSE_CURRENCY, INPUT_AMOUNT, CONFIRM_TRANSACTION = range(3)

async def get_user_service():
    # Assuming you have access to user_repository here
    user_repository = UserRepository()  # You'll need to create this
    return UserService(user_repository)  # Return an INSTANCE, not the class

async def get_wallet_service():
    wallet_repository = WalletRepository()
    return WalletService(wallet_repository)

async def start_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the transaction conversation and show currency selection."""
    keyboard = [
        [InlineKeyboardButton("USDC", callback_data='USDC')],
        [InlineKeyboardButton("USDT", callback_data='USDT')],
        [InlineKeyboardButton("PYUSD", callback_data='PYUSD')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome! Choose a Stablecoin",
        reply_markup=reply_markup
    )
    
    return CHOOSE_CURRENCY

async def currency_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle currency selection and ask for amount."""
    query = update.callback_query
    await query.answer()
    
    # Store the selected currency
    context.user_data['currency'] = query.data
    
    await query.edit_message_text(
        f"You selected: {query.data}\n\n"
        "Please enter the amount you want to transact:"
    )
    return INPUT_AMOUNT

async def amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle amount input and show confirmation."""
    try:
        amount = float(update.message.text)
        if amount <= 0:
            await update.message.reply_text(
                "Please enter a valid positive amount:"
            )
            return INPUT_AMOUNT    
        # Store the amount
        context.user_data['amount'] = amount      
        # Create confirmation keyboard
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data='confirm'),
                InlineKeyboardButton("❌ Cancel", callback_data='cancel')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        currency = context.user_data['currency']

        await update.message.reply_text(
            f"📋 Transaction Summary:\n"
            f"Currency: {currency}\n"
            f"Amount: {amount:,.2f} {currency}\n\n"
            f"Please confirm or cancel this transaction:",
            reply_markup=reply_markup
        )
        
        return CONFIRM_TRANSACTION
        
    except ValueError:
        await update.message.reply_text(
            "Invalid amount format. Please enter a numeric value:"
        )
        return INPUT_AMOUNT

async def transaction_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle transaction confirmation or cancellation."""
    query = update.callback_query
    user = update.effective_user
    await query.answer()
    
    if query.data == 'confirm':
        currency = context.user_data['currency']
        amount = context.user_data['amount']
        amount_lamports = int(amount * 1_000_000_000)
        swap = JupiterSwap()
        user_service = await get_user_service()
        wallet_service = await get_wallet_service()
        # Here you would implement your actual transaction logic
        # For now, we'll just simulate a successful transaction
        token_map = {
            "SOL":swap.tokens["SOL"],
            "USDC": swap.tokens["USDC"],
            "USDT": swap.tokens["USDT"],
            "PYUSD": swap.tokens["PYUSD"]
        }
        input_mint = token_map.get("SOL")
        output_mint = token_map.get(currency, swap.tokens["SOL"])
        quote = swap.get_quote(input_mint,output_mint,amount_lamports)
        print(quote["routePlan"])
        try:
            existing_user = await user_service.get_user(str(user.id))
            if existing_user:
               wallets = await wallet_service.get_user_wallets(str(existing_user.id),chain=Chain.SOLANA)
               address = wallets[0].address
            #    swap = swap.get_swap(quote,address)
        except Exception as e:
            logger.error(f"Error in start command for user {user.id}: {str(e)}")
            await update.message.reply_text(
                "⚠️ An error occurred while processing your request. Please try again later."
            )
            raise
        # swaps = swap.get_swap(quote)
        
        await query.edit_message_text(
            f"✅ Transaction Confirmed!\n\n"
            f"Currency: {currency}\n"
            f"Amount: {amount:,.2f} {currency}\n"
            f"Status: Processing...\n\n"
            f"You will receive a notification once the transaction is complete."
        )
        
        # Clear user data
        context.user_data.clear()
        
        # Here you could add your transaction processing logic
        # process_transaction(currency, amount, update.effective_user.id)
        
    elif query.data == 'cancel':
        await query.edit_message_text(
            "❌ Transaction cancelled.\n\n"
            "Use /transaction to start a new transaction."
        )
        
        # Clear user data
        context.user_data.clear()
    
    return ConversationHandler.END

async def cancel_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle manual cancellation via /cancel command."""
    await update.message.reply_text(
        "❌ Transaction cancelled.\n\n"
        "Use /transaction to start a new transaction."
    )
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END

async def timeout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle conversation timeout."""
    await update.message.reply_text(
        "⏰ Transaction timed out due to inactivity.\n\n"
        "Use /transaction to start a new transaction."
    )
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END
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




