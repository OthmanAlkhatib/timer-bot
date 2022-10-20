from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
import os
import logging
import sys
from datetime import timedelta
import time
import threading

TOKEN = os.getenv("TOKEN")
MODE = os.getenv("MODE")


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

if MODE == "dev":
    def run():
        logger.info("Start in DEV mode")
        updater.start_polling()
elif MODE == "prod":
    def run():
        logger.info("Start in PROD mode")
        updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get("PORT", 5000)), url_path=TOKEN,
                              webhook_url="https://{}.herokuapp.com/{}".format("binaa-timer-bot", TOKEN))
else:
    logger.error("No mode specified")
    sys.exit(1)

def start_handler(update: Update, context: CallbackContext):
    update.message.reply_text("""
أهلاً بك في Simple Timer.
تستطيع من خلال هذا البوت إنشاء مؤقت في المجموعات والقنوات في حال كان يوجد (امتحانات, مسابقات, تفاعليات, إلخ..)

يمكن استخدام البوت ببساطة باستخدام الأمر على الشكل التالي :
/timer hh:mm:ss   -->  ex. /timer 86:00:00

لإيقاف المؤقت أرسل الأمر :
/stop
    """)

is_running = True
thread = None
def start_timer(update: Update, context: CallbackContext):
    try:
        time_str = update.message.text.split(" ")[1]
        hours, minutes, seconds = list(map(int, time_str.split(":")))
        timer = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        second = timedelta(seconds=1)
        message_id = update.message.reply_text("========  " + str(timer) + "  ========")["message_id"]
        while str(timer) != "0:00:00" and is_running:
            time.sleep(1)
            timer -= second
            context.bot.editMessageText(chat_id=update.message.chat_id, message_id=message_id, text="========  " + str(timer) + "  ========")
        update.message.reply_text("انتهى الوقت!")

    except Exception as error:
        update.message.reply_text("خطأ, مؤقت غير صحيح!")

def stop_thread(update: Update, context: CallbackContext):
    global is_running
    is_running = False

def start_timer_thread(update: Update, context: CallbackContext):
    global thread
    global is_running
    is_running = True
    thread = threading.Thread(target=start_timer, args=(update, context))
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("timer", start_timer_thread))
    updater.dispatcher.add_handler(CommandHandler("stop", stop_thread))

    run()