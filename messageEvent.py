import asyncio
import telegram

token = "enter token bot here"
chatId = "enter chat id here"

async def sendMessage(message):
    bot = telegram.Bot(token=token)
    await bot.send_message(chat_id=chatId, text=message)
