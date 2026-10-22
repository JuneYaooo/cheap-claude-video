"""Blue/gold stage, paper archive and chalkboard probability film components.

All image assets are locally drawn. Simulation outcomes are seeded actual draws;
no source-video frames, source music or source identity is embedded.
"""
import math
import random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

GOLD='#e4c57f'; WHITE='#f1ead9'; BLUE='#b9cee8'; RED='#db8d72'; MUTED='#9ca8b3'

def clamp(x): return max(0,min(1,x))
def ease(x): x=clamp(x);return x*x*(3-2*x)
def poly(f,points,color):
    q=f.im.width/1280
    f.a.d.polygon([(round(x*q),round(y*q)) for x,y in points],fill=color)

@lru_cache(12)
def backdrop(width,theme):
    h=round(width*9/16);yy,xx=np.mgrid[:h,:width];u=xx/width;v=yy/h
    center=np.exp(-((u-.5)**2/.25+(v-.43)**2/.3))
    colors={'blue':(5,10,25,7,13,28),'paper':(12,9,5,30,22,10),'chalk':(8,22,18,17,24,16),'rose':(17,10,16,15,9,8)}
    r,g,b,rr,gg,bb=colors[theme];grain=np.random.default_rng(29).normal(0,.45,(h,width))
    return Image.fromarray(np.clip(np.stack([r+rr*center+grain,g+gg*center+grain,b+bb*center+grain],axis=-1),0,255).astype('uint8'))

def base(f,theme='blue'):
    f.im.paste(backdrop(f.im.width,theme))

def title(f,s,y=73):
    f.text(s.get('eyebrow',''),640,y-30,16,MUTED)
    f.text(s['heading'],640,y+14,34,WHITE)

def goat(f,x,y,z=1):
    a=f.a;a.ellipse(x,y+13*z,22*z,15*z,WHITE,True);a.ellipse(x,y-13*z,12*z,14*z,WHITE,True)
    a.ellipse(x-18*z,y-15*z,9*z,4*z,WHITE,True);a.ellipse(x+18*z,y-15*z,9*z,4*z,WHITE,True)
    for sign in (-1,1):
        a.line([(x+sign*6*z,y-25*z),(x+sign*10*z,y-34*z),(x+sign*16*z,y-36*z)],GOLD,2)
        a.line([(x+sign*13*z,y+22*z),(x+sign*13*z,y+35*z)],WHITE,3)
        a.ellipse(x+sign*4*z,y-15*z,1.8*z,color='#1c2533',fill=True)

def car(f,x,y,z=1):
    a=f.a;a.rect((x-45*z,y-8*z,x+45*z,y+13*z),GOLD,fill=True,r=8*z)
    poly(f,[(x-22*z,y-8*z),(x-9*z,y-23*z),(x+15*z,y-23*z),(x+32*z,y-8*z)],'#d9c08a')
    for dx in (-29,29):
        a.ellipse(x+dx*z,y+14*z,9*z,color='#101421',fill=True);a.ellipse(x+dx*z,y+14*z,4*z,color=WHITE,fill=True)

@lru_cache(64)
def door_tile(w,h,scale,opened):
    W,H=round(w*scale),round(h*scale);r=W/2
    yy,xx=np.mgrid[:H,:W];u=xx/max(1,W-1);v=yy/max(1,H-1)
    border=Image.new('L',(W,H));m=ImageDraw.Draw(border)
    m.ellipse((0,0,W-1,W-1),fill=255);m.rectangle((0,r,W-1,H-1),fill=255)
    inside=Image.new('L',(W,H));n=ImageDraw.Draw(inside);b=max(1,round(4*scale))
    n.ellipse((b,b,W-b-1,W-b-1),fill=255);n.rectangle((b,r,W-b-1,H-b-1),fill=255)
    shimmer=.56+.44*np.sin(u*np.pi)**2
    gold=np.stack([224*shimmer,192*shimmer,119*shimmer],axis=-1)
    glow=np.exp(-((u-.5)**2/.095+(v-.48)**2/.5))
    if opened: content=np.stack([58+171*glow,47+147*glow,30+88*glow],axis=-1)
    else: content=np.stack([8+8*glow,16+16*glow,35+29*glow],axis=-1)
    data=np.where(np.asarray(inside)[:,:,None]>0,content,gold)
    rgba=np.concatenate([np.uint8(data),np.asarray(border)[:,:,None]],axis=-1)
    return Image.fromarray(rgba,'RGBA')

def arch(f,x,y,w,h,number='',opened=0,content=None,chosen=False):
    a=f.a;r=w/2;col=GOLD
    scale=f.im.width/1280
    tile=door_tile(w,h,scale,opened>0)
    f.im.paste(tile,(round((x-r)*scale),round(y*scale)),tile)
    if opened>0:
        if content=='goat':goat(f,x,y+h*.77,w/125)
        if content=='car':car(f,x,y+h*.78,w/130)
        # Thin oblique leaf remains visible at the hinge.
        ww=w*(1-opened)
        poly(f,[(x-r,y+r),(x-r-25*opened,y+r-15*opened),(x-r-25*opened,y+h+10*opened),(x-r+ww,y+h)],'#0a1330')
        a.line([(x-r,y+r),(x-r-25*opened,y+r-15*opened),(x-r-25*opened,y+h+10*opened)],GOLD,1)
    else:
        if number:f.text(str(number),x,y+h*.33,min(46,w*.3),GOLD,latin=True,max_width=w*.8)
        if w>90:
            a.rect((x-r+20,y+h*.5,x+r-20,y+h-23),'#253354',width=1)
            a.ellipse(x+r-22,y+h*.58,3,color=GOLD,fill=True)
    if chosen:
        a.ellipse(x,y-28,17,color=GOLD,fill=True);f.text('你',x,y-28,18,'#101c42')
        poly(f,[(x-8,y-15),(x+8,y-15),(x,y-3)],GOLD)

def host(f,x,y,z=1):
    a=f.a;a.ellipse(x,y,15*z,22*z,'#050a12',True)
    poly(f,[(x-18*z,y+25*z),(x+18*z,y+25*z),(x+26*z,y+118*z),(x-25*z,y+118*z)],'#060b14')
    poly(f,[(x-9*z,y+24*z),(x+9*z,y+24*z),(x,y+52*z)],WHITE)
    a.line([(x-16*z,y+40*z),(x-80*z,y+22*z)],'#070d17',11*z);a.ellipse(x-82*z,y+22*z,5*z,color=WHITE,fill=True)
    for dx in (-12,12):a.line([(x+dx*z,y+110*z),(x+dx*z,y+190*z)],'#050a12',12*z)

def stage(f,s,t,reveal=False):
    base(f);a=f.a
    for i in range(7):
        x=170+i*155;poly(f,[(640+(i-3)*60,0),(x-30,540),(x+50,540)],'#16213b')
    a.line([(90,555),(1190,555)],'#444454',2)
    for i in range(44):
        theta=math.pi+i*math.pi/43;x=640+560*math.cos(theta);y=562+430*math.sin(theta)
        a.ellipse(x,y,2.5,color=GOLD,fill=True)
    xs=(360,640,920)
    for i,x in enumerate(xs):
        opened=ease((t-2)/1.1) if i==2 else ease((t-4)/1.4) if reveal and i==1 else 0
        arch(f,x,240,190,310,i+1,opened,'goat' if i==2 else 'car',i==(1 if reveal and t>3 else 0))
        for j in range(5):a.line([(x-70,568+j*7),(x+70,568+j*7)],'#162039',3)
    host(f,1125,337,1.05)
    if not reveal:
        f.text(s['heading'],640,80,49,WHITE)
        if t>3:
            for x,label,col in [(450,'坚持原门',BLUE),(810,'换另一门',GOLD)]:
                a.rect((x-120,134,x+120,185),col,fill=True,r=25);f.text(label,x,160,26,'#101421')
            f.text(str(max(0,math.ceil(9-t))),640,161,33,GOLD,latin=True)
    else:
        f.text(s['heading'],640,96,46,GOLD)
        if t>6:
            for i in range(85):
                x=(i*137.6)%1220+30;y=(i*79.1+(t-6)*55)%590
                a.rect((x,y,x+3+(i%3),y+5),[GOLD,BLUE,RED][i%3],fill=True)

def paper(f,s,t):
    base(f,'paper');a=f.a
    a.rect((340,100,940,590),'#ddd1ad',fill=True,r=2)
    f.text(s['data'].get('masthead','概率档案'),640,153,45,'#2b251d')
    f.text(s['data'].get('byline','一个关于选择的问题'),640,204,19,'#62563e')
    a.line([(380,231),(900,231)],'#7c715d',1)
    for j in range(3):
        arch(f,470+j*170,275,95,154,str(j+1),1 if j==2 else 0,'goat')
    for j in range(6):
        y=465+j*14;a.line([(380,y),(580+(j%2)*45,y)],'#a79d82',3);a.line([(650,y),(895-(j%3)*20,y)],'#a79d82',3)
    f.text(s['heading'],640,60,31,WHITE)

def typewriter(f,s,t):
    base(f,'paper');a=f.a
    a.rect((240,130,1040,439),'#e2d6b6',fill=True)
    lines=s['data']['lines']
    for i,line in enumerate(lines):
        visible=max(0,int((t-i*2.7)*14))
        f.text(line[:visible],295,205+i*85,35,'#302b21',anchor='left',max_width=700)
    a.rect((160,455,1120,600),'#28241e',fill=True,r=22)
    for row,keys in enumerate(['QWERTYUIOP','ASDFGHJKL','ZXCVBNM']):
        for j,key in enumerate(keys):
            x=320+j*67+(row*25);y=478+row*43;a.ellipse(x,y,18,color='#958d78',width=1.5);f.text(key,x,y,18,WHITE,latin=True)
    f.text(s['heading'],640,72,35,GOLD)

def letters(f,s,t):
    base(f,'paper');a=f.a
    # Representative visual letters, not a false historic count.
    rng=random.Random(61)
    for i in range(130):
        x=rng.uniform(80,1200);y=rng.uniform(430,585)
        y-= max(0,1-t/3)*rng.uniform(120,440)
        angle=rng.uniform(-.5,.5);w=rng.uniform(50,85);h=w*.55
        def point(dx,dy):return (x+dx*math.cos(angle)-dy*math.sin(angle),y+dx*math.sin(angle)+dy*math.cos(angle))
        pts=[point(-w/2,-h/2),point(w/2,-h/2),point(w/2,h/2),point(-w/2,h/2)]
        poly(f,pts,['#cbbf9e','#e2d6b4','#b9b39c'][i%3]);a.line([pts[0],point(0,3),pts[1]],'#938773',1)
    for j,line in enumerate(s['data']['questions']):
        x=365+j*550;y=230+math.sin(t*.4+j)*5
        a.rect((x-215,y-63,x+215,y+90),'#e4d8b7',fill=True)
        for h in range(4):a.line([(x-195,y-20+h*26),(x+195,y-20+h*26)],'#c1b697',1)
        f.text(line,x,y,29,'#37465a',max_width=390)
        f.text('一个直觉上的追问',x,y+54,18,'#746651')
    title(f,s)

def balance(f,s,t):
    base(f,'paper');a=f.a;title(f,s)
    a.line([(640,225),(640,535)],GOLD,7);poly(f,[(590,560),(690,560),(668,535),(612,535)],GOLD)
    angle=math.sin(t*1.4)*.018*(1-ease(t/5))
    left=(365,296+angle*240);right=(915,296-angle*240)
    a.line([left,right],GOLD,6);a.ellipse(640,296,10,color=GOLD,fill=True)
    for i,(x,y) in enumerate([left,right]):
        a.line([(x,y),(x-80,y+132),(x+80,y+132),(x,y)],GOLD,1.2)
        arch(f,x,y+15,76,112,str(i+1));f.text('50%',x,491,58,BLUE,latin=True)
    if t>4:f.text('两个结果 ≠ 两个结果等概率',640,580,35,RED)

def chalk(f,s,t):
    base(f,'chalk');a=f.a;title(f,s)
    host(f,258,280,1.4)
    # Glasses, chalk annotations and an old CRT are scene objects, not a dashboard.
    a.rect((235,275,255,290),WHITE,width=2,r=3);a.rect((260,275,280,290),WHITE,width=2,r=3);a.line([(255,282),(260,282)],WHITE,2)
    f.text('直觉',250,207,24,WHITE)
    a.rect((663,200,1080,475),'#b9b28c',fill=True,r=22);a.rect((690,227,1052,445),'#07170f',fill=True,r=10)
    a.rect((640,498,1100,563),'#b9b28c',fill=True,r=9)
    for i,line in enumerate(s['data']['lines']):
        f.text(line,716,268+i*50,21,'#a6d1aa',anchor='left',alpha=ease((t-i*1.3)/.6),max_width=310)
    a.arrow((410,385),(595,385),WHITE,2)
    f.text('交给可重复的试验',480,450,24,WHITE,max_width=290)

@lru_cache(16)
def outcomes(seed,n):
    rng=random.Random(seed);rows=[]
    for _ in range(n):
        prize=rng.randrange(3);choice=rng.randrange(3)
        options=[j for j in range(3) if j not in (prize,choice)]
        host=rng.choice(options);switch=next(j for j in range(3) if j not in (choice,host))
        rows.append((prize,choice,host,switch,int(prize==choice)))
    return tuple(rows)

def simulation(f,s,t):
    base(f);a=f.a;d=s['data'];n=d.get('trials',1000);rows=outcomes(d.get('seed',73),n)
    progress=clamp(t/(s['duration']-4))
    upto=n if progress>=1 else min(n,max(1,int(math.exp(progress*math.log(n)))))
    stay=sum(r[4] for r in rows[:upto]);switch=upto-stay
    f.text(f'第 {upto:,} 局',640,87,41,GOLD)
    f.text(f'本片程序模拟 · seed {d.get("seed",73)} · 每局重新随机放置',640,39,17,MUTED)
    last=rows[upto-1]
    for center,label,wins,col,chosen in [(240,'始终坚持',stay,BLUE,last[1]),(1040,'始终换门',switch,GOLD,last[3])]:
        a.rect((center-100,170,center+100,209),col,fill=True,r=19);f.text(label,center,190,24,'#07101c')
        for j in range(3):arch(f,center+(j-1)*82,260,65,120,str(j+1),1,'car' if last[0]==j else 'goat',j==chosen)
        f.text(f'{wins}',center,450,65,col,latin=True);f.text(f'{wins/upto:.1%}',center,511,31,col,latin=True)
    for i in range(n):
        x=441+i%40*10;y=170+i//40*10
        a.rect((x,y,x+7,y+7),GOLD if i<upto and not rows[i][4] else BLUE if i<upto else '#172139',fill=True)
    a.line([(440,570),(840,570)],MUTED,1)
    for val in (1/3,2/3):
        y=565-val*130;a.line([(440,y),(840,y)],'#2e3850',1);f.text('1/3' if val<.5 else '2/3',858,y,15,MUTED,anchor='left',latin=True)
    cum=0;pts_stay=[];pts_switch=[]
    for i,row in enumerate(rows[:upto]):
        cum+=row[4];x=440+400*math.log(i+1)/math.log(n)
        pts_stay.append((x,565-130*cum/(i+1)));pts_switch.append((x,565-130*(1-cum/(i+1))))
    if len(pts_stay)>1:a.line(pts_stay,BLUE,2);a.line(pts_switch,GOLD,2)
    f.text('1',440,592,14,MUTED,latin=True);f.text(str(n),840,592,14,MUTED,latin=True)

def hundred(f,s,t):
    base(f);a=f.a;remaining=s['data'].get('remaining',73)
    opened=min(98,int(ease((t-3)/(s['duration']-7))*98))
    candidates=[i for i in range(100) if i not in (0,remaining)]
    opened_set=set(candidates[:opened])
    f.text(f'主持人已排除 {opened} 扇空门',640,70,34,WHITE)
    if opened==98:f.text('初选：1%    换门：99%',640,120,28,GOLD)
    for i in range(100):
        x=100+i%20*57;y=160+i//20*83
        arch(f,x,y,39,66,str(i+1),1 if i in opened_set else 0,'goat',i==0)
    f.text('初选失误的 99%，集中在唯一未被排除的另一扇门' if opened==98 else '逐扇排除空门，初选门保持不动',640,599,25,GOLD)

def grouping(f,s,t):
    base(f);title(f,s);a=f.a
    for j,x in enumerate((360,640,920)):
        arch(f,x,245,160,260,str(j+1),ease((t-3)/1.2) if j==2 else 0,'goat',j==0)
    a.line([(555,204),(555,184),(1005,184),(1005,204)],GOLD,2)
    f.text('最初没选中的整组：2/3',780,150,29,GOLD)
    f.text('1/3',360,560,45,BLUE,latin=True)
    if t>5:f.text('2/3',640,560,45,GOLD,latin=True)

def conditions(f,s,t):
    base(f,'chalk');title(f,s);a=f.a
    for j,(heading,lines,col) in enumerate(s['data']['panels']):
        x=335+j*610;a.rect((x-255,213,x+255,574),'#1b302b',fill=True,r=10)
        f.text(heading,x,260,31,col)
        for i,line in enumerate(lines):f.text(line,x,344+i*77,27,WHITE,alpha=ease((t-i*.7)/.7),max_width=450)

def finale(f,s,t):
    base(f);a=f.a
    f.text('THE MONTY HALL PROBLEM',640,130,19,MUTED,latin=True)
    f.text(s['heading'],640,240,82,GOLD)
    for i,x in enumerate((550,640,730)):arch(f,x,330,58,100,str(i+1),ease((t-1)/1.3) if i==1 else 0,'car')
    f.text(s['data']['question'],640,490,32,WHITE)
    f.text('条件、模拟与直觉',640,548,20,MUTED)
    f.text('依据：UC Berkeley · The Monty Hall Problem',640,590,15,MUTED,latin=True)

DRAWERS={'probability_ref_stage':stage,'probability_ref_paper':paper,'probability_ref_typewriter':typewriter,'probability_ref_letters':letters,'probability_ref_balance':balance,'probability_ref_chalk':chalk,'probability_ref_simulation':simulation,'probability_ref_hundred':hundred,'probability_ref_grouping':grouping,'probability_ref_conditions':conditions,'probability_ref_return':lambda f,s,t:stage(f,s,t,True),'probability_ref_finale':finale}

def validate_scene(s):
    d=s.get('data',{})
    if s['kind']=='probability_ref_simulation' and (not isinstance(d.get('seed',73),int) or d.get('trials',1000)!=1000):raise ValueError('simulation requires integer seed and 1000 trials')
    if s['kind']=='probability_ref_hundred' and not 1<=d.get('remaining',73)<=99:raise ValueError('remaining door must differ from the initial door')
