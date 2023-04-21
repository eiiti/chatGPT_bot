import os
import openai
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import streamlit as st

# LINE APIの初期化
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

# OpenAI APIの初期化
openai.api_key = os.environ["OPENAI_API_KEY"]

# Streamlitアプリケーションのコード
st.title("LINE Bot with OpenAI ChatGPT")

# ChatGPT APIを呼び出して返信を生成する関数
def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = response.choices[0].text.strip()
    return message

# メッセージイベントの処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # ユーザーからのメッセージを取得
    user_message = event.message.text

    # OpenAI APIを使って、ユーザーのメッセージに対する返信を生成
    prompt = f"ユーザー: {user_message}\nChatGPT:"
    gpt_response = generate_response(prompt)

    # 返信をLINE botからユーザーに送信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=gpt_response)
    )

# Webhookエンドポイントの処理
def webhook(request):
    signature = request.headers["X-Line-Signature"]

    try:
        handler.handle(request.get_data(as_text=True), signature)
    except InvalidSignatureError:
        print("Invalid signature. Check your channel access token/channel secret.")
        abort(400)

    return "OK"

# StreamlitでWebhookエンドポイントを作成
if "server.context" in st.experimental_get_query_params():
    st.experimental_set_query_params()
    st.write(webhook(st.experimental_get_request()))
