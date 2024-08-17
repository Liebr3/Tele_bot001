from config import *
import os
import sys
import telebot
import time
from bs4 import BeautifulSoup
import requests
from selenium_to_bot import iniciar_webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from requests_html import HTMLSession
from flask import Flask, request  # to create local web server
from pyngrok import ngrok, conf  # to create tunneling bt host and server
from waitress import serve #execute server in production mode




session = HTMLSession()
# instance for telegram API
bot = telebot.TeleBot(TELEGRAM_TOKEN)
# instance for Flask web server
web_server = Flask(__name__)
# Manage POST requert from server
@web_server.route('/', methods=['POST'])
def webhook():
    # if request POST is JSON
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode('UTF-8'))
        bot.process_new_updates([update])
        return "OK", 200


@bot.message_handler(commands=["start", "ayuda", "help"])
def cms_start(message):                        # da la bienvenida al usuario del bot
    bot.reply_to(message, "Bienvenido al Liebre BOT" + "\n"
                          "Te doy el precio de Bitcoin o Ethereum en tiempo real" + "\n"
                          "con un desfase de + - 7 minutos" + "\n")


@bot.message_handler(commands=["btc", "BTC", "bitcoin", "eth", "ETH", "ethereum", "clp"])
def bitcoin_price_command(message):
    # mensaje = str(message)
    mensaje_text = message.text
    # print("mensaje como str: ", mensaje)
    print(" text from user: ", mensaje_text)
    if mensaje_text in ['/btc', '/BTC', '/bitcoin']:
        url = "https://coinmarketcap.com/currencies/bitcoin/"
        print("precio de bitcoin")
        bot.reply_to(message, crypto_currency(url) + " USD")
    elif mensaje_text in ['/eth', '/ETH', '/ethereum']:
        url = "https://coinmarketcap.com/currencies/ethereum/"
        print("precio de ethereum")
        bot.reply_to(message, crypto_currency(url) + " USD")
        # input("press enter...")
    elif mensaje_text.lower() in ["/clp"]:
        print("precio de bitcoin en clp")
        bot.reply_to(message, usd_clp() + " CLP")


@bot.message_handler(content_types=["text"])
def answ_text(message):
    salutes = ['hola', 'buenos dias', 'buen dia', 'buenas tardes', 'que tal']
    if message.text.lower() in salutes:
        bot.send_message(message.chat.id, "Hola, bienvenid@ al BOT :D")
    elif '/' in message.text[0]:
        bot.send_message(message.chat.id, "Commando no encontrado..."
                                          "Para una lista de comandos usa /help")
    else:
        bot.send_message(message.chat.id, "Bienvenido al Liebre BOT" + "\n"
                          "Te doy el precio de Bitcoin o Ethereum en tiempo real" + "\n"
                          "con un desfase de + - 7 minutos" + "\n")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
def beautiful(url):
    while True:
        try:
            page = requests.get(url)
            break
        except requests.exceptions.ConnectionError:
            print("Connection Error....the program is waiting for a moment to try again...")
            time.sleep(0.1)
    html_from_page = page.text
    soup = BeautifulSoup(html_from_page, 'lxml')
    return soup

def usd_clp():
    url ="https://wise.com/es/currency-converter/usd-to-clp-rate"
    price = beautiful(url).find('h3', class_="cc__source-to-target").find('span', class_="text-success").text
    urlbtc = "https://coinmarketcap.com/currencies/bitcoin/"
    #### string_to_int function goes here
    split_price = price.split(',')
    price = ".".join(split_price)
    btc_price = string_to_int(bitcoin_price(urlbtc))
    # split_bitcoin_price = btc_price.split(',')
    # btc_price = "".join(split_bitcoin_price)
    # btc_price = btc_price[1:(len(btc_price))]
    btc_price = int(float(price)* float(btc_price))
    clp_price = '$' + str(format_millar(btc_price))
    return clp_price

def string_to_int(number):
    split_bitcoin_price = number.split(',')
    btc_price = "".join(split_bitcoin_price)
    btc_price = btc_price[1:(len(btc_price))]
    return btc_price


def format_millar(number):
    newformat = '{:,}'.format(number).replace(',','.')
    return newformat


def bitcoin_price(url):
    price = beautiful(url).find('div', class_='sc-65e7f566-0 cNOiPd coin-stats-header').find('span', class_='sc-65e7f566-0 clvjgF base-text').text
    # price = beautiful(url).find('div', class_='sc-65e7f566-0 hhlNLK coin-converter').find('input', pattern='/^-?d+.?d*$/')
    return price


def crypto_currency(url):
    cryptocoin_price = bitcoin_price(url)
    return cryptocoin_price


def whale_alert():
    url = "https://coinmarketcap.com/currencies/bitcoin/"
    bitcoin_now = bitcoin_price(url)
    time.sleep(420)
    bitcoin_after = bitcoin_price(url)
    print("precio 1: ", bitcoin_now)
    print("precio 2: ", bitcoin_after)
    price_action = bitcoin_now - bitcoin_after
    precios = {
        'precio1': bitcoin_now,
        'precio2': bitcoin_after
    }
    return precios
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "Descripción del bot"),
        telebot.types.BotCommand("/btc", "Precio de Bitcoin en USD"),
        telebot.types.BotCommand("/eth", "Precio de Ethereum  en USD"),
        telebot.types.BotCommand("/clp", "Precio de bitcoin en CLP"),
    ])
    print(usd_clp())
    print('iniciando el bot...')
    # define path config file of ngrok
    conf.get_default().config_path = "./config_ngrok.yml"
    # region "sa" = south america
    conf.get_default().region = "sa"
    # credentials file from ngrok
    ngrok.set_auth_token(NGROK_TOKEN)
    #create tunnel https port 5000
    ngrok_tunel = ngrok.connect(5000, bind_tls=True)
    # urls from created tunnel
    ngrok_url = ngrok_tunel.public_url
    print("url_ngrok: ", ngrok_url)
    print("bot iniciado, ejecutando whale alert...")

    # print(whale_alert())
    # remove former webhook
    bot.remove_webhook()
    # littl pause
    time.sleep(1)
    # define webhook
    bot.set_webhook(url=ngrok_url)
    # start web server
    serve(web_server, host="0.0.0.0", port=5000)
    # print("bot iniciado, ejecutando whale alert...")

    # print(whale_alert())
