# Telegram bot ለመስራት የሚያስፈልጉ ነገሮችን እናስገባለን
import logging
import time
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    PicklePersistence
)

# የቦትዎን ቶክን (API Token) እዚህ ያስገቡ
BOT_TOKEN = "8000781039:AAFq76vrFtgXbwSp1xulo-lyuUhGepbhWE4"

# ቋሚ እሴቶችን እናስቀምጥ
BONUS_AMOUNT = 0.0079532
BONUS_COOLDOWN = 30  # በሰከንድ
REFERRAL_BONUS_INVITER = 3.47  # ለጋባዥ
REFERRAL_BONUS_INVITEE = 2.00  # ለተጋባዥ
JOINING_REWARD = 2.50  # ለአዲስ ተጠቃሚ
BONUS_CODE_AMOUNT = 86.00  # የቦነስ ኮድ መጠን
BONUS_CODE = "UBVCXTH"  # የቦነስ ኮድ

# የቻናል ID
CHANNEL_ID = -1002904187204

# Wallet Addresses
WALLET_BEP20 = "0x39bAAe6d93fD0cD1D57A41D46f085D6c54Ba72Ab"
WALLET_TRC20 = "TJQ83XXUhR1eqA58DHiAqn7KNuaYQMEy8k"

# ሎጊንግ (logging) እናዘጋጃለን - ስህተቶችን ለማሳየት ይጠቅማል
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ለእያንዳንዱ ተጠቃሚ የመጀመሪያ ዳታ ማዘጋጀት
def setup_user_data(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault('balance', 0.0)
    context.user_data.setdefault('last_claim_time', 0)
    context.user_data.setdefault('referral_count', 0)
    context.user_data.setdefault('bonus_code_used', False)
    context.user_data.setdefault('joined_channel', False)

# /start ኮማንድ ሲሰራ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    setup_user_data(context)
    
    # የግብዣ ኮድ ማረጋገጫ
    if context.args:
        try:
            referrer_id = int(context.args[0])
            # ራስን ማጋበዝ እንዳልተቻለ እና አዲስ ተጠቃሚ መሆኑን ማረጋገጫ
            if referrer_id != user_id and 'is_new_user' not in context.user_data:
                context.user_data['is_new_user'] = True # ዳግም እንዳይሰራ ለማድረግ
                
                # ለአዲስ ተጠቃሚ የመግቢያ እና የግብዣ ጉርሻ
                context.user_data['balance'] += JOINING_REWARD + REFERRAL_BONUS_INVITEE
                
                # ለጋባዥ ጉርሻ መጨመር እና ማሳወቅ
                referrer_data = context.application.user_data[referrer_id]
                referrer_data.setdefault('balance', 0.0)
                referrer_data.setdefault('referral_count', 0)
                referrer_data['balance'] += REFERRAL_BONUS_INVITER
                referrer_data['referral_count'] += 1
                
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text=f"🎉 **አዲስ ተጠቃሚ በግብዣዎ ተመዝግቧል!** 🎉\n\n"
                         f"👤 አዲስ ተጠቃሚ {update.effective_user.first_name} በግብዣ ሊንክዎ ተጠቅሟል።\n"
                         f"💰 **+{REFERRAL_BONUS_INVITER} USDT** ወደ ሂሳብዎ ተጨምሯል።\n"
                         f"🌟 አጠቃላይ የጋበዟቸው ሰዎች: {referrer_data['referral_count']}"
                )
        except (ValueError, KeyError) as e:
            logging.error(f"የሪፈራል ሂደት ላይ ስህተት ተፈጥሯል: {e}")

    keyboard = [
        [KeyboardButton("⛏️ Mining")],
        [KeyboardButton("💰 Balance"), KeyboardButton("🎁 Bonus"), KeyboardButton("📋 Task")],
        [KeyboardButton("ℹ️ About Us")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    user = update.effective_user
    await update.message.reply_html(
        f"ሠላም {user.mention_html()}!\n\nወደ ቦቱ እንኳን በደህና መጡ። ከታች ካሉት አማራጮች ይምረጡ።",
        reply_markup=reply_markup
    )

# ዋናዎቹን ቁልፎች ሲጫኑ
async def main_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    setup_user_data(context)
    button_text = update.message.text
    
    if button_text == "⛏️ Mining":
        text5="""👑 *VIP 5*
*ዋጋ:* 750 USDT
*ዕለታዊ ገቢ:* 350 USDT
*የቆይታ ጊዜ:* 30 ቀናት
---
*አጠቃላይ ገቢ:* 10500 USDT
*የተጣራ ትርፍ:* 9750 USDT"""; keyboard5=[[InlineKeyboardButton("Upgrade to VIP 5 ⬆️",callback_data='upgrade_vip_5')]]; await update.message.reply_text(text5,reply_markup=InlineKeyboardMarkup(keyboard5),parse_mode='Markdown')
        text4="""✨ *VIP 4*
*ዋጋ:* 300 USDT
*ዕለታዊ ገቢ:* 130 USDT
*የቆይታ ጊዜ:* 20 ቀናት
---
*አጠቃላይ ገቢ:* 2600 USDT
*የተጣራ ትርፍ:* 2300 USDT"""; keyboard4=[[InlineKeyboardButton("Upgrade to VIP 4 ⬆️",callback_data='upgrade_vip_4')]]; await update.message.reply_text(text4,reply_markup=InlineKeyboardMarkup(keyboard4),parse_mode='Markdown')
        text3="""🌟 *VIP 3*
*ዋጋ:* 120 USDT
*ዕለታዊ ገቢ:* 55 USDT
*የቆይታ ጊዜ:* 15 ቀናት
---
*አጠቃላይ ገቢ:* 825 USDT
*የተጣራ ትርፍ:* 705 USDT"""; keyboard3=[[InlineKeyboardButton("Upgrade to VIP 3 ⬆️",callback_data='upgrade_vip_3')]]; await update.message.reply_text(text3,reply_markup=InlineKeyboardMarkup(keyboard3),parse_mode='Markdown')
        text2="""⚡️ *VIP 2*
*ዋጋ:* 50 USDT
*ዕለታዊ ገቢ:* 25 USDT
*የቆይታ ጊዜ:* 10 ቀናት
---
*አጠቃላይ ገቢ:* 250 USDT
*የተጣራ ትርፍ:* 200 USDT"""; keyboard2=[[InlineKeyboardButton("Upgrade to VIP 2 ⬆️",callback_data='upgrade_vip_2')]]; await update.message.reply_text(text2,reply_markup=InlineKeyboardMarkup(keyboard2),parse_mode='Markdown')
        text1="""🔸 *VIP 1*
*ዋጋ:* 15 USDT
*ዕለታዊ ገቢ:* 7.97 USDT
*የቆይታ ጊዜ:* 7 ቀናት
---
*አጠቃላይ ገቢ:* 55.79 USDT
*የተጣራ ትርፍ:* 40.79 USDT"""; keyboard1=[[InlineKeyboardButton("Upgrade to VIP 1 ⬆️",callback_data='upgrade_vip_1')]]; await update.message.reply_text(text1,reply_markup=InlineKeyboardMarkup(keyboard1),parse_mode='Markdown')
    
    elif button_text == "💰 Balance":
        await show_balance_menu(update, context)

    elif button_text == "🎁 Bonus":
        await show_bonus_menu(update.message)

    elif button_text == "📋 Task":
        task_text = "እባክዎ ከታች ካሉት ተግባራት አንዱን ይምረጡ።"
        keyboard = [
            [InlineKeyboardButton("👥 ጓደኛ ይጋብዙ (Invite Friend)", callback_data='invite_friend')],
            [InlineKeyboardButton("📝 ዕለታዊ ተግባራት (Daily Tasks)", callback_data='daily_tasks')]
        ]
        await update.message.reply_text(task_text, reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif button_text == "ℹ️ About Us":
        await update.message.reply_text("ስለ እኛ መረጃ... ℹ️")

async def show_balance_menu(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    user = update_or_query.effective_user
    user_balance = context.user_data.get('balance', 0.0)
    referral_count = context.user_data.get('referral_count', 0)
    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={user.id}"
    
    balance_text = f"""📊 *የእርስዎ የሂሳብ መረጃ*

👤 *ስም:* {user.first_name}
🆔 *የቴሌግራም ID:* `{user.id}`
---
💰 *ቀሪ ሂሳብ:* `{user_balance:.2f} USDT`
👥 *የጋበዟቸው ሰዎች:* `{referral_count}`
🎁 *የግብዣ ጉርሻ:* `{REFERRAL_BONUS_INVITER} USDT` (ለጋባዥ)

🔗 *የእርስዎ የግል መጋበዣ ሊንክ:*
`{referral_link}`"""
    keyboard = [
        [InlineKeyboardButton("💵 ገንዘብ አስገባ (Deposit)", callback_data='deposit')],
        [InlineKeyboardButton("📤 ገንዘብ አውጣ (Withdraw)", callback_data='withdraw')]
    ]
    
    if hasattr(update_or_query, 'message') and update_or_query.message: # CallbackQuery
        await update_or_query.message.edit_text(balance_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else: # Message
        await update_or_query.message.reply_text(balance_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_bonus_menu(message):
    bonus_text = """🎁 **የጉርሻ ማዕከል** 🎁

ከታች ካሉት የጉርሻ አማራጮች ይምረጡ፡"""
    keyboard = [
        [InlineKeyboardButton("💰 ዕለታዊ ጉርሻ ይውሰዱ", callback_data='claim_bonus')],
        [InlineKeyboardButton("🔑 የቦነስ ኮድ ያስገቡ", callback_data='enter_bonus_code')],
        [InlineKeyboardButton("📢 ወደ ቻናል ይቀላቀሉ", callback_data='join_channel')]
    ]
    await message.edit_text(bonus_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# የቦነስ ኮድ ማስገባት ሂደት
async def handle_bonus_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = update.effective_user.id
    
    context.user_data['waiting_for_bonus_code'] = False # Reset state
    
    if user_message.upper() == BONUS_CODE:
        if not context.user_data.get('bonus_code_used', False):
            context.user_data['balance'] += BONUS_CODE_AMOUNT
            context.user_data['bonus_code_used'] = True
            
            success_message = f"""🎉 **እንኳን ደስ አለዎት!** 🎉
✅ **የቦነስ ኮድ በትክክል ገብቷል!**
💰 **+{BONUS_CODE_AMOUNT} USDT** ወደ ሂሳብዎ ተጨምሯል።
🌟 አዲስ ቀሪ ሂሳብዎ: **{context.user_data['balance']:.2f} USDT**"""
            
            await update.message.reply_text(success_message, parse_mode='Markdown')
            
            # ወደ ቻናል መልዕክት መላክ
            try:
                channel_message = f"""🎊 **አዲስ የቦነስ ኮድ ተጠቅሟል!** 🎊
👤 ተጠቃሚ: {update.effective_user.first_name}
🆔 ID: {user_id}
💰 የተገኘ ጉርሻ: {BONUS_CODE_AMOUNT} USDT"""
                await context.bot.send_message(chat_id=CHANNEL_ID, text=channel_message)
            except Exception as e:
                logging.error(f"ወደ ቻናል መልዕክት ላክ አልተቻለም: {e}")
        else:
            await update.message.reply_text("❌ **ይህን የቦነስ ኮድ አስቀድመው ተጠቅመዋል!**")
    else:
        await update.message.reply_text("❌ **የተሳሳተ የቦነስ ኮድ!**\n\nእባክዎ እንደገና ይሞክሩ ወይም /cancel ብለው ይውጡ።")

async def show_deposit_options(query):
    deposit_text = "💱 **የክፍያ መረብ ይምረጡ**\n\nእባክዎ ገንዘብ ለማስገባት የሚፈልጉበትን የUSDT መረብ (network) ይምረጡ።"
    keyboard = [
        [InlineKeyboardButton("USDT (BEP20)", callback_data='deposit_bep20')],
        [InlineKeyboardButton("USDT (TRC20)", callback_data='deposit_trc20')],
        [InlineKeyboardButton("⬅️ უკან", callback_data='back_to_balance')]
    ]
    await query.message.edit_text(deposit_text, reply_markup=InlineKeyboardMarkup(keyboard))


# ከመልዕክት ስር ያሉትን (Inline) ቁልፎች ሲጫኑ የሚሰራ
async def inline_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    setup_user_data(context)
    user = query.from_user

    # Navigation
    if query.data == 'back_to_balance':
        await show_balance_menu(query, context)
        return
    elif query.data == 'back_to_bonus':
        await show_bonus_menu(query.message)
        return

    # Main functionality
    if query.data == 'invite_friend':
        referral_count = context.user_data.get('referral_count', 0)
        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start={user.id}"
        
        invite_text = f"""🚀 **ገቢዎን ያሳድጉ! ጓደኞችዎን ይጋብዙ!** 🚀
💰 **ለጋባዥ ጉርሻ:** {REFERRAL_BONUS_INVITER} USDT
🎁 **ለተጋባዥ ጉርሻ:** {REFERRAL_BONUS_INVITEE} USDT
🔗 **የእርስዎ ልዩ የግብዣ ሊንክ:**
`{referral_link}`
👥 **እስካሁን የጋበዟቸው ሰዎች ብዛት:** {referral_count}
✨ **ብዙ ያጋብዙ ብዙ ያትሉ!**"""
        await query.message.reply_text(invite_text, parse_mode='Markdown')
    
    elif query.data == 'claim_bonus':
        last_claim_time = context.user_data.get('last_claim_time', 0)
        current_time = time.time()
        
        if current_time - last_claim_time >= BONUS_COOLDOWN:
            context.user_data['balance'] += BONUS_AMOUNT
            context.user_data['last_claim_time'] = current_time
            new_balance = context.user_data['balance']
            
            success_text = f"🎉 **እንኳን ደስ አለዎት!** 🎉\n\n`{BONUS_AMOUNT:.8f} USDT` ወደ ሂሳብዎ ተጨምሯል።\n\n*አዲሱ ቀሪ ሂሳብዎ:* `{new_balance:.8f} USDT`"
            keyboard = [[InlineKeyboardButton("⬅️ უკან", callback_data='back_to_bonus')]]
            await query.message.edit_text(text=success_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            remaining_time = int(BONUS_COOLDOWN - (current_time - last_claim_time))
            await query.answer(text=f"❌ እባክዎ ይጠብቁ! {remaining_time} ሰከንዶች ይቀራሉ።", show_alert=True)
    
    elif query.data == 'enter_bonus_code':
        if context.user_data.get('bonus_code_used', False):
            await query.answer(text="❌ ይህን የቦነስ ኮድ አስቀድመው ተጠቅመዋል!", show_alert=True)
        else:
            await query.message.reply_text("🔑 **የቦነስ ኮድ ያስገቡ**\n\nእባክዎ የቦነስ ኮድዎን ይጻፉ። ለማቋረጥ /cancel ብለው ይጻፉ።")
            context.user_data['waiting_for_bonus_code'] = True
    
    elif query.data == 'join_channel':
        if context.user_data.get('joined_channel', False):
            await query.answer(text="✅ አስቀድመው ቻናላችንን ተቀላቅለዋል!", show_alert=True)
        else:
            channel_message = f"""📢 **ወደ ቻናላችን ይቀላቀሉ እና ልዩ ጉርሻዎችን ያግኙ!**"""
            keyboard = [
                [InlineKeyboardButton("ቻናሉን ይቀላቀሉ 🔗", url=f"https://t.me/your_channel_username")], # TODO: የቻናል ሊንክ ያስገቡ
                [InlineKeyboardButton("⬅️ უკან", callback_data='back_to_bonus')]
            ]
            await query.message.edit_text(channel_message, reply_markup=InlineKeyboardMarkup(keyboard))
            context.user_data['joined_channel'] = True # For simplicity, we assume they join
    
    elif query.data.startswith('upgrade_vip_') or query.data == 'deposit':
        await show_deposit_options(query)

    elif query.data == 'deposit_bep20':
        text = f"""💰 **USDT (BEP20) ገንዘብ ማስገቢያ**
        
እባክዎ የሚፈልጉትን የUSDT መጠን ከታች ወዳለው የኪስ አድራሻ ይላኩ።

**አድራሻ:**
`{WALLET_BEP20}`
`(ለመቅዳት ይጫኑት)`

⚠️ **ማሳሰቢያ:** ወደዚህ አድራሻ **USDT BEP20** ብቻ ይላኩ። ሌላ አይነት ገንዘብ መላክ ወደማይመለስ ኪሳራ ይዳርጋል።

ክፍያውን ከፈጸሙ በኋላ፣ የስክሪንሻቱን (screenshot) ፎቶ እና የቴሌግራም IDዎን ለወኪላችን ይላኩ።"""
        keyboard = [[InlineKeyboardButton("⬅️ უკან", callback_data='deposit')]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'deposit_trc20':
        text = f"""💰 **USDT (TRC20) ገንዘብ ማስገቢያ**

እባክዎ የሚፈልጉትን የUSDT መጠን ከታች ወዳለው የኪስ አድራሻ ይላኩ።

**አድራሻ:**
`{WALLET_TRC20}`
`(ለመቅዳት ይጫኑት)`

⚠️ **ማሳሰቢያ:** ወደዚህ አድራሻ **USDT TRC20** ብቻ ይላኩ። ሌላ አይነት ገንዘብ መላክ ወደማይመለስ ኪሳራ ይዳርጋል።

ክፍያውን ከፈጸሙ በኋላ፣ የስክሪንሻቱን (screenshot) ፎቶ እና የቴሌግራም IDዎን ለወኪላችን ይላኩ።"""
        keyboard = [[InlineKeyboardButton("⬅️ უკან", callback_data='deposit')]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'withdraw': 
        await query.message.reply_text("ገንዘብ ለማውጣት ወኪላችንን ያግኙ: @የእርስዎ_የእርዳታ_ስም") # TODO: የእርዳታ ስም ያስገቡ
    elif query.data == 'daily_tasks': 
        await query.message.reply_text("ለዛሬ የተሰጡ ተግባራት ዝርዝር በቅርቡ ይጫናል።")

# መልዕክት ሂደት
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # የቦነስ ኮድ በመጠባበቅ ላይ ከሆነ
    if context.user_data.get('waiting_for_bonus_code', False):
        if update.message.text == '/cancel':
            context.user_data['waiting_for_bonus_code'] = False
            await update.message.reply_text("የቦነስ ኮድ የማስገባት ሂደት ተቋርጧል።")
        else:
            await handle_bonus_code_input(update, context)
    # ካልሆነ እንደ ዋና ቁልፍ እንቆጥረዋለን
    else:
        await main_button_handler(update, context)

def main() -> None:
    # ዳታን በፋይል ለማስቀመጥ (Persistence)
    persistence = PicklePersistence(filepath="bot_user_data")
    
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(inline_button_handler))
    
    application.run_polling()

if __name__ == '__main__':
    main()
