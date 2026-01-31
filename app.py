import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler  
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests

from dotenv import load_dotenv

load_dotenv()

TOKEN_tg = os.getenv('TELEGRAM_BOT_TOKEN')
API_KEY = os.getenv('OPENWEATHER_API_KEY')



WEIGHT, HEIGHT, AGE, ACTIVE, CITY, KEYBUTTON, EAT_WEIGHT, SET_PROFILE  = range(7)

async def set_profile(update, context):
    try:
        context.user_data['logged_calories'] = 0
        context.user_data['logged_water'] = 0
        context.user_data['burned_calories'] = 0
        await update.message.reply_text("Введите ваш вес (в кг):")
        return WEIGHT
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите вес.")
        return SET_PROFILE

async def get_weight(update, context):
    try:
        context.user_data['weight'] = float(update.message.text)
        await update.message.reply_text("Введите ваш рост (в см):")
        return HEIGHT
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите вес.")
        return WEIGHT

async def get_height(update, context):
    try:
        context.user_data['height'] = float(update.message.text)
        await update.message.reply_text("Введите ваш возраст:")
        return AGE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите рост.")
        return HEIGHT

async def get_age(update, context):
    try:
        context.user_data['age'] = float(update.message.text)
        await update.message.reply_text("Сколько минут активности у вас в день?")
        return ACTIVE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите возраст.")
        return AGE

async def get_active(update, context):
    try:
        context.user_data['activity'] = float(update.message.text)
        await update.message.reply_text("В каком городе вы находитесь?")
        return CITY
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите количество минут активности.")
        return ACTIVE

async def get_city(update, context):
    try:
        context.user_data['city'] = update.message.text
        context.user_data['calorie_standart'] = 10 * context.user_data['weight'] + 6.25 * context.user_data['height'] - 5 * context.user_data['age']
        context.user_data['water_standart'] = 30 * context.user_data['weight']
        # поиск темпы по городу
        
        API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={context.user_data['city']}&appid={API_KEY}&units=metric&lang=ru"    
        response = requests.get(API_URL)
        if response.status_code == 401:
            try:
                error_data = response.json()
                print(f'Ошибка 401: Invalid API key')
                print(f'Please see https://openweathermap.org/faq#error401 for more info.{error_data}')
            except:
                print('Ошибка 401: Invalid API key')

        try:
            response = requests.get(API_URL)
            data_from_API = response.json()       

            if response.status_code == 404 or data_from_API.get('cod') == '404':
                await update.message.reply_text("Такого города не знаем")
                return
            
            if response.status_code == 401:
                await update.message.reply_text("Неверный API ключ!")
                return
            
            if response.status_code != 200:
                await update.message.reply_text(f"Ошибка API: {response.status_code}")
                return        

            context.user_data['temp_city'] = data_from_API['main']['temp']
            await update.message.reply_text(f"Температура в Вашем городе: {context.user_data['temp_city']}°C")
            # не смог найти зависимость "количество воды, которое надо выпить/ температура в городе"
            
        except Exception as e:
            await update.message.reply_text(f"Ошибка:{str(e)}")
        return ConversationHandler.END
    
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите город.")
        return CITY

async def cancel(update, context):
    await update.message.reply_text("Отменено")
    return ConversationHandler.END


async def log_water(update, context):
    water_drinked = context.args
    if water_drinked:
        context.user_data['logged_water'] = context.user_data['logged_water'] + float(water_drinked[0])
        await update.message.reply_text(f"Осталось выпить воды: {float(context.user_data['water_standart']) - float(context.user_data['logged_water'])} мл.\n")
    else:
        await update.message.reply_text("Вы не указали количество употребленной воды\n")
        return ConversationHandler.END

async def log_workout(update, context):
    times = context.args
    if times:
        context.user_data['time_workout'] = context.args[0]
    else:
        await update.message.reply_text("Вы не указали количество времени, потраченного на тренировку\n")
        return

    keyboard = [
        # Первый ряд
        [InlineKeyboardButton("Ходьба пешком (4 км/ч)", callback_data='btn1'),
        InlineKeyboardButton("Йога (хатха)", callback_data='btn2')],
        # Второй ряд        
        [InlineKeyboardButton("Стретчинг", callback_data='btn3'),
        InlineKeyboardButton("Боулинг", callback_data='btn4')],
        # Третий ряд
        [InlineKeyboardButton("Быстрая ходьба (6 км/ч)", callback_data='btn5'),
        InlineKeyboardButton("Езда на велосипеде (15 км/ч)", callback_data='btn6')],
        # Четвертый ряд
        [InlineKeyboardButton("Плавание (спокойное)", callback_data='btn7'),
        InlineKeyboardButton("Силовая тренировка", callback_data='btn8')],
        # Пятый ряд
        [InlineKeyboardButton("Танцы (диско, балет)", callback_data='btn9'),
        InlineKeyboardButton("Волейбол (любительский)", callback_data='btn10')],
        # Шестой ряд
        [InlineKeyboardButton("Бег (10 км/ч)", callback_data='btn11'),
        InlineKeyboardButton("Плавание (кроль, интенсивно)", callback_data='btn12')],
        # Седьмой ряд
        [InlineKeyboardButton("Езда на велосипеде (20+ км/ч)", callback_data='btn13'),
        InlineKeyboardButton("Футбол, баскетбол (матч)", callback_data='btn14')],
        # Восьмой ряд
        [InlineKeyboardButton("Прыжки на скакалке", callback_data='btn15'),
        InlineKeyboardButton("Теннис (одиночный разряд)", callback_data='btn16')],
        # Девятый ряд
        [InlineKeyboardButton("Интервальные тренировки (HIIT)", callback_data='btn17'),
        InlineKeyboardButton("Бег в гору/по лестнице", callback_data='btn18')],
        # Десятый ряд
        [InlineKeyboardButton("Гребля (соревновательная)", callback_data='btn19'),
        InlineKeyboardButton("Боевые искусства (спарринг)", callback_data='btn20')]
    ]    
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Выберите тренировку, которая более похожа по активности на Вашу:",
        reply_markup=reply_markup
    )    
    return KEYBUTTON

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    workout_values = {
        'btn1': 2.9, 'btn2': 2.5, 'btn3': 2.3, 'btn4': 3.0,
        'btn5': 4.3, 'btn6': 4.0, 'btn7': 5.8, 'btn8': 5.0,
        'btn9': 4.8, 'btn10': 3.5, 'btn11': 10.0, 'btn12': 8.3,
        'btn13': 8.0, 'btn14': 10.0, 'btn15': 8, 'btn16': 11.0,
        'btn17': 12.0, 'btn18': 12.5, 'btn19': 13, 'btn20': 10.3
    }

    #Нашел рекомендации по употреблению воды на потраченные ккал:
    #Выпивать дополнительно 0.5 - 1 литр воды на каждые 1000 ккал, потраченных во время тренировки.
    #На 500 ккал → 250-500 мл дополнительной воды.
    #Я выбрал 250 мл на каждые потраченные 250 ккал
    
    if 'weight' in context.user_data:
        context.user_data['burned_calories'] =+ float(workout_values[query.data]) * float(context.user_data['weight']) * float(context.user_data['time_workout'])/60        
        if context.user_data['burned_calories'] // 250 >= 1:
            drink_water = f"Необходимо выпить примерно {(context.user_data['burned_calories'] // 250) * 250} мл. воды"
        else:
            drink_water = f"Необходимо выпить менее 500 мл. воды"
        await query.edit_message_text(f"Расход ккал = MET × вес (в кг) × (время в часах)\n Вы выбрали упажнение, МЕТ которого равен: {workout_values[query.data]} \n Вы занимались: {context.user_data['time_workout']} \n Вы потратили {context.user_data['burned_calories']} ккал \n {drink_water}")   
    else:
        await query.edit_message_text("Укажите свой вес в /set_profile")

    return ConversationHandler.END


async def log_food(update, context):
    eat_args = context.args
    context.user_data['api_eat_result'] = get_food_info(eat_args)
    print(get_food_info(eat_args))
    await update.message.reply_text(f"{context.user_data['api_eat_result']['name']} - {context.user_data['api_eat_result']['calories']} ккал на 100 г. Сколько грамм вы съели?\n")
    return EAT_WEIGHT

async def eat_weight(update, context):
    context.user_data['calorie_eat'] = update.message.text
    weiht_eat = float(context.user_data['calorie_eat'])/100 * float(context.user_data['api_eat_result']['calories'])
    context.user_data['logged_calories'] = weiht_eat
    await update.message.reply_text(f"Записано: {weiht_eat} ккал.")
    return ConversationHandler.END

def get_food_info(product_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        if products:  # Проверяем, есть ли найденные продукты
            first_product = products[0]
            return {
                'name': first_product.get('product_name', 'Неизвестно'),
                'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
            }
        return None
    print(f"Ошибка: {response.status_code}")
    return None

async def check_progress(update, context):
    await update.message.reply_text(f"Вода:\n - Выпито: {context.user_data['logged_water']} из {context.user_data['water_standart']} мл.\n - Осталось: {float(context.user_data['water_standart']) - float(context.user_data['logged_water'])} мл. \n\n Калории: - Потреблено: {context.user_data['logged_calories']} ккал из {context.user_data['calorie_standart']} ккал.\n - Сожжено: {context.user_data['burned_calories']} ккал.\n - Баланс: {float(context.user_data['logged_calories']) - float(context.user_data['burned_calories'])} ккал.")

def main():
    application = Application.builder().token(TOKEN_tg).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('set_profile', set_profile),
            CommandHandler('log_workout', log_workout),
            CommandHandler('log_water', log_water),
            CommandHandler('log_food', log_food),
            CommandHandler('check_progress', check_progress),
            

        ],
        states={
            WEIGHT: [MessageHandler(filters.TEXT, get_weight)],
            HEIGHT: [MessageHandler(filters.TEXT, get_height)],
            AGE: [MessageHandler(filters.TEXT, get_age)],
            ACTIVE: [MessageHandler(filters.TEXT, get_active)],
            CITY: [MessageHandler(filters.TEXT, get_city)],
            EAT_WEIGHT: [MessageHandler(filters.TEXT, eat_weight)],
            KEYBUTTON: [CallbackQueryHandler(button_handler)],
            SET_PROFILE: [CallbackQueryHandler(set_profile)],  
            },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', cancel)
    ]
    )
    application.add_handler(conv_handler)    
    print("Бот запущен")
    application.run_polling()


if __name__ == '__main__':
    main()
