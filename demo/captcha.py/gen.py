#!/usr/bin/env python
#-*- coding: utf8 -*-

import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

font_path = '/Library/Fonts/Arial.ttf'
number = 4
size = (100, 30)
bgcolor = (255, 255, 255)
fontcolor = (0, 0, 255)
linecolor = (255, 0, 0)
draw_line = True
line_number = (1, 3)
rand_seqs = list('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
# rand_seqs = list('0123456789')

font = ImageFont.truetype(font_path, 25)

def gene_text():
    return ''.join(random.sample(rand_seqs, number))

def gene_line(draw, width, height):
    begin = (random.randint(0, width), random.randint(0, height))
    end = (random.randint(0, width), random.randint(0, height))
    draw.line([begin, end], fill=linecolor)

def gene_code():
    width, height = size
    image = Image.new('RGBA', (width, height), bgcolor)
    draw = ImageDraw.Draw(image)
    text = gene_text()
    font_width, font_height = font.getsize(text)
    draw.text(((width - font_width) / number, (height - font_height) / number),
        text, font=font, fill=fontcolor)
    if draw_line:
        for i in xrange(random.randint(*line_number)):
            gene_line(draw, width, height)
    image = image.transform((width + 20, height + 10),
                            Image.AFFINE,
                            (1, -0.3, 0, -0.1, 1, 0),
                            Image.BILINEAR)  #创建扭曲
    image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)  #滤镜，边界加强
    return text, image

if __name__ == "__main__":
    text, image = gene_code()
    print text
    image.show()
