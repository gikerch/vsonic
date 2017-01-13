# coding:utf-8

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import time

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
    part.add_header('Content-Disposition', 'attachment', filename= "jd显示器排名.xls".encode('gb2312'))
    msg.attach(part)

    # jpg类型附件
    part = MIMEApplication(open('valicode.jpg', 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename="valicode.jpg")
    msg.attach(part)

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

if __name__ == '__main__':
    to_list = ["491315091@qq.com","693610802@qq.com"]
    re = SendEmail(to_list)
    print re