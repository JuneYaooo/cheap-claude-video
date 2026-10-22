"""Night-city simulation grammar: aerial streets, documents, routes and mechanics.

Geometry and captions are newly drawn. Road travel times use the episode model;
the animated cars are explanatory marks, not microscopic traffic simulation.
"""
import math
import random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter

BG = '#070d16'
WHITE = '#e8e5d6'
GOLD = '#e2c780'
RED = '#ec6570'
CYAN = '#64d4dd'


def ease(x):
    x = min(1, max(0, x)); return x*x*(3-2*x)


@lru_cache(6)
def city_image(width, perspective=False):
    im = Image.new('RGB', (1280,720), BG); d = ImageDraw.Draw(im)
    rng = random.Random(42)
    def pt(x,y,z=0):
        return (640+(x-640)*(.62+y/1500) + (y-360)*.35,
                80+y*.76-z) if perspective else (x,y-z)
    for y in range(-40,850,39):
        for x in range(-120,1400,40):
            h=rng.randint(4,23); w=rng.randint(19,30)
            col=rng.choice(['#101b2b','#152031','#111c2a','#182333'])
            roof=[pt(x,y,h),pt(x+w,y,h),pt(x+w,y+25,h),pt(x,y+25,h)]
            d.polygon([pt(x+w,y,h),pt(x+w,y+25,h),pt(x+w,y+25),pt(x+w,y)],fill='#0b131f')
            d.polygon([pt(x,y+25,h),pt(x+w,y+25,h),pt(x+w,y+25),pt(x,y+25)],fill='#0c1421')
            d.polygon(roof,fill=col)
            if rng.random()>.52:
                a=pt(x+5,y+25,h-4); d.line([a,(a[0]+7,a[1])],fill='#665e4b',width=1)
    if perspective:
        for x in range(0,1280,160): d.line([pt(x,-50),pt(x,850)],fill='#5b5b54',width=3)
        for y in range(0,850,160):d.line([pt(-100,y),pt(1400,y)],fill='#62605a',width=3)
        for _ in range(700):
            x=rng.randrange(1280); y=rng.randrange(720)
            if (x%160<6 or y%160<5):d.ellipse((x,y,x+2,y+2),fill=WHITE)
    else:
        d.polygon([(450,210),(805,165),(930,440),(640,580),(400,440)],fill='#08121b')
    im=Image.blend(im,Image.new('RGB',im.size,BG),.35)
    return im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)


def glowline(f, points, color, width=2):
    # A restrained halo keeps the route readable over the buildings.
    f.line(points,'#15212b',width+12)
    f.line(points,'#28333a',width+7)
    f.line(points,color,width)


def poly(f,points,color):
    scale=f.im.width/1280
    f.a.d.polygon([(x*scale,y*scale) for x,y in points],fill=color)


def hud(f, label, value='', color=GOLD):
    f.a.rect((34,30,270,145),'#0c1522',fill=True,r=8)
    f.a.rect((34,30,270,145),'#263442',width=1,r=8)
    f.text(label,52,54,15,'#a4afb9',anchor='left',max_width=215)
    if value:
        f.text(value,53,101,44,color,anchor='left',latin=True,max_width=212)


def route_points():
    # Four winding roads form an irregular ring around the central district.
    A=(158,383); U=(565,240); L=(666,535); B=(1110,360)
    def curved(a,b,amp,phase):
        return [(a[0]+(b[0]-a[0])*q,
                 a[1]+(b[1]-a[1])*q+amp*math.sin(math.pi*q)+11*math.sin(q*math.pi*4+phase)*math.sin(math.pi*q))
                for q in [j/60 for j in range(61)]]
    return [curved(A,U,-23,0),curved(U,B,-105,.4),curved(A,L,100,.9),curved(L,B,-4,1.4)], [U,L]


def at(points,u):
    x=u*(len(points)-1); i=min(len(points)-2,int(x)); q=x-i
    return tuple(points[i][j]*(1-q)+points[i+1][j]*q for j in (0,1))


def network(f,t,flow=0,link=False,closed=False,explain=False,model=None):
    routes,bridge=route_points()
    for i,pts in enumerate(routes):
        used=i in (0,3)
        color=RED if flow>.5 and used else '#b6b6ac' if flow<.5 else '#333d4b'
        glowline(f,pts,color,4 if flow>.5 and used else 2)
        count=52 if used and flow>.5 else 36 if flow<.5 else 8
        for j in range(count):
            x,y=at(pts,(j/count+t*.024)%1)
            f.a.ellipse(x,y,1.8,color=WHITE if flow<.5 else GOLD if used else '#59616a',fill=True)
    if link:
        glowline(f,bridge,CYAN if not closed else '#34414b',3)
        if not closed:
            for j in range(28):
                x,y=at(bridge,(j/28+t*.04)%1)
                f.a.ellipse(x,y,2,color='#b8f2eb',fill=True)
        f.text('封闭' if closed else f'新连接 · {model["shortcut"]:g} 分钟',735,366,19,RED if closed else CYAN,anchor='left',max_width=220)
        if closed:
            f.line([(596,374),(628,396)],RED,4); f.line([(628,374),(596,396)],RED,4)
    for x,y,label in [(158,383,'家'),(1110,360,'公司')]:
        f.a.ellipse(x,y,12,color='#30343a',fill=True)
        f.a.ellipse(x,y,5,color=GOLD,fill=True)
        f.text(label,x,y-29,22,GOLD)
    if explain:
        variable=f'流量 ÷ {model["divisor"]:g}'; fixed=f'固定 {model["fixed"]:g} 分钟'
        values=[variable,fixed,fixed,variable]
        for i,pts in enumerate(routes):
            x,y=at(pts,.5); f.text(values[i],x,y+(-35 if i<2 else 35),20,CYAN if i in(0,3) else GOLD,max_width=260)


def system_ref(f,s,t):
    d=s['data']; mode=d['mode']; duration=s['duration']
    model=d['model']; n=model['flow']; half=n/model['divisor']/2; full=half*2
    fixed=model['fixed']; shortcut=model['shortcut']; before=half+fixed; after=full*2+shortcut
    f.im.paste(city_image(f.im.width, mode in ('grid','news','phone','conclusion')), (0,0))
    if mode in ('hook','rules','before','temptation','flow','after','close','return'):
        q=ease(t/duration)
        flow=(q if mode=='flow' else 1 if mode in ('hook','after') else 0)
        network(f,t,flow,mode in ('hook','temptation','flow','after','close','return'),mode in ('close','return'),mode=='rules',model)
        val=(before+(after-before)*q if mode=='flow' else after if mode in ('hook','after') else before)
        hud(f,f'同一批 {n:g} 辆车',f'{val:.0f} min',RED if val>before else GOLD)
        if mode=='rules':
            f.text('两条路线 · 同一个目的地',640,115,34,WHITE)
        elif mode=='temptation':
            f.text(f'{half:g} + {shortcut:g} + {half:g} = {2*half+shortcut:g}',640,580,37,CYAN,latin=True)
        elif mode=='after':
            f.text(f'{full:g} + {shortcut:g} + {full:g} = {after:g}',640,580,37,RED,latin=True)
            f.text(f'单独绕回旧路：{full:g} + {fixed:g} = {full+fixed:g}',640,616,22,'#aeb8c5')
        elif mode=='before':
            f.text(f'{n/2:g} / 路线',640,570,26,WHITE,latin=True)
            f.text(f'{half:g} + {fixed:g} = {before:g}',640,608,29,GOLD,latin=True)
        elif mode in ('close','return'):
            f.text(f'少一条连接 · 节省 {after-before:g} 分钟',640,582,34,GOLD)
    elif mode=='grid':
        hud(f,'反直觉的城市网络','少 = 快？')
        for j in range(7):
            x=190+j*152; y=220+(j%3)*95
            f.a.ellipse(x,y,22+3*math.sin(t+j),color=RED,width=2)
            f.text('!',x,y,24,RED,latin=True)
        f.text('路越多，一定越快吗？',640,555,53,WHITE)
    elif mode=='news':
        x=318+12*math.sin(t*.15); y=145
        f.a.rect((x+12,y+12,x+672,y+425),'#030507',fill=True)
        f.a.rect((x,y,x+660,y+413),'#e8e2ca',fill=True)
        f.text('城市观察 · 网络与选择',x+330,y+35,19,'#5a594e')
        f.line([(x+28,y+62),(x+632,y+62)],'#63645b',1)
        f.text('少一条路，',x+35,y+108,44,'#282c2b',anchor='left')
        f.text('为什么反而更通畅？',x+35,y+169,40,'#282c2b',anchor='left')
        for c in range(3):
            for j in range(18):
                xx=x+36+c*204; yy=y+215+j*8
                f.line([(xx,yy),(xx+174-(j%5)*8,yy)],'#888574',.6)
        hud(f,'一个问题','一座城市')
    elif mode=='phone':
        f.a.rect((476,105,804,608),'#010306',fill=True,r=36)
        f.a.rect((489,120,791,593),'#152132',fill=True,r=26)
        for x in range(515,791,55):f.line([(x,152),(x,553)],'#263442',6)
        for y in range(165,550,71):f.line([(508,y),(771,y)],'#263442',6)
        pts=[(540,515),(540,380),(730,380),(730,225)]
        glowline(f,pts,GOLD,4)
        for j in range(15):
            # Navigation steps deliberately track the schematic polyline.
            x,y=at(pts,(t*.08+j/15)%1);f.a.ellipse(x,y,3,color=WHITE,fill=True)
        f.a.ellipse(540,515,12,color=CYAN,width=3)
        f.text('每个人都在选最快的路',640,78,31,WHITE)
    elif mode=='paper':
        f.a.rect((0,0,1280,720),'#0b1017',fill=True)
        f.a.rect((435,95,860,595),'#eee7ce',fill=True)
        f.text(str(d['history_year']),72,95,64,GOLD,anchor='left',latin=True)
        f.text('BRAESS PARADOX',648,158,26,'#42443e',latin=True,max_width=370)
        f.text('局部最优',648,267,41,'#363b36')
        f.text('≠',648,333,55,'#77705b')
        f.text('全局最优',648,403,41,'#363b36')
        for j in range(6):f.line([(477,485+j*10),(813,485+j*10)],'#9b9785',1)
    elif mode=='spring':
        f.a.rect((0,0,1280,720),BG,fill=True)
        f.a.rect((422,95,858,113),GOLD,fill=True)
        rise=ease((t-4)/4); end=546-83*rise
        def spring(x,y0,y1):
            points=[(x,y0)]+[(x+(-15 if j%2 else 15),y0+(y1-y0)*j/30) for j in range(1,30)]+[(x,y1)]
            f.line(points,WHITE,2)
        spring(585,115,290);spring(695,310,end)
        f.line([(585,290),(695,310)],'#555f6c' if rise>.5 else RED,3)
        f.line([(585,115),(695,end)],'#515d68',1)
        f.line([(695,115),(585,end)],'#515d68',1)
        f.a.rect((585,end,695,end+65),'#121e2b',fill=True,r=5)
        f.a.rect((585,end,695,end+65),GOLD,width=2,r=5)
        f.text('网络',640,end+32,25,GOLD)
        f.text('连接关系改变，平衡也会改变',640,610,30,WHITE)
        f.text('结构类比示意 · 非物理数值仿真',640,52,17,'#9aabbc')
    elif mode=='boundary':
        f.a.rect((0,0,1280,720),BG,fill=True)
        for i,(title,detail) in enumerate([('固定需求',f'同一批 {n:g} 辆车'),('自利选择','各自最小化通行时间'),('特定成本','拥挤道路随流量变慢')]):
            yy=195+i*135
            f.text(f'0{i+1}',203,yy,50,GOLD,latin=True)
            f.text(title,330,yy-10,35,WHITE,anchor='left')
            f.text(detail,330,yy+39,24,'#9aabbc',anchor='left')
        f.text('它不是“修路有害”的普遍结论',640,77,35,WHITE)
    else:
        overlay=Image.new('RGB',f.im.size,BG); f.im.paste(Image.blend(f.im,overlay,.66))
        f.a.rect((215,175,1065,544),'#233141',width=1,r=12)
        f.text('BRAESS PARADOX',640,215,20,'#8599a9',latin=True)
        f.text('每个人都选对了，',640,323,52,GOLD)
        f.text('为什么一起变慢？',640,402,52,GOLD)
        f.text('看清规则，也要看清彼此的连接。',640,493,25,'#aeb9c3')


def validate_scene(s):
    m=s['data'].get('model',{})
    if any(not isinstance(m.get(k),(int,float)) or not math.isfinite(m[k]) or m[k]<=0 for k in ('flow','divisor','fixed')):
        raise ValueError('road model needs positive flow, divisor and fixed time')
    if not isinstance(m.get('shortcut'),(int,float)) or m['shortcut']<0 or not m['flow']/m['divisor']+m['shortcut']<m['fixed']:
        raise ValueError('model must satisfy dominant-shortcut assumption')
    if 1.5*m['flow']/m['divisor']+m['shortcut']<=m['fixed']:
        raise ValueError('model does not demonstrate a worse shortcut equilibrium')
    if s['data'].get('mode') not in {'hook','grid','news','phone','paper','rules','before','temptation','flow','after','close','spring','boundary','return','conclusion'}:
        raise ValueError('unknown reference system scene')


DRAWERS={'system_ref':system_ref}
