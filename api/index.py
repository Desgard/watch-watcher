from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import json
import os
import re
from datetime import datetime

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

app = Flask(__name__)

# parse


def parse_watch_info(info_str):
    # 正则表达式模式
    url_pattern = r'https?://[^\s]+'
    watch_id_pattern = r'\b\d+\b'
    date_pattern = r'\b\d{4}\.\d{1,2}\b'
    condition_pattern = r'未使用|新品|中古'  # 根据实际情况调整
    additional_info_pattern = r'フルセット'  # 根据实际情况调整
    price_pattern = r'金額\d+万?'

    # 使用正则表达式查找匹配项
    url = re.search(url_pattern, info_str)
    watch_id = re.search(watch_id_pattern, info_str)
    date_str = re.search(date_pattern, info_str)
    condition = re.search(condition_pattern, info_str)
    additional_info = re.search(additional_info_pattern, info_str)
    price_str = re.search(price_pattern, info_str)

    # 解析和转换
    date_obj = datetime.strptime(date_str.group(), "%Y.%m").date() if date_str else None
    price = None
    if price_str:
        price_num = int(re.sub(r'\D', '', price_str.group()))
        if '万' in price_str.group():
            price = price_num * 10000
        else:
            price = price_num

    return {
        "url": url.group() if url else None,
        "id": watch_id.group() if watch_id else None,
        "date": date_obj.isoformat() if date_obj else None,  # 将日期转换为字符串
        "condition": condition.group() if condition else None,
        "note": additional_info.group() if additional_info else None,
        "price": price
    }


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

    # if event.message.type != "text":
    #     return

    app.logger.info("reply: " + event.message.text)

    result = parse_watch_info(event.message.text)

    try:
        if result.get('url') is None:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Can't parse watch info"))
        else:
            msg_res = ""
            msg_res += str(json.dumps(result, indent=2, ensure_ascii=False))
            msg_res += "\n[WatchWatcher] 录入成功"

            if result.get('price') is not None:
                # 计算汇率价格
                msg_res += "\n[WatchWatcher] 获取实时汇率 100 JPY = 5.0019 CNY"
                price_in_jpy = result['price']  # 例如，watch_info 是之前解析的字典
                # 实时汇率：100 JPY = 5.0019 CNY
                exchange_rate = 5.0019 / 100

                # 计算转换后的人民币价格
                price_in_cny = price_in_jpy * exchange_rate

                # 回复消息
                msg_res += f"\n[WatchWatcher] 转化价格是 {price_in_cny:.2f} CNY"

                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=msg_res)
                )

    except KeyError:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="error"))


if __name__ == "__main__":
    app.run()


