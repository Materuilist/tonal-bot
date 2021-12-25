from telebot import TeleBot, types
from tf_idf import get_summary
from tonality import get_stats
from youtube import get_comments, get_video_id

tg_token = '5042833294:AAEi9vmGVVMs5K_GBjJLaF3rWjwZFFn9lGw'

bot = TeleBot(tg_token)

STAGES = {
    'BEGIN': 1,
    'CHOOSE': 2,
}
users_stages = {}
users_videos = {}

button_tonal = types.KeyboardButton('Тональность комментариев')
button_summary = types.KeyboardButton('Комментарии вкратце')
button_back = types.KeyboardButton('Назад')
choose_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
choose_kb.add(button_tonal).add(button_summary).add(button_back)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/start':
        users_stages[message.from_user.id] = STAGES['BEGIN']
        bot.send_message(message.from_user.id, 'Привет! Введите корректную ссылку на ютуб видео')
    else:
        if users_stages[message.from_user.id] == STAGES['BEGIN']:
            video_id = get_video_id(message.text)
            if not video_id:
                bot.send_message(message.from_user.id, 'Некорректная ссылка! Пример: https://www.youtube.com/watch?v=mPn5WDCyr2o')
                return
            else:
                comments = get_comments(video_id)
                if len(comments) < 10:
                    bot.send_message(message.from_user.id, 'Выберите видео с числом комментариев >= 10')
                    return

                users_stages[message.from_user.id] = STAGES['CHOOSE']
                users_videos[message.from_user.id] = video_id
                bot.send_message(message.from_user.id, 'Что дальше?', reply_markup=choose_kb)

        elif users_stages[message.from_user.id] == STAGES['CHOOSE']:
            if message.text == 'Тональность комментариев':
                (summary, chart) = get_stats(users_videos[message.from_user.id])
                bot.send_message(message.from_user.id, summary, reply_markup=choose_kb)
                bot.send_photo(message.from_user.id, photo=chart)
                
            elif message.text == 'Комментарии вкратце':
                res = get_summary(users_videos[message.from_user.id])
                bot.send_message(message.from_user.id, res, reply_markup=choose_kb)

            elif message.text == 'Назад':
                users_stages[message.from_user.id] = STAGES['BEGIN']
                bot.send_message(message.from_user.id, 'Введите корректную ссылку на ютуб видео', reply_markup=types.ReplyKeyboardRemove())
            
            else:
                bot.send_message(message.from_user.id, 'Неверный ввод')                

        else:
            bot.send_message(message.from_user.id, 'Что-то пошло не так...')


bot.polling(none_stop=True, interval=0)
