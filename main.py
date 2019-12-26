from operator import itemgetter
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler, CommandHandler, conversationhandler
import pandas as pd
import numpy as np
import re


# 해커톤 채널 ID = -1001403049702
# 해커톤 그룹 ID = -330438385

api_key = '1020872802:AAF2Gm9sQo7jAxjiPexOx3pCua-w4G0S0lk' # 학생 봇 키
api_key2 = '901492688:AAFyZ--uCmd4nMkg_a3PLNUINgY5YR-oKa4' # 조교 봇 키

bot = telegram.Bot(token=api_key)                          # 학생 봇
bot2 = telegram.Bot(token=api_key2)                        # 조교 봇

updater = Updater(api_key)                                 # 학생 봇 업데이터
updater2 = Updater(api_key2)                               # 조교 봇 업데이터

updater.start_polling()                                    # 학생 봇에 주기적으로 텔레그램에 접근해서 메세지가 있다면 받아와라
updater2.start_polling()                                   # 조교 봇에 주기적으로 텔레그램에 접근해서 메세지가 있다면 받아와라

def build_button(text_list, callback_header = "") : # make button list
    button_list = []
    text_header = callback_header
    if callback_header != "" :
        text_header += ","

    for text in text_list :
        button_list.append(InlineKeyboardButton(text, callback_data=text_header + text))

    return button_list

def build_menu(buttons, n_cols, header_button=None, footer_buttons=None):
    menu = [buttons[i:i+n_cols] for i in range (0, len(buttons), n_cols)]
    if header_button:
        menu.insert(0, header_button)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def handler(bot, update):
    global solveNum  # 현재 풀고 있는 문제의 번호
    global nowSolve  # 현재 풀고 있는 문제의 답안


    text = update.message.text       # 보낸 메세지는 text에 저장된다
    sejongBot = update.message.chat_id # chat_id : 연결고리

    index = findNum(text)

    if index == -1:
        bot.send_message(chat_id=sejongBot, text='제가 모르는 문제예요.\n문제 번호를 다시 입력해주세요 ㅠㅠ.')
        return

    solveNum = int(index)
    nowSolve = solve[index-1] # 문제의 번호는 1번부터 시작한다. 1번을 입력했을 때 list의 0번 원소를 선택해야한다.
    bot.send_message(chat_id=sejongBot, text=str(index)+'번 문제의 오류 케이스를 빈도 순으로 알려드릴게요. 화이팅!')
    hint_num = 1
    for i in solve[index-1]:
        bot.send_message(chat_id=sejongBot, text = '힌트 ' + str(hint_num) + ': ' + i[0] + '\n이 힌트에 투표한 학생 수 : ' + str(i[1]))
        hint_num += 1

    button_list = build_button(["네", "아니오"])
    show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list)-1))
    update.message.reply_text("해결 하셨나요 ? 답변 부탁해요!", reply_markup = show_markup)

def callback(bot, update):
    global solveNum
    global nowSolve

    #sejongBot = update.callback_query.message.chat_id

    data_selected = update.callback_query.data
    indexList = []
    for i in range(0, len(nowSolve)):
        indexList.append(str(i+1))

    if '네' == data_selected:
         button_list = build_button(indexList)
         show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
         bot.edit_message_text(text="몇 번 케이스로 해결되셨나요?",
                               chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id,
                               reply_markup=show_markup)
    elif '아니오' == data_selected:

         bot.edit_message_text(text="미안해요.. 제가 더 노력할게요 ㅠㅠ.".format(update.callback_query.data),
                               chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
         bot.send_message(chat_id=update.callback_query.message.chat_id,
                           text='조교님한테 물어보고 다음에 알려드릴게요 !')
         bot2.send_message(chat_id=-330438385,
                           text= '@'+update.callback_query.from_user.username + ' 학생이 ' + str(solveNum)+'번 문제에 대해서 질문하고 있습니다.')
    else:
        nowSolve[int(data_selected)-1][1] += 1
        nowSolve.sort(key=lambda nowSolve: nowSolve[1], reverse = 1)
        #nowSolve = sorted(nowSolve, key=itemgetter(1), reverse=1)
        bot.edit_message_text(text="제가 도움이 되었다니 기뻐요.".format(update.callback_query.data),
                              chat_id=update.callback_query.message.chat_id,
                              message_id=update.callback_query.message.message_id)

def start_command(bot, update):
    sejongBot = update.message.chat_id  # chat_id : 연결고리
    bot.send_message(chat_id = sejongBot, text = "안녕하세요. \n세종대학교 SW ChatBot 조교 시스템 '소융대봇' 입니다 !"
                                                 "\n원하시는 문제의 번호를 입력해주시면 제가 알려드릴게요 !!"
                                                 "\n저는 지금 6개의 문제를 알고 있어요. 똑똑하죠 ?"
                                                 "\n소융대봇을 이용하는 방법이 궁금하시다면 \n/help 커맨드를 입력해주세요 !")
def help_command(bot, update):
    sejongBot = update.message.chat_id  # chat_id : 연결고리
    bot.send_message(chat_id = sejongBot, text = "저는 여러분의 코딩 실습을 도와줄 '소융대봇' 이예요."
                                                 "\n모르시는 문제의 번호를 알려주시면 \n해당 문제에 대해 제가 가지고 있는 정보를 알려드릴게요."
                                                 "\n저는 지금 6개의 문제를 알고 있어요!"
                                                 "\n예시) 소융대봇아 나 3번 문제 모르겠어 ㅠㅠ")

def findNum(text):
    number = re.findall('\d+', text)
    if not number:
        return -1
    elif 6 < int(number[0]):
        return -1
    else:
        number = int(number[0])
        return number


solve = [[['이렇게 저렇게 해보세요.', 0], ['이 케이스를 입력해보세요', 0], ['초기화는 잘 하셨나요?', 0]],
         [['초기화는 잘 하셨나요?', 0], ['반복문의 범위가 중요한 문제예요!', 0], ['이 케이스를 입력해보세요.', 0]],
         [['초기화는 잘 하셨나요?', 0], ['볼빨간 사춘기 노래를 들어보세요.', 0], ['조건문의 범위가 중요한 문제예요!', 0]],
         [['함수에서 변수의 값을 변경하는 방법을 알아보세요!', 0], ['이 케이스를 입력해보세요.', 0]],
         [['수식 관리가 중요한 문제예요!', 0], ['시간은 시, 분, 초 로 나눌 수 있어요 !', 0]],
         [['조건문의 범위가 중요한 문제예요!', 0], ['딘 노래를 들어보세요.', 0], ['이렇게 저렇게 해보세요.', 0]]]

updater.dispatcher.add_handler(MessageHandler(Filters.text, handler))   # 메세지가 입력되었을 때 불릴 핸들러
updater.dispatcher.add_handler(CallbackQueryHandler(callback))          # 버튼 클릭시 불릴 핸들러
updater.dispatcher.add_handler(CommandHandler('start', start_command))  # /start 커맨드 입력시 불릴 핸들러
updater.dispatcher.add_handler(CommandHandler('help',  help_command))   # /help 커맨드 입력시 불릴 핸들러
