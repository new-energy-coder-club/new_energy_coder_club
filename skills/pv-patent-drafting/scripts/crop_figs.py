# -*- coding: utf-8 -*-
"""裁剪 7 张附图 PNG 的白色边距，输出裁剪后尺寸（供嵌入计算）"""
from PIL import Image, ImageChops
import os, json

FIGDIR = '/mnt/d/Project_env/SolarGlyph/patent/figures'
FIGS = ['fig1_system', 'fig2_flow', 'fig3_grid_alignment', 'fig4_mask_rasterize',
        'fig5_constraint_check', 'fig6_effect_compare', 'fig7_aisle_offset']

sizes = {}
for name in FIGS:
    p = os.path.join(FIGDIR, name + '.png')
    im = Image.open(p).convert('RGB')
    # 与白色背景求差，找内容包围盒
    bg = Image.new('RGB', im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg)
    # 阈值：近白视为背景
    gray = diff.convert('L').point(lambda v: 255 if v > 12 else 0)
    bbox = gray.getbbox()
    if bbox:
        m = 12  # 留白边距
        l, t, r, b = bbox
        l = max(0, l - m); t = max(0, t - m)
        r = min(im.size[0], r + m); b = min(im.size[1], b + m)
        im2 = im.crop((l, t, r, b))
        im2.save(p)
        sizes[name] = im2.size
        print(name, 'cropped to', im2.size)
print(json.dumps(sizes))
