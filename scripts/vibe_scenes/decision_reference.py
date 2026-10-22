"""Reference-grounded full-frame decision film. Facts and computed data live in inputs."""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)


@lru_cache(4)
def backdrop(width):
    h=round(width*9/16);yy,xx=np.mgrid[0:h,0:width];r=((xx/width-.5)/.68)**2+((yy/h-.5)/.85)**2
    glow=np.maximum(0,1-r)**2
    arr=np.stack([3+7*glow,5+11*glow,8+18*glow],axis=2).astype('uint8')
    return Image.fromarray(arr)


@lru_cache(32)
def halo(radius,scale,color):
    size=max(5,round(radius*scale*2));im=Image.new('RGBA',(size,size));d=ImageDraw.Draw(im)
    for r in range(size//2,0,-2):
        alpha=round(70*(1-r/(size/2))**2)
        d.ellipse((size//2-r,size//2-r,size//2+r,size//2+r),fill=(*color,alpha))
    return im


def light(f,x,y,r=28,color=(235,173,70)):
    sc=f.im.width/1280;im=halo(r,sc,color);f.im.paste(im,(round(x*sc-im.width/2),round(y*sc-im.height/2)),im)
    f.a.ellipse(x,y,2.2,color=f.p['accent'],fill=True)


def base(f,s,t):
    f.im.paste(backdrop(f.im.width),(0,0));p=f.p
    for i in range(70 if s['data'].get('stars') else 28):
        x=70+(i*179.17)%1140;y=75+(i*67.97+t*(i%3+1)*.2)%540
        f.a.ellipse(x,y,.35+(i%3)*.22,color='#24303a',fill=True)
    if s['data'].get('show_heading',True):f.text(s['heading'],640,89,34,p['ink'],max_width=1130)


@lru_cache(12)
def title_layers(text,font,width):
    sc=width/1280;ft=ImageFont.truetype(font,round(270*sc));box=ft.getbbox(text);pad=round(64*sc);w=box[2]+2*pad;h=box[3]-box[1]+2*pad
    mask=Image.new('L',(w,h));d=ImageDraw.Draw(mask);d.text((pad,pad-box[1]),text,font=ft,fill=255)
    outline=Image.new('RGBA',(w,h));od=ImageDraw.Draw(outline);od.text((pad,pad-box[1]),text,font=ft,fill=(0,0,0,0),stroke_width=max(1,round(sc)),stroke_fill=(202,205,209,180))
    yy=np.linspace(0,1,h)[:,None];rgb=np.zeros((h,w,4),dtype='uint8');rgb[:,:,0]=255-45*yy;rgb[:,:,1]=218-85*yy;rgb[:,:,2]=100-65*yy;rgb[:,:,3]=np.asarray(mask)
    fill=Image.fromarray(rgb);glow=fill.filter(ImageFilter.GaussianBlur(13*sc))
    return outline,fill,glow


@lru_cache(4)
def beam_layer(width):
    sc=width/1280;w=round(140*sc);h=round(610*sc);x=np.linspace(-1,1,w);arr=np.zeros((h,w,4),dtype='uint8');arr[:,:,:3]=(232,176,76);arr[:,:,3]=np.round(92*np.exp(-12*x*x))[None,:];return Image.fromarray(arr)

def title(f,s,t):
    base(f,s,t);d=s['data'];p=f.p;sc=f.im.width/1280
    out,fill,glow=title_layers(d['display'],p['display_font'],f.im.width)
    x=round(640*sc-out.width/2);y=round(290*sc-out.height/2)
    f.im.paste(out,(x,y),out);q=ease(t/3.9);cut=max(1,round(fill.width*q));piece=fill.crop((0,0,cut,fill.height));gp=glow.crop((0,0,min(glow.width,cut+12),glow.height));f.im.paste(gp,(x,y),gp);f.im.paste(piece,(x,y),piece)
    bx=(x+cut)/sc
    beam=beam_layer(f.im.width);f.im.paste(beam,(round(bx*sc-beam.width/2),0),beam)
    f.line([(bx,0),(bx,610)],p['accent'],1)
    f.text(d.get('kicker',''),640,115,16,p['accent'],latin=True)
    f.text(d.get('note',''),640,528,29,p['ink'])


def field(f,s,t):
    base(f,s,t);d=s['data'];p=f.p;vals=d['values'];n=len(vals);x0,y0,w,h=120,526,1040,270;slot=w/n
    mode=d.get('mode','intro');cut=d.get('cutoff',37);threshold=max(vals[:cut]);chosen=next((i for i in range(cut,n) if vals[i]>threshold),n-1)
    if mode=='observe':upto=min(cut,max(1,round(cut*ease(t/4))))
    elif mode=='select':upto=min(chosen+1,cut+max(1,round((chosen-cut+1)*ease(t/6))))
    else:upto=n if mode in ('early','late') else max(1,round(n*ease(t/4)))
    if mode in ('observe','select'):
        f.a.rect((x0,220,x0+slot*cut,y0),'#101b2a',fill=True)
        f.line([(x0+slot*cut,178),(x0+slot*cut,y0+15)],p['accent'],1)
        f.text(d.get('ratio_label',''),x0+slot*cut,154,53,p['accent'],latin=True)
    for i,v in enumerate(vals):
        x=x0+i*slot;col=p['muted'] if i<upto else '#12202b'
        if mode=='early':col=p['accent'] if i==d['future_best'] else '#eff0eb' if i==d['selected'] else '#101a23'
        if mode=='late':col=p['accent'] if i==d['future_best'] else '#eff0eb' if i==d['selected'] else '#101a23'
        if mode=='select' and i==chosen and upto>chosen:col=p['accent']
        f.line([(x,y0),(x,y0-v*h)],col,2 if n<50 else 1.4)
    f.line([(x0,y0),(x0+w,y0)],'#37434d',.6)
    if mode in ('observe','select'):
        local=max(vals[:upto]) if mode=='observe' else threshold;yy=y0-local*h
        f.line([(x0-12,yy),(x0+slot*max(cut,upto),yy)],p['accent'],1)
        f.text(d.get('threshold_label',''),x0-15,yy,15,p['accent'],anchor='right')
        f.text(d.get('left_label',''),x0+slot*cut/2,563,18,p['muted'])
        f.text(d.get('right_label',''),x0+slot*(cut+n)/2,563,18,p['accent'])
        if mode=='select' and upto>chosen:
            xx=x0+slot*chosen;light(f,xx,yy,45);f.line([(xx,yy-140),(xx,y0+10)],p['accent'],2)
            f.text(d.get('action',''),min(1080,xx+110),yy-55,73,p['accent'],alpha=ease((t-5)/.7))
    elif mode in ('early','late'):
        for key,label in [('selected',d.get('selected_label','')),('future_best',d.get('best_label',''))]:
            i=d[key];xx=x0+i*slot;yy=y0-vals[i]*h;light(f,xx,yy,25);f.text(label,xx,yy-26,19,p['accent'] if key=='future_best' else p['ink'],max_width=250)
    f.text(d.get('note',''),640,590,17,p['muted'])


def curve(f,s,t):
    base(f,s,t);d=s['data'];p=f.p;x0,y0,w,h=155,530,940,330;pts=d['points'];mode=d.get('mode','build')
    for q in (0,.1,.2,.3,.4,.5):
        y=y0-q/.5*h;f.line([(x0,y),(x0+w,y)],'#16212a',.5);f.text(f'{q:.0%}',x0-15,y,15,p['muted'],anchor='right',latin=True)
    for q in (0,.25,.5,.75,1):f.text(f'{q:.0%}',x0+q*w,y0+24,15,p['muted'],latin=True)
    f.line([(x0,y0-h),(x0,y0),(x0+w,y0)],'#48515a',.8)
    f.text(d.get('y_label',''),x0,174,17,p['muted'],anchor='left');f.text(d.get('x_label',''),1095,579,17,p['muted'],anchor='right')
    progress=ease(t/7) if mode=='build' else 1
    if mode=='build':
        for i,(x,y) in enumerate(d['simulation']):
            if i/len(d['simulation'])>progress:continue
            px=x0+x*w;py=y0-y/.5*h;f.a.ellipse(px,py,1,color='#756642',fill=True)
        f.text(d.get('counter_label',''),1068,190,13,p['muted'],anchor='right',latin=True)
        f.text(f'{round(d["trials"]*progress):,}',1068,222,29,p['ink'],anchor='right',latin=True)
    path=[(x0+x*w,y0-y/.5*h) for x,y in pts]
    f.a.path(path,progress,p['accent'],2.4,glow=True)
    mx,my=d['marker'];xx=x0+mx*w;yy=y0-my/.5*h
    if mode!='build' or t>7:
        f.line([(xx,yy),(xx,y0)],'#a48242',.8);light(f,xx,yy,40)
        f.text(d['marker_label'],xx,573,27,p['accent'],latin=True)
    if mode in ('formula','peak'):
        f.text(d.get('formula',''),x0+28,223,30,p['ink'],anchor='left',latin=True)
        f.text(d.get('formula_note',''),x0+28,260,21,p['accent'],anchor='left',latin=True)
    if mode=='peak':
        f.line([(x0,yy),(xx,yy)],p['accent'],1.2);f.text(d.get('height_label',''),x0-22,yy,31,p['accent'],anchor='right',latin=True)
    f.text(d.get('note',''),640,608,16,p['muted'])


def tile_grid(f,data,t,rect=(140,160,1000,335),dim=False):
    p=f.p;outcomes=data['outcomes'];vals=data['mini_values'];x0,y0,w,h=rect;cellw=w/10;cellh=h/10
    seen=min(100,round(100*ease(t/max(1,data.get('reveal_seconds',6)))))
    for i,win in enumerate(outcomes):
        x=x0+(i%10)*cellw;y=y0+(i//10)*cellh;on=i<seen
        col=('#715b30' if win else '#492c2a') if on else '#17232c'
        if dim:col='#23282b'
        f.a.rect((x,y,x+cellw-6,y+cellh-4),col,width=.6)
        for j,v in enumerate(vals[i]):
            xx=x+4+j*(cellw-14)/len(vals[i]);f.line([(xx,y+cellh-8),(xx,y+cellh-8-v*(cellh-13))],col,.7)
    return seen


def trials(f,s,t):
    base(f,s,t);d=s['data'];p=f.p;seen=tile_grid(f,d,t)
    wins=sum(d['outcomes'][:seen]);f.text(d.get('left_label',''),300,555,20,p['muted']);f.text(str(wins),420,555,46,p['accent'],latin=True)
    f.text(d.get('right_label',''),800,555,20,p['muted']);f.text(str(seen-wins),930,555,46,p['secondary'],latin=True)
    f.text(d.get('note',''),640,597,17,p['muted'])


def words(f,s,t):
    base(f,s,t);d=s['data'];p=f.p
    if d.get('outcomes'):tile_grid(f,d,100,dim=True)
    if d.get('flow'):
        for i in range(65):
            x=((i*97.3+t*(40+i%5*7))%1600)-160;y=95+(i*53.7)%470
            f.line([(x,y),(x+90+i%4*24,y)],'#1d2931',.6);f.a.ellipse(x+90+i%4*24,y,.8,color='#67716d',fill=True)
    lines=d['lines']
    for i,line in enumerate(lines):f.text(line,640,315+i*75,45 if len(lines)>1 else 48,p['accent'] if i==len(lines)-1 else p['ink'],alpha=ease((t-i*.5)/1),max_width=1110)
    if d.get('note'):f.text(d['note'],640,510,23,p['muted'],alpha=ease((t-2)/1))


def age(f,s,t):
    base(f,s,t);d=s['data'];p=f.p;x0,w,y0=135,1010,513;lo,hi=d['range'];point=d['point'];xx=x0+(point-lo)/(hi-lo)*w
    f.line([(x0,y0),(x0+w,y0)],'#58616a',.8)
    for val in d['ticks']:
        x=x0+(val-lo)/(hi-lo)*w;f.line([(x,y0-5),(x,y0+5)],'#58616a',1);f.text(str(val),x,y0+27,19,p['muted'],latin=True)
    f.a.rect((x0,290,xx,y0),'#101d2a',fill=True)
    f.line([(xx,175),(xx,y0+20)],p['accent'],1.2);light(f,xx,y0,40)
    f.text(f'{point:.1f}',xx,238,70,p['accent'],latin=True);f.text(d.get('marker_label',''),xx,295,18,p['accent'])
    for i,event in enumerate(d['events']):
        x=x0+(i+1)/(len(d['events'])+1)*(xx-x0);y=360+(i%3)*40
        f.line([(x,y0),(x,y+18)],'#34424d',.6);f.text(event,x,y,18,p['muted'],alpha=ease((t-i*.5-1)/.8),max_width=110)
    f.text(d['note'],640,594,20,p['accent'])


def threshold(f,s,t):
    base(f,s,t);d=s['data'];p=f.p;x0,w,y0,h=135,1010,524,290;vals=d['values'];n=len(vals)
    shown=min(n,round(n*ease(t/4)))
    for i,v in enumerate(vals):
        if i>=shown:break
        x=x0+i*w/n;f.line([(x,y0),(x,y0-v*h)],p['muted'],2)
    path=[(x0+x*w,y0-y*h) for x,y in d['threshold_points']];f.a.path(path,1,p['accent'],2)
    f.text(d.get('line_label',''),x0,195,20,p['accent'],anchor='left');f.text(d.get('note',''),640,587,20,p['muted'])


def rank(f,s,t):
    base(f,s,t);d=s['data'];p=f.p;rows=d['rows'];idx=min(len(rows)-1,int(ease(t/6)*(len(rows)-1)));n,val=rows[idx]
    f.text(d.get('left_label',''),300,240,22,p['muted']);f.text(f'{n:,}',300,305,58,p['ink'],latin=True,max_width=480)
    f.text(d.get('right_label',''),925,240,22,p['muted']);f.text(f'{val:.2f}',925,316,90,p['accent'],latin=True)
    x0,y0,w=180,490,920;f.line([(x0,y0),(x0+w,y0)],'#46515b',1)
    marker=x0+(val-1)/9*w
    for i in range(1,11):
        x=x0+(i-1)/9*w;f.line([(x,y0-6),(x,y0+6)],'#46515b',.8);f.text(str(i),x,y0+29,18,p['muted'],latin=True)
    f.line([(x0,y0),(marker,y0)],p['accent'],3);light(f,marker,y0,35)
    f.text(d.get('note',''),640,581,22,p['accent'])


def recap(f,s,t):
    base(f,s,t);d=s['data'];p=f.p
    f.text(d.get('number',''),120,216,19,p['accent'],anchor='left',latin=True)
    f.line([(120,237),(153,237)],p['accent'],1)
    f.text(d['main'],120,310,44,p['ink'],anchor='left',max_width=650)
    f.text(d['sub'],120,371,23,p['muted'],anchor='left',max_width=635)
    if d.get('outcomes'):tile_grid(f,d,100,(850,210,340,220));return
    vals=d['values'];x0,y0,w,h=840,475,350,230;threshold=d['threshold'];shown=min(len(vals),1+int(ease(t/5)*(len(vals)-1)))
    for i,v in enumerate(vals):
        if i>=shown:break
        x=x0+i*w/len(vals);f.line([(x,y0),(x,y0-v*h)],p['accent'] if v>threshold else p['muted'],3)
    f.line([(x0,y0-threshold*h),(x0+w,y0-threshold*h)],p['accent'],1.2)


def end(f,s,t):
    base(f,s,t);d=s['data'];p=f.p
    if d.get('beam'):
        yy=365
        for j in range(18,0,-3):f.line([(0,yy),(1280,yy)],'#3c2b13' if j>9 else '#6a4f24',j)
        f.line([(0,yy),(1280,yy)],p['accent'],1)
    for i,line in enumerate(d['lines']):f.text(line,640,290+i*140,62 if len(d['lines'])>1 else 78,p['ink'] if i==0 else p['accent'],alpha=ease((t-i*.6)/1),max_width=1120)
    f.text(d.get('english',''),640,420,16,p['accent'],latin=True,alpha=ease((t-1.5)/1))
    f.text(d.get('note',''),640,531,25,p['muted'],alpha=ease((t-2)/1))


DRAWERS={'decision_ref_'+n:f for n,f in [('title',title),('field',field),('curve',curve),('trials',trials),('words',words),('age',age),('threshold',threshold),('rank',rank),('recap',recap),('end',end)]}


def validate_scene(s):
    d=s['data'];kind=s['kind']
    if 'values' in d and (not d['values'] or any(not isinstance(v,(float,int)) or not 0<=v<=1 for v in d['values'])):raise ValueError('candidate values must be normalized')
    if kind=='decision_ref_field' and not 1<=d.get('cutoff',37)<len(d['values']):raise ValueError('cutoff must split candidate sequence')
    if kind=='decision_ref_curve' and (len(d.get('points',[]))<2 or len(d.get('marker',[]))!=2):raise ValueError('curve needs points and marker')
    if kind=='decision_ref_title' and not d.get('display'):raise ValueError('title needs display')
    if 'outcomes' in d and (len(d['outcomes'])!=100 or len(d.get('mini_values',[]))!=100):raise ValueError('trial grid requires 100 actual outcomes')
