# Поддержать автора
# XMR Wallet
# 48M5dTkFpRUNjeevrZWgNk69bK3hNBXMgMUggq8LGtK8FWEN5G238ccgas93GFfo54aiy9pTW4Qp1D4rZ7ps1nSx9pREAS6

import subprocess, asyncio
from aiogram import Bot, Dispatcher, types
from termcolor import colored
from pyfiglet import figlet_format
import requests

TOKEN = '' # Токен бота с BotFather
ADMIN_ID = 123456789 # Вписать ID админа
WALLET_ADDR = '' #Ваш Кошелёк
WORKER_NAME = 'PC1' # Можно оставить как есть (Имя машины)
POOL = 'pool.hashvault.pro:80' # Пул
COIN = 'XMR' # Какую монету майним (То что может майнить XMRig)
DEBUG = False # Дебаг режим

process = None # НЕ ТРОГАТЬ
mining_is_active = False # НЕ ТРОГАТЬ

def is_not_admin(user_id):
    return user_id != ADMIN_ID

def parse_speed_description(description):
    parts = description.split(" ")

    max_speed = description.split(" max ")[1].replace('\n', '')
    fi_speed = parts[2]
    minute_speed = parts[3]
    fi_minute_speed = parts[4]

    parsed_description = f'''
<b>Информация о скорости</b>

Макс       - {max_speed}
15сек      - {fi_speed} H/s
1мин       - {minute_speed} H/s
15мин    - {fi_minute_speed} H/s
'''
    return parsed_description

def parse_job_description(description):
    parts = description.split(" ")
    
    job_type = parts[0]
    pool = parts[3].split(":")[0]
    difficulty = parts[5]
    algorithm = parts[7]
    block_height = parts[9]
    
    parsed_description = f'''
<b>Новая задача</b>

<i>Сложность</i>   - {difficulty}
<i>Алгоритм</i>      - {algorithm}
<i>Номер блока</i> - {block_height}'''
    
    return parsed_description

def parse_accepted_share_description(description):
    parts = description.split(" ")

    share_num = parts[1].replace('(', '').replace(')', '').split('/')[0]
    #print(parts[1].replace('(', '').replace(')', '').split('/'))
    diff = parts[3]
    time = parts[4].replace('(', '')

    parsed_description = f'''
<b>Найдена шара</b>

<i>Номер</i> - {share_num}
<i>Сложность</i> - {diff}
<i>Время</i> - {time} мс
'''
    return parsed_description

def parse_rejected_share_description(description):
    parts = description.split(" ")

    share_num = parts[1].replace('(', '').replace(')', '').split('/')[0]
    reason = description.split('"')
    print(reason)

    parsed_description = f'''
<b>Шара отклонена</b>

<i>Номер</i> - {share_num}
<i>Причина</i> - ?
'''
    return parsed_description

async def parse_output(output):
    if DEBUG:
        try:
            await bot.send_message(ADMIN_ID, output)
        except Exception:
            pass
        return
    else:
        print(colored(output.replace('\n', ''), color='green'))

    #if ']  cpu      READY threads' in output:
    #    await bot.send_message(ADMIN_ID, output.split(']  cpu      ', maxsplit=1)[1])
    if ']  net      new job' in output:
        await bot.send_message(ADMIN_ID, parse_job_description(output.split(']  net      ', maxsplit=1)[1]))
    elif ']  miner    speed' in output:
        await bot.send_message(ADMIN_ID, parse_speed_description(output.split(']  miner    ', maxsplit=1)[1]))
    elif ']  cpu      accepted' in output:
        await bot.send_message(ADMIN_ID, parse_accepted_share_description(output.split(']  cpu      accepted', maxsplit=1)[1]))
    elif ']  cpu      rejected' in output:
        await bot.send_message(ADMIN_ID, parse_rejected_share_description(output.split(']  cpu      rejected', maxsplit=1)[1]))
    elif '* CPU          ' in output:
        output = output.split('* CPU          ')[1]
        await bot.send_message(ADMIN_ID, '<b>Используемый процессор:</b>\n' + f'<i>{output}</i>')
    elif '* MOTHERBOARD  ' in output:
        output = output.split('* MOTHERBOARD  ')[1]
        await bot.send_message(ADMIN_ID, '<b>Используемая мат. плата:</b>\n' + f'<i>{output}</i>')
    elif '* MEMORY       ' in output:
        output = output.split('* MEMORY       ')[1]
        await bot.send_message(ADMIN_ID, '<b>Доступно RAM:</b>\n' + f'<i>{output}</i>')
    elif '* DONATE       ' in output:
        output = output.split('* DONATE       ')[1]
        await bot.send_message(ADMIN_ID, '<b>Комиссия разработчикам:</b>\n' + f'<i>{output}</i>')

def stopp_mining():
    global process
    global mining_is_active
    process.terminate()
    mining_is_active = False

async def run_mining():
    global process
    global mining_is_active
    command = ['XMRig.exe', '--coin', COIN, '-o', POOL, '-u', f'{WALLET_ADDR}.{WORKER_NAME}', '-p', 'x', '--nicehash', '--no-color', '--health-print-time=60', '--cpu-priority=2']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    mining_is_active = True
    #print(process.stdout.readline())
   
async def async_mining():
    await bot.send_message(ADMIN_ID, PyMinerTG_nocolored + '\n<b>Бот запущен</b>')
    global process
    while True:
        await asyncio.sleep(0.1)
        #print(mining_is_active)
        if mining_is_active:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                await parse_output(output)

bot = Bot(token=TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if is_not_admin(message.from_user.id):
        await message.answer(f"<b>Извини {message.from_user.full_name} 😢</b>\nНо бот доступен только пользователю с ID {ADMIN_ID}\n<i>Твой ID {message.from_user.id}</i>")
        return

    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add('👤 HashVault.pro')
    buttons = ['Начать майнинг', 'Остановить майнинг']
    keyboard.add(*buttons)
    await message.answer(f"<b>Привет {message.from_user.full_name}!</b>\nЭто бот для майнинга на пуле HashVault.pro\nВыбери действие:", reply_markup = keyboard)

@dp.message_handler(lambda message: message.text == '👤 HashVault.pro')
async def hashvault_info(message: types.Message):
    if is_not_admin(message.from_user.id):
        await message.answer(f"<b>Извини {message.from_user.full_name} 😢</b>\nНо бот доступен только пользователю с ID {ADMIN_ID}\n<i>Твой ID {message.from_user.id}</i>")
        return
    response = requests.get(f'https://api.hashvault.pro/v3/monero/wallet/{WALLET_ADDR}/stats')
    response = response.json()
    collective = response["collective"]
    c_hashRate = collective["hashRate"]
    c_avg1hashRate = collective["avg1hashRate"]
    c_avg3hashRate = collective["avg3hashRate"]
    c_avg6hashRate = collective["avg6hashRate"]
    c_avg24hashRate = collective["avg24hashRate"]
    c_totalHashes = collective["totalHashes"]
    c_validShares = collective["validShares"]
    c_invalidShares = collective["invalidShares"]
    c_staleShares = collective["staleShares"]
    c_foundBlocks = collective["foundBlocks"]

    solo = response["solo"]
    s_hashRate = solo["hashRate"]
    s_avg1hashRate = solo["avg1hashRate"]
    s_avg3hashRate = solo["avg3hashRate"]
    s_avg6hashRate = solo["avg6hashRate"]
    s_avg24hashRate = solo["avg24hashRate"]
    s_totalHashes = solo["totalHashes"]
    s_validShares = solo["validShares"]
    s_invalidShares = solo["invalidShares"]
    s_staleShares = solo["staleShares"]
    s_foundBlocks = solo["foundBlocks"]

    text = f'''
👤 <b>Статистика HashVault</b>
<b>Статистика пул</b>
<i>Текущий Хэшрейт</i>: {c_hashRate}
<i>Хэшрейт 1час</i>: {c_avg1hashRate}
<i>Хэшрейт 3часа</i>: {c_avg3hashRate}
<i>Хэшрейт 6часов</i>: {c_avg6hashRate}
<i>Хэшрейт 24часа</i>: {c_avg24hashRate}
<i>Всего хэшей</i>: {c_totalHashes}
<i>Валидные Шары</i>: {c_validShares}
<i>Испорченые Шары</i>: {c_invalidShares}
<i>Запоздалые Шары</i>: {c_staleShares}
<i>Найдено Блоков</i>: {c_foundBlocks}

<b>Статистика соло</b>
<i>Текущий Хэшрейт</i>: {s_hashRate}
<i>Хэшрейт 1час</i>: {s_avg1hashRate}
<i>Хэшрейт 3часа</i>: {s_avg3hashRate}
<i>Хэшрейт 6часов</i>: {s_avg6hashRate}
<i>Хэшрейт 24часа</i>: {s_avg24hashRate}
<i>Всего хэшей</i>: {s_totalHashes}
<i>Валидные Шары</i>: {s_validShares}
<i>Испорченые Шары</i>: {s_invalidShares}
<i>Запоздалые Шары</i>: {s_staleShares}
<i>Найдено Блоков</i>: {s_foundBlocks}
'''
    await message.answer(text)

@dp.message_handler(lambda message: message.text == 'Начать майнинг')
async def start_mining(message: types.Message):
    if is_not_admin(message.from_user.id):
        await message.answer(f"<b>Извини {message.from_user.full_name} 😢</b>\nНо бот доступен только пользователю с ID {ADMIN_ID}\n<i>Твой ID {message.from_user.id}</i>")
        return

    if not mining_is_active:
        await run_mining()
        await message.answer('<b>Майнинг начат</b>')
        await message.answer(f'<b>Используемый Пул:</b>\n{POOL}\n<b>Монета:</b>\n{COIN}')
    else:
        await message.answer('<b>Майнинг уже запущен</b>')

@dp.message_handler(lambda message: message.text == 'Остановить майнинг')
async def stop_mining(message: types.Message):
    if is_not_admin(message.from_user.id):
        await message.answer(f"<b>Извини {message.from_user.full_name} 😢</b>\nНо бот доступен только пользователю с ID {ADMIN_ID}\n<i>Твой ID {message.from_user.id}</i>")
        return

    if mining_is_active:
        stopp_mining()
        await message.answer('<b>Майнинг остановлен</b>')
    else:
        await message.answer('<b>Майнинг и так остановлен</b>')

if __name__ == '__main__':
    from aiogram import executor
    loop = asyncio.get_event_loop()
    loop.create_task(async_mining())
    executor.start_polling(dp, loop=loop)