import telebot
import pandas as pd
from sklearn.linear_model import LinearRegression

bot = telebot.TeleBot('5488884442:AAE6Mgr8PV7kbNEWm3EPq5z4es1nwmEBtiQ')

def get_data(data):
    return pd.read_csv(data, delimiter=',')

df = get_data('players_20.csv')[lambda x: x['player_positions'] != 'GK']

df['surname'] = df['short_name'].str.split('.').apply(lambda x: x[-1]).str.strip()

df0 = df[['surname', 'overall', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']]

model1 = LinearRegression()
model1.fit(df0[['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']], df0['overall'])

df['positions'] = df['player_positions'].str.find('ST')
df2 = df[lambda x: x['positions'] > -1][['surname', 'overall', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']]

model2 = LinearRegression()
model2.fit(df2[['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']], df2['overall'])

model =LinearRegression()

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/model':
        bot.send_message(message.from_user.id, "Выберите модель. Для этого напишите /model1 или /model2")
        bot.register_next_step_handler(message, get_model)
    else:
        bot.send_message(message.from_user.id, 'Напишите /model, чтобы выбрать модель')


def get_model(message):
    global model
    if message.text == '/model1':
        model = model1
        bot.send_message(message.from_user.id, 'Теперь выберите футболиста')
        bot.register_next_step_handler(message, get_player)
    elif message.text == '/model2':
        model = model2
        bot.send_message(message.from_user.id, 'Теперь выберите футболиста')
        bot.register_next_step_handler(message, get_player)
    else:
        bot.send_message(message.from_user.id, 'Кажется, Вы ошиблись. Попробуйте снова!')
        bot.send_message(message.from_user.id, "Выберите модель. Для этого напишите /model1 или /model2")
        bot.register_next_step_handler(message, get_model)

def get_player(message):
    global a
    if message.text in df0['surname'].unique():
        a = message.text
        df1 = df0[lambda x: x['surname'] == a].reset_index()
        prediction = model.predict(pd.DataFrame([[df1.loc[0, 'pace'], df1.loc[0, 'shooting'], df1.loc[0, 'passing'],
                                                  df1.loc[0, 'dribbling'], df1.loc[0, 'defending'], df1.loc[0, 'physic']]]))
        bot.send_message(message.from_user.id, f"Вы выбрали {a} \n"
                                               f"\n"
                                               f"Показатели футболиста: \n"
                                               f"Pace: {df1.loc[0, 'pace']}\n"
                                               f"Shooting: {df1.loc[0, 'shooting']}\n"
                                               f"Passing: {df1.loc[0, 'passing']}\n"
                                               f"Dribbling: {df1.loc[0, 'dribbling']}\n"
                                               f"Defending: {df1.loc[0, 'defending']}\n"
                                               f"Physic: {df1.loc[0, 'physic']}\n"
                                               f"\n"
                                               f"Рейтинг футболиста в FIFA: {df1.loc[0, 'overall']} \n"
                                               f"Предсказываемый рейтинг: {prediction[0]}")
        bot.send_message(message.from_user.id, 'Вы можете выбрать другого футболиста, написав его фамилию, или другую модель, написав /model')
        bot.register_next_step_handler(message, get_player)

    elif message.text == '/model':
        bot.send_message(message.from_user.id, 'Выберите модель. Для этого напишите /model1 или /model2')
        bot.register_next_step_handler(message, get_model)
    else:
        bot.send_message(message.from_user.id, 'Такого футболиста нет в базе данных. Попробуйте снова!')
        bot.register_next_step_handler(message, get_player)

bot.polling(none_stop=True, interval=0)