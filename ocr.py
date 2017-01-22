# coding=utf-8
from PIL import Image
import requests
import time
import os
import hashlib
import math

# # 建立文件夹
# for i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
#     if not os.path.exists(i):
#         os.makedirs(i)

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
                    print y[0]
        guess.sort(reverse=True)
        print "", guess[0]

        count += 1
