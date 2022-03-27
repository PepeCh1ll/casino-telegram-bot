import telebot
from telebot.types import BotCommand, ReplyKeyboardRemove
import config
from textwrap import dedent
import sqlite3
from keyboards import get_spin_keyboard
from functions import profile, change, complete_change, replenishment, check_replenishment, conclusion, get_conclusion, check_conclusion, cmd_spin

bot = telebot.TeleBot(config.token)

conn = sqlite3.connect('casino.db', check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (id TEXT, balance INTEGER, login TEXT, gk TEXT, sk TEXT)")
conn.commit()

commands = [
	BotCommand(command="start", description="Перезапустить казино"),
	BotCommand(command="spin", description="Показать клавиатуру и сделать бросок"),
	BotCommand(command="stop", description="Убрать клавиатуру"),
	BotCommand(command="help", description="Справочная информация"),
        ]
bot.set_my_commands(commands=commands)

@bot.message_handler(commands=['start'])
def cmd_start(message):
	r = c.execute(f"SELECT balance FROM users WHERE id='{message.chat.id}'").fetchone()
	if r == None:
		points = 0
		c.execute(f"INSERT INTO users VALUES ('{message.chat.id}', 0, '', '', '')")
		conn.commit()
	else:
		points = str(r[0])
	bot.send_message(message.chat.id, text=dedent(config.start_text).format(points=points, sale=config.sale), reply_markup=get_spin_keyboard(), parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def cmd_help(message):
	bot.send_message(message.chat.id, config.help_text)

@bot.message_handler(commands=['stop'])
def cmd_stop(message):
	bot.send_message(message.chat.id, "Клавиатура удалена. Начать заново: /start, вернуть клавиатуру и продолжить: /spin", reply_markup=ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.text == 'В меню')
def back(message):
	bot.send_message(message.chat.id, 'Возвращаю в меню', reply_markup=get_spin_keyboard(), parse_mode='Markdown')

@bot.message_handler(commands=['spin'])
@bot.message_handler(func=lambda message: message.text == config.SPIN_TEXT)
def spin(message):
	score = c.execute(f"SELECT balance FROM users WHERE id='{message.chat.id}'").fetchone()[0]
	cmd_spin(message, score, bot, c, conn)

@bot.message_handler(func=lambda message: message.text == 'Профиль')
def cmd_pofile(message):
	profile(message, bot, c, conn)

@bot.message_handler(func=lambda message: message.text == 'Изменить')
def cmd_change(message):
	change(message, bot, c, conn)
	bot.register_next_step_handler(message, cmd_complete_change)

def cmd_complete_change(message):
	complete_change(message, bot, c, conn)

@bot.message_handler(func=lambda message: message.text == 'Пополнить')
def cmd_replenishment(message):
	replenishment(message, bot, c, conn)

@bot.message_handler(func=lambda message: message.text == 'Вывести')
def cmd_conclusion(message):
	conclusion(message, bot, c, conn)
	if message.text != 'В меню':
		bot.register_next_step_handler(message, cmd_get_conclusion)

def cmd_get_conclusion(message):
	get_conclusion(message, bot, c, conn)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	if call.data == 'check_r':
		check_replenishment(call, bot, c, conn)
	elif call.data == 'check_c':
		check_conclusion(call, bot, c, conn)

if __name__ == '__main__':
	bot.polling(none_stop=True)
	conn.close()