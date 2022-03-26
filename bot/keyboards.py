from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import config

def get_spin_keyboard():
	kb = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton(config.SPIN_TEXT))
	kb.row(KeyboardButton('Профиль'))

	return kb

def profile_keyboard():
	kb = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton('Изменить'))
	kb.row(KeyboardButton('Пополнить'), KeyboardButton('Вывести'))
	kb.row(KeyboardButton('В меню'))

	return kb

def back_keyboard():
	kb = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton('В меню'))

	return kb

def replenishment_keyboard():
	kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Проверить оплату', callback_data='check_r'))
	return kb

def conclusion_keyboard():
	kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Проверить оплату', callback_data='check_c'))
	return kb