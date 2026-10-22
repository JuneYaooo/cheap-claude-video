"""Cinematic, data-driven decision-model scenes for the Vibe drawing runtime.

The scene input supplies every topic claim. This module supplies only visual grammar.
"""
import math


def ease(x):
    x = max(0.0, min(1.0, x))
    return x*x*(3-2*x)


def base(f, s, t, chapter=True):
    p=f.p
    f.a.rect((0,0,1280,720),p['background'],fill=True)
    # Thin concentric contours and a quiet gold dust field, not a card dashboard.
    for j in range(5):
        f.a.ellipse(1130,360,200+j*70,230+j*60,color=p['grid'],width=.5)
    for j in range(23):
        x=100+(j*177.1)%1080; y=130+(j*61.7+t*1.2)%445
        f.a.ellipse(x,y,.5+(j%3)*.25,color=p['grid'],fill=True)
    if chapter:
        f.text(s.get('eyebrow',''),84,68,17,p['accent'],anchor='left',max_width=1080)
        f.line([(84,92),(175,92)],p['accent'],1)
    f.text(s['heading'],84,150,39,p['ink'],anchor='left',max_width=1110)


def opening(f,s,t):
    base(f,s,t,False);p=f.p;d=s['data']
    f.text(d.get('kicker',''),84,73,16,p['accent'],anchor='left',latin=True)
    vals=d['values'];horizon=515
    # Moving candidates pass the decision line. A fading past and an unknown future.
    for i,v in enumerate(vals):
        x=85+i*126-t*22
        if x<65 or x>1220:continue
        h=45+v*170
        f.line([(x,horizon),(x,horizon-h)],p['muted'] if x<640 else p['grid'],2.5)
        f.a.ellipse(x,horizon-h,3,color=p['accent'] if x<640 else p['muted'],fill=True)
    f.line([(70,horizon),(1210,horizon)],p['muted'],.6)
    f.line([(640,282),(640,540)],p['accent'],1.6)
    f.text(d.get('present_label',''),640,570,19,p['accent'])
    for i,line in enumerate(d['lines']):
        f.text(line,640,269+i*66,55,p['ink'] if i==0 else p['accent'],alpha=ease((t-.35-i*.55)/.8))


def conditions(f,s,t):
    base(f,s,t);p=f.p;d=s['data'];items=d['items']
    for i,item in enumerate(items):
        x=95+(i%2)*590;y=265+(i//2)*137
        alpha=ease((t-i*.75)/.6)
        f.text(str(i+1).zfill(2),x,y,43,p['accent'],anchor='left',latin=True,alpha=alpha)
        f.text(item,x+84,y,29,p['ink'],anchor='left',max_width=460,alpha=alpha)
        if alpha>.9:f.line([(x+84,y+38),(x+490,y+38)],p['grid'],1)
    f.text(d.get('note',''),640,553,24,p['muted'],alpha=ease((t-4)/.8))


def track(f,s,t):
    base(f,s,t);p=f.p;d=s['data'];vals=d['values'];n=len(vals)
    cutoff=d['cutoff'];threshold=max(vals[:cutoff]);slot=1040/n
    chosen=next((i for i in range(cutoff,n) if vals[i]>threshold),None)
    # Hold the discovery, stop revealing at the chosen candidate; future stays unknown.
    reveal=min(n if chosen is None else chosen+1, int(max(0,t-.6)/d.get('step_seconds',.75))+1)
    y0=505;scale=260
    for i,v in enumerate(vals):
        x=120+i*slot;visible=i<reveal
        if not visible:
            f.text('·',x+20,y0-12,31,p['grid']);continue
        h=scale*v;col=p['muted'] if i<cutoff else p['accent']
        if i<reveal-1 and i!=chosen:col=p['muted']
        grow=ease((t-.6-i*d.get('step_seconds',.75))/.5)
        f.a.rect((x,y0-h*grow,x+40,y0),col,fill=True,r=2)
        f.text(str(i+1),x+20,y0+26,17,p['muted'],latin=True)
        if i==chosen and reveal>chosen:
            f.a.ellipse(x+20,y0-h-21,5,color=p['accent'],fill=True)
            f.text(d.get('chosen_label',''),x+20,y0-h-53,26,p['accent'])
    f.line([(106,y0+1),(1175,y0+1)],p['grid'],1)
    divide=120+cutoff*slot-32
    f.line([(divide,243),(divide,540)],p['secondary'],1)
    if reveal>=cutoff:
        yy=y0-threshold*scale
        for x in range(105,1175,18):f.line([(x,yy),(x+6,yy)],p['secondary'],1)
        f.text(d.get('threshold_label',''),1150,yy-22,19,p['secondary'],anchor='right')
    f.text(d.get('left_label',''),105,572,21,p['muted'],anchor='left')
    f.text(d.get('right_label',''),1170,572,21,p['accent'],anchor='right')


def curve(f,s,t):
    base(f,s,t);p=f.p;d=s['data']
    x0,y0,w,h=130,526,720,275
    for q in (0,.25,.5,.75,1):
        y=y0-q*h
        f.line([(x0,y),(x0+w,y)],p['grid'],.7)
        f.text(f'{q*d["y_max"]*100:.0f}%',x0-18,y,15,p['muted'],anchor='right',latin=True)
    for q in (0,.25,.5,.75,1):
        f.text(f'{q*100:.0f}%',x0+q*w,y0+27,15,p['muted'],latin=True)
    f.line([(x0,y0-h),(x0,y0),(x0+w,y0)],p['muted'],1)
    points=[(x0+x*w,y0-y*h) for x,y in d['points']]
    progress=ease(t/4.5)
    f.a.path(points,progress,p['accent'],3,glow=True)
    if t>3.5:
        x,y=d['marker'];mx,my=x0+x*w,y0-y*h
        f.line([(mx,my),(mx,y0)],p['secondary'],1)
        f.a.ellipse(mx,my,6,color=p['accent'],fill=True)
        f.text(d['marker_label'],1020,345,74,p['accent'],latin=True,max_width=330,alpha=ease((t-3.5)/1))
        f.text(d.get('marker_note',''),1020,416,20,p['muted'],max_width=330,alpha=ease((t-4.2)/.8))
    f.text(d.get('x_label',''),495,587,20,p['muted'])
    f.text(d.get('y_label',''),132,218,19,p['muted'],anchor='left')
    f.text(d.get('formula',''),1020,490,25,p['ink'],latin=True,max_width=320,alpha=ease((t-5)/.8))


def odds(f,s,t):
    base(f,s,t);p=f.p;d=s['data'];values=d['values'];total=sum(values);fraction=values[0]/total
    cx,cy,r=340,390,125
    for i in range(100):
        angle=-math.pi/2+i*2*math.pi/100
        shown=i<100*ease(t/3)
        col=(p['accent'] if i<round(fraction*100) else p['grid']) if shown else p['background']
        f.line([(cx+math.cos(angle)*r,cy+math.sin(angle)*r),(cx+math.cos(angle)*(r+20),cy+math.sin(angle)*(r+20))],col,3)
    f.text(d['display'][0],cx,cy,69,p['accent'],latin=True)
    f.text(d['labels'][0],cx,cy+65,23,p['muted'])
    f.text(d['display'][1],725,350,80,p['secondary'],anchor='left',latin=True,alpha=ease((t-2)/1))
    f.text(d['labels'][1],725,425,29,p['ink'],anchor='left',alpha=ease((t-2.8)/1))
    f.text(d.get('note',''),640,579,22,p['muted'])


def epilogue(f,s,t):
    base(f,s,t,False);p=f.p;d=s['data']
    # The last choice becomes a single opening, while the language regains space.
    for j in range(3):
        xx=640+(j-1)*63
        f.line([(xx,233),(xx,270)],p['grid'] if j!=1 else p['accent'],1)
    for i,line in enumerate(d['lines']):
        f.text(line,640,333+i*80,54,p['ink'] if i==0 else p['accent'],alpha=ease((t-.3-i*.85)/1),max_width=1100)
    f.text(d.get('note',''),640,554,23,p['muted'],alpha=ease((t-3.3)/1))


DRAWERS={f'decision_{name}':fn for name,fn in [('opening',opening),('conditions',conditions),('track',track),('curve',curve),('odds',odds),('epilogue',epilogue)]}


def validate_scene(scene):
    """Reject malformed geometry before rendering; semantic claims remain editorial."""
    kind=scene['kind'];d=scene['data']
    def normalized(values):
        return isinstance(values,list) and values and all(isinstance(x,(int,float)) and math.isfinite(x) and 0<=x<=1 for x in values)
    if kind in ('decision_opening','decision_track'):
        if not normalized(d.get('values')) or not 3<=len(d['values'])<=16:raise ValueError('decision sequence requires 3–16 normalized values')
    if kind=='decision_track':
        if not isinstance(d.get('cutoff'),int) or not 1<=d['cutoff']<len(d['values']):raise ValueError('decision cutoff must split the sequence')
        if not isinstance(d.get('step_seconds',.75),(int,float)) or not .25<=d.get('step_seconds',.75)<=2:raise ValueError('invalid decision step duration')
    if kind in ('decision_opening','decision_epilogue') and (not isinstance(d.get('lines'),list) or not 1<=len(d['lines'])<=2):raise ValueError('decision text requires one or two lines')
    if kind=='decision_conditions' and (not isinstance(d.get('items'),list) or len(d['items'])!=4):raise ValueError('decision conditions require four items')
    if kind=='decision_curve':
        pts=d.get('points',[])
        if not isinstance(pts,list) or len(pts)<2 or any(not isinstance(v,list) or len(v)!=2 or not normalized(v) for v in pts):raise ValueError('decision curve requires normalized 2D points')
        if any(b[0]<a[0] for a,b in zip(pts,pts[1:])):raise ValueError('curve x must be monotonic')
        if not normalized(d.get('marker')) or len(d['marker'])!=2 or not 0<d.get('y_max',0)<=1:raise ValueError('invalid decision curve axes')
    if kind=='decision_odds':
        if not normalized(d.get('values')) or len(d['values'])!=2 or sum(d['values'])<=0 or any(len(d.get(key,[]))!=2 for key in ('labels','display')):raise ValueError('decision odds need two values and labels')
