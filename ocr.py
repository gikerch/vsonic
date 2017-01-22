# coding=utf-8
from PIL import Image
import requests
import time
import os
import hashlib
import math

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# # 建立文件夹
# for i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
#     if not os.path.exists(i):
#         os.makedirs(i)

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
    msg["Subject"] = "%s验证码识别成功运行" %date
    msg["From"] = from_addr
    # msg["To"] = to_addr
    # 发送给多人
    msg['To'] = ",".join(to_list)

    #---这是文字部分---
    part = MIMEText('周威，验证码识别成功，祝你天天开心')
    msg.attach(part)

    #---这是附件部分---
    # xlsx类型附件
    # part = MIMEApplication(open(u'JD显示器数据.xls', 'rb').read())
    # part.add_header('Content-Disposition', 'attachment', filename= "jd显示器排名.xls".encode('gb2312'))
    # msg.attach(part)

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


base_path = 'F:\Python'
DEFAULT_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36 Core/1.47.210.400 QQBrowser/9.3.7336.400'
}

# 向量空间图像识别
class VectorCompare:

    def magnitude(self, concordance):
        total = 0
        for word, count in concordance.iteritems():
            total += count ** 2
        return math.sqrt(total)

    def relation(self, concordance1, concordance2):
        relevance = 0
        topvalue = 0
        for word, count in concordance1.iteritems():
            if concordance2.has_key(word):
                topvalue += count * concordance2[word]
        return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))

# 二值化（需要根据验证码调整阈值）
def get_bin_table():
    threshold = 231
    table = []
    for ii in range(256):
        if ii < threshold:
            table.append(0)
        else:
            table.append(1)
    return table


# 判断像素点是黑点还是白点
def getflag(img, x, y):
    tmp_pixel = img.getpixel((x, y))
    if tmp_pixel > 228:  # 白点
        tmp_pixel = 0
    else:  # 黑点
        tmp_pixel = 1
    return tmp_pixel


# 黑点个数
def sum_9_region(img, x, y):
    width = img.width
    height = img.height
    flag = getflag(img, x, y)
    # 如果当前点为白色区域,则不统计邻域值
    if flag == 0:
        return 0
    # 如果是黑点
    if y == 0:  # 第一行
        if x == 0:  # 左上顶点,4邻域
            # 中心点旁边3个点
            total = getflag(img, x, y + 1) + getflag(img, x + 1, y) + getflag(img, x + 1, y + 1)
            return total
        elif x == width - 1:  # 右上顶点
            total = getflag(img, x, y + 1) + getflag(img, x - 1, y) + getflag(img, x - 1, y + 1)
            return total
        else:  # 最上非顶点,6邻域
            total = getflag(img, x - 1, y) + getflag(img, x - 1, y + 1) + getflag(img, x, y + 1) \
                    + getflag(img, x + 1, y) \
                    + getflag(img, x + 1, y + 1)
            return total
    elif y == height - 1:  # 最下面一行
        if x == 0:  # 左下顶点
            # 中心点旁边3个点
            total = getflag(img, x + 1, y) + getflag(img, x + 1, y - 1) + getflag(img, x, y - 1)
            return total
        elif x == width - 1:  # 右下顶点
            total = getflag(img, x, y - 1) + getflag(img, x - 1, y) + getflag(img, x - 1, y - 1)
            return total
        else:  # 最下非顶点,6邻域
            total = getflag(img, x - 1, y) + getflag(img, x + 1, y) + getflag(img, x, y - 1) + getflag(img, x - 1, y - 1) + getflag(img, x + 1, y - 1)
            return total
    else:  # y不在边界
        if x == 0:  # 左边非顶点
            total = getflag(img, x, y - 1) + getflag(img, x, y + 1) + getflag(img, x + 1, y - 1) + getflag(img, x + 1, y) + getflag(img, x + 1, y + 1)
            return total
        elif x == width - 1:  # 右边非顶点
            total = getflag(img, x, y - 1) + getflag(img, x, y + 1) + getflag(img, x - 1, y - 1) + getflag(img, x - 1, y) + getflag(img, x - 1, y + 1)
            return total
        else:  # 具备9领域条件的
            total = getflag(img, x - 1, y - 1) + getflag(img, x - 1, y) + getflag(img, x - 1, y + 1) + getflag(img, x, y - 1) \
                    + getflag(img, x, y + 1) + getflag(img, x + 1, y - 1) + getflag(img, x + 1, y) + getflag(img, x + 1, y + 1)
            return total


# 下载训练集验证码
def downloads_pic(pic_path, picname):
    url = "http://172.20.3.252:9090/check2code.action" 
    res = requests.get(url, stream=True)
    with open(pic_path + picname + '.jpg', 'wb') as f:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
        f.close()

# 分割图片
def spiltimg(img):
    # 按照图片的特点,进行切割,这个要根据具体的验证码来调整像素值. # 见原理图
    # :param img:
    # :return:
    child_img_list = []
    for index in range(4):
        x = 15 + index * (12 + 10) 
        y = 6
        child_img = img.crop((x, y, x + 12, img.height - 9))
        child_img_list.append(child_img)
    return child_img_list
    # for index in range(4):
    #     x = 15 + index * (12 + 10)  # 见原理图
    #     y = 3
    #     child_img = img.crop((x, y, x + 13, img.height - 2))
    #     child_img_list.append(child_img)
    # return child_img_list


def toGrey(im):
    imgry = im.convert('L')  # 转化为灰度图
    table = get_bin_table()
    out = imgry.point(table, '1')
    return out


# 去除杂质点
def greyimg(image):
    width = image.width
    height = image.height
    box = (0, 0, width, height)
    imgnew = image.crop(box)
    for i in range(0, height):
        for j in range(0, width):
            num = sum_9_region(image, j, i)
            if num < 2:
                imgnew.putpixel((j, i), 255)  # 设置为白色
            else:
                imgnew.putpixel((j, i), 0)  # 设置为黑色
    return imgnew


# 验证码灰度化并且分割图片
# param 待分割图片入境  分割后图片路径
def begin(pic_path, split_pic_path):
    for f in os.listdir(pic_path):
        if os.path.isfile(pic_path + f):
            if f.endswith(".jpg"):
                pic = Image.open(pic_path + f)
                pic = toGrey(pic)
                pic.save("new_code.jpg")
                pic = Image.open("new_code.jpg")
                #newpic = greyimg(pic)
                childs = spiltimg(pic)
                count = 0
                for c in childs:
                    c.save(split_pic_path + f.split(".")[0] + "-" + str(count) + '.jpg')
                    count += 1


# 将图片转换为矢量
def buildvector(im):
    d1 = {}
    count = 0
    for i in im.getdata():
        d1[count] = i
        count += 1
    return d1


if __name__ == "__main__":
    print "start..."
    # 下载训练集
    # for i in range(15):
    #     downloads_pic('./pic',str(i))
    
    # 实例化识别模型
    v = VectorCompare()

    # 加载训练集
    iconset = ['a', 'b', 'c', 'd', 'e', 'f', 'g',
           'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    imageset = []

    for letter in iconset:
        for img in os.listdir('./trainset/%s/' % (letter)):
            temp = []
            if img != "Thumbs.db" and img != ".DS_Store":  # windows check...
                temp.append(buildvector(Image.open(
                    "./trainset/%s/%s" % (letter, img))))
            # 把每一个img对象放在对应的字母下
            imageset.append({letter: temp})
            # [{A:[{0:,1:,2:}],A:[{}]},B:[,],C:[,]...}]
    # print imageset
    # 切割测试集图片
    begin('pic/','pic2/')
    
    
    # 开始识别每个字符
    count = 0
    # 验证码的字符循环4次
    for letter in os.listdir('./pic2'):
        m = hashlib.md5()
        # 切割图片
        im3 = Image.open('pic2/%s' % letter)
        guess = []
        # 训练样本的循环A-Z
        for image in imageset:
            # x字母，y列表[],每个像素的亮度值
            # 每个字母下的样本的循环
            for x, y in image.iteritems():
                if len(y) != 0:
                    guess.append((v.relation(y[0], buildvector(im3)), x))
                    # print y[0]
        guess.sort(reverse=True)
        print "", guess[0]
        count += 1

    to_list = ['491315091@qq.com']
    re = SendEmail(to_list)
    print re
