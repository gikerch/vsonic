# coding: utf-8

import json
import time
start = time.clock()
import requests
import re
from bs4 import BeautifulSoup
import datetime
import xlwt
from xlwt import Formula
from selenium import webdriver

# 邮件
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import time

"""
京东价格接口
http://p.3.cn/prices/mgets?skuIds=J_3535341,J_&type=1
"""
wb = xlwt.Workbook(encoding='gbk')
day = str(datetime.date.today())[2:]
ws1 = wb.add_sheet(u'京东显示器%s' % day, cell_overwrite_ok=True)
style0 = xlwt.easyxf(
    'font:name SimSun,bold on;align:vert centre, horiz center', num_format_str='#,##0.00')
style1 = xlwt.easyxf('font:name SimSun,bold on', num_format_str='#,##0.00')

#首行标题#
ws1.write(0, 0, u'今日排名', style0)
ws1.write(0, 1, u'品牌', style0)
ws1.write(0, 2, u'型号', style0)
ws1.write(0, 3, u'面板', style0)
ws1.write(0, 4, u'今日价格', style0)
ws1.write(0, 5, u'商品id', style0)
ws1.write(0, 6, u'链接', style0)
ws1.write(0, 7, u'品名', style0)

for t in range(0, 7):
    ws1.col(t).width = 5000
ws1.col(7).width = 16000


name = []
skuid = []
link = []
price = []
brand = []
model = []
version = []

# phantomjs获取当前页面cookie


def get_cookies(url, cookies_list):

    dirver = webdriver.PhantomJS()

    # 添加cookies，去掉其他的不需要的键
    for cookie in cookies_list:
        dirver.add_cookie({k: cookie[k] for k in (
            'name', 'value', 'domain', 'path', 'expiry') if k in cookie})

    # 访问页面
    dirver.get(url)
    # 获取当前页面cookie
    new_cookies_list = dirver.get_cookies()

    cookie_dict = {}
    for cookie in new_cookies_list:
        if cookie.has_key('name') and cookie.has_key('value'):
            cookie_dict[cookie['name']] = cookie['value']
    return cookie_dict, new_cookies_list

# 带cookie访问页面


def get_page(url, cookie):

    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               "Connection": "keep-alive",
               "Cookie": cookie,
               "Host": "list.jd.com",
               "Referer": "https://list.jd.com/list.html?cat=670,677,688&page=6&trans=1&JL=6_0_0",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36"}
    timeout = 5
    r = requests.get(url, headers=headers, timeout=timeout)
    return r.url


# 获取第6页的cookies
def get_global_cookies():

    # 获取首页cookie
    cookies1, cookies_list1 = get_cookies(
        'https://list.jd.com/list.html?cat=670,677,688', [])
    # 获取第五cookie
    cookies5, cookies_list5 = get_cookies(
        'https://list.jd.com/list.html?cat=670,677,688&page=5&trans=1&JL=6_0_0', cookies_list1)
    # 获取第6页cookie
    cookies6, cookies_list6 = get_cookies(
        'https://list.jd.com/list.html?cat=670,677,688&page=6&trans=1&JL=6_0_0', cookies_list5)

    # 将cookie处理成k=v;的形式
    cookies = ''
    for k, v in cookies6.items():
        cookies += k + '=' + v + ';'
    cookies = cookies[:-1]
    cookiesk = ''
    for k, v in cookies1.items():
        cookiesk += k + '=' + v + ';'
    cookiesk = cookiesk[:-1]
    return cookies, cookiesk

# 邮件函数
def SendEmail(to_list):

    from_addr = "491315091@qq.com"
    sslcode = "kioylteorsmzbiji"
    # pwd = "qq_9314zhouwei"
    # 收件人列表
    # to_addr = ["491315091@qq.com","693610802@qq.com"]
    smtp_server = 'smtp.qq.com'

    # 当前日期
    date = time.strftime('%Y年%m月%d日')

    # 如名字所示Multipart就是分多个部分
    msg = MIMEMultipart()
    msg["Subject"] = "京东显示器%s排名" %date
    msg["From"] = from_addr
    # msg["To"] = to_addr
    # 发送给多人
    msg['To'] = ",".join(to_list)

    #---这是文字部分---
    part = MIMEText('<html><body><h3>Dear all:</h3>' +
        '<p>京东显示器%s排名</p>' %date + '<p>请查收</p>' +
        '</body></html>', 'html', 'utf-8')
    msg.attach(part)

    #---这是附件部分---
    # xlsx类型附件
    part = MIMEApplication(open(u'JD显示器数据.xls', 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename="jd显示器排名.xls".encode('gb2312'))
    msg.attach(part)

    # jpg类型附件
    # part = MIMEApplication(open('valicode.jpg', 'rb').read())
    # part.add_header('Content-Disposition', 'attachment', filename="valicode.jpg")
    # msg.attach(part)

    # #pdf类型附件
    # part = MIMEApplication(open('foo.pdf','rb').read())
    # part.add_header('Content-Disposition', 'attachment', filename="foo.pdf")
    # msg.attach(part)

    # #mp3类型附件
    # part = MIMEApplication(open('foo.mp3','rb').read())
    # part.add_header('Content-Disposition', 'attachment', filename="foo.mp3")
    # msg.attach(part)
    try:
        s = smtplib.SMTP_SSL(smtp_server, 465)
        s.login(from_addr, sslcode)
        s.sendmail(from_addr, to_list, msg.as_string())
        s.quit()
        return "Success!"
    except smtplib.SMTPException, e:
        return "Falied,%s" % e


# 获取通用的cookies字符串
cookies, cookiesk = get_global_cookies()
print '第6页cookies获取成功'

# 检测是否成功访问到第6页
url = get_page(
    'https://list.jd.com/list.html?cat=670,677,688&page=6&trans=1&JL=6_0_0', cookies)
if re.match(u'&page=6&', url):
    print u'成功或取第6页cookies'


headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
           "Connection": "keep-alive",
           "Cookie": cookies,
           "Host": "list.jd.com",
           "Referer": "https://list.jd.com/list.html?cat=670,677,688&page=5&trans=1&JL=6_0_0",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36"}

# 爬取1至20页数据
print u'开始爬取数据'
for p in range(1, 2):
    req = requests.get(
        'https://list.jd.com/list.html?cat=670,677,688&page=%s&trans=1&JL=6_0_0&ms=5#J_main' % p, headers=headers)
    # print req.cookies
    # print req.text
    soup = BeautifulSoup(req.text, "html.parser")
    items = soup.findAll(attrs={"class": "gl-item"})
    for i in range(0, 55):
        # 商品名称
        name.append(items[i].find(attrs={"class": "p-name"}).em.text.strip())
        print items[i].find(attrs={"class": "p-name"}).em.text.strip()
        id_num = items[i].a.get('href')[14:][:-5]
        print id_num
        skuid.append(id_num)
        # 链接
        link.append("http://item.jd.com/%s.html" % id_num)
for p in range(2, 21):
    req = requests.get(
        'https://list.jd.com/list.html?cat=670,677,688&page=%s&trans=1&JL=6_0_0&ms=5#J_main' % p, headers=headers)
    # print req.cookies
    # print req.text
    soup = BeautifulSoup(req.text, "html.parser")
    items = soup.findAll(attrs={"class": "gl-item"})
    for i in range(len(items)):
        # 商品名称
        name.append(items[i].find(attrs={"class": "p-name"}).em.text.strip())
        print items[i].find(attrs={"class": "p-name"}).em.text.strip()
        id_num = items[i].a.get('href')[14:][:-5]
        print id_num
        skuid.append(id_num)
        # 链接
        link.append("http://item.jd.com/%s.html" % id_num)

for p in range(21, 22):
    req = requests.get(
        'https://list.jd.com/list.html?cat=670,677,688&page=%s&trans=1&JL=6_0_0&ms=5#J_main' % p, headers=headers)
    # print req.cookies
    # print req.text
    soup = BeautifulSoup(req.text, "html.parser")
    items = soup.findAll(attrs={"class": "gl-item"})
    for i in range(0, 5):
        # 商品名称
        name.append(items[i].find(attrs={"class": "p-name"}).em.text.strip())
        print items[i].find(attrs={"class": "p-name"}).em.text.strip()
        id_num = items[i].a.get('href')[14:][:-5]
        print id_num
        skuid.append(id_num)
        # 链接
        link.append("http://item.jd.com/%s.html" % id_num)

for i in range(len(skuid)):
    price.append(0)
    print i

# 价格
# for K in skuid:
#     r = requests.get('http://p.3.cn/prices/mgets?skuIds=J_' + str(K)).text
#     data = json.loads(r)[0]
#     PreferentialPrice = data['p']
#     price.append(PreferentialPrice)

for iname in name:
    if u"飞利浦" in iname:
        version.append(re.compile(
            r'PLS|IPS|TN|VA|MVA|ADS').findall(iname[12:]))
    else:
        version.append(re.compile(r'PLS|IPS|TN|VA|MVA|ADS').findall(iname))
    iname = ' '.join(iname.split())

    if u'） ' in iname[:20]:
        brand.append(iname.split(u'）')[0] + u'）')
        model.append(iname.split(u'）')[1].strip().split(' ')[0])
    elif u'）' in iname[:20]:
        brand.append(iname.split(u'）')[0] + u'）')
        model.append(iname.split(u'）')[1].strip().split(' ')[0])
    else:
        try:
            model.append(iname.split(' ')[1])
            brand.append(iname.split(' ')[0])
        except:
            brand.append(iname[0:10])
            model.append('')


#'品牌'型号',参数','价格''商品id','链接',
n = 0
for m in range(len(name)):
    ws1.write(n + 1, 0, int(n + 1), style1)
    ws1.write(n + 1, 1, brand[m], style1)
    ws1.write(n + 1, 2, model[m], style1)
    ws1.write(n + 1, 3, version[m], style1)
    ws1.write(n + 1, 4, price[m], style1)
    ws1.write(n + 1, 5, skuid[m], style1)
    b = '"%s"' % link[m]
    ws1.write(n + 1, 6, Formula('HYPERLINK(%s;"link")' % b))
    ws1.write(n + 1, 7, name[m], style1)
#       ws1.write(n+1,7,invest_amount[m],style1)
#       ws1.write(n+1,8,repayment[m],style1)
    n += 1

print n

# 保存到excle
print u'保存到文件'
wb.save(u'JD显示器数据.xls')
print 'well done!'

# 发送邮件
to_list = ["491315091@qq.com","693610802@qq.com"]
re = SendEmail(to_list)
print re

# 程序运行用时
end = time.clock()
print u'程序运行耗时:', end - start
