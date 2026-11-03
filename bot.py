import os
import random
import logging
import telebot
from telebot import types
from telebot.async_telebot import AsyncTeleBot

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Retrieve BOT_TOKEN from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN variable is not set!")

bot = AsyncTeleBot(BOT_TOKEN)

# In-memory storage for points/balance (For production, connect a PostgreSQL database)
USER_BALANCES = {}
INITIAL_BALANCE = 1000

def get_balance(user_id: int) -> int:
    if user_id not in USER_BALANCES:
        USER_BALANCES[user_id] = INITIAL_BALANCE
    return USER_BALANCES[user_id]

def update_balance(user_id: int, amount: int):
    current = get_balance(user_id)
    USER_BALANCES[user_id] = max(0, current + amount)

def main_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_coin = types.InlineKeyboardButton("🪙 Coin Flip (50 pts)", callback_data="game_coin")
    btn_dice = types.InlineKeyboardButton("🎲 Dice Roll (100 pts)", callback_data="game_dice")
    btn_slots = types.InlineKeyboardButton("🎰 Slots (100 pts)", callback_data="game_slots")
    btn_balance = types.InlineKeyboardButton("💳 My Balance", callback_data="check_balance")
    btn_claim = types.InlineKeyboardButton("🎁 Claim Daily Bonus", callback_data="daily_bonus")
    
    markup.add(btn_coin, btn_dice)
    markup.add(btn_slots, btn_balance)
    markup.add(btn_claim)
    return markup

@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    welcome_text = (
        f"🎰 *Welcome to the Telegram Boost Casino!* 🎰\n\n"
        f"Hello *{message.from_user.first_name}*!\n"
        f"Your current balance: *{balance} points*\n\n"
        f"Play games to boost group activity and win points!"
    )
    await bot.send_message(
        chat_id=message.chat.id, 
        text=welcome_text, 
        parse_mode="Markdown", 
        reply_markup=main_menu_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
async def handle_callbacks(call: types.CallbackQuery):
    user_id = call.from_user.id
    balance = get_balance(user_id)

    if call.data == "check_balance":
        await bot.answer_callback_query(call.id, f"Your balance is: {balance} points", show_alert=True)

    elif call.data == "daily_bonus":
        update_balance(user_id, 200)
        new_bal = get_balance(user_id)
        await bot.answer_callback_query(call.id, "🎁 You claimed +200 bonus points!", show_alert=True)
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🎰 *Telegram Boost Casino*\n\nBalance updated: *{new_bal} points*",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    elif call.data == "game_coin":
        cost = 50
        if balance < cost:
            await bot.answer_callback_query(call.id, "❌ Not enough points! Claim daily bonus.", show_alert=True)
            return

        outcome = random.choice(["Heads", "Tails"])
        win = random.choice([True, False])
        
        if win:
            update_balance(user_id, cost)
            result_msg = f"🪙 **Coin Flip:** It landed on *{outcome}*! You WON *+{cost}* points! 🎉"
        else:
            update_balance(user_id, -cost)
            result_msg = f"🪙 **Coin Flip:** It landed on *{outcome}*! You LOST *-{cost}* points. 😢"

        await bot.send_message(call.message.chat.id, result_msg, parse_mode="Markdown")
        await bot.answer_callback_query(call.id)

    elif call.data == "game_dice":
        cost = 100
        if balance < cost:
            await bot.answer_callback_query(call.id, "❌ Not enough points!", show_alert=True)
            return

        # Send native animated dice to telegram
        dice_msg = await bot.send_dice(call.message.chat.id, emoji="🎲")
        dice_value = dice_msg.dice.value

        if dice_value >= 4:
            update_balance(user_id, cost)
            res = f"🎲 You rolled a *{dice_value}*! You WIN *+{cost}* points! 🔥"
        else:
            update_balance(user_id, -cost)
            res = f"🎲 You rolled a *{dice_value}*! You LOSE *-{cost}* points. 💀"

        await bot.send_message(call.message.chat.id, res, parse_mode="Markdown")
        await bot.answer_callback_query(call.id)

    elif call.data == "game_slots":
        cost = 100
        if balance < cost:
            await bot.answer_callback_query(call.id, "❌ Not enough points!", show_alert=True)
            return

        # Send native animated slot machine
        slot_msg = await bot.send_dice(call.message.chat.id, emoji="🎰")
        slot_val = slot_msg.dice.value

        # Telegram slot jackpot value is 64
        if slot_val == 64:
            reward = cost * 5
            update_balance(user_id, reward)
            res = f"🎰 **JACKPOT!!** You hit 777! You WON *+{reward}* points! 🚨🎉"
        elif slot_val in [1, 22, 43]:
            update_balance(user_id, cost)
            res = f"🎰 **Match!** You WON *+{cost}* points! ✨"
        else:
            update_balance(user_id, -cost)
            res = f"🎰 No match. You lost *-{cost}* points."

        await bot.send_message(call.message.chat.id, res, parse_mode="Markdown")
        await bot.answer_callback_query(call.id)

if __name__ == "__main__":
    import asyncio
    print("Casino Boost Bot started successfully...")
    asyncio.run(bot.polling(non_stop=True))
