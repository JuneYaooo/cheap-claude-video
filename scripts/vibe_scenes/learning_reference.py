"""Full-bleed navy line-diagram grammar observed in a learning-film reference.

Original vector scenes and episode-supplied wording; no reference video pixels,
audio, retention percentages or author identity are embedded in this module.
"""
from functools import lru_cache
import math
import numpy as np
from PIL import Image

WHITE='#e8e5db'
MUTED='#8c929d'
DIM='#303a4c'
YELLOW='#e8b949'
BLUE='#405d80'


def ease(t):
    t=max(0,min(1,t));return t*t*(3-2*t)


@lru_cache(3)
def navy(width):
    height=round(width*9/16)
    yy,xx=np.mgrid[:height,:width];u=xx/width;v=yy/height
    center=np.exp(-((u-.5)**2/.10+(v-.48)**2/.30))
    ring=np.exp(-((np.sqrt(((u-.5)/.64)**2+((v-.5)/.92)**2)-.47)/.13)**2)
    noise=np.random.default_rng(17).normal(0,.18,(height,width))
    arr=np.stack([5+9*center+2*ring+noise,8+16*center+3*ring+noise,15+27*center+6*ring+noise],axis=-1)
    return Image.fromarray(np.uint8(np.clip(arr,0,255)))


def stage(f):
    f.im.paste(navy(f.im.width),(0,0))


def text(f,value,x,y,size=40,color=WHITE,align='center',alpha=1,width=1100):
    f.text(value,x,y,size,color,anchor=align,alpha=alpha,max_width=width)


def poly(f,pts,color,outline=None,width=1.5):
    sc=f.im.width/1280
    f.a.d.polygon([(round(x*sc),round(y*sc)) for x,y in pts],fill=color)
    if outline:f.line(pts+pts[:1],outline,width)


def copy_right(f,d,t,x=770,y=300):
    lines=d.get('lines',[])
    for i,line in enumerate(lines):
        text(f,line,x,y+i*72,52 if i==len(lines)-1 else 31,
             YELLOW if i==d.get('accent_line',-1) else WHITE,
             'left',ease((t-i*.55)/.5),width=430)
    if d.get('note'):text(f,d['note'],x,y+len(lines)*72+27,22,MUTED,'left',width=440)


def stick(f,x,y,scale=1,pose='read',t=0):
    a=f.a
    def pt(dx,dy):return x+dx*scale,y+dy*scale
    a.ellipse(x,y,19*scale,color=WHITE,width=2*scale)
    f.line([pt(0,19),pt(0,85)],WHITE,3*scale)
    f.line([pt(0,85),pt(-28,131)],WHITE,3*scale)
    f.line([pt(0,85),pt(33,131)],WHITE,3*scale)
    if pose=='write':
        dy=math.sin(t*4)*3
        f.line([pt(0,42),pt(31,66),pt(70,61+dy)],WHITE,2.5*scale)
        f.line([pt(65,70+dy),pt(79,45+dy)],YELLOW,3*scale)
        f.line([pt(0,42),pt(-23,72),pt(35,78)],WHITE,2.5*scale)
    elif pose=='think':
        f.line([pt(0,42),pt(29,55),pt(16,14)],WHITE,2.5*scale)
        f.line([pt(0,42),pt(-24,67),pt(12,75)],WHITE,2.5*scale)
    else:
        f.line([pt(0,42),pt(27,65),pt(48,48)],WHITE,2.5*scale)
        f.line([pt(0,42),pt(-23,66),pt(35,73)],WHITE,2.5*scale)


def small_book(f,x,y,w=54,h=65,opened=False,color=YELLOW):
    if opened:
        poly(f,[(x-w,y),(x,y+8),(x+w,y),(x+w,y+h),(x,y+h+8),(x-w,y+h)],'#151d2d',color,1.5)
        f.line([(x,y+9),(x,y+h+8)],color,1)
    else:
        f.a.rect((x,y,x+w,y+h),color,fill=True,r=1)
        f.line([(x+8,y+3),(x+8,y+h-3)],'#7d693c',1)
        f.line([(x+17,y+13),(x+w-9,y+13)],'#1c2230',2)
        f.line([(x+17,y+23),(x+w-9,y+23)],'#1c2230',2)


def lr_title(f,s,t):
    stage(f);d=s['data']
    text(f,d['title'],640,340,94,WHITE,alpha=ease(t/.6))
    if t>d.get('sub_at',1.8):text(f,d.get('subtitle',''),640,445,32,YELLOW,alpha=ease((t-d.get('sub_at',1.8))/.5))


def lr_clock(f,s,t):
    stage(f);d=s['data'];a=f.a;x,y=330,320;r=126
    a.ellipse(x,y,r,color=MUTED,width=1.4)
    for i in range(60):
        ang=i*math.pi/30
        rr=r-15 if i%5==0 else r-6
        f.line([(x+rr*math.sin(ang),y-rr*math.cos(ang)),(x+r*math.sin(ang),y-r*math.cos(ang))],MUTED if i%5==0 else DIM,1)
    theta=-.6+t*.48
    f.line([(x,y),(x+92*math.sin(theta),y-92*math.cos(theta))],YELLOW,3)
    f.line([(x,y),(x-54,y-73)],WHITE,2)
    a.ellipse(x,y,4,color=YELLOW,fill=True)
    text(f,d.get('clock_label',''),330,490,24,MUTED)
    a.rect((254,550,287,582),MUTED,width=1.5,r=3)
    a.ellipse(294,562,8,10,color=MUTED,width=1)
    copy_right(f,d,t,650,270)


def lr_bucket(f,s,t):
    stage(f);d=s['data'];a=f.a;cx=330;top=235;bottom=565
    repaired=d.get('repaired',False)
    level=.30 if not repaired else .32+.48*ease(t/(s['duration']-1))
    yy=bottom-(bottom-top)*level
    left=226+(yy-top)/(bottom-top)*42;right=434-(yy-top)/(bottom-top)*42
    poly(f,[(left,yy),(right,yy),(392,bottom),(268,bottom)],'#a88b37' if repaired else BLUE)
    a.ellipse(cx,top,104,17,color=MUTED,width=1.6)
    f.line([(226,top),(268,bottom),(392,bottom),(434,top)],MUTED,1.6)
    a.ellipse(cx,bottom,62,10,color=MUTED,width=1)
    f.line([(cx,120),(cx,yy)],YELLOW if repaired else BLUE,4)
    wave=[(left+i*(right-left)/35,yy+2*math.sin(i*.6+t*3)) for i in range(36)]
    f.line(wave,YELLOW if repaired else '#8ca1bc',1.4)
    for j in range(4):
        hole_y=330+j*63;hole_x=226+(hole_y-top)/(bottom-top)*42
        a.ellipse(hole_x,hole_y,3,color=YELLOW if repaired else '#b16b62',fill=True)
        if not repaired:
            q=(t*.65+j*.21)%1
            f.line([(hole_x-5-q*26,hole_y+q*q*50),(hole_x-7-q*26,hole_y+q*q*50+4)],BLUE,1.7)
    copy_right(f,d,t,640,270)


def lr_chapter(f,s,t):
    stage(f);d=s['data']
    text(f,d['number'],640,342,94,'#1c283b',alpha=ease(t/.5))
    text(f,d.get('label',''),640,285,22,YELLOW)
    text(f,d['title'],640,365,64,WHITE,alpha=ease(t/.7))
    q=ease((t-.7)/.7)
    f.line([(510,419),(510+260*q,419)],YELLOW,2)


def lr_notes(f,s,t):
    stage(f);d=s['data'];a=f.a
    a.rect((165,180,475,560),'#151e2b',fill=True,r=7)
    a.rect((165,180,475,560),DIM,width=1.5,r=7)
    for i in range(10):
        yy=215+i*32
        f.line([(192,yy),(441-(i%3)*30,yy)],'#293245',2)
    for i in (0,4,7):
        q=ease((t-i*.35)/.7)
        f.line([(193,215+i*32),(193+200*q,215+i*32)],YELLOW if i>0 else WHITE,8)
    if t>3:
        text(f,d.get('tag',''),320,606,22,MUTED,alpha=ease((t-3)/.6))
    copy_right(f,d,t,600,265)


def lr_film(f,s,t):
    stage(f);d=s['data'];a=f.a
    for i in range(9):
        x=-130+i*190-(t*24)%190
        a.rect((x,151,x+175,258),DIM,width=1,r=3)
        for j in range(6):
            a.rect((x+9+j*27,157,x+20+j*27,163),DIM,fill=True)
            a.rect((x+9+j*27,246,x+20+j*27,252),DIM,fill=True)
        a.ellipse(x+131,185,8,color=YELLOW,fill=True)
        f.line([(x+17,232),(x+61,190),(x+94,222),(x+121,208),(x+161,236)],DIM,2)
    text(f,d.get('label',''),640,327,23,YELLOW)
    for i,line in enumerate(d['lines']):text(f,line,640,390+i*65,40 if i<2 else 27,WHITE if i<2 else MUTED,alpha=ease((t-.5*i)/.6))


def lr_case(f,s,t):
    stage(f);d=s['data'];a=f.a;open_phase=t>d.get('open_at',3)
    x=320;y=421
    a.rect((160,362,480,533),WHITE,width=1.5,r=11)
    f.line([(266,360),(275,333),(363,333),(373,360)],WHITE,2)
    for xx in (234,402):f.line([(xx,364),(xx,530)],'#977d39',2)
    for i in range(6):
        xx=182+i*46
        yy=402+(i%2)*13-160*ease((t-d.get('open_at',3))/1.2) if open_phase else 322+(i%2)*13+80*ease(t/2)
        small_book(f,xx,yy,29,68,False,YELLOW if i%2 else '#89919d')
    a.rect((160,360,480,401),'#172238',fill=True,r=10)
    a.rect((160,360,480,401),WHITE,width=1.6,r=10)
    for i in range(3):
        xx=220+i*100
        if not open_phase:
            q=(t*.4+i*.2)%1;a.arrow((xx,245+q*40),(xx,290+q*40),MUTED,1)
        else:
            q=ease((t-d.get('open_at',3)-.4*i)/.8)
            if q>0:a.arrow((xx,342),(xx,342-90*q),YELLOW,1.8)
    copy_right(f,d,t,625,275)


def lr_pool(f,s,t):
    stage(f);d=s['data'];a=f.a
    f.line([(125,470),(300,470),(300,590),(570,590),(570,470),(650,470)],MUTED,1.2)
    poly(f,[(301,493),(569,493),(569,589),(301,589)],BLUE)
    for j in range(2):f.line([(301+i*9,493+j*5+math.sin(i*.7+t*2)*1.8) for i in range(30)],'#758ba8',1)
    if t<d.get('jump_at',4):
        stick(f,242,331,.9,'read',t)
        small_book(f,279,371,42,48)
    else:
        q=ease((t-d.get('jump_at',4))/1.7);x=245+188*q;y=332+147*q-80*math.sin(q*math.pi)
        a.ellipse(x,y,16,color=WHITE,width=2)
        f.line([(x-15,y+7),(x-72,y+27),(x-117,y+15)],WHITE,3)
        f.line([(x-72,y+27),(x-115,y+42)],WHITE,2)
        f.line([(x-30,y+14),(x-58,y-7)],WHITE,2)
        small_book(f,185,434,35,38)
    copy_right(f,d,t,700,260)


def lr_recall(f,s,t):
    stage(f);d=s['data'];hidden=d['hide_at']<=t<d['reveal_at']
    text(f,d.get('title',''),640,160,43,WHITE)
    for i,word in enumerate(d['items']):
        x=330+(i%3)*310;y=295+(i//3)*115
        text(f,'?' if hidden else word,x,y,45,MUTED if hidden else WHITE)
        f.line([(x-80,y+40),(x+80,y+40)],DIM,1)
    if hidden:
        remaining=math.ceil(d['reveal_at']-t)
        text(f,str(remaining),640,560,64,YELLOW)
    else:text(f,d['phase_labels'][1 if t>=d['reveal_at'] else 0],640,560,29,YELLOW)
    text(f,d.get('note',''),640,641,18,MUTED)


def lr_pyramid(f,s,t):
    stage(f);d=s['data'];a=f.a
    for i,label in enumerate(d['levels']):
        y1=253+i*63;y2=y1+63
        half1=46+i*49;half2=half1+49;active=i<2 and t>1
        poly(f,[(340-half1,y1),(340+half1,y1),(340+half2,y2),(340-half2,y2)],'#80682e' if active else '#222b39',YELLOW if active else DIM,1)
        text(f,label,340,y1+32,24,WHITE)
    copy_right(f,d,t,685,280)
    text(f,d.get('diagram_note',''),640,651,18,MUTED)


def lr_practice(f,s,t):
    stage(f);d=s['data'];a=f.a
    for i in range(3):
        x=145+i*135;q=ease((t-i*.65)/.5)
        a.rect((x,215,x+110,350),'#433b24',fill=True,r=7)
        a.rect((x,215,x+110,350),YELLOW,width=1.3,r=7)
        if q>0:f.line([(x+25,282),(x+47,305),(x+84,257)],YELLOW,4)
    for i,label in enumerate(d.get('steps',[])):
        yy=427+i*58
        text(f,label,160,yy,24,MUTED,'left',width=380)
        f.line([(160,yy+25),(160+355*ease((t-1-i*.7)/1.1),yy+25)],YELLOW if i==2 else DIM,5)
    copy_right(f,d,t,650,270)


def lr_delay(f,s,t):
    stage(f);d=s['data'];a=f.a
    for i,(x,label) in enumerate(zip((250,505),d['delays'])):
        a.rect((x-86,280,x+86,447),'#192536',fill=True,r=4)
        a.rect((x-86,280,x+86,447),MUTED,width=1.2,r=4)
        f.line([(x-86,319),(x+86,319)],YELLOW,3)
        for dx in (-45,45):f.line([(x+dx,265),(x+dx,292)],YELLOW,2)
        text(f,label,x,377,35,WHITE,alpha=ease((t-i*.8)/.6))
    a.arrow((345,369),(405,369),MUTED,1)
    copy_right(f,d,t,705,255)
    text(f,d.get('source_label',''),640,645,18,MUTED)


def lr_cards(f,s,t):
    stage(f);d=s['data'];a=f.a
    for i,(title,lines) in enumerate(zip(d['titles'],d['lines'])):
        x=290+i*350;q=ease((t-i*2)/.7)
        if q<=0:continue
        a.rect((x-151,205,x+151,590),'#121b29',fill=True,r=8)
        a.rect((x-151,205,x+151,590),DIM,width=1,r=8)
        text(f,title,x,258,30,YELLOW,alpha=q,width=275)
        f.line([(x-110,295),(x+110,295)],DIM,1)
        for j,line in enumerate(lines):text(f,line,x,354+j*54,25,WHITE,alpha=q,width=260)
        if t>i*2+1:
            a.ellipse(x,527,24,color=YELLOW,width=1.3)
            f.line([(x-10,527),(x-2,536),(x+13,516)],YELLOW,2)
    text(f,d.get('note',''),640,651,20,MUTED)


DRAWERS={name:fn for name,fn in list(globals().items()) if name.startswith('lr_') and callable(fn)}


def validate_scene(s):
    d=s.get('data',{});kind=s['kind']
    if not s.get('full_bleed'):raise ValueError('reference learning scenes require full_bleed')
    if kind=='lr_recall':
        if len(d.get('items',[]))!=6 or any(not isinstance(x,str) or len(x)>6 for x in d['items']):raise ValueError('recall requires six short words')
        if not 0<d.get('hide_at',0)<d.get('reveal_at',0)<s['duration']:raise ValueError('invalid recall phases')
    if kind=='lr_pyramid' and len(d.get('levels',[]))!=4:raise ValueError('four action levels required')
    if kind=='lr_delay' and len(d.get('delays',[]))!=2:raise ValueError('two delayed test labels required')
    if kind=='lr_cards' and (len(d.get('titles',[]))!=3 or len(d.get('lines',[]))!=3):raise ValueError('three action cards required')
