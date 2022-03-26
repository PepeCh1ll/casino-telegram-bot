from keyboards import get_spin_keyboard, back_keyboard, conclusion_keyboard, profile_keyboard, replenishment_keyboard
from dice_check import get_combo_data
from key_generator.key_generator import generate
import requests
import time
from textwrap import dedent
import config
from telebot.types import ReplyKeyboardRemove

def profile(message, bot, c, conn):
	r = c.execute(f"SELECT * FROM users WHERE id='{message.chat.id}'").fetchone()
	bot.send_message(message.chat.id, f'Логин кошелька: {r[2]}\nБаланс: {r[1]} прокрутов', reply_markup=profile_keyboard())

def change(message, bot, c, conn):
	m = bot.send_message(message.chat.id, 'Введите логин кошелька', reply_markup=back_keyboard())

def complete_change(message, bot, c, conn):
	if message.text == 'В меню':
		bot.send_message(message.chat.id, 'Возвращаю в меню', reply_markup=get_spin_keyboard(), parse_mode='Markdown')
	else:
		c.execute(f"UPDATE users SET login='{message.text}' WHERE id='{message.chat.id}'")
		conn.commit()
		bot.send_message(message.chat.id, 'Данные изменены', reply_markup=get_spin_keyboard())

def replenishment(message, bot, c, conn):
	r = c.execute(f"SELECT login FROM users WHERE id='{message.chat.id}'").fetchone()
	if r[0] == '':
		bot.send_message(message.chat.id, 'Вы не ввели логин в профиле, повторите попытку', reply_markup=get_spin_keyboard(), parse_mode='Markdown')
	elif message.text == 'В меню':
		bot.send_message(message.chat.id, 'Возвращаю в меню', reply_markup=get_spin_keyboard(), parse_mode='Markdown')
	else:
		key = generate()
		GK = key.get_key()
		c.execute(f"UPDATE users SET gk='{str(GK)}' WHERE id='{message.chat.id}'")
		conn.commit()

		bot.send_message(message.chat.id, f'❗️❗️❗️Внимание❗️❗️❗️\nВводите сумму, кратную цене прокрута (1 прокрут = {config.sale} DUCO)\n\nЗаявка на пополнение средств\n\nПереведите сумму на логин: {config.admin}\nДобавьте следующий код в примечание к пополнению: {GK}\n\nСтатус: Не подтверждён', reply_markup=replenishment_keyboard())

def check_replenishment(call, bot, c, conn):
	time.sleep(3)
	user = c.execute(f"SELECT * FROM users WHERE id='{call.message.chat.id}'").fetchone()
	r = requests.get('https://server.duinocoin.com/user_transactions/'+user[2])
	response = r.json()
	for dicts in response['result']:
		if dicts['memo'] == user[3] and dicts['recipient'] == config.admin:
			bot.edit_message_text(f'❗️❗️❗️Внимание❗️❗️❗️\nВводите сумму, кратную цене прокрута (1 прокрут = {config.sale} DUCO)\n\nЗаявка на пополнение средств\n\nПереведите сумму на логин: {config.admin}\nДобавьте следующий код в примечание к пополнению: {user[3]}\n\nСтатус: Подтверждён', call.message.chat.id, call.message.message_id, reply_markup='')
			c.execute(f"UPDATE users SET gk='', balance={user[1]+int(dicts['amount']/config.sale)} WHERE id='{call.message.chat.id}'")
			conn.commit()
			bot.send_message(call.message.chat.id, 'Возвращаю в меню', reply_markup=get_spin_keyboard(), parse_mode='Markdown')
			break

def conclusion(message, bot, c, conn):
	r = c.execute(f"SELECT login FROM users WHERE id='{message.chat.id}'").fetchone()
	if r[0] == '':
		bot.send_message(message.chat.id, 'Вы не ввели логин в профиле, повторите попытку', reply_markup=get_spin_keyboard(), parse_mode='Markdown')
	elif message.text == 'В меню':
		bot.send_message(message.chat.id, 'Возвращаю в меню', reply_markup=get_spin_keyboard(), parse_mode='Markdown')
	else:
		bot.send_message(message.chat.id, f'Введите количество прокрутов на вывод (1 прокрут = {config.sale} DUCO)', reply_markup=ReplyKeyboardRemove())

def get_conclusion(message, bot, c, conn):
	try:
		time.sleep(3)
		key = generate()
		GK = key.get_key()
		c.execute(f"UPDATE users SET sk='{str(GK)}' WHERE id='{message.chat.id}'")
		conn.commit()
		summ = abs(float(message.text))
		r = c.execute(f"SELECT balance FROM users WHERE id='{message.chat.id}'").fetchone()
		if r[0] < summ:
			bot.send_message(message.chat.id, 'Вы ввели неверную сумму, повторите попытку', reply_markup=get_spin_keyboard(), parse_mode='Markdown')
		else:
			user = c.execute(f"SELECT * FROM users WHERE id='{message.chat.id}'").fetchone()
			r = requests.get(f'https://server.duinocoin.com/transaction?username={config.admin}&password={config.password}&recipient={user[2]}&amount={summ*config.sale}&memo={GK}')
			response = r.json()
			bot.send_message(message.chat.id, f'Заявка на вывод средств средств\n\nСтатус: Не подтверждён', reply_markup=conclusion_keyboard())
	except ValueError:
		bot.send_message(message.chat.id, 'Вы ввели неверную сумму, повторите попытку', reply_markup=get_spin_keyboard(), parse_mode='Markdown')

def check_conclusion(call, bot, c, conn):
	user = c.execute(f"SELECT * FROM users WHERE id='{call.message.chat.id}'").fetchone()
	r = requests.get('https://server.duinocoin.com/user_transactions/'+config.admin)
	response = r.json()
	time.sleep(3)
	for dicts in response['result']:
		if dicts['memo'] == user[4] and dicts['recipient'] == user[2]:
			bot.edit_message_text(f'Заявка на вывод средств средств\n\nСтатус: Подтверждён', call.message.chat.id, call.message.message_id, reply_markup='')
			c.execute(f"UPDATE users SET sk='', balance={user[1]-int(dicts['amount']/config.sale)} WHERE id='{call.message.chat.id}'")
			conn.commit()
			bot.send_message(call.message.chat.id, 'Возвращаю в меню', reply_markup=get_spin_keyboard(), parse_mode='Markdown')
			break

def cmd_spin(message, score, bot, c, conn):
	if score == 0:
		bot.send_sticker(message.chat.id, config.STICKER_FAIL)
		bot.send_message(message.chat.id, "Ваш баланс равен нулю. Вы можете смириться с судьбой и продолжить жить своей жизнью, а можете нажать /start, чтобы начать всё заново. Или /stop, чтобы просто убрать клавиатуру."
		)
		return
	
	answer_text_template = """🎰Ваша комбинация: {combo_text} (№{dice_value}).{win_or_lose_text} Ваш счёт: {new_score}."""

	msg = bot.send_dice(message.chat.id, emoji="🎰", reply_markup=get_spin_keyboard())

	score_change, combo_text = get_combo_data(msg.dice.value)
	if score_change < 0:
		win_or_lose_text = "К сожалению, вы не выиграли."
	else:
		win_or_lose_text = f"Вы выиграли {score_change} очков!"

	new_score = score + score_change

	c.execute(f"UPDATE users SET balance={new_score} WHERE id='{message.chat.id}'")
	conn.commit()
	time.sleep(2)
	bot.send_message(message.chat.id, 
		dedent(answer_text_template).format(
			combo_text=combo_text,
			dice_value=msg.dice.value,
			win_or_lose_text=win_or_lose_text,
			new_score=new_score
		), reply_markup=get_spin_keyboard())