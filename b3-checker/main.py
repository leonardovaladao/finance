# -*- coding: utf-8 -*-
"""
Created on Wed May 19 18:40:33 2021

@author: Leonardo Valadão
"""

import requests
from datetime import date
import pandas as pd
import numpy as np
import telebot
import matplotlib.pyplot as plt

TOKEN = '1720234893:AAFBGqr4kosQzjwOd7pJbfGvYHn7epSE2fE'
leo_id = 1570169277
bot = telebot.TeleBot(TOKEN)


first_string = "==================================\nAqui está a variação da sua carteira hoje!\n=================================="
bot.send_message(leo_id, first_string, parse_mode="Markdown")

today = str(date.today()).replace("-", "")

f = open("info.txt", "r")
acoes = f.readlines()
f.close()

acoes = [acao.split() for acao in acoes]
lista_acoes = [linha[0][:-1] for linha in acoes]
datas = [linha[1][:-1] for linha in acoes]
b_prices_unique = [float(linha[2][:-1]) for linha in acoes]
b_quant = [float(linha[3]) for linha in acoes]
b_prices = [i*j for i,j in zip(b_quant,b_prices_unique)]
b_total = sum(b_prices)
w = [b/b_total for b in b_prices]
    
json_acoes = [
    requests.get("https://www.okanebox.com.br/api/acoes/hist/"+acao+"/"+data+"/"+today).json()
    for acao,data
    in zip(lista_acoes, datas)
]

returns = []
c_prices = []
sm = Stock_Model(lista_acoes, datas[0], w)

for acao, j, data in zip(lista_acoes, json_acoes, datas):
    r = pd.DataFrame(j)["PREULT"].iloc[-1] / pd.DataFrame(j)["PREULT"].iloc[0] - 1
    returns.append(r)
    c_prices.append(pd.DataFrame(j)["PREULT"].iloc[-1])
    var_stocks = "Variação de {:s} entre {:s}/{:s}/{:s} e {:s}/{:s}/{:s}: {:.2f}%".format(acao,
                                                                                   data[-2:], 
                                                                                   data[4:6],
                                                                                   data[2:4],
                                                                                   today[-2:],
                                                                                   today[4:6],
                                                                                   today[2:4],
                                                                                   r*100)
    count_year = (( date.today() - date(int(data[0:4]), int(data[4:6]), int(data[-2:])) ).days) / 365
    var_ann = "Rentabilidade anualizada: {:.2f}%".format( (r*100)/count_year )
    bot.send_message(leo_id, var_stocks, parse_mode="Markdown")
    bot.send_message(leo_id, var_ann, parse_mode="Markdown")
    
    plt.figure()
    graph = plt.plot(
        pd.DataFrame(j)['PREULT'].dropna() / pd.DataFrame(j)['PREULT'].dropna().iloc[0],
        ls='--', lw=1
    )
    plt.grid(ls='--')
    plt.ylabel('Standartized price of stock')
    plt.xlabel('Days since first date')
    plt.title('Historical Prices: {:s}'.format(acao))
    plt.savefig("plot")
    with open("plot.png", "rb") as im:
        bot.send_photo(leo_id, im)
    bot.send_message(leo_id, "==================================", parse_mode="Markdown")
