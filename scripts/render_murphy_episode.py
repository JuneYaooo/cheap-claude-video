#!/usr/bin/env python3
"""Render 'The Shape of the Unexpected', a procedural Murphy's law short.

python3 scripts/render_murphy_episode.py --output output/murphy_law
Use --preview for a contact sheet; --sample for the first 16 seconds.
Requires Pillow, numpy, FFmpeg. No network or generative media services.
Override MURPHY_SERIF_FONT / MURPHY_LATIN_FONT on non-macOS systems.
All geometric simulations and the original instrumental score are deterministic.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import wave
import zipfile
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
GOLD = '#e5c581'
WHITE = '#eee7d5'
RED = '#e87d60'
TEAL = '#91b9ac'
MUTED = '#aca18d'
DIM = '#514a3c'
SERIF = os.environ.get('MURPHY_SERIF_FONT', '/System/Library/Fonts/Supplemental/Songti.ttc')
LATIN = os.environ.get('MURPHY_LATIN_FONT', '/System/Library/Fonts/Supplemental/Times New Roman.ttf')
SCALE = 1.5
FPS = 30
SCENES = [
    ('墨菲定律', '意外的形状', '一切都安排好了。除了，那一个小小的意外。'),
    ('01 / 意外', '偏偏，是这个时候', '越是重要的时刻，一次小故障，越显得刺眼。'),
    ('02 / 定律', '墨菲定律', '“可能出错的事，终会出错。”'),
    ('03 / 起点', '1949', '一种广为流传的起源说法：工程试验中，传感器被接反了。'),
    ('04 / 一次', '只有 1%', '假设每次出错概率都是 1%，而且各次相互独立。'),
    ('05 / 重复', '把一次，交给时间', '重复 100 次，至少出错一次的概率，已经约为 63.4%。'),
    ('06 / 累积', '小概率，有很多次机会', '重复 1,000 次，这个概率约为 99.996%。'),
    ('07 / 边界', '接近必然 ≠ 注定发生', '这是独立重复的概率模型；墨菲定律本身，是一句经验格言。'),
    ('08 / 连锁', '真正麻烦的，是连锁', '一处故障，如果没有被隔离，就可能拖倒后面的每一环。'),
    ('09 / 转折', '让错误，停在这里', '留一道隔离，把一次失误，留在一次失误里。'),
    ('10 / 防错', '先让错误难以发生', '与其反复提醒“别接反”，不如让接口只能正确地接上。'),
    ('11 / 备用', '再给重要的事，另一条路', '两路故障若相互独立，且各为 1%，同时失效就是 0.01%。'),
    ('12 / 关联', '两份，不一定是两重保障', '如果两条路共用同一个故障源，独立性的假设就不成立。'),
    ('13 / 余量', '给意外，留一点位置', '提前备份，预留时间。缓冲不会消灭意外，却能减少代价。'),
    ('14 / 重新出发', '世界依然会有意外', '防错、备用、缓冲，让一次偏离，不必成为终点。'),
    ('尾声', '准备的形状', '你不必预知每一次意外。你可以，让自己多一种选择。'),
]
DURATION = len(SCENES) * 8

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x):
    x = clamp(x)
    return x*x*(3-2*x)
def rgb(c): return tuple(int(c[i:i+2], 16) for i in (1,3,5))
def shade(c, value): return tuple(round(v*value) for v in rgb(c))
def lerp(a, b, x): return a+(b-a)*x

@lru_cache(128)
def font(size, latin=False): return ImageFont.truetype(LATIN if latin else SERIF, round(size*SCALE))

@lru_cache(2048)
def glyph(text, size, color, latin):
    f=font(size, latin); b=f.getbbox(text)
    im=Image.new('RGBA', (max(1,b[2]-b[0]+8), max(1,b[3]-b[1]+8)))
    ImageDraw.Draw(im).text((4-b[0],4-b[1]), text, font=f, fill=color)
    return im

class Canvas:
    def __init__(self, image): self.im=image; self.d=ImageDraw.Draw(image)
    def line(self, pts, color=GOLD, width=1):
        self.d.line([(round(x*SCALE),round(y*SCALE)) for x,y in pts], fill=color, width=max(1,round(width*SCALE)), joint='curve')
    def ellipse(self,x,y,rx,ry=None,color=GOLD,fill=False,width=1):
        ry=rx if ry is None else ry
        box=((x-rx)*SCALE,(y-ry)*SCALE,(x+rx)*SCALE,(y+ry)*SCALE)
        self.d.ellipse(box,fill=color if fill else None,outline=None if fill else color,width=max(1,round(width*SCALE)))
    def rect(self,box,color=GOLD,fill=False,width=1,r=0):
        b=tuple(v*SCALE for v in box)
        self.d.rounded_rectangle(b,radius=r*SCALE,fill=color if fill else None,outline=None if fill else color,width=max(1,round(width*SCALE)))
    def text(self,text,x,y,size=26,color=WHITE,anchor='center',alpha=1,latin=False):
        if alpha<=0: return
        p=glyph(text,size,color,latin)
        if alpha<.999:
            p=p.copy();p.putalpha(p.getchannel('A').point(lambda v:round(v*alpha)))
        px=x*SCALE-(p.width/2 if anchor=='center' else p.width if anchor=='right' else 0)
        self.im.paste(p,(round(px),round(y*SCALE-p.height/2)),p)
    def glow(self,x,y,r=4,color=GOLD):
        for k,v in [(5,.06),(3,.12),(1.8,.3)]: self.ellipse(x,y,r*k,color=shade(color,v),fill=True)
        self.ellipse(x,y,r,color=color,fill=True)
    def path(self,pts,p=1,color=GOLD,width=1.4,glow=False):
        q=pts[:max(2,int(len(pts)*clamp(p)))]
        if glow:
            self.line(q,shade(color,.09),width+8)
            self.line(q,shade(color,.2),width+3)
        self.line(q,color,width)
    def arrow(self,a,b,color=GOLD,width=1):
        self.line([a,b],color,width)
        theta=math.atan2(b[1]-a[1],b[0]-a[0])
        self.line([(b[0]-10*math.cos(theta-.45),b[1]-10*math.sin(theta-.45)),b,(b[0]-10*math.cos(theta+.45),b[1]-10*math.sin(theta+.45))],color,width)

@lru_cache(1)
def background():
    h,w=round(H*SCALE),round(W*SCALE)
    yy,xx=np.mgrid[:h,:w];u=xx/w;v=yy/h
    glow=np.exp(-((u-.45)**2/.12+(v-.43)**2/.3))
    blue=np.exp(-((u-.9)**2/.12+(v-.65)**2/.2))
    noise=np.random.default_rng(42).normal(0,.85,(h,w))
    arr=np.stack([9+9*glow+noise,11+7*glow+noise,14+4*glow+5*blue+noise],axis=-1)
    return Image.fromarray(np.uint8(np.clip(arr,0,255)))

PARTICLES=np.random.default_rng(16).random((86,4))

def bezier(a,b,c,d,n=140):
    return [((1-t)**3*a[0]+3*(1-t)**2*t*b[0]+3*(1-t)*t*t*c[0]+t**3*d[0],(1-t)**3*a[1]+3*(1-t)**2*t*b[1]+3*(1-t)*t*t*c[1]+t**3*d[1]) for t in np.linspace(0,1,n)]

def orbit(a,t,center=(640,360),r=220,flatten=.42,color=DIM):
    pts=[]
    for z in np.linspace(0,2*math.pi,180):
        x,y=r*math.cos(z),r*flatten*math.sin(z)
        pts.append((center[0]+x*.94-y*.34,center[1]+x*.34+y*.94))
    a.path(pts,color=color,width=.65)
    pos=pts[int((t*.04)%1*179)];a.glow(*pos,2.6)

def node(a,x,y,label,color=GOLD,r=30):
    a.ellipse(x,y,r,color=color)
    a.text(label,x,y,22,color)

def circuit(a,t,good=False):
    pts=bezier((180,405),(430,310),(700,490),(1090,335))
    a.path(pts,color=DIM,width=1.5)
    gap=80
    a.path(pts[:gap],ease(t/.9),color=GOLD,glow=True)
    if good:
        alt=bezier(pts[gap],(760,220),(880,200),pts[120])
        a.path(alt,ease((t-1)/2),color=TEAL,glow=True)
        a.text('备用路径',847,231,20,TEAL,alpha=ease((t-1.2)/1))
        path=pts[:gap]+alt+pts[120:]
    else:path=pts
    progress=clamp((t-.5)/4.4)
    n=min(len(path)-1,int(progress*(len(path)-1)))
    if not good and n>=gap:
        x,y=pts[gap];drop=ease((t-3)/1.4);y+=180*drop
        a.glow(x,y,6,RED)
        a.line([(pts[gap][0]-13,pts[gap][1]-13),(pts[gap][0]+13,pts[gap][1]+13)],RED,2)
        a.line([(pts[gap][0]+13,pts[gap][1]-13),(pts[gap][0]-13,pts[gap][1]+13)],RED,2)
    else:
        a.path(path[:n+1],color=TEAL if good else GOLD,width=2,glow=True)
        a.glow(*path[n],6,TEAL if good else GOLD)
    a.ellipse(180,405,10,color=GOLD);a.ellipse(1090,335,10,color=TEAL if good else DIM)

def domino(a,t,stop=False):
    ground=495
    a.line([(190,ground),(1110,ground)],DIM)
    for j in range(12):
        x=230+j*72
        angle=ease((t-1-j*.18)/.65)*1.17
        if stop and j>=5:angle=0
        if stop and j==4:angle=min(angle,.30)
        h=115;w=18
        # Rotate about the bottom right corner; each tile top moves to the right.
        pts=[]
        for xx,yy in [(-w,0),(0,0),(0,-h),(-w,-h),(-w,0)]:
            pts.append((x+xx*math.cos(angle)-yy*math.sin(angle),ground+xx*math.sin(angle)+yy*math.cos(angle)))
        a.path(pts,color=RED if angle>.3 else GOLD,width=2)
        a.text(f'{j+1:02}',x-7,529,16,MUTED,latin=True)
    if stop:
        a.rect((557,340,569,495),TEAL,fill=True)
        a.text('隔离',565,305,26,TEAL)
        a.text('故障止步',420,595,27,RED)
        a.text('其余照常',820,595,27,TEAL)

def connector(a,t,keyed=False):
    x=350+80*ease((t-.6)/1.6)
    if keyed:x+=80*ease((t-3)/1.6)
    a.line([(160,390),(x,390)],DIM,2)
    a.rect((x,335,x+165,445),GOLD,width=2,r=9)
    for j in range(4):a.line([(x+165,355+j*23),(x+205,355+j*23)],GOLD,5)
    a.rect((715,310,945,470),TEAL if keyed else GOLD,width=2,r=10)
    for j in range(4):a.ellipse(747,352+j*25,5,color=GOLD)
    a.line([(945,390),(1110,390)],DIM,2)
    if keyed:
        a.rect((x+165,321,x+205,335),TEAL,fill=True)
        a.rect((715,321,755,335),TEAL,width=2)
        a.text('定位凸起',x+165,270,23,TEAL)
        a.text('唯一方向',850,537,26,TEAL)
        a.arrow((620,390),(690,390),TEAL,2)
    else:
        for j in range(4):
            p=bezier((x+205,355+j*23),(650,355+j*23),(660,427-j*25),(747,427-j*25))
            a.path(p,ease((t-2)/2),RED,1.5,True)
        a.text('方向反了，数据也错了',640,548,29,RED,alpha=ease((t-3)/1))

def graphic(a,i,t):
    p=ease(t/1.3)
    if i==0:
        circuit(a,t)
        a.text('THE SHAPE OF THE UNEXPECTED',640,179,16,MUTED,latin=True,alpha=ease((t-.4)/1))
    elif i==1:
        # A graceful save arc halts one degree short of completion.
        x,y=640,356
        points=[(x+113*math.cos(z),y+113*math.sin(z)) for z in np.linspace(-math.pi/2,-math.pi/2+2*math.pi*.99*ease(t/2.8),160)]
        a.path(points,color=GOLD,width=2.3,glow=True)
        a.text(f'{round(99*ease(t/2.8))}%',x,y,66,GOLD,latin=True)
        a.text('正在保存',640,505,26,MUTED)
        if t>3:
            a.line([(594,529),(686,529)],RED,1.5)
            a.text('连接中断',640,570,28,RED,alpha=ease(t-3))
    elif i==2:
        for j in range(4):orbit(a,t+j*3,r=130+j*64,flatten=.42,color=shade(GOLD,.12+j*.025))
        a.text('凡是可能出错的事',640,316,48,WHITE,alpha=p)
        a.text('终会出错',640,391,65,GOLD,alpha=ease((t-1)/1.4))
        a.text("MURPHY’S LAW",640,498,20,MUTED,latin=True,alpha=ease((t-2)/1))
    elif i==3:connector(a,t)
    elif i==4:
        for j in range(100):
            x=245+(j%10)*31;y=254+(j//10)*29
            r=4*ease((t-j*.007)/.6)
            a.glow(x,y,r,RED) if j==49 else a.ellipse(x,y,r,color=shade(GOLD,.7),fill=True)
        a.text('99 次顺利 · 1 次出错',383,583,24,MUTED)
        a.text('1%',885,338,114,RED,latin=True,alpha=p)
        a.text('一次遇上故障的概率',885,440,25,WHITE)
        a.text('示意比例，不代表每 100 次必错 1 次',885,510,18,MUTED)
    elif i==5:
        n=max(1,round(100*ease(t/5)))
        prob=(1-.99**n)*100
        for j in range(100):
            x=225+(j%10)*30;y=250+(j//10)*29
            active=j<n
            a.ellipse(x,y,6,color=GOLD if active else DIM,fill=active)
        a.text(f'{n} 次',362,584,29,GOLD)
        a.text(f'{prob:.1f}%',897,335,100,RED,latin=True)
        a.text('至少一次出错',897,435,30,WHITE)
        a.text('1 − 0.99ⁿ',897,506,35,GOLD,latin=True)
    elif i==6:
        x0,y0=196,535;ww,hh=870,288
        a.line([(x0,y0-hh-25),(x0,y0),(x0+ww+30,y0)],MUTED)
        for v in [0,.5,1]:
            y=y0-hh*v;a.line([(x0,y),(x0+ww,y)],shade(MUTED,.22));a.text(f'{v*100:.0f}%',x0-20,y,18,MUTED,anchor='right',latin=True)
        for n in [0,100,500,1000]:
            x=x0+ww*n/1000;a.text(str(n),x,y0+29,18,MUTED,latin=True)
        n=1000*ease(t/5.5)
        pts=[(x0+ww*k/1000,y0-hh*(1-.99**k)) for k in np.linspace(0,max(1,n),220)]
        a.path(pts,color=GOLD,width=2,glow=True);a.glow(*pts[-1],4)
        a.text('至少一次出错的概率',x0,y0-hh-55,23,MUTED,anchor='left')
        a.text('99.996%',920,397,56,GOLD,latin=True,alpha=ease((t-4)/1))
        a.text('独立重复 1,000 次',920,454,23,MUTED,alpha=ease((t-4)/1))
        a.text('重复次数 n',1080,592,18,MUTED)
    elif i==7:
        a.text('P = 1 − (1 − p)ⁿ',640,305,65,GOLD,latin=True,alpha=p)
        a.line([(420,374),(860,374)],DIM)
        a.text('相互独立',385,427,29,WHITE)
        a.text('概率固定',640,427,29,WHITE)
        a.text('有限次数',895,427,29,WHITE)
        a.text('p < 1 时，有限次重复不会把概率变成 100%',640,528,25,MUTED,alpha=ease((t-1.8)/1))
    elif i in (8,9):domino(a,t,i==9)
    elif i==10:connector(a,t,True)
    elif i in (11,12):
        start=(225,389);end=(1075,389)
        paths=[bezier(start,(415,yy),(870,yy),end) for yy in (205,573)]
        for j,path in enumerate(paths):
            a.path(path,ease(t/1.5),GOLD if j==0 else TEAL,1.5,True)
            pt=path[int(((t*.18+j*.3)%1)*(len(path)-1))];a.glow(*pt,4,GOLD if j==0 else TEAL)
        node(a,*start,'入');node(a,*end,'出',TEAL)
        if i==11:
            a.text('主路  1%',640,235,28,GOLD)
            a.text('备用  1%',640,544,28,TEAL)
            a.text('1% × 1% = 0.01%',640,390,46,WHITE,latin=True,alpha=ease((t-1)/1))
            a.text('两路独立失效 · 任一路可维持运行',640,601,20,MUTED)
        else:
            a.rect((540,335,740,445),RED,width=1.5,r=5)
            a.text('同一电源',640,390,31,RED)
            a.line([(640,335),(640,253)],RED,2);a.line([(640,445),(640,525)],RED,2)
            if t>2:
                for path in paths:a.path(path,ease((t-2)/1.5),RED,2,True)
            a.text('共同故障源',640,589,29,RED,alpha=ease((t-2)/1))
    elif i==13:
        a.text('没有余量',208,305,27,MUTED,anchor='left')
        a.text('预留缓冲',208,463,27,TEAL,anchor='left')
        for y in (354,512):a.line([(210,y),(1070,y)],DIM,2)
        a.rect((210,335,880,373),shade(GOLD,.35),fill=True)
        a.rect((210,493,760,531),shade(GOLD,.35),fill=True)
        a.rect((760,493,1030,531),shade(TEAL,.22),fill=True)
        a.text('缓冲',895,512,21,TEAL)
        a.line([(1030,278),(1030,558)],RED,1)
        a.text('截止时间',1030,253,22,RED)
        delta=210*ease((t-1)/3)
        a.rect((880,335,880+delta,373),RED,fill=True)
        a.rect((760,493,760+delta,531),TEAL,fill=True)
        a.text('同样的延误，不同的结果',640,603,28,WHITE,alpha=ease((t-3)/1))
    elif i==14:
        circuit(a,t,True)
        for j,word in enumerate(['防错','备用','缓冲']):
            a.text(word,420+j*220,560,30,TEAL if j==1 else GOLD,alpha=ease((t-.3-j*.5)/1))
    elif i==15:
        for j in range(5):orbit(a,t+j*7,center=(640,365),r=160+j*61,flatten=.38,color=shade(GOLD,.13+j*.02))
        a.text('意外有它的概率',640,315,49,WHITE,alpha=ease(t/1.8))
        a.text('你有准备的余地',640,397,60,GOLD,alpha=ease((t-1.1)/1.8))
        a.text('墨 菲 定 律',640,531,22,MUTED,alpha=ease((t-3)/1))

def frame(time):
    i=min(len(SCENES)-1,int(time/8));t=time-i*8
    im=background().copy();a=Canvas(im)
    for x,y,r,phase in PARTICLES:
        xx=(x*W+math.sin(time*.08+phase*6)*16)%W
        yy=(y*H-time*(3+r*6))%H
        a.ellipse(xx,yy,.65+r*1.15,color=shade(GOLD,.18+.26*(.5+.5*math.sin(time*.4+phase*7))),fill=True)
    # A constant fine border maintains visual continuity across scene dissolves.
    a.line([(58,55),(95,55)],shade(GOLD,.6));a.line([(58,55),(58,80)],shade(GOLD,.6))
    a.line([(1222,665),(1185,665)],shade(GOLD,.6));a.line([(1222,665),(1222,640)],shade(GOLD,.6))
    title=SCENES[i][1]
    a.text(SCENES[i][0],83,84,17,MUTED,anchor='left',alpha=ease(t/.6))
    a.text(title,640,135,48 if i not in (0,3) else 61,GOLD,alpha=ease(t/.8))
    graphic(a,i,t)
    a.text(SCENES[i][2],640,655,25,WHITE,alpha=ease((t-.5)/.7))
    # A restrained continuous dolly keeps long diagram-reading beats alive.
    zoom=1+.025*t/8
    ox=(im.width-im.width/zoom)/2
    oy=(im.height-im.height/zoom)/2
    im=im.transform(im.size,Image.Transform.AFFINE,(1/zoom,0,ox,0,1/zoom,oy),Image.Resampling.BICUBIC)
    # Fade against the same textured background, avoiding accidental black frames.
    visibility=min(ease(t/.45),ease((8-t)/.45))
    if visibility<1:im=Image.blend(background(),im,visibility)
    return im

def synth_score(out,seconds):
    """Original 90-BPM chamber-electronic score: felt keys, pads, bass and ticks."""
    sr=48000;n=int(sr*seconds)
    mix=np.zeros((n,2),dtype=np.float32)
    rng=np.random.default_rng(73)
    def note(start,dur,midi,gain,pan=0,tone='piano'):
        k=round(start*sr);length=min(round(dur*sr),n-k)
        if length<=0 or k<0:return
        tt=np.arange(length,dtype=np.float32)/sr;f=440*2**((midi-69)/12)
        if tone=='pad':
            sig=(np.sin(2*np.pi*f*tt)+.35*np.sin(2*np.pi*f*1.002*tt)+.18*np.sin(2*np.pi*f*2*tt))
            env=np.minimum(1,tt/.8)*np.minimum(1,(dur-tt)/1.5)*.45
        elif tone=='bass':
            sig=np.sin(2*np.pi*f*tt)+.15*np.sin(2*np.pi*f*2*tt)
            env=(1-np.exp(-tt*30))*np.exp(-tt*1.3)
        elif tone=='tick':
            sig=rng.normal(0,1,length)*.18+np.sin(2*np.pi*f*tt)*.4
            env=np.exp(-tt*44)
        else:
            sig=np.sin(2*np.pi*f*tt)*np.exp(-tt*1.1)
            sig+=.3*np.sin(2*np.pi*f*2.003*tt)*np.exp(-tt*2.1)
            sig+=.12*np.sin(2*np.pi*f*3.99*tt)*np.exp(-tt*3.5)
            env=(1-np.exp(-tt*180))*np.minimum(1,(dur-tt)/.12)
        sig=(sig*env*gain).astype(np.float32)
        mix[k:k+length,0]+=sig*math.sqrt((1-pan)/2)
        mix[k:k+length,1]+=sig*math.sqrt((1+pan)/2)
    # D minor → B-flat → F → C; the ending resolves to D major.
    chords=[(50,57,62,65),(46,53,58,62),(41,48,57,60),(48,55,60,64)]
    beat=2/3
    for bar in range(math.ceil(seconds/(beat*4))):
        start=bar*beat*4;section=int(start/8)
        chord=chords[(bar//3)%4]
        if start>=120:chord=(50,57,62,66)
        dynamic=.7 if section in (0,2,7,15) else 1
        for m in chord:note(start,4.4,m,.05*dynamic,(m%3-1)*.4,'pad')
        note(start,2.4,chord[0]-12,.13*dynamic,0,'bass')
        for step in range(8):
            m=chord[[0,2,1,3,2,1,3,2][step]]+12
            note(start+step*beat/2,2.1,m,.065*dynamic,(-.35 if step%2 else .35))
        if 16<=start<120:
            for step in (0,2):note(start+step*beat,.2,37,.07,0,'tick')
        if 40<=start<112:
            for step in (1,3):note(start+step*beat,.12,90,.035,.15,'tick')
    melody=[74,77,81,79,77,74,72,69,70,74,77,76,72,69,67,69]
    for j,m in enumerate(melody*3):
        start=8+j*2.4
        if start>=seconds-7:break
        note(start,3.6,m,.075,.15)
    for s in (3.7,11,24,40,56,64,72,80,88,96,104,112):note(s,.25,42 if s<72 else 74,.07,0,'tick')
    # Sparse stereo echoes provide a room without obscuring transients.
    dry=mix.copy()
    for delay,gain in [(.19,.16),(.37,.13),(.61,.085),(.89,.045)]:
        d=round(delay*sr);mix[d:]+=dry[:-d,::-1]*gain
    fade=np.minimum(1,np.arange(n)/sr/2)*np.minimum(1,(n-np.arange(n))/sr/4)
    mix*=fade[:,None]
    mix*=.78/max(.01,float(np.max(np.abs(mix))))
    with wave.open(str(out),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes(np.int16(mix*32767).tobytes())

def srt_time(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def prepare(run):
    for name in ['release','work','qa','logs']:(run/name).mkdir(parents=True,exist_ok=True)
    data={'title':'意外的形状｜墨菲定律','duration':DURATION,'width':round(W*SCALE),'height':round(H*SCALE),'fps':FPS,'delivery_promise':{'promise_type':'reference_remake','description':'Procedural dark-gold mathematical animation with original instrumental music'},'scenes':[{'id':i,'start':8*i,'duration':8,'chapter':s[0],'title':s[1],'caption':s[2]} for i,s in enumerate(SCENES)]}
    (run/'storyboard.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    (run/'qa/visible_copy.txt').write_text('\n'.join('\n'.join(s) for s in SCENES))
    (run/'release/字幕.srt').write_text('\n\n'.join(f'{i+1}\n{srt_time(i*8+.5)} --> {srt_time((i+1)*8-.3)}\n{s[2]}' for i,s in enumerate(SCENES)),encoding='utf-8')
    (run/'release/发布文案.txt').write_text('《意外的形状》｜墨菲定律\n\n小概率有很多次机会，我们也可以有不止一种选择。\n\n#墨菲定律 #概率 #知识动画 #思维方式\n',encoding='utf-8')
    (run/'release/内容与来源.txt').write_text('意外的形状｜墨菲定律\n\n墨菲定律是经验格言，不是严格的概率定理。片中概率示例假定各次相互独立、出错概率固定为 1%。备用路径示例假定两路独立失效，且任何一路正常即可维持运行。\n\n历史起源存在多个版本；片中采用 NASA ASRS 介绍的一种说法。\nhttps://asrs.arc.nasa.gov/publications/callback/cb_381.html\n\n二项分布：NIST/SEMATECH e-Handbook\nhttps://itl.nist.gov/div898/handbook/eda/section3/eda366i.htm\n\n工程中的错误预防与恢复：NASA Human Performance and Error\nhttps://www.nasa.gov/reference/5-0-human-performance-and-error-vol-2/\n\n配乐：原创程序合成器乐。\n',encoding='utf-8')
    return data

def main():
    global SCALE,FPS
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('output/murphy_law_20261019'))
    parser.add_argument('--preview',action='store_true')
    parser.add_argument('--sample',action='store_true')
    parser.add_argument('--scale',type=float,default=1.5)
    parser.add_argument('--fps',type=int,default=30)
    args=parser.parse_args();SCALE=args.scale;FPS=args.fps
    if SCALE<=0 or FPS<=0:parser.error('Scale and FPS must be positive')
    if round(W*SCALE)%2 or round(H*SCALE)%2:parser.error('H.264 dimensions must be even')
    run=args.output.resolve();prepare(run)
    if args.preview:
        sheet=Image.new('RGB',(1280,4*204),(9,11,14))
        for i in range(16):
            im=frame(i*8+5.5);im.save(run/'qa'/f'scene_{i:02}.jpg',quality=93)
            sheet.paste(im.resize((320,180),Image.Resampling.LANCZOS),((i%4)*320,(i//4)*204))
            ImageDraw.Draw(sheet).text(((i%4)*320+8,(i//4)*204+182),f'{i*8:03d}s / {i+1:02d}',fill='white')
        sheet.save(run/'qa/contact_sheet.jpg',quality=95)
        cover=background().copy();a=Canvas(cover)
        for j in range(5):orbit(a,j*7,center=(640,350),r=170+j*65,flatten=.48,color=shade(GOLD,.15+j*.035))
        a.text('意外的形状',640,295,88,GOLD)
        a.text('墨 菲 定 律',640,406,35,WHITE)
        a.text('THE SHAPE OF THE UNEXPECTED',640,471,18,MUTED,latin=True)
        a.text('让每一次意外，都还有另一种选择。',640,622,26,WHITE)
        cover.save(run/'release/封面.jpg',quality=96)
        print(run/'qa/contact_sheet.jpg');return
    seconds=16 if args.sample else DURATION
    audio=run/'work/original_score.wav';synth_score(audio,seconds)
    dest=run/('work/sample.mp4' if args.sample else 'release/意外的形状_墨菲定律.mp4')
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{round(W*SCALE)}x{round(H*SCALE)}','-r',str(FPS),'-i','-','-i',str(audio),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-af','loudnorm=I=-18:TP=-1.5:LRA=10','-t',str(seconds),'-movflags','+faststart',str(dest)]
    with (run/'logs/render.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for k in range(round(seconds*FPS)):
                proc.stdin.write(frame(k/FPS).tobytes())
                if k%(FPS*8)==0:print(f'{k/FPS:.0f}/{seconds}s rendered',flush=True)
        finally:proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError('FFmpeg failed; see logs/render.log')
    if not args.sample:
        shutil.copy2(__file__,run/'release/动画源码.py')
        (run/'release/requirements.txt').write_text('numpy>=1.24\nPillow>=10.0\n')
        (run/'release/重新渲染.txt').write_text('安装 Python 3.10+ 与 FFmpeg。\npython3 -m pip install -r requirements.txt\npython3 动画源码.py --output output/murphy_law\n\n--preview：导出分镜缩略图；--sample：导出前 16 秒。\n默认 1920×1080 / 30fps / 128 秒。\n非 macOS 系统需设置 MURPHY_SERIF_FONT 为支持中文的宋体字体文件，MURPHY_LATIN_FONT 为拉丁衬线字体文件。\n',encoding='utf-8')
        with zipfile.ZipFile(run/'release/重渲染工程.zip','w',zipfile.ZIP_DEFLATED) as z:
            for name in ['动画源码.py','requirements.txt','重新渲染.txt']:z.write(run/'release'/name,name)
        artifacts=[('final_video',dest),('code_rendered_video',dest),('cover_image',run/'release/封面.jpg'),('subtitles',run/'release/字幕.srt'),('publishing_copy',run/'release/发布文案.txt'),('source_code',run/'release/动画源码.py'),('render_project',run/'release/重渲染工程.zip'),('reference_analysis',run/'work/reference_analysis.json'),('decision_log',run/'work/decision_log.json')]
        manifest={'workflow':'procedural_math_film','delivery_promise':{'promise_type':'reference_remake','description':'Code-rendered dark-gold mathematical explainer; original score'},'artifacts':[{'category':c,'path':str(p)} for c,p in artifacts]}
        (run/'artifact_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(dest,flush=True)

if __name__=='__main__':main()
