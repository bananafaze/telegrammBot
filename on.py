## -*- coding: utf-8 -*-
import telebot
import sys
import pickle
import requests
from bs4 import BeautifulSoup

class user():
    def __init__(self, id, money):
        self.id = id
        self.money = money 

def norm(text):
    textnorm = '' 
    for i in text.lower():
        if i == ' ' or i == '\n':
            continue 
        textnorm += i
    return textnorm    

def biggest(list):
    global userlist 
    values = []
    owners = list 
    goodowners = []

    for i in list: 
        values.append(i.money)

    while len(owners) > 0:
        value_index = values.index( max(values) )
        goodowners.append(owners[value_index])
        values.pop(value_index)
        owners.pop(value_index)
    
    userlist = goodowners
    pickle.dump(userlist, open('database.pickle', 'wb'))

if int(input('Create user database?')) == 1:
    userlist = []
    pickle.dump(userlist, open('database.pickle', 'wb')) 

try:
    userlist = pickle.load(open('database.pickle', 'rb'))
    file = open('database.txt', 'r',encoding="utf-8").read()
    token = file[ file.index('[token]:[') + 9: file.index(']1') ]
    group_id = file[ file.index('[groupid]:[') + 11: file.index(']2')]
    text_welcome = file[ file.index('[text_welcome]:[') + 16: file.index(']3')]
    text_goodbye = file[ file.index('[text_goodbye]:[') + 16: file.index(']4')]
    channel_id = file[ file.index('[chanid]:[') + 10: file.index(']5')] 
    if int(input('Test')) == 1:
        print(token)
        print(group_id)
        print(text_welcome)
        print(text_goodbye)
        print(channel_id)
except Exception as e:
    print(e)
    file = open('database.txt', 'w')
    print('Пожалуйста, заполните \'базу данных\'')
    a = input()
    sys.exit()


bot = telebot.TeleBot(token)
print(u'Работа Начата')
@bot.message_handler(content_types = ['new_chat_members'])
def hello(message):
    try:
        if str(message.chat.id) == group_id:
            bot.send_message(group_id, text_welcome)
    except Exception as e:
        print(f"Произошла серьезная ошибка - {e}")

@bot.message_handler(content_types = ['left_chat_member'])
def bye(message):
    try:
        if str(message.chat.id) == group_id:
            bot.send_message(group_id, text_goodbye)
    except Exception as e:
        print(f"Произошла серьезная ошибка - {e}")

@bot.channel_post_handler()
def update(message):
    try:
        if str(message.chat.id) == channel_id:
            bot.forward_message(chat_id= group_id,  from_chat_id = message.chat.id, message_id = message.message_id)
            #работа с аккаунтами и их заработком 
            if message.entities == None:
                return
            if message.entities[0].type != 'text_mention':
                return
            text = norm(message.text)
            if '💰суммапополнения:' not in text:
                return 

            money = int(text[text.index('💰суммапополнения:') + 17: text.index('rub💵')])

            o = True
            for i in userlist:
                if i.id == message.entities[0].user.id: 
                    i.money += money 
                    o = False
                    print(i.id)
                    break
            if o == True:
                userlist.append(user(message.entities[0].user.id, money)) 

            biggest(userlist)
            return
    except Exception as e:
        print(f"Произошла серьезная ошибка - {e}")
   
@bot.message_handler( commands = ['top'])
def top(message):
    try:
        if str(message.chat.id) != group_id:
            return
        text1 = ''
        lenage = 10
        if len(userlist) < 10:
            lenage = len(userlist)
        for i in range(lenage):
            text1 += f"{i + 1}\.[ { bot.get_chat_member(user_id = userlist[i].id, chat_id = group_id).user.first_name } ](tg://user?id={userlist[i].id}) Заработал {userlist[i].money} RUB \n"
        if text1 != '':
            bot.send_message(group_id, text1, parse_mode='MarkdownV2')
        else:
            bot.send_message(group_id, "К сожалению, список пуст")
    except Exception as e:
        print(f"Произошла серьезная ошибка - {e}")

@bot.message_handler( commands = ['btc'])
def btc(message):
    try:
        if str(message.chat.id) != group_id:
            return 
        soup = BeautifulSoup(requests.get('https://www.rbc.ru/crypto/currency/btcusd').text, 'lxml')
        need = soup.find_all('div', {'class' : "chart__subtitle js-chart-value"})
        dell = norm(need[0].find_all('span')[0].text)
        texxt = norm(need[0].text)
        texxt = texxt.replace(dell, '') 
        bot.send_message(group_id, f"Актуальная цена биткоина ${texxt}")
    except Exception as e:
        print(f"Произошла серьезная ошибка - {e}")

bot.polling(none_stop=True, interval=0)


