# coding=utf-8
import os
import re
import imp
import cStringIO
import threading
import datetime

M = ['requests', 'bs4', 'PIL']
for _m in M:
    try:
        imp.find_module(_m)
    except:
        if _m != 'PIL':
            os.system('pip install ' + _m)
        else:
            os.system('pip install Pillow')
        print '-' * 30, '\n'
from Tkinter import *
try:
    from PIL import Image, ImageEnhance
except:
    from pillow import Image, ImageEnhance
import requests
import bs4


class App(object):
    def __init__(self):
        self.root = Tk()
        self.root.title(u'武汉大学图书馆座位')
        self.headers = {
            'Host': 'seat.lib.whu.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://seat.lib.whu.edu.cn/login?targetUri=%2F',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.requests_obj = requests.Session()
        self.flag_done = False
        self.current_task_number = 0

        l_username = Label(self.root, text=u'学号：', width=5)
        l_username.grid(row=0, column=1, sticky=W)
        self.e_username = Entry(self.root, width=15)
        self.e_username.grid(row=0, column=2, sticky=W, columnspan=1)

        l_password = Label(self.root, text=u'密码：', width=5)
        l_password.grid(row=0, column=3, sticky=W)
        self.e_password = Entry(self.root, width=15)
        self.e_password['show'] = '*'
        self.e_password.grid(row=0, column=4, sticky=E, columnspan=1)

        l_captcha = Label(self.root, text=u'验证码：')
        l_captcha.grid(row=2, column=1, sticky=W)
        self.suspected_captcha_stringvar = StringVar()
        self.suspected_captcha_stringvar.set('')
        self.e_captcha = Entry(self.root, width=10, textvariable=self.suspected_captcha_stringvar)
        self.e_captcha.grid(row=2, column=2, sticky=W)

        b_getcode = Button(self.root, text=u'获取验证码', command=self.get_code)
        b_getcode.grid(row=2, column=3, sticky=NW, columnspan=2)
        b_login = Button(self.root, text=u'登录', command=self.do_login, width=10)
        b_login.grid(row=2, column=4, sticky=E, columnspan=2)

        self.text = Text(self.root, width=65)
        self.text.grid(row=3, column=1, sticky=NW, columnspan=4)
        self.text.bind('<KeyPress>', lambda e: 'break')

        l_startHour = Label(self.root, text=u'开始时间：')
        l_startHour.grid(row=5, column=1, sticky=NW)
        self.e_startHour = Entry(self.root, width=12)
        self.e_startHour.grid(row=5, column=2, sticky=NW, columnspan=2)

        l_endHour = Label(self.root, text=u'结束时间：')
        l_endHour.grid(row=5, column=3, sticky=NW)
        self.e_endHour = Entry(self.root, width=12)
        self.e_endHour.grid(row=5, column=4, sticky=NW, columnspan=2)

        l_room = Label(self.root, text=u'房间号：')
        l_room.grid(row=6, column=1, sticky=NW)
        self.e_room = Entry(self.root, width=12)
        self.e_room.grid(row=6, column=2, sticky=NW, columnspan=2)

        l_seat = Label(self.root, text=u'座位号：')
        l_seat.grid(row=6, column=3, sticky=NW)
        self.e_seat = Entry(self.root, width=12)
        self.e_seat.grid(row=6, column=4, sticky=NW, columnspan=2)

        l_date = Label(self.root, text=u'日期：')
        l_date.grid(row=7, column=1, sticky=NW)

        date_default_value = StringVar()
        date_value = datetime.date.today()
        if datetime.datetime.now().time().hour > 21:
            date_value = date_value + datetime.timedelta(days=1)
        date_default_value.set(date_value)
        self.e_date = Entry(self.root, width=12, textvariable=date_default_value)
        self.e_date.grid(row=7, column=2, sticky=NW, columnspan=2)

        self.b_stop = Button(self.root, text=u'停止', command=self.stop)
        self.b_stop.grid(row=8, column=3, sticky=W, columnspan=2)
        self.b_stop.config(state=DISABLED)

        self.b_pick = Button(self.root, text=u'抢座', command=self.seat_pick, width=10)
        self.b_pick.grid(row=8, column=4, sticky=W, columnspan=2)

        self.b_cancel = Button(self.root, text=u'取消当前预约', command=self.cancel_reservation, width=10)
        self.b_cancel.grid(row=8, column=1, sticky=W, columnspan=2)

        self.img_label = Label(self.root)
        self.img_label.grid(row=8, column=3, sticky=NW)

        l_thread = Label(self.root, text=u'线程数：')
        l_thread.grid(row=7, column=3, sticky=NW)
        thread_default_value = StringVar()
        thread_default_value.set('40')
        self.e_thread = Entry(self.root, width=12, textvariable=thread_default_value)
        self.e_thread.grid(row=7, column=4, sticky=NW, columnspan=2)

        self.root.mainloop()

    def get_code(self):
        try:
            '''
            captha_file = open('captcha.png', 'wb')
            captha_file.write(self.requests_obj.get(url='http://seat.lib.whu.edu.cn/simpleCaptcha/captcha', headers=self.headers).content)
            captha_file.close()
            image = Image.open('captcha.png')
            '''
            image = Image.open(
                cStringIO.StringIO(
                    self.requests_obj.get(url='http://seat.lib.whu.edu.cn/simpleCaptcha/captcha', headers=self.headers).content))

            try:
                get_code_text = requests.post(url='http://www.zhzzhz.com/Seat/returnCaptcha.php', data={'cookie':self.requests_obj.cookies['JSESSIONID']})
                suspected_captcha = get_code_text.text.split('\n')[0]
                self.suspected_captcha_stringvar.set(suspected_captcha)
            except:
                pass
            (imgLong, imgWidth) = (image.size[0], image.size[1])
            for i in range(0, imgLong):
                for j in range(0, imgWidth):
                    if image.getpixel((i, j))[0] > 137:
                        image.putpixel((i, j), (255, 255, 255))
            enhancer = ImageEnhance.Contrast(image)
            image_enhancer = enhancer.enhance(4)
            image_enhancer.show()
        except Exception, e_get_code:
            self.text.insert(END, u'[!] 无法获得验证码，请稍后重试 %s\n' % str(e_get_code))

    def do_login(self):
        self.load_user_info()
        if self.real_do_login():
            print 'good'
            self.text.insert(END, u'\t======== Room ID List ========\n')
            self.text.insert(END, u'\t4\t一楼创客空间\n')
            self.text.insert(END, u'\t5\t一楼创新学习区\n')
            self.text.insert(END, u'\t13\t3C创客-电子资源阅览区\n')
            self.text.insert(END, u'\t14\t3C创客-双屏电脑\n')
            self.text.insert(END, u'\t15\t创新学习-MAC电脑\n')
            self.text.insert(END, u'\t16\t创新学习-云桌面\n')
            self.text.insert(END, u'\t6\t二楼自然科学图书借阅区西\n')
            self.text.insert(END, u'\t7\t二楼自然科学图书借阅区东\n')
            self.text.insert(END, u'\t8\t三楼社会科学图书借阅区西\n')
            self.text.insert(END, u'\t10\t三楼社会科学图书借阅区东\n')
            self.text.insert(END, u'\t12\t三楼自主学习区\n')
            self.text.insert(END, u'\t9\t四楼图书阅览区西\n')
            self.text.insert(END, u'\t11\t四楼图书阅览区东\n')

        else:
            print 'bad'

    def load_user_info(self):
        self.username = self.e_username.get()
        self.password = self.e_password.get()
        self.captcha = self.e_captcha.get()

    def real_do_login(self):
        # 0 for manually login, 1 for automatically login
        login_mode = '0'

        if login_mode == '0':
            # Manually
            vcode = self.captcha
        elif login_mode == '1':
            # Auto
            print 'Not finished'
            exit()
        else:
            print 'Login Mode:', login_mode
            print '[!] Error Login Mode'
            exit()

        data = {
            'username': self.username,
            'password': self.password,
            'captcha': vcode
        }
        try:
            login_response_obj = self.requests_obj.post('http://seat.lib.whu.edu.cn/auth/signIn',
                                                      headers=self.headers, data=data, timeout=5)
            # print LoginResponseTmp.text
            if '00:00' in login_response_obj.text:
                self.text.delete(1.0, END)
                self.text.insert(END, u'[*] 登录成功\n')
                return True
            else:
                try:
                    fail_info = re.findall('showmsg\("(.+)", 5000\);', login_response_obj.text)[0]
                except:
                    fail_info = u'登录失败，请重试'
                self.text.insert(END, u'[!] %s\n' % fail_info)
                return False
        except:
            return False

    def seat_list_generator(self):
        self.SEAT_LIST = {}
        SeatList = {}
        SLResponse = self.requests_obj.get(
            url='http://seat.lib.whu.edu.cn/mapBook/getSeatsByRoom?room={0}&date={1}'.format(self.e_room.get(),
                                                                                             self.e_date.get()))
        SLResponseText = SLResponse.text.replace('<li>&nbsp;</li>', '')
        SLResponseText = SLResponseText.split(',', 2)[0][12:-1]
        SLSoup = bs4.BeautifulSoup(SLResponseText, 'html.parser')
        for tag in SLSoup.findAll('li'):
            SeatList[tag.code.get_text()[1:]] = re.findall('^seat_(\d+)$', tag['id'])[0]
        self.SEAT_LIST = SeatList
        return True

    def seat_pick(self):
        self.b_pick.config(state=DISABLED)
        self.b_stop.config(state=ACTIVE)
        self.flag_done = False  # enable the button again
        self.current_task_number = 0
        self.max_task_number = self.e_thread.get()

        self.seat_list_generator()
        startMin = str(int(float(self.e_startHour.get()) * 60))
        endMin = str(int(float(self.e_endHour.get()) * 60))
        SeatSet = self.e_seat.get().split(',')

        self.requests_obj.keep_alive = False

        # SeatSet stores id of seats which is to be checked
        if SeatSet[0] == 'all':
            SeatSet = []
            for _s in self.SEAT_LIST:
                SeatSet.append(_s)

        def picker(count):
            if not self.flag_done:
                # print SeatSet
                id = count % len(SeatSet)
                info = {
                    'date': self.e_date.get(),
                    'seat': self.SEAT_LIST[SeatSet[id]],
                    'start': startMin,
                    'end': endMin
                }

                def short_do_pick():
                    self.current_task_number = self.current_task_number + 1
                    output_line = u'-已尝试: {0}次\t-正尝试: {1} '.format(count, SeatSet[id])
                    print '+1s\n'
                    try:
                        PSResponse = self.requests_obj.post(url='http://seat.lib.whu.edu.cn/selfRes',
                                                            headers=self.headers,
                                                            data=info, timeout=3)
                        if u'系统已经为您预定好了' in PSResponse.text:
                            output_line += u'恭喜，抢座成功'
                            self.flag_done = True
                            self.b_pick.config(state=ACTIVE)
                            self.b_stop.config(state=DISABLED)
                        elif u'其他时段或座位' in PSResponse.text:
                            output_line += u'已被占用，正在尝试其他座位'
                        else:
                            sp = bs4.BeautifulSoup(PSResponse.text, 'html.parser')
                            output_line += sp.find_all('div', class_='layoutSeat')[0].get_text(). \
                                replace('\n', '').replace(u'预约失败! ', '')
                        self.text.delete(1.0, 2.0)
                        self.text.insert(1.0, output_line + '\n')
                    except Exception, request_error:
                        self.text.insert(1.0, u'请求失败，即将重试...\n')
                    self.text.after(1, picker, count + 1)
                    self.current_task_number = self.current_task_number - 1

                if self.current_task_number < self.max_task_number:
                    threading.Thread(target=short_do_pick).start()

            else:
                self.b_pick.config(state=ACTIVE)

        picker(0)

    def stop(self):
        self.flag_done = True
        self.b_pick.config(state=ACTIVE)
        self.b_stop.config(state=DISABLED)

    def cancel_reservation(self):
        cancel_response_text = self.requests_obj.get(url='http://seat.lib.whu.edu.cn/history?type=SEAT',
                                                     headers=self.headers).text
        soup = bs4.BeautifulSoup(cancel_response_text, 'html.parser')

        if u'取消预约' not in soup.findAll('div', class_='myReserveList')[0].get_text():
            self.text.insert(1.0, u'未找到有效预约\n')
        else:
            if len(soup.findAll('a', class_='normal showLoading')) > 0:
                CRURL = 'http://seat.lib.whu.edu.cn' + soup.findAll('a', class_='normal showLoading')[0]['href']
                self.requests_obj.get(url=CRURL, headers=self.headers)
                self.text.insert(1.0, u'[*] 已发出取消预约请求\n')
            cancel_response_text = self.requests_obj.get(url='http://seat.lib.whu.edu.cn/history?type=SEAT',
                                                         headers=self.headers).text
            soup = bs4.BeautifulSoup(cancel_response_text, 'html.parser')
            if u'取消预约' not in soup.findAll('div', class_='myReserveList')[0].get_text():
                self.text.insert(1.0, u'[*] 已取消预约\n')
            else:
                self.text.insert(1.0, u'[!] 取消失败，请手动尝试\n')


if __name__ == '__main__':
    app = App()
