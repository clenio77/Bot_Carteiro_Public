# -*- encoding: utf8 -*-
import telebot #biblioteca bot
import json
import urllib.request  # tratar urls
from bs4 import BeautifulSoup
import requests, sys
import unicodedata, unidecode
import geopandas as gpds
import geopy.geocoders
from telebot import util
import pandas as pd


token = '1314523673:AAEIOD2IOrtuUgBduENpN27fwb8SdjFnNLA'  # @botfather cdd_udia_bot


bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])  # recebo a msg start
def send_welcome(message):
    cid = message.chat.id  # recebo  o id da conversa
    msg = bot.reply_to(message, "Olá, esse é um bot desenvolvido  por Clênio Moura. \n"
                                "em caso de dúvida, mande email para clenioti@gmail.com \n")
    bot.send_message(cid, "Caso precise de ajuda, use a função /ajuda.")


@bot.message_handler(commands=['ajuda'])
def send_help(message):
    cid = message.chat.id  # id da conversa
    msg_help = bot.reply_to(message, "Você não se lembra das funções? \n Opção 1: /start - Inicia o bot"
                                     "\n Opção 2: /ajuda - lista as opções de funções "
                                     "\n Opção 3: /cep - pesquisa de endereço pelo cep"
                                     "\n Opção 4: /rua - pesquisa de endereço pelo nome da rua - ex: MG/UBERLÂNDIA/AFONSO PENA"
                                     "\n Opção 5: /rastrear - rastreio de objetos")
    bot.send_message(cid, "Caso ainda encontre dificuldades, entre em contato pelo email: clenioti@gmail.com ")


@bot.message_handler(commands=['cep'])  # mensagem digitada
def send_cep(message):
    # msg = bot.reply_to(message, """Digite o cep que deseja consultar: """)  # responde o comando /cep com uma mensagem
    cid = message.chat.id  # pegar o id da conversa
    # bot.register_next_step_handler(msg, send_cep_step)  # armazena a informação digitada e passa para o proximo passo


@bot.message_handler(commands=['rua'])
def send_rua(message):
    msg = bot.reply_to(message,
                       """ Digite a rua que deseja pesquisar o cep, colocando uma '/' separando - ex: mg/Uberlândia/afonso pena""")
    cid = message.chat.id
    bot.register_next_step_handler(msg, send_rua_step)

    # state = bot.reply_to(message, "digite o estado que deseja pesquisar: ")
    # cidade = bot.reply_to(message,'digite a cidade que deseja pesquisar: ')
    # rua = bot.reply_to(message, 'digite a rua que deseja pesquisar: ')
    # bot.register_next_step_handler(state, cidade, rua, send_rua_step)


def send_rua_step(message):
    cid = message.chat.id
    # print(type(message))
    msg = message.text
    msg_limpa = str(unidecode.unidecode(msg))
    # print(msg_limpa)
    texto = str(msg_limpa).replace(' ', '%20').upper()
    # print('texto', texto)

    message_rua = texto
    print(message_rua)
    try:
        url = "https://viacep.com.br/ws/" + message_rua + "/json/"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())

        for end in data:
            cep = end['cep']
            logradouro = end['logradouro']
            complemento = end['complemento']
            bairro = end['bairro']
            localidade = end['localidade']
            uf = end['uf']

            bot.send_message(cid, "CEP: " + cep +
                             "\nLogragouro: " + logradouro +
                             "\nComplemento: " + complemento +
                             "\nBairro: " + bairro +
                             "\nLocalidade: " + localidade +
                             "\nUF: " + uf)
    except:
        bot.send_message(cid, "formato errado - precisa ser nesse formato - ex: afonso+pena")


def send_cep_step(message):
    cid = message.chat.id  # pegar o id da conversa
    mensagem_cep = message.text  #

    try:
        url = "https://viacep.com.br/ws/" + mensagem_cep + "/json/"
        response = urllib.request.urlopen(url)  # abrir a url que coloquei, que seria o json
        data = json.loads(response.read())  # carrega o json e ler os valores do json

        cep = data['cep']
        logradouro = data['logradouro']
        complemento = data['complemento']
        bairro = data['bairro']
        localidade = data['localidade']
        uf = data['uf']
        bot.send_message(cid, "CEP: " + cep +
                         "\nLogragouro: " + logradouro +
                         "\nComplemento: " + complemento +
                         "\nBairro: " + bairro +
                         "\nLocalidade: " + localidade +
                         "\nUF: " + uf)
    except:
        bot.send_message(cid, "cep invalido")


# função de rastreamento
@bot.message_handler(commands=['rastrear'])
def rastrear(message):
    msg = bot.reply_to(message, "Digite o código de rastreamento")
    cid = message.chat.id
    bot.register_next_step_handler(msg, send_rastreio_step)


def send_rastreio_step(message, horas=[], eventos=[]):
    # Sending Post
    cid = message.chat.id
    codigo = message.text
    rastreio = requests.post('https://www2.correios.com.br/sistemas/rastreamento/resultado.cfm',
                             data={'Objetos': codigo}).text
    soup = BeautifulSoup(rastreio, "lxml")
    # Scraping
    for table in soup.find_all('table', class_='listEvent sro'):
        for hora in table.find_all('td', class_='sroDtEvent'):
            horas.append(hora.text.replace('\n', '').replace('      ', ''))
        for evento in table.find_all('td', class_='sroLbEvent'):
            eventos.append(evento.text.replace("\t", "").replace("\r", "").replace("\n", " ").replace('  ', ''))
        # Printing

        if (len(horas) < 1):
            bot.send_message(cid, 'Número de rastreio ' + codigo + ' incorreto ou inexistente !' + '\n')
        else:
            bot.send_message(cid,
                             '||=========' + codigo + ' ==========||')
            print('\n')
            for x in range(0, len(horas)):
                bot.send_message(cid, '⦿ [' + horas[x] + '] » ' + eventos[x])
            print('\n')
        # Clearing Lists
        horas.clear()
        eventos.clear()

        # def main():
        horas = []
        eventos = []

        if len(sys.argv) <= 1:
            cod_rastreio = []  # Items Tracking Code
            for x in range(0, len(cod_rastreio)):
                rastreio(cod_rastreio[x], horas, eventos)
        else:
            for z in range(1, len(sys.argv)):
                rastreio(sys.argv[z], horas, eventos)


@bot.message_handler(commands=['local'])
def local(message):
    msg = bot.reply_to(message, "Digite o endereço para obter os pontos de localização: ")
    cid = message.chat.id
    bot.register_next_step_handler(msg, send_local_step)


def send_local_step(message):
    cid = message.chat.id
    msg = message.text
    dado = gpds.tools.geocode(msg, provider="nominatim", user_agent="Intro Geocode")
    bot.send_message(cid, dado['geometry'])


bot.polling()
