import telegram
from telegram.ext import Updater, CommandHandler, CallbackContext
import threading
import time
import schedule
from datetime import datetime
import logging

# ሎጂንግ ማስተካከያ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# የBot መረጃዎች
BOT_TOKEN = "8049839864:AAEjd5q1ngi17WnGkJbWLYka25i489aTqwI"
CHANNEL_ID = "-1003195810666"  # Orbit Tv ቻናል

# Bot ፍጠር
bot = telegram.Bot(token=BOT_TOKEN)

def start(update, context):
    """የstart ትእዛዝ ሲገኝ"""
    user = update.effective_user
    update.message.reply_text(
        f"ሰላም {user.first_name}! ✨\n"
        f"ይህ የOrbit Tv ቦት ነው።\n"
        f"በሁለት ሰዓት እረፍት ለቻናል መልእክት እልካለሁ።"
    )

def send_auto_message():
    """ለቻናል አውቶማቲክ መልእክት ማስተላለፍ"""
    try:
        message = f"📺 **Orbit Tv - አውቶማቲክ መልእክት**\n\n" \
                 f"ጊዜ፦ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" \
                 f"ይህ አውቶማቲክ መልእክት ነው።\n" \
                 f"በሁለት ሰዓት እረፍት ይልካል! 🎬"
        
        bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode='Markdown'
        )
        print(f"✅ መልእክት ተልኳል፦ {datetime.now()}")
    except Exception as e:
        print(f"❌ ስህተት፦ {e}")

def schedule_messages():
    """የመልእክት መልክዓ ሰዓት ማስተካከያ"""
    # በሁለት ሰዓት እረፍት መልእክት ላክ
    schedule.every(2).hours.do(send_auto_message)
    
    print("⏰ የመልእክት መልክዓ ሰዓት ተጀምሯል...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # በደቂቃ ያረጋግጡ

def main():
    """ዋና ፕሮግራም"""
    try:
        # Updater ፍጠር
        updater = Updater(token=BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # ትእዛዞችን አክል
        dispatcher.add_handler(CommandHandler("start", start))
        
        # የሰሌዳ መልእክቶችን በትር ፍጠር
        schedule_thread = threading.Thread(target=schedule_messages)
        schedule_thread.daemon = True
        schedule_thread.start()
        
        print("🤖 Bot እየሰራ ነው...")
        print("📅 በሁለት ሰዓት እረፍት መልእክት ይልካል")
        print("🛑 ለማቆም Ctrl+C ን ተጫን")
        
        # Bot ጀምር
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        print(f"❌ ዋና ፕሮግራም ስህተት፦ {e}")

if __name__ == '__main__':
    main()