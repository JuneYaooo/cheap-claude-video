"""Paper-and-ink learning scenes, independent of the episode's factual claims.

Drawers use the host renderer's logical 1280x720 canvas. The same illustrated
learner, notebook and desk persist across shots; all visible copy is input data.
"""
import math


def ease(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


def poly(f, points, color, outline=None, width=2):
    scale = f.im.width / 1280
    f.a.d.polygon([(round(x * scale), round(y * scale)) for x, y in points], fill=color)
    if outline:
        f.line(points + points[:1], outline, width)


def paper(f, x, y, w, h, lines=3, written=0):
    p, a = f.p, f.a
    poly(f, [(x+8,y+8),(x+w+8,y+8),(x+w+8,y+h+8),(x+8,y+h+8)],p['grid'])
    poly(f, [(x,y),(x+w-20,y),(x+w,y+20),(x+w,y+h),(x,y+h)],'#fbf8ef',p['ink'],2)
    f.line([(x+w-20,y),(x+w-20,y+20),(x+w,y+20)],p['muted'],1.5)
    for i in range(lines):
        yy=y+40+i*max(22,(h-60)/max(1,lines))
        f.line([(x+20,yy),(x+w-20,yy)],p['grid'],1)
        if written>i:
            f.line([(x+22,yy-4),(x+w-25,yy-4)],p['accent'],2)


def book(f, x, y, w=180, h=110, opened=True, tint=None):
    p, a = f.p, f.a
    color=tint or p['accent']
    if not opened:
        a.rect((x-w/2,y-h/2+8,x+w/2,y+h/2+8),'#fbf8ef',fill=True,r=2)
        a.rect((x-w/2,y-h/2+8,x+w/2,y+h/2+8),p['ink'],width=2,r=2)
        for yy in range(round(y+h/2),round(y+h/2+7),3):f.line([(x-w/2+6,yy),(x+w/2-3,yy)],p['muted'],1)
        a.rect((x-w/2,y-h/2,x+w/2,y+h/2),color,fill=True,r=3)
        f.line([(x-w/2+13,y-h/2+2),(x-w/2+13,y+h/2-2)],p['background'],1.5)
        return
    poly(f,[(x-w/2-5,y-h/2),(x,y-h/2+10),(x+w/2+5,y-h/2),(x+w/2+5,y+h/2+6),(x,y+h/2+15),(x-w/2-5,y+h/2+6)],color,p['ink'],2)
    poly(f,[(x-w/2,y-h/2-7),(x,y-h/2+8),(x+w/2,y-h/2-7),(x+w/2,y+h/2),(x,y+h/2+10),(x-w/2,y+h/2)],'#fbf8ef',p['ink'],2)
    f.line([(x,y-h/2+8),(x,y+h/2+9)],p['muted'],1.2)
    for side in (-1,1):
        for j in range(4):
            yy=y-h*.27+j*h*.16
            f.line([(x+side*15,yy+4),(x+side*(w/2-15),yy-3)],p['grid'],1.5)


def pencil(f, x, y, scale=1, angle=-.55):
    p=f.p
    ux,uy=math.cos(angle),math.sin(angle)
    vx,vy=-uy,ux
    pt=lambda r,z:(x+scale*(ux*r+vx*z),y+scale*(uy*r+vy*z))
    poly(f,[pt(0,0),pt(13,-5),pt(75,-5),pt(75,5),pt(13,5)],p['secondary'],p['ink'],1.5)
    poly(f,[pt(0,0),pt(13,-5),pt(13,5)],'#e5cba0',p['ink'],1)
    f.line([pt(0,0),pt(5,0)],p['ink'],2)


def person(f, x, y, scale=1, pose='read', t=0, color=None):
    """Head centre (x,y); seated body ends near y+150*scale."""
    p,a=f.p,f.a; color=color or p['accent']
    bob=math.sin(t*1.8)*1.2*scale
    tx=lambda xx:x+xx*scale
    ty=lambda yy:y+yy*scale+bob
    # Chair stays beneath the body and gives the learner a physical setting.
    f.line([(tx(-34),ty(75)),(tx(-34),ty(136)),(tx(48),ty(136))],p['muted'],3*scale)
    f.line([(tx(-25),ty(136)),(tx(-38),ty(184))],p['muted'],3*scale)
    a.ellipse(x,ty(0),26*scale,color='#f5d8b1',fill=True)
    a.ellipse(x,ty(0),26*scale,color=p['ink'],width=2.5*scale)
    f.line([(tx(-25),ty(-7)),(tx(-18),ty(-22)),(tx(0),ty(-29)),(tx(16),ty(-20))],p['ink'],4*scale)
    gaze=4 if pose in ('write','think','check') else -1
    a.ellipse(tx(-6+gaze),ty(1),1.8*scale,color=p['ink'],fill=True)
    a.ellipse(tx(10+gaze),ty(1),1.8*scale,color=p['ink'],fill=True)
    f.line([(tx(0),ty(13)),(tx(8),ty(14))],p['ink'],1.5*scale)
    poly(f,[(tx(-14),ty(30)),(tx(14),ty(30)),(tx(30),ty(48)),(tx(32),ty(110)),(tx(-30),ty(110)),(tx(-28),ty(48))],color,p['ink'],2*scale)
    f.line([(tx(-15),ty(111)),(tx(27),ty(137)),(tx(37),ty(182))],p['ink'],4*scale)
    f.line([(tx(15),ty(111)),(tx(52),ty(134)),(tx(61),ty(180))],p['ink'],4*scale)
    f.line([(tx(34),ty(182)),(tx(51),ty(182))],p['ink'],4*scale)
    f.line([(tx(58),ty(180)),(tx(75),ty(180))],p['ink'],4*scale)
    if pose=='think':
        f.line([(tx(22),ty(45)),(tx(48),ty(55)),(tx(23),ty(15))],p['ink'],3*scale)
        f.line([(tx(-23),ty(45)),(tx(-39),ty(92)),(tx(24),ty(92))],p['ink'],3*scale)
    else:
        reach=math.sin(t*5)*3 if pose in ('write','check') else math.sin(t*2)*2
        f.line([(tx(-23),ty(46)),(tx(-42),ty(83)),(tx(6),ty(92))],p['ink'],3*scale)
        f.line([(tx(23),ty(46)),(tx(55),ty(69)),(tx(80+reach),ty(91))],p['ink'],3*scale)
        if pose in ('write','check'):pencil(f,tx(79+reach),ty(94),.55*scale,-1.05)


def tabletop(f, y=498):
    p=f.p
    f.a.ellipse(640,y+79,480,17,color=p['grid'],fill=True)
    f.line([(126,y),(1154,y)],p['ink'],3)
    f.line([(177,y+2),(160,y+82)],p['muted'],2.5)
    f.line([(1105,y+2),(1123,y+82)],p['muted'],2.5)


def lamp(f,x,y):
    p=f.p
    f.line([(x,y),(x+18,y-118),(x-40,y-167)],p['ink'],3)
    poly(f,[(x-40,y-167),(x-91,y-142),(x-28,y-112)],p['secondary'],p['ink'],2)
    f.line([(x-27,y),(x+27,y)],p['ink'],4)


def bubble(f,x,y,w,h,text,size=24):
    p=f.p
    f.a.ellipse(x,y,w/2,h/2,color='#fbf8ef',fill=True)
    f.a.ellipse(x,y,w/2,h/2,color=p['muted'],width=1.5)
    f.a.ellipse(x-w*.32,y+h*.55,6,color=p['muted'],width=1.5)
    f.a.ellipse(x-w*.37,y+h*.77,3,color=p['muted'],width=1.5)
    f.text(text,x,y,size,p['ink'],max_width=w-25)


def learning_desk(f,s,t):
    d,p,a=s['data'],f.p,f.a
    tabletop(f,500)
    lamp(f,1040,499)
    # Repeated page marks travel from the book towards the learner, then stop.
    person(f,449,325,1.0,'read' if t<d.get('switch_at',3) else 'think',t)
    for j in range(3):book(f,242,481-j*23,157,17,False,p['secondary'] if j==1 else p['accent'])
    book(f,632,448,215,85,t<d.get('switch_at',3))
    paper(f,788,384,132,112,3,0)
    if t<d.get('switch_at',3):
        for j in range(3):
            q=(t*.45+j/3)%1
            x,y=635-q*120,380-math.sin(q*math.pi)*65
            f.line([(x,y),(x+20,y-3)],p['secondary'],2)
        bubble(f,662,275,228,65,d.get('reading_thought',''),26)
    else:
        bubble(f,662,275,238,75,d.get('recall_thought',''),28)
        a.ellipse(854,438,23,color=p['secondary'],width=2)
        f.text('?',854,439,28,p['secondary'],latin=True)
    f.text(d.get('left_label',''),242,548,23,p['muted'],max_width=260)
    f.text(d.get('right_label',''),854,548,23,p['accent'],max_width=280)
    f.text(d.get('note',''),640,594,21,p['muted'])


def learning_recall(f,s,t):
    d,p,a=s['data'],f.p,f.a
    hide,reveal=d['hide_at'],d['reveal_at'];hidden=hide<=t<reveal
    if hidden:
        book(f,640,403,650,250,False)
        f.text(d.get('hidden_title',''),640,360,37,'#fbf8ef',max_width=570)
        f.text(d.get('prompt',''),640,424,25,'#fbf8ef',max_width=570)
        remaining=max(0,math.ceil(reveal-t))
        a.ellipse(1092,385,49,color=p['grid'],width=3)
        scale=f.im.width/1280
        a.d.arc(tuple(v*scale for v in (1043,336,1141,434)),-90,-90+359*(reveal-t)/(reveal-hide),fill=p['secondary'],width=round(4*scale))
        f.text(str(remaining),1092,385,37,p['secondary'],latin=True)
    else:
        book(f,640,403,650,250,True)
        for i,word in enumerate(d['items']):
            x=485 if i<3 else 795;y=330+(i%3)*65
            f.text(str(i+1).zfill(2),x-95,y,18,p['secondary'],latin=True)
            f.text(word,x+10,y,31,p['ink'],max_width=230)
        if t>=reveal:
            for x in (485,795):
                for y in (330,395,460):
                    f.line([(x-96,y+17),(x-90,y+23),(x-79,y+8)],p['accent'],2)
        else:
            f.text(f'{max(0,math.ceil(hide-t))}',1092,385,37,p['secondary'],latin=True)
    pencil(f,188,502,.95,-.9)
    f.text(d.get('phase_labels',['','',''])[1 if hidden else 2 if t>=reveal else 0],640,570,27,p['accent'])
    f.text(d.get('note',''),640,602,18,p['muted'])


def learning_practice(f,s,t):
    d,p,a=s['data'],f.p,f.a
    steps=d['steps'];active=min(2,int(t/(s['duration']/3)))
    for i,x in enumerate((270,640,1010)):
        col=p['accent'] if i==active else p['muted']
        person(f,x-46,315,.77,('read','write','check')[i],t,col)
        f.line([(x-133,426),(x+140,426)],p['ink'],2.5)
        f.line([(x-109,426),(x-118,514)],p['muted'],2)
        f.line([(x+111,426),(x+120,514)],p['muted'],2)
        if i==0:book(f,x+44,402,106,56,True)
        elif i==1:
            book(f,x-97,409,50,24,False)
            paper(f,x+20,368,65,49,2,2 if active>=1 else 0)
        else:
            book(f,x+47,400,104,59,True)
            if active==2:
                f.line([(x+99,350),(x+108,360),(x+127,337)],p['secondary'],3)
        f.text(f'{i+1:02d}',x,264,19,col,latin=True)
        f.text(steps[i],x,556,27,col,max_width=310)
        if i==active:
            f.line([(x-90,589),(x+90,589)],p['secondary'],3)
    for x in (455,825):a.arrow((x-30,380),(x+30,380),p['secondary'],2)


def learning_questions(f,s,t):
    d,p,a=s['data'],f.p,f.a
    person(f,245,335,1.03,'write',t)
    f.line([(170,435),(420,435)],p['ink'],3)
    book(f,200,410,65,36,False)
    paper(f,310,416,85,30,0)
    f.line([(320,429),(320+50*ease((t%2)/1.5),429)],p['accent'],1.5)
    paper(f,532,247,540,330,0)
    for j,label in enumerate(d['questions']):
        yy=305+j*100;shown=ease((t-j*1.7)/.7)
        f.text(f'{j+1:02d}',572,yy,19,p['secondary'],latin=True)
        f.text(label,625,yy,29,p['ink'],anchor='left',alpha=shown,max_width=405)
        f.line([(625,yy+35),(1008,yy+35)],p['grid'],1)
        if t>j*1.7+.7:
            q=ease((t-j*1.7-.7)/1)
            f.line([(625,yy+30),(625+230*q,yy+30)],p['accent'],1.8)
    pencil(f,1028,565,1.15,-1.23)
    f.text(d.get('note',''),287,576,22,p['muted'],max_width=350)


def learning_evidence(f,s,t):
    d,p,a=s['data'],f.p,f.a
    # Calendars represent the tested delays, never invented quantitative bars.
    for i,(x,label) in enumerate(zip((397,882),d['delays'])):
        a.rect((x-156,265,x+156,474),'#fbf8ef',fill=True,r=8)
        a.rect((x-156,265,x+156,474),p['ink'],width=2,r=8)
        a.rect((x-156,265,x+156,306),p['secondary'] if i==0 else p['accent'],fill=True,r=8)
        for xx in (x-95,x+95):f.line([(xx,252),(xx,280)],p['ink'],4)
        f.text(label,x,371,48,p['ink'],alpha=ease((t-i*.8)/.6),max_width=285)
        f.text(d.get('calendar_label',''),x,437,23,p['muted'])
    a.arrow((578,371),(697,371),p['secondary'],2)
    f.text(d.get('finding',''),640,527,30,p['accent'],max_width=1100)
    f.text(d.get('source_label',''),640,573,18,p['muted'],latin=True)
    f.text(d.get('note',''),640,603,18,p['muted'])


def learning_action(f,s,t):
    d,p,a=s['data'],f.p,f.a
    tabletop(f,500)
    person(f,380,326,1.02,'write',t)
    book(f,244,471,141,39,False)
    paper(f,454,415,83,69,2,2)
    paper(f,570,261,408,297,0)
    for i,item in enumerate(d['items']):
        yy=318+i*79
        a.rect((604,yy-11,625,yy+10),p['muted'],width=1.5,r=2)
        f.text(item,653,yy,28,p['ink'],anchor='left',max_width=290)
        q=ease((t-1-i*1.8)/.6)
        if q>0:
            points=[(608,yy-1),(614,yy+6),(630,yy-14)]
            a.path(points,q,p['secondary'],3)
    pencil(f,1017,476,1.1,-1.2)
    f.text(d.get('note',''),640,596,23,p['accent'],max_width=1100)


DRAWERS = {
    'learning_desk': learning_desk,
    'learning_recall': learning_recall,
    'learning_practice': learning_practice,
    'learning_questions': learning_questions,
    'learning_evidence': learning_evidence,
    'learning_action': learning_action,
}


def validate_scene(scene):
    """Reject unsafe layouts and mismatched practice timing before rendering."""
    kind, data, duration = scene['kind'], scene.get('data', {}), scene['duration']
    if kind == 'learning_recall':
        if not 0 < data.get('hide_at', 0) < data.get('reveal_at', 0) < duration:
            raise ValueError('learning_recall requires visible, hidden and answer phases')
        if len(data.get('items', [])) != 6 or any(not isinstance(v,str) or not 1<=len(v)<=6 for v in data['items']):
            raise ValueError('learning_recall requires six short words')
        if len(data.get('phase_labels', [])) != 3:
            raise ValueError('learning_recall requires three phase labels')
    required = {'learning_practice': ('steps',3,10), 'learning_questions': ('questions',3,12),
                'learning_action': ('items',3,14), 'learning_evidence': ('delays',2,8)}
    if kind in required:
        key,count,maxlen = required[kind]
        if len(data.get(key, [])) != count or any(not isinstance(v,str) or not 1<=len(v)<=maxlen for v in data[key]):
            raise ValueError(f'{kind} requires {count} short {key}')
    if kind == 'learning_desk' and not 0 < data.get('switch_at', 3) < duration:
        raise ValueError('learning_desk requires a switch within the scene')
