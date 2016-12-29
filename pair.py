#! usr/bin/python
#coding=utf-8
# -*- coding:cp936 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('pytesser')
from pytesser import *
import requests
from PIL import Image, ImageEnhance 
import cStringIO
import time
from bs4 import BeautifulSoup


player1 = ('2013000000000', '******')
player2 = ('2014000000000', '******')


date = '2016-12-30'
startMin = '1260' # Minutes counted from 00:00
endMin = '1290' # eg. 21:30 = 21.5 * 60 = 1290

info1 = {
    'date': date,
    'seat': '3956',
    'start': startMin,
    'end': endMin
}
info2 = {
    'date': date,
    'seat': '3956',
    'start': startMin,
    'end': endMin
}
seatRequirement = {
    'onDate': date,
    'building': '1',
    'room': '5', # 1 floor Inovative Room
    'hour': 'null',
    'startMin': startMin,
    'endMin': endMin,
    'power': '1',
    'window': ''
}

#


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


def realDoLogin(player):
    
    login_request = requests.session()

    login_response_first = login_request.get(url = 'http://seat.lib.whu.edu.cn/login?targetUri=%2F', headers = headerme)
    #print login_response_first.cookies['JSESSIONID'],

    DIVISION = 137
    img = Image.open(cStringIO.StringIO(login_request.get(url='http://seat.lib.whu.edu.cn/simpleCaptcha/captcha', headers = headerme).content))
    (imgLong, imgWidth) = (img.size[0] - 1, img.size[1] - 1) 
    for i in range(0, imgLong):
        for j in range(0, imgWidth):
            if img.getpixel((i, j))[0] > DIVISION:
                img.putpixel((i, j), (255,255,255))
    enhancer = ImageEnhance.Contrast(img) 
    image_enhancer = enhancer.enhance(4)
    vcode = image_to_string(img).replace(' ', '')
    for i in vcode:
        if i not in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            vcode = vcode.replace(i, '')
    #print vcode, 

    datame = {
            'username': player[0],
            'password': player[1],
            'captcha': vcode
    }
    #print datame['username'], '\r'
    login_response_second = login_request.post('http://seat.lib.whu.edu.cn/auth/signIn', headers = headerme, data = datame)
    #print login_response_second.content
    if '00:00' in login_response_second.content:
        print 'Success'
        return login_request
    else:
        return 0


def doLogin(player):

    print '[*] Logining...'
    login_request = 0
    count = 0
    while login_request == 0:
        count = count + 1
        #print '[*] Trying login ', count,
        login_request = realDoLogin(player)
    return login_request


def cancelReservation(login_request):

    cr_response_text = login_request.get(url = 'http://seat.lib.whu.edu.cn/history?type=SEAT', headers = headerme).text
    soup = BeautifulSoup(cr_response_text, "html.parser")
    if len(soup.findAll('a', class_ = 'normal showLoading')) > 0:
        cancelUrl = 'http://seat.lib.whu.edu.cn' + soup.findAll('a', class_ = 'normal showLoading')[0]['href']
        print cancelUrl
        #login_request.get(url = cancelUrl, headers = headerme)




def pickSeat(login_request_1, login_request_2, waitingList):

    for i in range(0, len(waitingList)):
        print '[=>]target ', i
        info1['seat'] = waitingList[i][0]
        info2['seat'] = waitingList[i][1]    
        flag1 = 0
        flag2 = 0
        ps_responce_1 = login_request_1.post('http://seat.lib.whu.edu.cn/selfRes', headers = headerme, data = info1)
        ps_responce_2 = login_request_2.post('http://seat.lib.whu.edu.cn/selfRes', headers = headerme, data = info2)
        if u'已有1个有效预约' in ps_responce_1.content:
            print 'Player1 succeeded.'
            flag1 = 1
        else:
            print 'Player1 failed.'
        if u'已有1个有效预约' in ps_responce_2.content:
            print 'Player2 succeeded.'
            flag2 = 1
        else:
            print 'Player2 failed.'
        if flag1  + flag2 == 2:
            print '\n####################################'
            print '[!] Congratulations! Double Kill! [!]'
            return 1
        elif flag1 + flag1 == 1:
            print '[~] Only one succeeded [~]'
            cancelUrl(login_request_1)
            cancelUrl(login_request_2)
        else:
            print '[] So sad [] '
    return 0


def seatListGenerator(login_request):
    
    seatList = {}

    sl_response = login_request.post('http://seat.lib.whu.edu.cn/freeBook/ajaxSearch', headers = headerme, data = seatRequirement)
    sl_response_text = sl_response.text.replace('\\n', '\n').replace('\"', '"').replace('\u002f', '/').replace('\\', '')
    sl_response_text = sl_response_text.split(',', 2)[0][12:-1]
    sl_soup = BeautifulSoup(sl_response_text, "html.parser")
    for tag in sl_soup.findAll('li'):
        seatList[tag.dt.get_text()[1:]] = tag['id'][5:]
    return seatList


def powerListGenerator():
    powerList = []
    for i in range(17, 35, 2):
        powerList.append((str(i), str(i+1)))
    return powerList


def waitingListGenerator(powerList, seatList):
    waitingList = [[3956, 3957], [4049, 4080], [9131, 4142], [4194, 4195], [4193, 4192], [4190, 4191], [4188, 4189], [4185, 4186], [4183, 4184]]
    for pair in powerList:
        try:
            print seatList[pair[0]], seatList[pair[1]]
            waitingList.append([seatList[pair[0]], seatList[pair[1]]])
        except:
            pass
    #waitingList = [[3956, 3957], [4049, 4080], [9131, 4142], [4194, 4195], [4193, 4192], [4190, 4191], [4188, 4189], [4185, 4186], [4183, 4184]]
    return waitingList
    

def main():
    print '\n####### START #######'
    login_request_1 = doLogin(player1)
    login_request_2 = doLogin(player2)
    seatList = seatListGenerator(login_request_1)
    powerList = powerListGenerator()
    waitingList = waitingListGenerator(powerList, seatList)

    count = 1
    #print '\n[*] --- Round ', count, '---'
    while pickSeat(login_request_1, login_request_2, waitingList) != 1:
    #    count = count + 1
    #    print '\n[*] --- Round ', count, '---'
        pass


if __name__ == '__main__':
    main()