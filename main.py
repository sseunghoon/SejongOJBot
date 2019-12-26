from operator import itemgetter
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler, CommandHandler, ConversationHandler
from emoji import emojize
import pandas as pd
import numpy as np
import re
import csv


# 해커톤 채널 ID = -1001403049702
# 해커톤 그룹 ID = -330438385

api_key = '1020872802:AAF2Gm9sQo7jAxjiPexOx3pCua-w4G0S0lk' # 학생 봇 키
api_key2 = '901492688:AAFyZ--uCmd4nMkg_a3PLNUINgY5YR-oKa4' # 조교 봇 키

bot = telegram.Bot(token=api_key)                          # 학생 봇
bot2 = telegram.Bot(token=api_key2)                        # 조교 봇

updater = Updater(api_key)                                 # 학생 봇 업데이터
#updater2 = Updater(api_key2)                               # 조교 봇 업데이터

updater.start_polling()                                    # 학생 봇에 주기적으로 텔레그램에 접근해서 메세지가 있다면 받아와라
#updater2.start_polling()                                   # 조교 봇에 주기적으로 텔레그램에 접근해서 메세지가 있다면 받아와라

NUMBER = range(1)
FIRST, SECOND, THIRD, FOURTH = range(4)
ONE,TWO = range(2)

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
        bot.send_message(chat_id=sejongBot, text=emojize('제가 도움을 드릴 수가 없어요\n유효한 문제번호를 입력해주세요:sweat_smile:',use_aliases=True))
        return

    solveNum = int(index)
    nowSolve = data[index-1] # 문제의 번호는 1번부터 시작한다. 1번을 입력했을 때 list의 0번 원소를 선택해야한다.
    bot.send_message(chat_id=sejongBot, text=emojize(str(index)+'번 문제의 오류 케이스를 빈도 순으로 알려드릴게요. 파이팅!:clap:',use_aliases=True))
    hint_num = 1
    for i in data[index-1]:
        bot.send_message(chat_id=sejongBot, text = '힌트 ' + str(hint_num) + ': ' + i[0] + '\n이 힌트에 투표한 학생 수 : ' + str(i[1]))
        hint_num += 1

    button_list = build_button(["네", "아니오"])
    show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list)-1))
    update.message.reply_text("해결 하셨나요 ? 답변 부탁해요!", reply_markup = show_markup)
    return FIRST
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
         return SECOND
    elif '아니오' == data_selected:
         button_list = build_button(["1", "2", "3", "4", "5"])
         show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))

         bot.edit_message_text(text=emojize("미안해요:cry:",use_aliases=True).format(update.callback_query.data),
                               chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
         bot.send_message(chat_id=update.callback_query.message.chat_id,
                           text=emojize("조교님한테 더 배워올테니 다음에 꼭 다시 질문해주세요:smiley:",use_aliases=True))
         bot.send_message(text="난이도를 평가해주세요",
                               chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id,
                               reply_markup=show_markup)
         bot2.send_message(chat_id=-330438385,
                           text= '@'+update.callback_query.from_user.username + ' 학생이 ' + str(solveNum)+'번 문제에 대해서 질문하고 있습니다.')

         return FOURTH
    else:
        button_list = build_button(["1", "2", "3", "4", "5"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        nowSolve[int(data_selected)-1][1] += 1
        nowSolve.sort(key=lambda nowSolve: nowSolve[1], reverse = 1)
        bot.edit_message_text(text=emojize("제가 도움이 되었다니 다행이에요:satisfied:", use_aliases=True).format(update.callback_query.data),
                              chat_id=update.callback_query.message.chat_id,
                              message_id=update.callback_query.message.message_id)
        bot.send_message(text="난이도를 평가해주세요",
                         chat_id=update.callback_query.message.chat_id,
                         message_id=update.callback_query.message.message_id,
                         reply_markup=show_markup)
        return FOURTH

def callback2(bot, update):
    global solveNum
    data_selected = update.callback_query.data
    bot.edit_message_text(text=("감사합니다 !"),
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id)
    with open('difficulty.csv','a',newline='') as f:
        makeWrite = csv.writer(f)
        data2 = []
        data2 = [update.callback_query.from_user.username, solveNum, int(data_selected)]
        makeWrite.writerow(data2)

    print(data_selected)
    return -1


def start_command(bot, update):
    sejongBot = update.message.chat_id  # chat_id : 연결고리
    bot.send_message(chat_id=sejongBot, text=emojize("세종대학교 SW ChatBot 조교 시스템 '소융대봇' 을 찾아주셔서 고마워요:innocent:"
                                                     "\n도움을 원하시는 문제의 번호를 입력해주세요!"
                                                     "\n이용하는 방법이 궁금하시다면 \n/help 커맨드를 입력해주세요:smiley:", use_aliases=True))
def help_command(bot, update):
    sejongBot = update.message.chat_id  # chat_id : 연결고리
    bot.send_message(chat_id = sejongBot, text =emojize("저는 여러분의 코딩 실습을 도와줄 '소융대봇' 이예요."
                                                 "\n도움이 필요한 문제의 번호를 알려주시면\n해당 문제의 힌트를 제공해드립니다:wink:."
                                                 "\n한 번에 한 문제씩 입력해주시면 고마울 것 같아요!"
                                                 "\n저는 지금 30개의 문제를 알고 있어요!"
                                                 "\n예시) 소융대봇아 나 3번 문제 좀 도와줘 ㅠㅠ",use_aliases=True))
def end_command(bot, update):
    with open('myData.csv','w',newline='') as f:
        makeWrite = csv.writer(f)

        for value in data:
            data2=[]
            for cell in value:
                data3=cell[0]+':'+str(cell[1])
                data2.append(data3)

            makeWrite.writerow(data2)
    sejongBot = update.message.chat_id  # chat_id : 연결고리
    bot.send_message(chat_id=sejongBot, text=emojize("여러분의 솔루션이 저장되었어요! \n오늘 실습하시느라 고생하셨습니다:wink:.", use_aliases=True))

def call_command(bot, update):
    sejongBot = update.message.chat_id  # chat_id : 연결고리
    bot.send_message(chat_id=sejongBot, text=("조교님을 호출해드릴게요 !"))
    bot2.send_message(chat_id=-330438385,
                      text='@' + update.message.from_user.username + ' 학생이 조교님을 찾고 있어요!')

def bestAnswer_command(bot, update):
    sejongCoBot = update.message.chat_id  # chat_id : 연결고리
    bot.send_message(chat_id=sejongCoBot, text="세종대학교 소융대 조교봇입니다."
                                               "\n모범답안을 확인할 문제의 번호를 입력해주세요.")
    return NUMBER
def done_command(bot, update):
    sejongCoBot = update.message.chat_id
    bot.send_message(chat_id=sejongCoBot,
                     text = "항목 입력을 종료하겠습니다.")
    return -1

def number(bot,update):
    sejongCoBot = update.message.chat_id
    text = update.message.text

    index = findNum(text)

    if index == -1:
        bot.send_message(chat_id=sejongCoBot,
                         text="저장되어 있는 문제의 번호를 입력해주세요.")
        return

    with open("bestAnswer.csv", 'r') as f:
        reader2 = csv.reader(f)
        answerList=list(reader2)

    TF=int(answerList[index-1][1])

    if(TF):
        bot.send_message(chat_id=sejongCoBot, text=answerList[index-1][0])
    else:
        bot.send_message(chat_id=sejongCoBot, text="세종대학교 소융대 조교봇입니다."
        "                                           해당 문제는 현재 모범 답안을 볼 수 없습니다.")

    return -1

def pearsonR(s1, s2):
    s1_c = s1 - s1.mean()
    s2_c = s2 - s2.mean()
    return np.sum(s1_c * s2_c) / np.sqrt(np.sum(s1_c ** 2) * np.sum(s2_c ** 2))

def relevant_command(bot,update):
    sejongCoBot = update.message.chat_id  # chat_id : 연결고리
    bot.send_message(chat_id=sejongCoBot, text="연관된 문제가 궁금하신가요?"
                                               "\n연관 문제를 확인할 문제의 번호를 입력해주세요.")
    return ONE

def relevant_one(bot,update):
    global rel_list
    sejongCoBot = update.message.chat_id
    text = update.message.text
    input=findNum(text)

    diff.rating = pd.to_numeric(diff.rating)  # 문자열을 숫자로 변환
    #diff.user_id = pd.to_numeric(diff.user_id)

    data = pd.merge(diff, meta, on='que_id', how='inner')
    matrix = data.pivot_table(index='user_id', columns='que_id', values='rating')

    GENRE_WEIGHT = 1
    input_genres = meta[meta['que_id'] == input]['genre'].iloc(0)[0]
    rel_list=[]
    similar_genre=True
    for que in matrix.columns:
        if que == input:
            continue
        cor = pearsonR(matrix[input], matrix[que])

        if similar_genre and len(input_genres) > 0:
            temp_genres = meta[meta['que_id'] == que]['genre'].iloc(0)[0]
            same_count = np.sum(np.isin(input_genres, temp_genres))
            cor += (GENRE_WEIGHT * same_count)

        if np.isnan(cor):
            continue
        else:
            rel_list.append((que, '{:.2f}'.format(cor), temp_genres))

    rel_list.sort(key=lambda r: r[1], reverse=True)
    cnt = 1
    for i in rel_list:
        if cnt > 3:
            break
        bot.send_message(chat_id=sejongCoBot, text = str(cnt) + '. 연관된 문제는 '+ str(i[0])+'번, 상관 계수는 ' + str(i[1]) + ' 입니다.')
        cnt += 1
    return -1

def findNum(text):
    number = re.findall('\d+', text)
    if not number:
        return -1
    elif 30 < int(number[0]):
        return -1
    else:
        number = int(number[0])
        return number

with open("myData.csv",'r') as f:

    # reader = 파일 전체 / data = 구조체 2차원 배열 / row = csv를 위에서 부터 한 행씩 불러온 것
    # cell = csv 상에서 한 칸 / struct = 구조체 1개 / data2 = 구조체로 이루어진 한 행
    reader = csv.reader(f)
    data = []
    for row in reader:
        data2=[]
        for cell in row:
            struct=[]
            struct=cell.split(':')
            struct[1]=int(struct[1])
            data2.append(struct)
        data.append(data2)

meta = pd.read_csv('question.csv')
diff = pd.read_csv('difficulty.csv')

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('bestAnswer', bestAnswer_command)],
    states={
     NUMBER: [MessageHandler(Filters.text, number)]
    },
    fallbacks=[CommandHandler('done', done_command)]
)

conv_handler2 = ConversationHandler(
    entry_points=[MessageHandler(Filters.text, handler)],
    states={
        FIRST:  [CallbackQueryHandler(callback)],      # 네, 아니오 버튼
        SECOND: [CallbackQueryHandler(callback)],      # (네라면) 케이스 버튼
        THIRD:  [CallbackQueryHandler(callback)],      # (아니오라면) 조교에게 전달
        FOURTH: [CallbackQueryHandler(callback2)]     # (케이스가 눌렸다면) 점수를 입력해주세요 1 ~ 5
    },
    fallbacks=[CommandHandler('done', done_command)]
)
conv_handler3 = ConversationHandler(
    entry_points=[CommandHandler('relevant', relevant_command)],
    states={
        ONE:[MessageHandler(Filters.text, relevant_one)],
    },
    fallbacks=[CommandHandler('done', done_command)]
)
updater.dispatcher.add_handler(conv_handler3)
updater.dispatcher.add_handler(conv_handler)
updater.dispatcher.add_handler(conv_handler2)

#updater.dispatcher.add_handler(MessageHandler(Filters.text, handler))   # 메세지가 입력되었을 때 불릴 핸들러
#updater.dispatcher.add_handler(CallbackQueryHandler(callback))          # 버튼 클릭시 불릴 핸들러
updater.dispatcher.add_handler(CommandHandler('start', start_command))  # /start 커맨드 입력시 불릴 핸들러
updater.dispatcher.add_handler(CommandHandler('help',  help_command))   # /help 커맨드 입력시 불릴 핸들러
updater.dispatcher.add_handler(CommandHandler('call',  call_command))
updater.dispatcher.add_handler(CommandHandler('end',  end_command))