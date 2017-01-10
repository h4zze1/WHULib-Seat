#! usr/bin/python
#coding=utf-8
# -*- coding:cp936 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from pytesser import *
from PIL import Image, ImageEnhance 
from bs4 import BeautifulSoup
import cStringIO
import requests


# Example: python single.py 20133025 888888 5 17 2007-01-01 12.5 21.5
'''
username
password
room = sys.argv[3]
seat = sys.argv[4]
date = sys.argv[5]
startMin = sys.argv[6]
endMin = sys.argv[7]
'''

def load_user_info():
    print '[*] Loading User Information...'
    UserInfo = {}
    try:
        fp = open('./user.txt')
    except:
        print '[-] Fail to load user.txt.'
        return False

    for line in fp:
        tmp = line.replace('\n', '').split("=")
        UserInfo[tmp[0].strip()] = tmp[1].strip()
    print '  - username: {0}\n  - password: {1}\n  - room: {2}\n  - seat: {3}\n  - date: {4}\n  - start Hour: {5}\n  - end Hour: {6}\n'.format(UserInfo['username'], UserInfo['password'], UserInfo['room'], UserInfo['seat'], UserInfo['date'], UserInfo['startHour'], UserInfo['endHour'])
    confirm = raw_input('Ensure your info are correct. [Y/N]: ')
    if confirm.lower() == 'n':
        return False
    else:
        headerme = {
        'Host': 'seat.lib.whu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://seat.lib.whu.edu.cn/login?targetUri=%2F',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded'
        }
        UserInfo['header'] = headerme
        return UserInfo

def read_do_login(UserInfo, manual):
    try:
        LoginRequestTmp = requests.Session()
        LoginResponseTmp = LoginRequestTmp.get(url = 'http://seat.lib.whu.edu.cn/login?targetUri=%2F', headers = UserInfo['header'])
        img = Image.open(cStringIO.StringIO(LoginRequestTmp.get(url = 'http://seat.lib.whu.edu.cn/simpleCaptcha/captcha', headers = UserInfo['header']).content))
        (imgLong, imgWidth) = (img.size[0] - 1, img.size[1] - 1) 
        for i in range(0, imgLong):
            for j in range(0, imgWidth):
                if img.getpixel((i, j))[0] > 137:
                    img.putpixel((i, j), (255,255,255))
        if manual == 0:
            enhancer = ImageEnhance.Contrast(img) 
            image_enhancer = enhancer.enhance(4)
            vcode = image_to_string(img).replace(' ', '')
            for i in vcode:
                if i not in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    vcode = vcode.replace(i, '')
            print '..',
        elif manual == 1:
            img.show()
            vcode = raw_input('[!] Input the captcha: ')
        datame = {
            'username': UserInfo['username'],
            'password': UserInfo['password'],
            'captcha': vcode
        }
        LoginResponseTmp = LoginRequestTmp.post('http://seat.lib.whu.edu.cn/auth/signIn', headers = UserInfo['header'], data = datame)
        if '00:00' in LoginResponseTmp.content:
            return LoginRequestTmp
        else:
            return False
    except:
        return False

def do_login(UserInfo):
    print '\nLoging ..',
    LoginRequest = 0
    for manual in range(0, 2):
        for i in range(0, 10):
            LoginRequest = read_do_login(UserInfo, manual)
            if LoginRequest != 0:
                print '\n[*] Login Success!'        
                return LoginRequest
        print 'Some Problem occurs. Input manually.'
    print '[ Sorry. ]'
    exit()

def seat_list_generator(LoginRequest, UserInfo):
    SeatList = {}
    SLResponse = LoginRequest.get(url = 'http://seat.lib.whu.edu.cn//mapBook/getSeatsByRoom?room={0}&date={1}'.format(UserInfo['room'], UserInfo['date']))
    SLResponseText = SLResponse.text.replace('\\n', '\n').replace('\"', '"').replace('\u002f', '/').replace('\\', '').replace('<li>&nbsp;</li>', '')
    SLResponseText = SLResponseText.split(',', 2)[0][12:-1]
    SLSoup = BeautifulSoup(SLResponseText, "html.parser")
    for tag in SLSoup.findAll('li'):
        SeatList[tag.code.get_text()[1:]] = tag['id'][5:]
    return SeatList

def seat_pick(LoginRequest, SeatList, UserInfo):
    seat = SeatList[UserInfo['seat']]
    startMin = str(int(float(UserInfo['startHour']) * 60))
    endMin = str(int(float(UserInfo['endHour']) * 60))

    Result = 0
    count = 0
    LoginRequest.keep_alive = False
    info = {
    'date' : UserInfo['date'],
    'seat' : seat,
    'start' : startMin,
    'end' : endMin
    }
    while Result == 0:
        PSResponse = LoginRequest.post(url = 'http://seat.lib.whu.edu.cn/selfRes', headers = UserInfo['header'], data = info)
        if u'系统已经为您预定好了' in PSResponse.content:
            return True
        else:
            count = count + 1
            print '  -Try: ', count, '\r',
    return False

def main():
    UserInfo = load_user_info()
    Connection = do_login(UserInfo)
    SeatList = seat_list_generator(Connection, UserInfo)
    if seat_pick(Connection, SeatList, UserInfo):
        print '\n\n***** Reservation Complete *****\n\n'

if __name__ == '__main__':
     main() 