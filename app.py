
from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
)

import urllib
import json
import re

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


pokemon = open('./pokedex.json','r')
pokemon_list = json.load(pokemon)



u_dict = {'Normal':'ノーマル',
          'Fire':'ほのお',
          'Water':'みず' ,
          'Grass':'くさ' ,
          'Water':'みず' ,
          'Electric':'でんき' ,
          'Ice':'こおり' ,
          'Fighting':'かくとう' ,
          'Poison':'どく' ,
          'Ground':'じめん' ,
          'Flying':'ひこう' ,
          'Psychic':'エスパー' ,
          'Bug':'むし' ,
          'Rock':'いわ' ,
          'Ghost':'ゴースト' ,
          'Dragon':'ドラゴン' ,
          'Dark':'あく' ,
          'Steel':'はがね',
          'Fairy':'フェアリー' 
         }
def type_to_jn(types):
    jn_types = []
    for type in types:
        for word, read in u_dict.items():
            if(word == type):
                jn_types.append(type.replace(word, read))
    return jn_types
def get_status(list):
    no = '図鑑No.:' + str(list['id']) + '\n'
    name = '名前:' + str(list['name']['japanese']) + '\n'
    type = 'タイプ:' + str(type_to_jn(list['type'])) + '\n'
    HP = 'H:' + str(list['base']['HP']) + '\n'
    ATK = 'A:' + str(list['base']['Attack']) + '\n'
    DEF = 'B:' + str(list['base']['Defense']) + '\n'
    STK = 'C:' + str(list['base']['Sp. Attack']) + '\n'
    SEF = 'D:' + str(list['base']['Sp. Defense']) + '\n'
    SPD = 'S:' + str(list['base']['Speed']) + '\n'
    TOTAL = 'TOTAL:' + str(list['base']['HP']+list['base']['Attack']+list['base']['Defense']+list['base']['Sp. Attack']+list['base']['Sp. Defense']+list['base']['Speed'])
    return no+name+type+HP+ATK+DEF+STK+SEF+SPD+TOTAL

def get_tettei_kouryaku(pokemon_id):
    return "https://yakkun.com/swsh/zukan/n"+str(pokemon_id)

def cal_type_score(input_types):
    double_list_json = open('./double.json','r')
    half_list_json = open('./half.json','r')
    zero_list_json = open('./zero.json','r')

    double_list = json.load(double_list_json)
    half_list = json.load(half_list_json)
    zero_list = json.load(zero_list_json)

    keys = list(u_dict.values())
    values = [1 for i in range(len(keys))]
    types_score = dict(zip(keys, values))

    input_types = input_types.split()
    for type in input_types:
        for i in range(len(double_list['types'])):
            if (type in double_list['types'][i]):
                for double_types in double_list['types'][i].values():
                    for double_type in double_types:
                        types_score[double_type] *= 2
        for i in range(len(half_list['types'])):
            if (type in double_list['types'][i]):
                for half_types in half_list['types'][i].values():
                    for half_type in half_types:
                        types_score[half_type] *= 0.5
        for i in range(len(zero_list['types'])):
            if (type in zero_list['types'][i]):
                for zero_types in zero_list['types'][i].values():
                    for zero_type in zero_types:
                        types_score[zero_type] *= 0
    return types_score

def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]

def export_type_score(types_score):
    type_score_message ="タイプ相性"
    four_times_types = get_keys_from_value(types_score, 4)
    if len(four_times_types)!=0 :
        type_score_message += "\n-----4倍-----\n"
        type_score_message += '\n'.join(four_times_types)
    two_times_types = get_keys_from_value(types_score, 2)
    if len(two_times_types)!=0 :
        type_score_message += "\n-----2倍-----\n"
        type_score_message += '\n'.join(two_times_types)
    half_types = get_keys_from_value(types_score, 0.5)
    if len(half_types)!=0 :
        type_score_message += "\n-----0.5倍-----\n"
        type_score_message += '\n'.join(half_types)
    quarter_types = get_keys_from_value(types_score, 0.25)
    if len(quarter_types)!=0 :
        type_score_message += "\n-----0.25倍-----\n"
        type_score_message += '\n'.join(quarter_types)
    zero_types = get_keys_from_value(types_score, 0)
    if len(zero_types)!=0 :
        type_score_message += "\n-----0倍-----\n"
        type_score_message += '\n'.join(zero_types)
    return type_score_message

def search_pokemon_data(message):
    reply_message = ""
    for i in range(len(pokemon_list)):
        if(pokemon_list[i]['name']['japanese']==message):
            search_info = get_status(pokemon_list[i])
            search_info += "じゃぞ！！\n\n"
            pokemon_url = str(pokemon_list[i]['name']['japanese']) + "のポケモン徹底攻略のページじゃぞ！\n" + get_tettei_kouryaku(pokemon_list[i]['id'])
            reply_message = search_info + pokemon_url + "\nポケモンゲットじゃぞ！！！"
            break
    
    return reply_message


@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # message = "そんなポケモンはおらん！！！！"
    message = search_pokemon_data(event.message.text)
    if(len(message) >= 1):
        line_bot_api.reply_message(
        event.reply_token,
        [TextSendMessage(text=message)]
        )
        # if(pokemon_list[i]['name']['japanese']==event.message.text):
        #     search_info = get_status(pokemon_list[i])
        #     search_info += "じゃぞ！！\n\n"
        #     pokemon_url = str(pokemon_list[i]['name']['japanese']) + "のポケモン徹底攻略のページじゃぞ！\n" + get_tettei_kouryaku(pokemon_list[i]['id'])
        #     message = search_info + pokemon_url + "\nポケモンゲットじゃぞ！！！"
        #     exit
    # image_message = ImageSendMessage(
    #     original_content_url="https://2.bp.blogspot.com/-Ten5Y3wa1s8/VMItaHv6ikI/AAAAAAAAqtU/HVC0kvCwPYo/s800/character_hakase.png", #JPEG 最大画像サイズ：240×240 最大ファイルサイズ：1MB(注意:仕様が変わっていた)
    #     preview_image_url="https://2.bp.blogspot.com/-Ten5Y3wa1s8/VMItaHv6ikI/AAAAAAAAqtU/HVC0kvCwPYo/s800/character_hakase.png" #JPEG 最大画像サイズ：1024×1024 最大ファイルサイズ：1MB(注意:仕様が変わっていた)
    #     )
    


    elif([event.message.text.split()[i] in u_dict.values() for i in range(len(event.message.text.split()))].count(True) >= 1):
        types_score = cal_type_score(event.message.text)
        type_score_message = export_type_score(types_score)
        line_bot_api.reply_message(
        event.reply_token,
        [TextSendMessage(text=type_score_message)]
        )
    else:
        data = {
            "apikey": os.environ["YOUR_TALK_API_KEY"],
            "query": event.message.text ,
        }
    
        data = urllib.parse.urlencode(data).encode("utf-8")
        with urllib.request.urlopen("https://api.a3rt.recruit.co.jp/talk/v1/smalltalk", data=data) as res:
            #response = res.read().decode("utf-8")
            reply_json = json.loads(res.read().decode("unicode_escape"))
    
            if reply_json['status'] == 0:
                reply = reply_json['results'][0]['reply']
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply + "じゃぞ！"))

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)