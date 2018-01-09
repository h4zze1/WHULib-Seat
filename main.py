# coding=utf-8
import os
import imp
import threading
import datetime

'''
Initial work to install required modules
'''
REQUIRED_MODULES = ['requests']
for single_module in REQUIRED_MODULES:
    try:
        imp.find_module(single_module)
    except:
        os.system('pip install ' + single_module)
        print '-' * 30, '\n'
from Tkinter import *
import requests
import json


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

        self.user_token = ''
        # self.requests_obj = requests.Session()
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
        self.suspected_captcha_stringvar.set(u'无需输入')
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
        self.suspected_captcha_stringvar.set(u'听话，别输了')
        return False

    def do_login(self):
        # Combination of all login work.
        def load_user_info(self):
            self.username = self.e_username.get()
            self.password = self.e_password.get()

        def real_do_login(self):
            try:
                url_for_login = 'http://seat.lib.whu.edu.cn/rest/auth?username=%s&password=%s' % (self.username, self.password)
                resp_of_login = requests.get(url=url_for_login, headers=self.headers)
            except:
                self.text.insert(1.0, u'[!] 网络原因，登录失败，请重试…\n')

            print resp_of_login.text
            resp_of_login_json = json.loads(resp_of_login.text)
            if resp_of_login_json['status'] == 'success':
                self.user_token = resp_of_login_json['data']['token']
                try: # Try to retrieve user's real name friendly
                    url_for_realname = 'http://seat.lib.whu.edu.cn/rest/v2/user?token=%s' % self.user_token
                    resp_of_realname = requests.get(url=url_for_realname, headers=self.headers)
                    print resp_of_realname.text
                    resp_of_realname_json = json.loads(resp_of_realname.text)
                    real_name = resp_of_realname_json['data']['name']
                except:
                    real_name = ''
                return (True, real_name)
            else:
                return (False, resp_of_login_json['message'])

        def retrieve_room_info(self):

            url_for_room = 'http://seat.lib.whu.edu.cn/rest/v2/free/filters?token=' + self.user_token
            resp_of_room = requests.get(url=url_for_room, headers=self.headers)
            resp_of_room_json = json.loads(resp_of_room.text)
            
            if resp_of_room_json['status'] != 'success':
                print 'Retrieve Room Info Failed. ' + resp_of_room_json['message']

            specified_room_dict = {}
            for room_item in resp_of_room_json['data']['rooms']:
                room_id = room_item[0]
                room_name = room_item[1]
                building_id = room_item[2]
                # Classify room_item into different buildings.
                if building_id not in specified_room_dict:
                    specified_room_dict[building_id] = [room_item]
                else:
                    specified_room_dict[building_id].append(room_item)

            # Print room information classified.
            for building_item in resp_of_room_json['data']['buildings']:
                building_id = building_item[0]
                building_name = building_item[1]
                self.text.insert(END, u'== %s ==\n' % building_name)
                for room_item in specified_room_dict[building_id]:
                    self.text.insert(END, u'- %d\t%s\n' % (room_item[0], room_item[1]))

        # Call in-built functions and print result.
        load_user_info(self)
        result_for_login = real_do_login(self)
        if result_for_login[0]:
            # Login Suceeded, save token value.
            self.user_realname = result_for_login[1]
            self.text.insert(END, u'[*] %s您好，登录成功，请输入座位信息进行抢座\n' % self.user_realname)
            self.text.insert(END, u'[*] 你好闰土，我是猹\n')
            try:
                retrieve_room_info(self)
            except:
                self.text.insert(END, u'[!] 获取图书馆数据失败，可能为服务端问题\n')
        else:
            # Login failed, print error message. 
            self.text.insert(END, u'[!] %s\n' % result_for_login[1])


    def seat_pick(self):

        def retrieve_seat_map(self, room_id):
            startMin = str(int(float(self.e_startHour.get()) * 60))
            endMin = str(int(float(self.e_endHour.get()) * 60))
            date = self.e_date.get()
            url_for_seat_map_base = 'http://seat.lib.whu.edu.cn/rest/v2/searchSeats/%s/%s/%s?token=%s&roomId=%s' % (date, '0', '0', self.user_token, room_id)

            page_number = 1
            seat_map = {}
            while True:
                url_for_seat_map =  url_for_seat_map_base + '&page=' + str(page_number)
                print url_for_seat_map
                resp_of_seat_map = requests.get(url=url_for_seat_map, headers=self.headers)
                resp_of_seat_map_json = json.loads(resp_of_seat_map.text)
                if len(resp_of_seat_map_json['data']['seats']) != 0:
                    for seat_item in resp_of_seat_map_json['data']['seats']:
                        seat_map[resp_of_seat_map_json['data']['seats'][seat_item]['name']] = str(resp_of_seat_map_json['data']['seats'][seat_item]['id'])
                    # print 'Seat Map:', seat_map
                    page_number += 1
                else:
                    break
            return seat_map

        self.b_pick.config(state=DISABLED)
        self.b_stop.config(state=ACTIVE)
        self.flag_done = False  # enable the button again
        self.current_task_number = 0
        self.max_task_number = self.e_thread.get()

        startMin = str(int(float(self.e_startHour.get()) * 60))
        endMin = str(int(float(self.e_endHour.get()) * 60))
        expected_seat_set = self.e_seat.get().split(',')
        room_id = self.e_room.get()


        try:
            self.seat_map = retrieve_seat_map(self, room_id)
        except:
            self.text.insert(1.0, u'[!] 获取座位信息失败，请重试...\n')
        print expected_seat_set
        print self.seat_map


        # SeatSet stores id of seats which is to be checked
        if expected_seat_set[0] == 'all':
            expected_seat_set = []
            for _s in self.seat_map:
                expected_seat_set.append(_s)

        def picker(count):
            if not self.flag_done:
                seat_ptr = count % len(expected_seat_set)
                info = {
                    'date': self.e_date.get(),
                    'token': self.user_token,
                    'seat': self.seat_map[expected_seat_set[seat_ptr].zfill(3)],
                    'startTime': startMin,
                    'endTime': endMin
                }

                def short_do_pick():
                    self.current_task_number = self.current_task_number + 1
                    output_line = u'-已尝试: {0}次\t-正尝试: {1} '.format(count, expected_seat_set[seat_ptr])
                    # print output_line, info['seat']
                    print '+1s\n'
                    try:
                        resp_of_pick = requests.post(url='http://seat.lib.whu.edu.cn/rest/v2/freeBook',
                                                            headers=self.headers,
                                                            data=info, timeout=3)
                        resp_of_pick_json = json.loads(resp_of_pick.text)
                        if resp_of_pick_json['status'] == 'success':
                            output_line += u'恭喜，抢座成功'
                            self.flag_done = True
                            self.b_pick.config(state=ACTIVE)
                            self.b_stop.config(state=DISABLED)

                        else:
                            output_line += resp_of_pick_json['message']

                        self.text.delete(1.0, 2.0)
                        self.text.insert(1.0, output_line + '\n')
                    except Exception, request_error:
                        self.text.insert(1.0, u'请求失败，正在重试...\n')

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
        '''
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
        '''
        self.text.insert(1.0, u'[!] 预约功能暂不可用\n')
        self.text.insert(1.0, u'[!] 别点了，这功能还没做呢\n')


if __name__ == '__main__':
    app = App()
