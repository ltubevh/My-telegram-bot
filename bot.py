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
REFERRAL_BONUS_INVITER = 3.47  # ለጋባዥ
REFERRAL_BONUS_INVITEE = 2.00  # ለተጋባዥ
JOINING_REWARD = 2.50  # ለአዲስ ተጠቃሚ
BONUS_CODE_AMOUNT = 86.00  # የቦነስ ኮድ መጠን
BONUS_CODE = "UBVCXTH"  # የቦነስ ኮድ

# የቻናል ID
CHANNEL_ID = -1002904187204

# የዊይለት አድራሻዎች
USDT_BEP20 = "0x39bAAe6d93fD0cD1D57A41D46f085D6c54Ba72Ab"
USDT_TRC20 = "TJQ83XXUhR1eqA58DHiAqn7KNuaYQMEy8k"

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
    setup_user_data(context)
    
    # የግብዣ ኮድ ማረጋገጫ
    if context.args:
        referrer_id = context.args[0]
        if referrer_id.isdigit():
            referrer_id = int(referrer_id)
            current_user_id = update.effective_user.id
            
            # ራስን ማጋበዝ እንዳልተቻለ ማረጋገጫ
            if referrer_id != current_user_id:
                # ለአዲስ ተጠቃሚ ጉርሻ
                context.user_data['balance'] += JOINING_REWARD
                
                # ለጋባዥ ጉርሻ መጨመር
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎉 **አዲስ ተጠቃሚ በግብዣዎ ተጠቅሟል!** 🎉\n\n"
                             f"👤 አዲስ ተጠቃሚ በግብዣ ሊንክዎ ተጠቅሟል።\n"
                             f"💰 **+{REFERRAL_BONUS_INVITER} USDT** ወደ ሂሳብዎ ተጨምሯል።\n"
                             f"🌟 እንደዚህ አይነት ብዙ አዲስ ተጠቃሚዎችን ይጋብዙ ብዙ ያትሉ።"
                    )
                except Exception as e:
                    logging.error(f"ለጋባዥ መልዕክት ላክ አልተቻለም: {e}")

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

# /cancel ኮማንድ
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop('waiting_for_bonus_code', None)
    await update.message.reply_text("❌ **ምንም አይነት ሂደት ተሰርዟል!**\n\n🔙 ወደ ዋናው መንገድ ተመለስዎ።")

# የ Deposit ገፅ
async def show_deposit_page(update: Update, context: ContextTypes.DEFAULT_TYPE, from_vip: bool = False) -> None:
    deposit_text = """💵 **ገንዘብ አስገባ (Deposit)**

እባክዎ የሚፈልጉትን የኔትወርክ ዓይነት ይምረጡ፡"""

    keyboard = [
        [InlineKeyboardButton("USDT (BEP20)", callback_data='deposit_bep20')],
        [InlineKeyboardButton("USDT (TRC20)", callback_data='deposit_trc20')],
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
    ]
    
    if from_vip:
        deposit_text = f"""💵 **ገንዘብ አስገባ (Deposit) - ለ VIP ማሻሻል**

💰 የተመረጠዎትን የ VIP ፕላን ለማሟላት ገንዘብ ያስገቡ።

እባክዎ የሚፈልጉትን የኔትወርክ ዓይነት ይምረጡ፡"""
    
    if hasattr(update, 'message'):
        await update.message.reply_text(deposit_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.edit_message_text(deposit_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# የ BEP20 Deposit ዝርዝር
async def show_bep20_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bep20_text = f"""📥 **USDT (BEP20) Deposit**

🔗 **የዊይለት አድራሻ:**
`{USDT_BEP20}`

📋 **መመሪያዎች:**
1. ወደ ተጠቀሰው ዊይለት አድራሻ **USDT** ያስገቡ
2. **BEP20** ኔትወርክን ይምረጡ
3. የግብይት መለያ (TXID) ያስቀምጡ
4. ገንዘብዎ በ 10-30 ደቂቃ ውስጥ ይገኛል

⚠️ **ማስጠንቀቂያ:**
• ሌላ ኮይን አትላኩ
• ትክክለኛውን ኔትወርክ ያረጋግጡ
• ዝርዝር መረጃዎችን ያረጋግጡ

📞 ማንኛውም ችግር ካጋጠመዎት: @የእርስዎ_የእርዳታ_ስም"""

    keyboard = [
        [InlineKeyboardButton("🔙 Back to Deposit", callback_data='back_to_deposit')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
    ]
    
    await update.edit_message_text(bep20_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# የ TRC20 Deposit ዝርዝር
async def show_trc20_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trc20_text = f"""📥 **USDT (TRC20) Deposit**

🔗 **የዊይለት አድራሻ:**
`{USDT_TRC20}`

📋 **መመሪያዎች:**
1. ወደ ተጠቀሰው ዊይለት አድራሻ **USDT** ያስገቡ
2. **TRC20** ኔትወርክን ይምረጡ
3. የግብይት መለያ (TXID) ያስቀምጡ
4. ገንዘብዎ በ 2-5 ደቂቃ ውስጥ ይገኛል

✨ **ጥቅሞች:**
• ፈጣን የግብይት ፍጥነት
• ዝቅተኛ የግብይት ክፍያ
• ከፍተኛ የደህንነት ደረጃ

⚠️ **ማስጠንቀቂያ:**
• ሌላ ኮይን አትላኩ
• ትክክለኛውን ኔትወርክ ያረጋግጡ

📞 ማንኛውም ችግር ካጋጠመዎት: @የእርስዎ_የእርዳታ_ስም"""

    keyboard = [
        [InlineKeyboardButton("🔙 Back to Deposit", callback_data='back_to_deposit')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
    ]
    
    await update.edit_message_text(trc20_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ቦነስ ቁልፍ ሲጫን
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    setup_user_data(context)
    button_text = update.message.text
    user = update.effective_user
    
    if button_text == "Mining":
        # VIP ፕላኖችን ማሳየት
        text5="""👑 *VIP 5*
*ዋጋ:* 750 USDT
*ዕለታዊ ገቢ:* 350 USDT
*የቆይታ ጊዜ:* 30 ቀናት
---
*አጠቃላይ ገቢ:* 10500 USDT
*የተጣራ ትርፍ:* 9750 USDT"""
        keyboard5=[[InlineKeyboardButton("Upgrade to VIP 5 ⬆️",callback_data='upgrade_vip_5')]]
        await update.message.reply_text(text5,reply_markup=InlineKeyboardMarkup(keyboard5),parse_mode='Markdown')
        
        text4="""✨ *VIP 4*
*ዋጋ:* 300 USDT
*ዕለታዊ ገቢ:* 130 USDT
*የቆይታ ጊዜ:* 20 ቀናት
---
*አጠቃላይ ገቢ:* 2600 USDT
*የተጣራ ትርፍ:* 2300 USDT"""
        keyboard4=[[InlineKeyboardButton("Upgrade to VIP 4 ⬆️",callback_data='upgrade_vip_4')]]
        await update.message.reply_text(text4,reply_markup=InlineKeyboardMarkup(keyboard4),parse_mode='Markdown')
        
        text3="""🌟 *VIP 3*
*ዋጋ:* 120 USDT
*ዕለታዊ ገቢ:* 55 USDT
*የቆይታ ጊዜ:* 15 ቀናት
---
*አጠቃላይ ገቢ:* 825 USDT
*የተጣራ ትርፍ:* 705 USDT"""
        keyboard3=[[InlineKeyboardButton("Upgrade to VIP 3 ⬆️",callback_data='upgrade_vip_3')]]
        await update.message.reply_text(text3,reply_markup=InlineKeyboardMarkup(keyboard3),parse_mode='Markdown')
        
        text2="""⚡️ *VIP 2*
*ዋጋ:* 50 USDT
*ዕለታዊ ገቢ:* 25 USDT
*የቆይታ ጊዜ:* 10 ቀናት
---
*አጠቃላይ ገቢ:* 250 USDT
*የተጣራ ትርፍ:* 200 USDT"""
        keyboard2=[[InlineKeyboardButton("Upgrade to VIP 2 ⬆️",callback_data='upgrade_vip_2')]]
        await update.message.reply_text(text2,reply_markup=InlineKeyboardMarkup(keyboard2),parse_mode='Markdown')
        
        text1="""🔸 *VIP 1*
*ዋጋ:* 15 USDT
*ዕለታዊ ገቢ:* 7.97 USDT
*የቆይታ ጊዜ:* 7 ቀናት
---
*አጠቃላይ ገቢ:* 55.79 USDT
*የተጣራ ትርፍ:* 40.79 USDT"""
        keyboard1=[[InlineKeyboardButton("Upgrade to VIP 1 ⬆️",callback_data='upgrade_vip_1')]]
        await update.message.reply_text(text1,reply_markup=InlineKeyboardMarkup(keyboard1),parse_mode='Markdown')
    
    elif button_text == "Balance":
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
            [InlineKeyboardButton("📤 ገንዘብ አውጣ (Withdraw)", callback_data='withdraw')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
        ]
        await update.message.reply_text(balance_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif button_text == "bonus":
        bonus_text = """🎁 **የጉርሻ ማዕከል** 🎁

ከታች ካሉት የጉርሻ አማራጮች ይምረጡ፡"""

        keyboard = [
            [InlineKeyboardButton("💰 ዕለታዊ ጉርሻ ይውሰዱ", callback_data='claim_bonus')],
            [InlineKeyboardButton("🔑 የቦነስ ኮድ ያስገቡ", callback_data='enter_bonus_code')],
            [InlineKeyboardButton("📢 ወደ ቻናል ይቀላቀሉ", callback_data='join_channel')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
        ]
        await update.message.reply_text(bonus_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif button_text == "task":
        task_text = "እባክዎ ከታች ካሉት ተግባራት አንዱን ይምረጡ።"
        keyboard = [
            [InlineKeyboardButton("👥 ጓደኛ ይጋብዙ (Invite Friend)", callback_data='invite_friend')],
            [InlineKeyboardButton("📝 ዕለታዊ ተግባራት (Daily Tasks)", callback_data='daily_tasks')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
        ]
        await update.message.reply_text(task_text, reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif button_text == "about us":
        about_text = """ℹ️ **ስለ እኛ**

🌟 **እኛ እንግዳ አይደለንም!**
እኛ በመስክዎ ውስጥ ከሚገኙ ተጨቛኞች ጋር እየሰራን ያለን የቴሌግራም ቦት ነን።

🎯 **ራሳችንን የወሰንነው፡**
• ለተጠቃሚዎች ቀላል እና አስደሳች ተሞክሮ ለመፍጠር
• ግልጽነት እና አስተማማኝነት ለማረጋገጥ
• ለማንኛውም ጥያቄ ድጋፍ ለመስጠት

📞 **እንደዚህ ለማንኛውም ጥያቄ ያግኙን፡**
@የእርስዎ_የእርዳታ_ስም

✨ **እናመሰግናለን የቦታችንን ተጠቃሚ ስለሆኑ!**"""
        await update.message.reply_text(about_text, parse_mode='Markdown')

# የቦነስ ኮድ ማስገባት ሂደት
async def handle_bonus_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = update.effective_user.id
    
    if user_message.upper() == BONUS_CODE:
        if not context.user_data.get('bonus_code_used', False):
            context.user_data['balance'] += BONUS_CODE_AMOUNT
            context.user_data['bonus_code_used'] = True
            
            success_message = f"""🎉 **እንኳን ደስ አለዎት!** 🎉

✅ **የቦነስ ኮድ በትክክል ተገምግሟል!**

💰 **+{BONUS_CODE_AMOUNT} USDT** ወደ ሂሳብዎ ተጨምሯል።

🌟 አዲስ ቀሪ ሂሳብዎ: **{context.user_data['balance']:.2f} USDT**

🔔 ይህ የቦነስ ኮድ አንድ ጊዜ ብቻ ሊጠቀም ይችላል።"""

            # ወደ ቻናል መልዕክት መላክ
            channel_message = f"""🎊 **አዲስ የቦነስ ኮድ ተጠቅሟል!** 🎊

👤 ተጠቃሚ: {update.effective_user.first_name}
🆔 ID: {user_id}
💰 የተገኘ ጉርሻ: {BONUS_CODE_AMOUNT} USDT
🔑 ኮድ: {BONUS_CODE}

✨ እርስዎም ይህን ብርቱ ጉርሻ ለማግኘት ቦታችን ይቀላቀሉ!"""

            try:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=channel_message
                )
            except Exception as e:
                logging.error(f"ወደ ቻናል መልዕክት ላክ አልተቻለም: {e}")

            await update.message.reply_text(success_message, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ **ይህን የቦነስ ኮድ አስቀድመው ተጠቅመዋል!**\n\n🔔 እያንዳንዱ የቦነስ ኮድ አንድ ጊዜ ብቻ ሊጠቀም ይችላል።")
    else:
        await update.message.reply_text("❌ **የተሳሳተ የቦነስ ኮድ!**\n\nእባክዎ ትክክለኛውን የቦነስ ኮድ ያስገቡ።")

# ከመልዕክት ስር ያሉትን (Inline) ቁልፎች ሲጫኑ የሚሰራ
async def inline_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    setup_user_data(context)
    user = query.from_user

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

📢 **አግድም ሂደት:**
1. ሊንኩን ለወዳጅዎ ያጋሩ
2. ወዳጅዎ በሊንኩ ቦቱን ይቀላቀል
3. ወዳጅዎ **{JOINING_REWARD} USDT** የመግቢያ ጉርሻ ያገኛል
4. እርስዎ **{REFERRAL_BONUS_INVITER} USDT** ጉርሻ ያገኛሉ

✨ **ብዙ ያጋብዙ ብዙ ያትሉ!**"""

        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_tasks')],
            [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
        ]
        await query.edit_message_text(invite_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == 'claim_bonus':
        last_claim_time = context.user_data.get('last_claim_time', 0)
        current_time = time.time()
        
        if current_time - last_claim_time >= BONUS_COOLDOWN:
            context.user_data['balance'] += BONUS_AMOUNT
            context.user_data['last_claim_time'] = current_time
            new_balance = context.user_data['balance']
            
            success_text = f"🎉 **እንኳን ደስ አለዎት!** 🎉\n\n`{BONUS_AMOUNT:.8f} USDT` ወደ ሂሳብዎ ተጨምሯል።\n\n*አዲሱ ቀሪ ሂሳብዎ:* `{new_balance:.8f} USDT`"
            
            keyboard = [
                [InlineKeyboardButton("💰 እንደገና ይውሰዱ", callback_data='claim_bonus')],
                [InlineKeyboardButton("🔙 Back", callback_data='back_to_bonus')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
            ]
            await query.edit_message_text(text=success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        else:
            remaining_time = int(BONUS_COOLDOWN - (current_time - last_claim_time))
            error_text = f"❌ **እባክዎ ይጠብቁ!**\n\n⏳ የሚቀጥለውን ጉርሻ ለመውሰድ {remaining_time} ሰከንዶች ይቀራሉ።"
            
            keyboard = [
                [InlineKeyboardButton("🔄 እንደገና ይሞክሩ", callback_data='claim_bonus')],
                [InlineKeyboardButton("🔙 Back", callback_data='back_to_bonus')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
            ]
            await query.edit_message_text(text=error_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == 'enter_bonus_code':
        if context.user_data.get('bonus_code_used', False):
            await query.message.reply_text("❌ **ይህን የቦነስ ኮድ አስቀድመው ተጠቅመዋል!**\n\n🔔 እያንዳንዱ የቦነስ ኮድ አንድ ጊዜ ብቻ ሊጠቀም ይችላል።")
        else:
            bonus_code_text = """🔑 **የቦነስ ኮድ ያስገቡ**

📝 እባክዎ የቦነስ ኮድዎን ከታች ይጻፉ፡

💡 **ማስታወሻ:** የቦነስ ኮድ አንድ ጊዜ ብቻ ሊጠቀም ይችላል።

❌ ለመሰረዝ: /cancel"""

            keyboard = [
                [InlineKeyboardButton("🔙 Back", callback_data='back_to_bonus')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
            ]
            await query.edit_message_text(text=bonus_code_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            context.user_data['waiting_for_bonus_code'] = True
    
    elif query.data == 'join_channel':
        if context.user_data.get('joined_channel', False):
            await query.edit_message_text("✅ **አስቀድመው በቻናላችን ተጠቅመዋል!**\n\n🌟 ለተጨማሪ ጉርሻዎች ከቦታችን ጋር ይቀጥሉ።")
        else:
            channel_message = f"""📢 **ወደ ቻናላችን ይቀላቀሉ!** 📢

🎁 **ልዩ ጉርሻዎችን እና መረጃዎችን ያግኙ!**

🌟 **በቻናላችን ውስጥ የሚገኙት፡**
• የተለያዩ የቦነስ ኮዶች
• የማይታወቁ መረጃዎች  
• ልዩ ዕድሎች
• እና ብዙ ተጨማሪ...

🔔 **በየ 24 ሰዓት አዳዲስ መረጃዎች እና ጉርሻዎች ይላካሉ!**

✨ **አሁን ተቀላቀሉ እና ልዩ ጉርሻዎችን ያግኙ!**"""

            keyboard = [
                [InlineKeyboardButton("🔙 Back", callback_data='back_to_bonus')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
            ]
            await query.edit_message_text(channel_message, reply_markup=InlineKeyboardMarkup(keyboard))
            context.user_data['joined_channel'] = True
    
    # Deposit ተዛማጅ ቁልፎች
    elif query.data == 'deposit':
        await show_deposit_page(query, context)
    
    elif query.data == 'deposit_bep20':
        await show_bep20_details(query, context)
    
    elif query.data == 'deposit_trc20':
        await show_trc20_details(query, context)
    
    elif query.data == 'back_to_deposit':
        await show_deposit_page(query, context)
    
    # VIP ማሻሻል ቁልፎች
    elif query.data.startswith('upgrade_vip_'):
        plan_name = query.data.replace('upgrade_','').upper()
        await show_deposit_page(query, context, from_vip=True)
    
    # Back buttons
    elif query.data == 'back_to_main':
        main_text = "🏠 **ዋና መንገድ**\n\nከታች ካሉት አማራጮች ይምረጡ።"
        keyboard = [
            [InlineKeyboardButton("Mining", callback_data='mining')],
            [InlineKeyboardButton("Balance", callback_data='balance')],
            [InlineKeyboardButton("Bonus", callback_data='bonus')],
            [InlineKeyboardButton("Task", callback_data='task')],
            [InlineKeyboardButton("About Us", callback_data='about')]
        ]
        await query.edit_message_text(main_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == 'back_to_bonus':
        bonus_text = """🎁 **የጉርሻ ማዕከል** 🎁

ከታች ካሉት የጉርሻ አማራጮች ይምረጡ፡"""
        keyboard = [
            [InlineKeyboardButton("💰 ዕለታዊ ጉርሻ ይውሰዱ", callback_data='claim_bonus')],
            [InlineKeyboardButton("🔑 የቦነስ ኮድ ያስገቡ", callback_data='enter_bonus_code')],
            [InlineKeyboardButton("📢 ወደ ቻናል ይቀላቀሉ", callback_data='join_channel')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
        ]
        await query.edit_message_text(bonus_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == 'back_to_tasks':
        task_text = "እባክዎ ከታች ካሉት ተግባራት አንዱን ይምረጡ።"
        keyboard = [
            [InlineKeyboardButton("👥 ጓደኛ ይጋብዙ (Invite Friend)", callback_data='invite_friend')],
            [InlineKeyboardButton("📝 ዕለታዊ ተግባራት (Daily Tasks)", callback_data='daily_tasks')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
        ]
        await query.edit_message_text(task_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    # ሌሎች ቁልፎች
    elif query.data == 'withdraw': 
        await query.edit_message_text("ገንዘብ ለማውጣት ወኪላችንን ያግኙ: @የእርስዎ_የእርዳታ_ስም")
    elif query.data == 'daily_tasks': 
        await query.edit_message_text("ለዛሬ የተሰጡ ተግባራት ዝርዝር በቅርቡ ይጫናል።")
    elif query.data in ['mining', 'balance', 'bonus', 'task', 'about']:
        # ለዋና መንገድ ቁልፎች ተመሳሳይ ተግባር ማከናወን
        await button_handler(update, context)

# መልዕክት ሂደት
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('waiting_for_bonus_code', False):
        context.user_data['waiting_for_bonus_code'] = False
        await handle_bonus_code_input(update, context)
    else:
        await button_handler(update, context)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(inline_button_handler))
    application.run_polling()

if __name__ == '__main__':
    main()