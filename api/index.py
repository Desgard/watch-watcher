from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from parse import parse_watch_info

import json
import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

app = Flask(__name__)

# domain root


# domain root
@app.route('/')
def home():
    return 'Hello, World!'


@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if event.message.type != "text":
        return

    app.logger.info("reply: " + event.message.text)

    result = parse_watch_info(event.message.text)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=json.dumps(result, indent=2)))


if __name__ == "__main__":
    app.run()
