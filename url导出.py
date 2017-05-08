# -*- coding: utf-8 -*-
__author__ = 'acer-zhou'
import os
import urllib
import urllib2
import cookielib
import time

# 验证码图片地址, 登陆post地址,数据导出地址
valicode_url = 'http://172.20.3.252:9090/check2code.action'
login_url = 'http://172.20.3.252:9090/LoginAction.action'
export_url = 'http://172.20.3.252:9090/url/url-export.action'

# 将cookies绑定到一个opener cookie由cookielib自动管理
cookie = cookielib.CookieJar()
handler = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(handler)

# 用户名和密码
username = 'test2'
password = 'Test12#$'

# 用openr访问验证码地址,获取cookie
picture = opener.open(valicode_url).read()
# 把验证码保存到本地
# local = open('E:/resource_find/valicode.jpg', 'wb')
local = open('F:/Python/resource_find/valicode.jpg', 'wb')
local.write(picture)
local.close()
# 打开保存的验证码输入
valicode = raw_input('input valicode:')

# post_data
post_data = {'form.userID': username,
             'form.password': password,
             'form.validateCode': valicode,
             'form.code': 'on'}
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
}
# 生成post数据 ?key1=value1&key2=value2的形式
data = urllib.urlencode(post_data)
# 构造request请求，方法为post
request = urllib2.Request(login_url, data, headers)
try:
    response = opener.open(request)
    result = response.read().decode('utf-8')
    print result
except urllib2.HTTPError, e:
    print e.code

# 进度条
# def cbk(a, b, c):
#     per = 100.0 * a * b / c
#     if per > 100:
#         per = 100
#     print '%.2f%%' % per

# 利用之前存有cookie的opener登录页面
# TODO
# urllib方法，没有成功传cookie，暂时未解决
# local = 'F:/PycharmProjects/data.csv'
# urllib.urlretrieve(export_url,local,cbk)

# urllib2方法
# 导出CSV文件函数


def download_csv(start, end, retry_num=5):
    """下载csv文件

    Args:
        start (str): 起始时间
        end (str): 截止时间
        retry_num (int, optional): 重试次数

    Returns:
        .csv: csv文件
    """
    form_post = {'form.today': 2,
                 'form.dto.dip': '',
                 'form.dto.subtype': '',
                 'form.dto.type': '',
                 'form.dto.username': '',
                 'form.dto.descid': '',
                 'form.dto.domain': '',
                 'form.dto.browser': '',
                 'form.dto.platform': '',
                 'form.dto.action': '',
                 'form.dto.dir': '',
                 'form.dto.line': '',
                 'form.dto.url': '',
                 'form.time1': start,
                 'form.time2': end,
                 'form.dto.sip': 'IP'}

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36', }

    # 生成post数据 ?key1=value1&key2=value2的形式
    data2 = urllib.urlencode(form_post)
    # 重试5次，如果失败打印消息
    try:
        request2 = urllib2.Request(export_url, data2, headers)
        response2 = opener.open(request2).read()
    except Exception, e:
        print e.message
        if retry_num > 0:
            return download_csv(start, end, retry_num=retry_num - 1)
        else:
            print 'get Failed'
            return ''

    # 构造文件名称格式：日期_开始时间_结束时间：161230_2000_2020
    date = start[2:10]
    stime = start[11:16].replace(':', '')
    etime = end[11:16].replace(':', '')
    filename = date + '_' + stime + '_' + etime
    local = '%s.csv' % filename
    path = date
    if not os.path.exists(path):
        os.makedirs(path)
    f = open(date + '/' + local, 'w')
    f.write(response2)
    f.close()
    print 'file saved in:' + date


def datetime_timestamp(dt):
    # dt为字符串
    # 中间过程，一般都需要将字符串转化为时间数组
    time.strptime(dt, '%Y-%m-%d %H:%M:%S')
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=-1)
    # 将"2012-03-28 06:53:40"转化为时间戳
    s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
    return int(s)


def timestamp_datetime(value):
    format = '%Y-%m-%d %H:%M:%S'
    # value为传入的值为时间戳(整形)，如：1332888820
    value = time.localtime(value)
    # 经过localtime转换后变成
    # time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    dt = time.strftime(format, value)
    return dt


def dealtime(start, end, m=5):
    """时间处理

    Args:
        start (str): 开始时间
        end (str): 结束时间
        m (int, optional): 间隔分钟数

    Returns:
        list: [（开始，结束）]
    """
    # 转换为时间戳
    startstamp = datetime_timestamp(start)
    endstamp = datetime_timestamp(end)
    p = (endstamp - startstamp) / 300  # 计算分段数量
    s_list = [startstamp + m * 60 * i for i in range(p)]
    e_list = [startstamp + m * 60 * (i + 1) for i in range(p)]
    # 将时间戳转换为str字符
    start_list = [timestamp_datetime(s) for s in s_list]
    end_list = [timestamp_datetime(e) for e in e_list]
    time_list = []
    # 构造tunple
    for s, e in zip(start_list, end_list):
        _time = (s, e)
        time_list.append(_time)
    return time_list

if __name__ == '__main__':
    # 时间格式为：2016-12-28 00:00:00
    # time_list = [('2016-12-30 20:00:00', '2016-12-30 20:20:00'),
    #              ('2016-12-30 21:40:00', '2016-12-30 22:00:00')]

    Start = '2017-03-01 22:00:00'
    End = '2017-03-02 00:30:00'
    # 生成时间段列表
    time_list = dealtime(Start, End, 10)
    print time_list

    # 下载文件
    for i in time_list:
        start, end = i
        download_csv(start, end)
    print 'well done'
