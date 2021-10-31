
from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

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

def get_status(list):
    no = '図鑑No.:' + str(list['id']) + '\n'
    name = '名前:' + str(list['name']['japanese']) + '\n'
    type = 'タイプ:' + str(list['type']) + '\n'
    HP = 'H:' + str(list['base']['HP']) + '\n'
    ATK = 'A:' + str(list['base']['Attack']) + '\n'
    DEF = 'B:' + str(list['base']['Defense']) + '\n'
    STK = 'C:' + str(list['base']['Sp. Attack']) + '\n'
    SEF = 'D:' + str(list['base']['Sp. Defense']) + '\n'
    SPD = 'S:' + str(list['base']['Speed']) + '\n'
    return no+name+type+HP+ATK+DEF+STK+SEF+SPD


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
    search_info = "そんなポケモンはおらん！！！！"
    for i in range(len(pokemon_list)):
        if(pokemon_list[i]['name']['japanese']==event.message.text):
            search_info = get_status(pokemon_list[i])
            exit
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=search_info+"じゃぞ！！\nポケモンゲットじゃぞ！！！"))

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)