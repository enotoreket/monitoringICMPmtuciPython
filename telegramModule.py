import telebot
import threading
import subprocess
import time

bot = telebot.TeleBot('token')
bot.remove_webhook()
workList = []
redWorkList = []

def run_cmd_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Ошибка выполнения команды: {e.stderr}"

def send_messages():
    """Функция для бесконечной отправки сообщений"""
    while True:
        try:
            msg = run_cmd_command("main.py -c -")
            # Отправка сообщений общему списку
            for user_id in workList:
                try:
                    bot.send_message(user_id, msg)
                except Exception as e:
                    print(f"Ошибка отправки общему списку {user_id}: {e}")
            # Отправка сообщений тихому списку (реже)
            if msg.find("DOWN")!=-1:
                for user_id in redWorkList:
                    try:
                        bot.send_message(user_id, msg)
                    except Exception as e:
                        print(f"Ошибка отправки тихому списку {user_id}: {e}")

        except Exception as e:
            print(f"Общая ошибка в цикле отправки: {e}")
        time.sleep(30)
@bot.message_handler(commands=['green'])
def get_text_messages(message):
    workList.append(message.from_user.id)
    try:
        redWorkList.remove(message.from_user.id)
    except Exception as e:
        pass
    bot.send_message(message.from_user.id,"Вы добавлены в общий список мониторинга")
@bot.message_handler(commands=['red'])
def get_text_messages(message):
    redWorkList.append(message.from_user.id)
    try:
        workList.remove(message.from_user.id)
    except Exception as e:
        pass
    bot.send_message(message.from_user.id,"Вы добавлены в тихий список мониторинга")

@bot.message_handler(commands=['red'])
def handle_red(message):
    """Добавление в тихий список"""
    user_id = message.from_user.id
    if user_id not in redWorkList:
        redWorkList.append(user_id)
    try:
        workList.remove(user_id)
    except ValueError:
        pass
    bot.send_message(user_id, "🔇 Вы добавлены в тихий список мониторинга (редкие уведомления)")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    """Удаление из всех списков"""
    user_id = message.from_user.id
    try:
        workList.remove(user_id)
    except ValueError:
        pass
    try:
        redWorkList.remove(user_id)
    except ValueError:
        pass
    bot.send_message(user_id, "⏹ Вы удалены из всех списков мониторинга")

# Запуск потока для отправки сообщений
sender_thread = threading.Thread(target=send_messages)
sender_thread.daemon = True  # Демонизируем поток, чтобы он завершался с основным
sender_thread.start()

# Запуск бота
print("Бот запущен и готов к работе!")
bot.polling(none_stop=True, interval=0)
