import os
import random


# Load Token from Environment Variables
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:

# In-memory storage for user balances
user_balances = {}

def get_balance(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = 1000  # Default starting bonus points
    return user_balances[user_id]

# --- KEYBOARDS (KHMER) ---

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_casino = types.InlineKeyboardButton("🎰 កាស៊ីណូ និងហ្គេម", callback_data="menu_casino")
    btn_boost = types.InlineKeyboardButton("🚀 ប៊ូសឆានែល (Boost)", callback_data="menu_boost")
    btn_balance = types.InlineKeyboardButton("💰 សមតុល្យរបស់ខ្ញុំ", callback_data="check_balance")
    btn_help = types.InlineKeyboardButton("❓ ជំនួយ", callback_data="menu_help")
    markup.add(btn_casino, btn_boost, btn_balance, btn_help)
    return markup

def casino_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_slots = types.InlineKeyboardButton("🎰 លេងស្លត (Slots)", callback_data="game_slots")
    btn_dice = types.InlineKeyboardButton("🎲បោះគ្រាប់ឡុកឡាក់", callback_data="game_dice")
    btn_coin = types.InlineKeyboardButton("🪙 ទាយកាក់", callback_data="game_coin")
    btn_back = types.InlineKeyboardButton("⬅️ ត្រឡប់ក្រោយ", callback_data="main_menu")
    markup.add(btn_slots, btn_dice, btn_coin, btn_back)
    return markup

def boost_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_boost_info = types.InlineKeyboardButton("⭐ ព័ត៌មានអត្ថប្រយោជន៍ Boost", callback_data="boost_info")
    btn_claim_reward = types.InlineKeyboardButton("🎁 ដកប្រាក់រង្វាន់ Boost (១០០ ពិន្ទុ)", callback_data="claim_boost")
    btn_back = types.InlineKeyboardButton("⬅️ ត្រឡប់ក្រោយ", callback_data="main_menu")
    markup.add(btn_boost_info, btn_claim_reward, btn_back)
    return markup

# --- COMMAND HANDLERS ---

@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    text = (
        f"👋 សូមស្វាគមន៍មកកាន់ **Casino & Boost Hub**, {message.from_user.first_name}!\n\n"
        f"💰 **សមតុល្យបច្ចុប្បន្ន៖** `{balance}` ពិន្ទុ\n"
        "សូមជ្រើសរើសជម្រើសខាងក្រោមដើម្បីលេងហ្គេម ឬប៊ូសសហគមន៍របស់អ្នក៖"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())

# --- CALLBACK QUERY HANDLERS ---

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    balance = get_balance(user_id)

    if call.data == "main_menu":
        bot.edit_message_text(
            f"🏠 **ម៉ឺនុយដើម**\n💰 **សមតុល្យបច្ចុប្បន្ន៖** `{balance}` ពិន្ទុ",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

    elif call.data == "menu_casino":
        bot.edit_message_text(
            "🎰 **តំបន់កាស៊ីណូ**\nសូមជ្រើសរើសហ្គេមខ្នាតតូចខាងក្រោមដើម្បីភ្នាល់ និងឈ្នះពិន្ទុ!",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode="Markdown",
            reply_markup=casino_menu()
        )

    elif call.data == "menu_boost":
        bot.edit_message_text(
            "🚀 **តំបន់ Telegram Channel Boost**\n\n"
            "ប៊ូសសហគមន៍របស់អ្នកដើម្បីដោះសោ Custom Emojis, Audio Messages និង Stories!",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode="Markdown",
            reply_markup=boost_menu()
        )

    elif call.data == "check_balance":
        bot.answer_callback_query(call.id, f"💰 សមតុល្យ: {balance} ពិន្ទុ", show_alert=True)

    # --- GAMES LOGIC ---
    elif call.data == "game_slots":
        bet = 50
        if balance < bet:
            bot.answer_callback_query(call.id, "❌ ពិន្ទុមិនគ្រាន់ទេ! ត្រូវការ ៥០ ពិន្ទុ។", show_alert=True)
            return

        user_balances[user_id] -= bet
        msg = bot.send_dice(chat_id, emoji="🎰")
        val = msg.dice.value

        if val == 64:
            reward = 500
            user_balances[user_id] += reward
            bot.send_message(chat_id, f"🎉 **ជេកផត (JACKPOT)!** អ្នកឈ្នះ `{reward}` ពិន្ទុ! 🎰", parse_mode="Markdown")
        elif val in [1, 22, 43]:
            reward = 100
            user_balances[user_id] += reward
            bot.send_message(chat_id, f"✨ ឈ្នះធំ! អ្នកឈ្នះ `{reward}` ពិន្ទុ!", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, f"❌ អ្នកបានចាញ់ `{bet}` ពិន្ទុ។ សូមព្យាយាមម្តងទៀត!", parse_mode="Markdown")

    elif call.data == "game_dice":
        bet = 20
        if balance < bet:
            bot.answer_callback_query(call.id, "❌ ពិន្ទុមិនគ្រាន់ទេ! ត្រូវការ ២០ ពិន្ទុ។", show_alert=True)
            return

        user_balances[user_id] -= bet
        msg = bot.send_dice(chat_id, emoji="🎲")
        val = msg.dice.value

        if val >= 4:
            reward = bet * 2
            user_balances[user_id] += reward
            bot.send_message(chat_id, f"🎲 ចេញលេខ `{val}`! អ្នកឈ្នះ `{reward}` ពិន្ទុ!", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, f"🎲 ចេញលេខ `{val}`។ អ្នកបានចាញ់ `{bet}` ពិន្ទុ។", parse_mode="Markdown")

    elif call.data == "game_coin":
        bet = 25
        if balance < bet:
            bot.answer_callback_query(call.id, "❌ ពិន្ទុមិនគ្រាន់ទេ! ត្រូវការ ២៥ ពិន្ទុ។", show_alert=True)
            return
        
        outcome = random.choice(["Heads", "Tails"])
        if outcome == "Heads":
            reward = 50
            user_balances[user_id] += reward
            bot.send_message(chat_id, f"🪙 លទ្ធផល៖ **ក្បាល (Heads)**! អ្នកឈ្នះ `{reward}` ពិន្ទុ!", parse_mode="Markdown")
        else:
            user_balances[user_id] -= bet
            bot.send_message(chat_id, f"🪙 លទ្ធផល៖ **សॉ (Tails)**! អ្នកបានចាញ់ `{bet}` ពិន្ទុ។", parse_mode="Markdown")

    # --- BOOST LOGIC ---
    elif call.data == "boost_info":
        info_text = (
            "🚀 **របៀប Boost Telegram Channel៖**\n\n"
            "១. ចូលទៅកាន់ម៉ឺនុយឆានែលរបស់អ្នក។\n"
            "២. ចុចពាក្យ **Boost**។\n"
            "៣. ជួយឆានែលរបស់អ្នកឡើងកម្រិតខ្ពស់ដើម្បីដោះសោរង្វាន់ពិសេស!"
        )
        bot.send_message(chat_id, info_text, parse_mode="Markdown")

    elif call.data == "claim_boost":
        user_balances[user_id] += 100
        bot.answer_callback_query(call.id, "🎁 ទទួលបានប្រាក់រង្វាន់ ១០០ ពិន្ទុជោគជ័យ!", show_alert=True)

    elif call.data == "menu_help":
        help_text = (
            "❓ **ជំនួយ និងរបៀបលេង៖**\n\n"
            "- ចុចលើ **កាស៊ីណូ និងហ្គេម** ដើម្បីលេង Slots, Dice និង Coin Flip។\n"
            "- ឈ្នះពិន្ទុបន្ថែមតាមរយៈការទស្សន៍ទាយលទ្ធផលហ្គេម!\n"
            "- ប្រើប្រាស់ពិន្ទុរបស់អ្នកដើម្បីរីករាយជាមួយសសសភេសជ្ជៈសហគមន៍។"
        )
        bot.send_message(chat_id, help_text, parse_mode="Markdown")

if __name__ == "__main__":
    logging.info("Bot starting with Khmer locale...")
    bot.infinity_polling(skip_pending_updates=True)
