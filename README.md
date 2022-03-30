# Казино-бот в Telegram
Основа для бота-казино в Telegram с внутренним балансом
Работает с криптовалютой Duinocoin

Согласно документации на тип Dice в Bot API, слот-машина может принимать значения от 1 до 64 включительно. В файле `dice_check.py` вы найдёте функции для сопоставления значения дайса с тройкой выпавших элементов игрового автомата.

# Технологии
*[pytelegrambotapi](https://pypi.org/project/pyTelegramBotAPI/) — работа с Telegram Bot API
*[sqlite3](https://docs.python.org/3/library/sqlite3.html) - работа с базами данных
*[Duinocoin](https://wallet.duinocoin.com) — задействованная криптовалюта

# Установка
1. Установить библиотеки командой `pip install -r requirements.txt`
2. В файле `config.py` вставьте токен бота, логин и пароль вашего кошелька, поменяйте параметры по своему желанию
3. Запустите `main.py`
