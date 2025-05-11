import time
import requests
from datetime import datetime

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from pprint import pprint

# from src.binance_api import get_binance_ticker_price

# Replace 'YOUR_TOKEN' with the token you obtained from BotFather
TOKEN = '6041794044:AAHdd2S1CSR9CVhr-TrduVETEUJr3uxbqxU'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your demo bot. Type /help to see available commands.')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('You can use the following commands:\n'
                              '/start - Start the bot\n'
                              '/help - Display help message\n'
                              '/echo <message> - Echo the provided message')

def echo(update: Update, context: CallbackContext, profits) -> None:
    prices = calculate_max_profit()
    update.message.reply_text(f'You said: {prices}')
    # update.message.reply_text(f'You said: {update.message.text}')
    # update.message.chat('ccol')


class get_coin_profit:
    def __init__(self):
        self.last_ticker = self.get_usdt_ticker()

    def get_usdt_ticker(self):
        new_ticker_price = []
        # ticker_price = get_binance_ticker_price()
        ticker_price = []
        for coin in ticker_price:
            if coin['symbol'].endswith('USDT'):
                new_ticker_price.append(coin)
        return new_ticker_price

    def calculate_max_profit(self):
        ticker_price = self.get_usdt_ticker()
        profits = {}
        for cur_ticker, last_ticker in zip(ticker_price, self.last_ticker):
            profit = (float(cur_ticker['price']) - float(last_ticker['price'])) / float(last_ticker['price'])
            profits[cur_ticker['symbol']] = profit
        sorted_profit = dict(sorted(profits.items(), key=lambda item: item[1], reverse=True))
        # print(sorted_profit)
        self.last_ticker = ticker_price
        return sorted_profit


def main(ProfitGetter) -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Register a message handler to echo messages
    sorted_profit = ProfitGetter.calculate_max_profit()
    best_profits = []
    n = 5
    for idx, (symbol, profit) in enumerate(sorted_profit.items()):
        if idx >= n:
            break
        best_profits.append(f'{symbol} -> {profit*100:.2f} %')
    print(Filters.text)
    print(best_profits)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop (Ctrl+C)
    updater.idle()


def send_msg(message_text):
    bot_token = TOKEN
    chat_id = "1745246461"

    # Set the API endpoint URL
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Set the payload data
    payload = {
        'chat_id': chat_id,
        'text': message_text
    }

    # Send the POST request
    response = requests.post(url, data=payload)

    # Print the response content
    print(response.text)

if __name__ == '__main__':
    while True:
        send_msg(message_text=f'Current time is {datetime.now()}')
        time.sleep(30*60)

    # ProfitGetter = get_coin_profit()
    # while True:
    #     sorted_profit = ProfitGetter.calculate_max_profit()
    #     best_profits = []
    #     n = 5
    #     for idx, (symbol, profit) in enumerate(sorted_profit.items()):
    #         if idx >= n:
    #             break
    #         best_profits.append(f'{symbol} -> {profit*100:.2f} %')
    #     pprint(best_profits)
    #     time.sleep(5)
    # # main(ProfitGetter)
