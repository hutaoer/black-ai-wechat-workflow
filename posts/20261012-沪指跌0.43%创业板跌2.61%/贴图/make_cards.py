# -*- coding: utf-8 -*-
"""把长文压成竖版卡片贴图（1080x1440）。涨=红，跌=绿。
字体：只用 PingFang SC（HK/TC 字面缺部分简体字形，如“稳”）。"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1440
PAD = 96
MAXW = W - PAD * 2

BG      = "#F6F5F2"
INK     = "#1B1B1B"
INK2    = "#5A5A5A"
INK3    = "#8C8C8C"
RED     = "#C0392B"   # 涨
GREEN   = "#1E8E5A"   # 跌
LINE    = "#DEDCD6"
CHIP_BG = "#EAE7E0"

FONT_PATH = "/System/Library/Fonts/PingFang.ttc"

# ---- 字体：锁定简体中文字面（PingFang SC），再按字重挑 ----
def _scan_faces():
    faces = {}
    for i in range(16):
        try:
            faces[i] = ImageFont.truetype(FONT_PATH, 40, index=i).getname()
        except Exception:
            break
    return faces

_FACES = _scan_faces()
_SC = {i: n for i, n in _FACES.items() if "SC" in n[0]} or dict(_FACES)

def _pick(styles):
    for s in styles:                      # 先按字重优先级，再扫字面
        for i, (fam, st) in _SC.items():
            if st.lower() == s:
                return i
    return next(iter(_SC))

_IDX_REG  = _pick(("regular", "light", "medium"))
_IDX_BOLD = _pick(("semibold", "bold", "medium"))

def F(size, bold=False):
    return ImageFont.truetype(FONT_PATH, size,
                              index=_IDX_BOLD if bold else _IDX_REG)

# ---- 断行 ----
_PUNCT = "，。、；：！？（）《》\u201c\u201d\u2018\u2019—…·%"
_LEADING_BAD = "，。、；：！？）》”’%·"

def tokenize(text):
    """CJK 单字成 token，ASCII/数字连成一 token，避免把数字拆断。"""
    toks, buf = [], ""
    def flush():
        nonlocal buf
        if buf:
            toks.append(buf); buf = ""
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff' or ch in _PUNCT:
            flush(); toks.append(ch)
        elif ch == " ":
            flush(); toks.append(" ")
        else:
            buf += ch
    flush()
    return toks

def wrap(draw, text, font, maxw):
    lines, cur = [], ""
    for t in tokenize(text):
        if t == "\n":
            lines.append(cur); cur = ""; continue
        # 避免行首标点：把它贴回上一行行尾
        if cur == "" and t in _LEADING_BAD and lines:
            lines[-1] += t
            continue
        trial = cur + t
        if draw.textlength(trial, font=font) <= maxw or cur == "":
            cur = trial
        else:
            lines.append(cur); cur = t.lstrip()
    if cur:
        lines.append(cur)
    # 后处理：行首标点回收（含数字 token 后紧跟标点被换行的情况）
    for i in range(1, len(lines)):
        while lines[i] and lines[i][0] in _LEADING_BAD:
            lines[i-1] += lines[i][0]
            lines[i] = lines[i][1:].lstrip()
    return [ln for ln in lines if ln]

# ---- 画布 ----
def new_card(page, total):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=INK)
    d.text((W - PAD, H - 74), f"{page:02d} / {total:02d}", font=F(30), fill=INK3, anchor="rs")
    return img, d

def draw_chip(d, x, y, text):
    f = F(34, bold=True)
    tw = d.textlength(text, font=f)
    padx, pady = 26, 14
    d.rounded_rectangle([x, y, x + tw + padx*2, y + 34 + pady*2], radius=10, fill=CHIP_BG)
    d.text((x + padx, y + pady - 2), text, font=f, fill=INK)
    return y + 34 + pady*2

def render(blocks, page, total, footer=""):
    img, d = new_card(page, total)
    y = 120
    for b in blocks:
        t = b["t"]
        if t == "gap":
            y += b.get("h", 30)
        elif t == "rule":
            d.line([PAD, y, W - PAD, y], fill=LINE, width=2); y += 40
        elif t == "chip":
            y = draw_chip(d, PAD, y, b["x"]); y += 46
        else:
            size = {"h1": 74, "h2": 52, "p": 42, "big": 46, "note": 33, "up": 42, "down": 42}[t]
            bold = t in ("h1", "h2", "big", "up", "down")
            col = {"up": RED, "down": GREEN, "note": INK3}.get(t, b.get("c", INK))
            f = F(size, bold=bold)
            lh = int(size * 1.55)
            for line in wrap(d, b["x"], f, MAXW):
                d.text((PAD, y), line, font=f, fill=col)
                y += lh
            y += b.get("gap", 14)
    if footer:
        d.text((PAD, H - 74), footer, font=F(28), fill=INK3, anchor="ls")
    return img

cards = []

# 01 封面
cards.append(render([
    {"t":"gap","h":70},
    {"t":"chip","x":"10·12　A股复盘"},
    {"t":"gap","h":60},
    {"t":"h1","x":"今天A股，"},
    {"t":"h1","x":"跌的不是“指数”"},
    {"t":"gap","h":40},
    {"t":"down","x":"沪指  -0.43%"},
    {"t":"down","x":"创业板指  -2.61%"},
    {"t":"gap","h":10},
    {"t":"p","x":"一句大白话，看懂今天的下跌。", "c":INK2},
], 1, 7, footer="数据来源：中证网 · 新华财经 2026-10-12"))

# 02 核心结论
cards.append(render([
    {"t":"chip","x":"一句话"},
    {"t":"gap","h":40},
    {"t":"h1","x":"指数没崩，"},
    {"t":"h1","x":"崩的是涨得最凶的"},
    {"t":"h1","x":"那批科技股"},
    {"t":"gap","h":30},
    {"t":"rule"},
    {"t":"down","x":"沪指  -0.43%　深成指  -2.03%"},
    {"t":"down","x":"创业板指  -2.61%"},
    {"t":"gap","h":16},
    {"t":"p","x":"超 4300 只个股下跌，成交 1.55 万亿，比上周五缩了一截。"},
], 2, 7, footer="数据来源：中证网 · 中新网 2026-10-12"))

# 03 谁跌谁涨
cards.append(render([
    {"t":"chip","x":"盘面"},
    {"t":"gap","h":36},
    {"t":"h1","x":"谁在跌，谁在涨"},
    {"t":"gap","h":34},
    {"t":"down","x":"跌 · 高位科技"},
    {"t":"p","x":"光通信 · PCB · CPO · 半导体", "c":INK2},
    {"t":"p","x":"星网锐捷跌停，中际旭创 -6%", "c":INK2, "gap":26},
    {"t":"up","x":"涨 · 红利与低位"},
    {"t":"p","x":"银行 · 白酒 · 传媒", "c":INK2},
    {"t":"p","x":"建行/招行/农行 +3%", "c":INK2, "gap":30},
    {"t":"rule"},
    {"t":"h2","x":"钱从高位科技，挪进红利和低位"},
], 3, 7, footer="数据来源：中证网收评 2026-10-12"))

# 04 为什么
cards.append(render([
    {"t":"chip","x":"三股力量"},
    {"t":"gap","h":36},
    {"t":"h1","x":"为什么跌？"},
    {"t":"gap","h":30},
    {"t":"h2","x":"① 涨多了，要兑现"},
    {"t":"p","x":"AI硬件、光模块这一年涨上天，资金今天在“高低切换”。", "gap":26},
    {"t":"h2","x":"② 外头的绳子还勒着"},
    {"t":"p","x":"10年期美债收益率还在 5.2% 上方，最贵的成长股先挨压。", "gap":26},
    {"t":"h2","x":"③ 十月是业绩照妖镜"},
    {"t":"p","x":"三季报开始披露，光讲故事、业绩跟不上的票最难受。"},
], 4, 7, footer="数据来源：中证网 · 金投网 2026-10-12"))

# 05 后市
cards.append(render([
    {"t":"chip","x":"后市"},
    {"t":"gap","h":36},
    {"t":"h1","x":"会跌多久？"},
    {"t":"gap","h":34},
    {"t":"h2","x":"震荡分化，不是系统性大跌"},
    {"t":"p","x":"中金：下跌空间有限；申万宏源：两波大涨之间的休整。", "gap":30},
    {"t":"rule"},
    {"t":"big","x":"关口  沪指 3800 · 创业板 3000"},
    {"t":"gap","h":20},
    {"t":"h2","x":"真正的变量是两个"},
    {"t":"p","x":"9月 CPI·PPI 数据，和下旬的政策落地。"},
], 5, 7, footer="数据来源：财经 · 中国经济时报 2026-10-12"))

# 06 黄金债市
cards.append(render([
    {"t":"chip","x":"黄金 · 债市"},
    {"t":"gap","h":36},
    {"t":"h1","x":"钱往哪躲"},
    {"t":"gap","h":34},
    {"t":"h2","x":"黄金：摸高，也跳水"},
    {"t":"p","x":"现货报 4174 美元，盘中破 4200；短线看 4100、配置盘看 4000；央行连买 23 个月。", "gap":28},
    {"t":"h2","x":"债市：今天最稳的一块"},
    {"t":"p","x":"股弱债强。30年国债期货涨 0.49% 创年内新高，10年国债收益率 1.66%、30年 2.08%。"},
], 6, 7, footer="数据来源：金投网 · 财联社 2026-10-12"))

# 07 收尾
cards.append(render([
    {"t":"chip","x":"最后一句"},
    {"t":"gap","h":40},
    {"t":"h1","x":"别把“指数没跌”"},
    {"t":"h1","x":"当成“你的账户没事”"},
    {"t":"gap","h":34},
    {"t":"rule"},
    {"t":"p","x":"持仓结构不同，过的是两种日子。", "gap":40},
    {"t":"h2","x":"你今天账户是红是绿？"},
    {"t":"h2","x":"打开看一眼，回来报个数。"},
], 7, 7, footer="10·12 A股复盘　|　仅供参考，不构成投资建议"))

for i, im in enumerate(cards, 1):
    im.save(os.path.join(OUT, f"{i:02d}.png"))

# 长图
gap = 24
total_h = sum(im.height for im in cards) + gap * (len(cards) - 1)
strip = Image.new("RGB", (W, total_h), "#EFEDE8")
yy = 0
for im in cards:
    strip.paste(im, (0, yy)); yy += im.height + gap
strip.save(os.path.join(OUT, "长图-全篇.png"))

print("done:", len(cards), "cards | font:", _FACES[_IDX_REG], "/", _FACES[_IDX_BOLD])
