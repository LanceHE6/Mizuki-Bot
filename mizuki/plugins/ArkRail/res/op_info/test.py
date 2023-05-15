# -*- coding = utf-8 -*-
# @File:test.py
# @Author:Hycer_Lance
# @Time:2023/5/13 9:42
# @Software:PyCharm

from PIL import Image, ImageDraw, ImageFont

def line_break(line: str, line_count: int)-> str:
    """
    实现在字符串固定字符数后添加换行符
    :param line: 待处理字符串
    :param line_count: 在line_count个字后换行
    :return: 处理后的字符串
    """
    line_char_count = line_count * 2  # 每行字符数：12个中文字符
    table_width = 4
    ret = ''
    width = 0
    for c in line:
        if len(c.encode('utf8')) == 3:  # 中文
            if line_char_count == width + 1:  # 剩余位置不够一个汉字
                width = 2 #挪到下一行
                ret += '\n' + c
            else: # 中文宽度加2，注意换行边界
                width += 2
                ret += c
        else:
            if c == '\t':
                space_c = table_width - width % table_width  # 已有长度对TABLE_WIDTH取余
                ret += ' ' * space_c
                width += space_c
            elif c == '\n':
                width = 0
                ret += c
            else:
                width += 1
                ret += c
        if width >= line_char_count:
            ret += '\n'
            width = 0
    if ret.endswith('\n'):
        return ret
    return ret + '\n'


bg_img = Image.open("bg.png")
op_img = Image.open("37_big.png")
max_health_img = Image.open("max_health.png")
atk_img = Image.open("atk.png")
def_img = Image.open("def.png")
crit_d_img = Image.open("crit_d.png")
crit_r_img = Image.open("crit_r.png")
res_img = Image.open("res.png")
speed_img = Image.open("speed.png")

img = Image.new("RGBA", bg_img.size, (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

img.paste(bg_img, (0, 0))
img.paste(op_img,(1450, 100), mask=op_img)
level_img = Image.open("level.png")
img.paste(level_img, (50, 200), mask=level_img)
#七种属性图标
img.paste(max_health_img, (50, 520))
img.paste(atk_img, (50, 580))
img.paste(def_img, (50, 640))
img.paste(res_img, (50, 700))
img.paste(speed_img, (400, 520))
img.paste(crit_r_img, (400, 580))
img.paste(crit_d_img, (400, 640))
#属性值
font = ImageFont.truetype("simhei", 100)
draw.text((95, 245), "90", font= font, fill='white', stroke_fill='black', stroke_width=2)
font = ImageFont.truetype("simhei", 50)
draw.text((50, 460), "属性>>", font= font, fill= 'black')
draw.text((250, 515), "2745",font= font, fill= "black")#max_health
draw.text((250, 575), "828",font= font, fill= "black")#atk
draw.text((250, 635), "155",font= font, fill= "black")#def
draw.text((250, 695), "0",font= font, fill= "black")#res
draw.text((600, 515), "100.0",font= font, fill= "black")#speed
draw.text((600, 575), "5%",font= font, fill= "black")#crit_r
draw.text((600, 635), "50%",font= font, fill= "black")#crit_d

#干员模型
box = Image.new("RGBA", (480, 395), (0,0,0,150))
op_models = Image.open("../models/37.png").resize((900, 900))
img.paste(box, (280, 105), mask=box)
img.paste(op_models, (50, -250), mask=op_models)

#干员信息
stars = Image.open("../stars/6.png").resize((350, 92))#星级
img.paste(stars, (40, 760), mask= stars)
font = ImageFont.truetype("simhei", 150)
draw.text((50, 860), "玛恩纳", font= font, fill= 'white', stroke_fill='black', stroke_width=2)#name

pro_img = Image.open("../profession/近卫_big.png")
img.paste(pro_img, (50, 1020))
font = ImageFont.truetype("simhei", 60)
draw.text((240, 1020), "近卫", font= font, fill= 'white', stroke_fill='black', stroke_width=1)
draw.text((240, 1090), "蓄能", font= font, fill= 'white', stroke_fill='black', stroke_width=1)

#技能详情
box = Image.open("box.png")
img.paste(box, (650, 200), mask=box)

draw.text((800, 220), "技能", font= font, fill= 'white', stroke_fill='black', stroke_width=1)
draw.text((1180, 220), "描述", font= font, fill= 'white', stroke_fill='black', stroke_width=1)
draw.text((1410, 220), "技力", font= font, fill= 'white', stroke_fill='black', stroke_width=1)

font = ImageFont.truetype("simhei", 48)
draw.text((780, 380), "无动于衷", font= font, fill= 'white', stroke_fill='black', stroke_width=2)
draw.text((780, 680), "二连击", font= font, fill= 'white', stroke_fill='black', stroke_width=2)
draw.text((780, 980), "未照耀的荣光", font= font, fill= 'white', stroke_fill='black', stroke_width=2)
font = ImageFont.truetype("simhei", 30)
draw.text((1100, 360), line_break("嘲讽敌方所有单位，自身防御力增加200%，每次受到攻击自身攻击力增加20%(最高增加200%)且不会随技能结束而清除，持续200回合",10), font= font, fill= 'white', stroke_fill='black', stroke_width=2)
draw.text((1100, 660), line_break("连续对敌人造成两次相当于自身攻击力${r1_float} ~ ${r2_float}的伤害",10), font= font, fill= 'white', stroke_fill='black', stroke_width=2)
draw.text((1100, 960), line_break("对敌方所有单位造成相当于自身攻击力${r1_float}的物理伤害和自身攻击力${r2_float}的真实伤害，然后清除自身伤害加成",10), font= font, fill= 'white', stroke_fill='black', stroke_width=2)
font = ImageFont.truetype("simhei", 64)
draw.text((1450, 380), "5", font= font, fill= 'white', stroke_fill='black', stroke_width=2)
draw.text((1450, 680), "35", font= font, fill= 'white', stroke_fill='black', stroke_width=2)
draw.text((1450, 980), "42", font= font, fill= 'white', stroke_fill='black', stroke_width=2)

img.show()
