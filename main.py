# coding=utf-8
import os
import sys
import re
import imp
M = ['requests', 'bs4', 'PIL']
for _m in M:
    try:
        imp.find_module(_m)
    except:
        if _m != 'PIL':
            os.system('pip install ' + _m)
        else:
            os.system('pip install Pillow')
        print '-'*30, '\n'
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageEnhance

reload(sys)
sys.setdefaultencoding('utf8')

global OPERATION_SYSTEM
global USER_INFO
global SEAT_LIST


def load_user_info():
    global USER_INFO

    print '[*] Loading User Information...'
    user_info = {}

    try:
        fp = open('./user.txt')
    except:
        print '[!] Error when open the config file.'
        exit()

    for line in fp:
        if not line.startswith('#') and '=' in line:
            key_in_line = re.findall('([a-zA-Z]+)', line)[0]
            value_in_line = re.findall('= (\S+)', line)[0]
            user_info[key_in_line] = value_in_line
            print '    + %s: %s' % (key_in_line, value_in_line)
    user_info['seat'] = user_info['seat'].replace(' ', '').split(',')

    if raw_input('Confirm the information. [Y/n]').lower() != 'n':
        user_info['headers'] = {
            'Host': 'seat.lib.whu.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://seat.lib.whu.edu.cn/login?targetUri=%2F',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    else:
        print '[!] Incorrect Information'
        exit()
    USER_INFO = user_info
    return True


def real_do_login():
    global USER_INFO
    # 0 for manual login, 1 for auto login
    login_mode = USER_INFO['AutoLogin']
    LoginRequestTmp = requests.Session()
    LoginResponseTmp = LoginRequestTmp.get(url='http://seat.lib.whu.edu.cn/login?targetUri=%2F',
                                           headers=USER_INFO['headers'])
    with open('captcha.bmp', 'wb') as captcha:
        captcha.write(LoginRequestTmp.get(url='http://seat.lib.whu.edu.cn/simpleCaptcha/captcha').content)

    image = Image.open('captcha.bmp')
    (imgLong, imgWidth) = (image.size[0] - 1, image.size[1] - 1)
    for i in range(0, imgLong):
        for j in range(0, imgWidth):
            if image.getpixel((i, j))[0] > 137:
                image.putpixel((i, j), (255, 255, 255))
    enhancer = ImageEnhance.Contrast(image)
    image_enhancer = enhancer.enhance(4)
    image_enhancer.show()

    if login_mode == '0':
        # Manually
        vcode = raw_input('[!] Input the captcha please: ')
    elif login_mode == '1':
        # Auto
        print 'Not finished'
        exit()
    else:
        print 'Login Mode:', login_mode
        print '[!] Error Login Mode'
        exit()

    data = {
        'username': USER_INFO['username'],
        'password': USER_INFO['password'],
        'captcha': vcode
    }
    try:
        LoginResponseTmp = LoginRequestTmp.post('http://seat.lib.whu.edu.cn/auth/signIn', headers=USER_INFO['headers'],
                                                data=data, timeout=5)
        if '00:00' in LoginResponseTmp.text:
            return LoginRequestTmp
        else:
            return False
    except:
        return False


def do_login():
    for _x in xrange(0, 5):
        LoginRequest = real_do_login()
        if LoginRequest != False:
            print 'Login Success'
            return LoginRequest
    print '[!] 5 times login failure. Try later.'
    exit()


def seat_list_generator(LoginRequest):
    global SEAT_LIST, USER_INFO
    SeatList = {}
    SLResponse = LoginRequest.get(
        url='http://seat.lib.whu.edu.cn/mapBook/getSeatsByRoom?room={0}&date={1}'.format(USER_INFO['room'],
                                                                                         USER_INFO['date']))
    SLResponseText = SLResponse.text.replace('<li>&nbsp;</li>', '')
    SLResponseText = SLResponseText.split(',', 2)[0][12:-1]
    SLSoup = BeautifulSoup(SLResponseText, 'html.parser')
    for tag in SLSoup.findAll('li'):
        SeatList[tag.code.get_text()[1:]] = re.findall('^seat_(\d+)$', tag['id'])[0]
    SEAT_LIST = SeatList
    return True


def seat_pick(LoginRequest):
    global SEAT_LIST, USER_INFO

    startMin = str(int(float(USER_INFO['startHour']) * 60))
    endMin = str(int(float(USER_INFO['endHour']) * 60))
    SeatSet = USER_INFO['seat']

    count = 0
    LoginRequest.keep_alive = False

    if SeatSet[0] == 'all':
        SeatSet.remove('all')
        for _s in SEAT_LIST:
            SeatSet.append(_s)

    while True:
        for seat in SeatSet:
            info = {
                'date': USER_INFO['date'],
                'seat': SEAT_LIST[seat.zfill(2)],
                'start': startMin,
                'end': endMin
            }
            count = count + 1
            print '\r  -Try: {0}\t-ID: {1}'.format(count, seat),
            try:
                PSResponse = LoginRequest.post(url='http://seat.lib.whu.edu.cn/selfRes', headers=USER_INFO['headers'],
                                               data=info, timeout=3)
                if u'系统已经为您预定好了' in PSResponse.content:
                    return True
                elif u'其他时段或座位' in PSResponse.content:
                    print 'is OCCUPIED. Trying others...',
                else:
                    pass
            except KeyboardInterrupt:
                print '[!] User Abort'
                exit()
            except:
                pass


def cancel_reservation(LoginRequest):
    CRResponseText = LoginRequest.get(url='http://seat.lib.whu.edu.cn/history?type=SEAT',
                                      headers=USER_INFO['headers']).text
    soup = BeautifulSoup(CRResponseText, "html.parser")
    if len(soup.findAll('a', class_='normal showLoading')) > 0:
        CRURL = 'http://seat.lib.whu.edu.cn' + soup.findAll('a', class_='normal showLoading')[0]['href']
        print '[*] Canceling...', CRURL
        LoginRequest.get(url=CRURL, headers=USER_INFO['header'])


def main():
    global USER_INFO
    load_user_info()
    RequestsObj = do_login()
    seat_list_generator(RequestsObj)

    if USER_INFO['cancel'] == '1':
        cancel_reservation(RequestsObj)

    if seat_pick(RequestsObj):
        print '\n\n***** Reservation Complete *****\n\n'

    raw_input('\nPress <Enter> to exit')


if __name__ == '__main__':
    main()
