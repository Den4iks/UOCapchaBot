# -*- coding: utf-8 -*-
import pyscreenshot as ImageGrab
import time
import numpy as np
import sys
import schedule
import cv2
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

sys.path.append('/usr/local/lib/python2.7/site-packages')
screen_size = None
screen_start_point = None
screen_end_point = None


# Сперва мы проверяем размер экрана и берём начальную и конечную точку для будущих скриншотов
def check_screen_size():
    print "Checking screen size"
    img = ImageGrab.grab()
    # img.save('temp.png')
    global screen_size
    global screen_start_point
    global screen_end_point
    # я так и не смог найти упоминания о коэффициенте в методе grab с параметром bbox, но на моем макбуке коэффициент составляет 2. то есть при создании скриншота с координатами x1=100, y1=100, x2=200, y2=200), размер картинки будет 200х200 (sic!), поэтому делим на 2
    coefficient = 2
    screen_size = (img.size[0] / coefficient, img.size[1] / coefficient)
    # берем примерно девятую часть экрана примерно посередине.
    screen_start_point = (screen_size[0], screen_size[1])
    screen_end_point = (screen_size[0], screen_size[1])
    print ("Screen size is " + str(screen_size))


def make_screenshot():
    print 'Capturing screen'
    screenshot = ImageGrab.grab(
        bbox=(0, 55, 810, 660))
    # сохраняем скриншот, чтобы потом скормить его в OpenCV
    screenshot_name = 'screens/uo_session' + str(int(time.time())) + '.jpg'
    screenshot.save(screenshot_name)
    return screenshot_name


def find_float(screenshot_name):
    print 'Looking for a float'
    for x in range(1, 2):
        # загружаем шаблон
        template = cv2.imread('template' + str(x) + '.jpg', 0)
        # загружаем скриншот и изменяем его на чернобелый
        src_rgb = cv2.imread(screenshot_name)
        src_gray = cv2.cvtColor(src_rgb, cv2.COLOR_BGR2GRAY)
        # берем ширину и высоту шаблона
        w, h = template.shape[::-1]
        # магия OpenCV, которая и находит наш темплейт на картинке
        res = cv2.matchTemplate(src_gray, template, cv2.TM_CCOEFF_NORMED)
        # понижаем порог соответствия нашего шаблона с 0.8 до 0.6, ибо поплавок шатается и освещение в локациях иногда изменяет его цвета, но не советую ставить ниже, а то и рыба будет похожа на поплавок
        threshold = 0.6
        # numpy фильтрует наши результаты по порогу
        loc = np.where(res >= threshold)
        # выводим результаты на картинку
        for pt in zip(*loc[::-1]):
            cv2.rectangle(src_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        # и если результаты всё же есть, то возвращаем координаты и сохраняем картинку
        if loc[0].any():
            print 'Found float at ' + str(x)
            capcha = 'capchas/uo_session_' + str(int(time.time())) + '_success.png'
            cv2.imwrite(capcha, src_rgb)
            return capcha
#            return (loc[1][0] + w / 2) / 2, (loc[0][
#                                                 0] + h / 2) / 2  # опять мы ведь помним, что макбук играется с разрешениями? поэтому снова приходится делить на 2
    return ''


def bot_initializer():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    updater = Updater("244382714:AAGzUf3SFmeogXjr85i1hPStZTRI-TG5gHw")
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    caps_handler = CommandHandler('caps', caps, pass_args=True)
    dispatcher.add_handler(caps_handler)
    dispatcher.add_handler(start_handler)
    updater.start_polling()


def start(bot, update):
    schedule.every(10).seconds.do(main)
    while 1:
        schedule.run_pending()
    bot.sendPhoto(chat_id=update.message.chat_id, photo=open('capchas/uo_session_1504135781_success.png', 'rb'))


def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)


def main():
    check_screen_size()
    img_name = make_screenshot()
    return find_float(img_name)


if __name__ == "__main__":
    bot_initializer()
    schedule.every(10).seconds.do(main)
    while 1:
        schedule.run_pending()
