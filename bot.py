# Telegram bot ለመስራት የሚያስፈልጉ ነገሮችን እናስገባለን
import logging
import time
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# የቦትዎን ቶክን (API Token) እዚህ ያስገቡ
BOT_TOKEN = "8000781039:AAFq76vrFtgXbwSp1xulo-lyuUhGepbhWE4"

# ቋሚ እሴቶችን እናስቀምጥ
BONUS_AMOUNT = 0.0079532
BONUS_COOLDOWN = 30  # በሰከንድ
REFERRAL_BONUS = 2.79

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

# /start ኮማንድ ሲሰራ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    setup_user_data(context) # ለመጀመሪያ ጊዜ ከሆነ የተጠቃሚውን ዳታ ያዘጋጃል
    keyboard = [
        [KeyboardButton("Mining")],
        [KeyboardButton("Balance"), KeyboardButton("bonus"), KeyboardButton("task")],
        [KeyboardButton("about us")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    user = update.effective_user
    await update.message.reply_html(
        f"ሠላም {user.mention_html()}!\n\nወደ ቦቱ እንኳን በደህና መጡ። ከታች ካሉት አማራጮች ይምረጡ።",
        reply_markup=reply_markup
    )

# ከታች ያሉትን ዋና ቁልፎች ሲጫኑ የሚሰራ
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    setup_user_data(context) # ተጠቃሚው ዳታ እንዳለው ያረጋግጣል
    button_text = update.message.text
    user = update.effective_user
    
    # "Mining" ሲጫን
    if button_text == "Mining":
        # ... (የ Mining ፕላኖች ኮድ ምንም አልተለወጠም)
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
    
    # "Balance" ሲጫን
    elif button_text == "Balance":
        user_balance = context.user_data.get('balance', 0.0)
        referral_count = context.user_data.get('referral_count', 0)
        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start={user.id}"
        
        balance_text = f"""📊 *የእርስዎ የሂሳብ መረጃ*

👤 *ስም:* {user.first_name}
🆔 *የቴሌግራም ID:* `{user.id}`
---
💰 *ቀሪ ሂሳብ:* `{user_balance:.8f} USDT`
👥 *የጋበዟቸው ሰዎች:* `{referral_count}`
🎁 *የግብዣ ጉርሻ:* `{REFERRAL_BONUS} USDT` (ለአንድ ሰው)

🔗 *የእርስዎ የግል መጋበዣ ሊንክ:*
`{referral_link}`"""
        keyboard = [
            [InlineKeyboardButton("💵 ገንዘብ አስገባ (Deposit)", callback_data='deposit')],
            [InlineKeyboardButton("📤 ገንዘብ አውጣ (Withdraw)", callback_data='withdraw')]
        ]
        await update.message.reply_text(balance_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    # "bonus" ሲጫን
    elif button_text == "bonus":
        last_claim_time = context.user_data.get('last_claim_time', 0)
        current_time = time.time()
        time_passed = current_time - last_claim_time
        
        if time_passed >= BONUS_COOLDOWN:
            bonus_text = f"✨ የእርስዎ ጉርሻ ዝግጁ ነው! ✨\n\n'Claim' የሚለውን ቁልፍ በመጫን የ `{BONUS_AMOUNT}` USDT ተሸላሚ ይሁኑ።"
            keyboard = [[InlineKeyboardButton("Claim Bonus 💰", callback_data='claim_bonus')]]
            await update.message.reply_text(bonus_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        else:
            remaining_time = int(BONUS_COOLDOWN - time_passed)
            bonus_text = f"⏳ እባክዎ ይጠብቁ ⏳\n\nየሚቀጥለውን ጉርሻዎን ለመውሰድ ገና `{remaining_time}` ሰከንዶች ይቀሩዎታል።"
            await update.message.reply_text(bonus_text, parse_mode='Markdown')

    # "task" ሲጫን
    elif button_text == "task":
        task_text = "እባክዎ ከታች ካሉት ተግባራት አንዱን ይምረጡ።"
        keyboard = [
            [InlineKeyboardButton("👥 ጓደኛ ይጋብዙ (Invite Friend)", callback_data='invite_friend')],
            [InlineKeyboardButton("📝 ዕለታዊ ተግባራት (Daily Tasks)", callback_data='daily_tasks')]
        ]
        await update.message.reply_text(task_text, reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif button_text == "about us":
        await update.message.reply_text("ስለ እኛ መረጃ... ℹ️")

# ከመልዕክት ስር ያሉትን (Inline) ቁልፎች ሲጫኑ የሚሰራ
async def inline_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    setup_user_data(context) # ዳታ መኖሩን እናረጋግጥ
    user = query.from_user

    # "ጓደኛ ይጋብዙ" ሲጫን
    if query.data == 'invite_friend':
        referral_count = context.user_data.get('referral_count', 0)
        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start={user.id}"
        invite_text = f"""🚀 *ገቢዎን ያሳድጉ!* 🚀

ጓደኞችዎን በመጋበዝ ከእኛ ጋር ያትርፉ። በእርስዎ የግል ሊንክ አማካኝነት ቦቱን ለሚቀላቀል እያንዳንዱ ሰው `{REFERRAL_BONUS} USDT` የጉርሻ ክፍያ ያገኛሉ።

🔗 *የእርስዎ ሊንክ:*
`{referral_link}`

👥 *እስካሁን የጋበዟቸው ሰዎች ብዛት:* `{referral_count}`

ሊንኩን ኮፒ በማድረግ ለወዳጅ ዘመድዎ ያጋሩ!"""
        await query.message.reply_text(invite_text, parse_mode='Markdown')
    
    # "Claim Bonus" ሲጫን
    elif query.data == 'claim_bonus':
        last_claim_time = context.user_data.get('last_claim_time', 0)
        current_time = time.time()
        
        if current_time - last_claim_time >= BONUS_COOLDOWN:
            context.user_data['balance'] += BONUS_AMOUNT
            context.user_data['last_claim_time'] = current_time
            new_balance = context.user_data['balance']
            
            success_text = f"🎉 *እንኳን ደስ አለዎት!* 🎉\n\n`{BONUS_AMOUNT:.8f} USDT` ወደ ሂሳብዎ ተጨምሯል።\n\n*አዲሱ ቀሪ ሂሳብዎ:* `{new_balance:.8f} USDT`"
            await query.edit_message_text(text=success_text, parse_mode='Markdown')
        else:
            await query.edit_message_text(text="❌ ይህን ጉርሻ አስቀድመው ወስደዋል! እባክዎ የሚቀጥለውን ጊዜ ይጠብቁ።")
    
    # ለሌሎች ቁልፎች...
    elif query.data.startswith('upgrade_vip_'):
        plan_name = query.data.replace('upgrade_','').upper(); await query.message.reply_text(f"የ {plan_name} ፕላንን ለማሻሻል ወኪላችንን ያግኙ።\n\nያግኙን: @የእርስዎ_የእርዳታ_ስም")
    elif query.data == 'deposit': await query.message.reply_text("ገንዘብ ለማስገባት ወኪላችንን ያግኙ: @የእርስዎ_የእርዳታ_ስም")
    elif query.data == 'withdraw': await query.message.reply_text("ገንዘብ ለማውጣት ወኪላችንን ያግኙ: @የእርስዎ_የእርዳታ_ስም")
    elif query.data == 'daily_tasks': await query.message.reply_text("ለዛሬ የተሰጡ ተግባራት ዝርዝር በቅርቡ ይጫናል።")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
    application.add_handler(CallbackQueryHandler(inline_button_handler))
    application.run_polling()

if __name__ == '__main__':
    main()
