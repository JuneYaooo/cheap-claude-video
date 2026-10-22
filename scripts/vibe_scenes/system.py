"""City-map components for a four-node, two-route congestion model.

All model parameters, labels and scene copy come from the episode. Moving vehicles
illustrate direction and density; their speed is not a traffic simulation.
"""
import math


def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)


def metrics(d):
    n=d['total_flow'];v=n/d['flow_divisor'];fixed=d['fixed_time'];shortcut=d['shortcut_time']
    return {'half':v/2,'full':v,'before':v/2+fixed,'after':2*v+shortcut,'deviation':v+fixed}


def validate_scene(scene):
    d=scene['data']
    for key in ('total_flow','flow_divisor','fixed_time'):
        value=d.get(key)
        if not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:
            raise ValueError('system model requires positive finite '+key)
    if not isinstance(d.get('shortcut_time'),(int,float)) or not 0<=d['shortcut_time']<d['fixed_time']:
        raise ValueError('invalid shortcut time')
    m=metrics(d)
    if m['full']+d['shortcut_time']>=d['fixed_time']:
        raise ValueError('this component demonstrates a dominant shortcut; model parameters do not satisfy that condition')
    if len(d.get('node_labels',[]))!=4:
        raise ValueError('system city requires four node labels')
    if d.get('mode') not in ('hook','rules','baseline','shortcut','equilibrium','compare'):
        raise ValueError('unsupported system stage')


def num(v):
    return str(int(v)) if v==int(v) else f'{v:.1f}'


def car(f,x,y,angle,color,scale=1):
    # A directional vehicle glyph, not an undirected dot.
    c,s=math.cos(angle),math.sin(angle)
    points=[]
    for dx,dy in [(-7,-3),(4,-3),(8,0),(4,3),(-7,3)]:
        points.append(((x+(dx*c-dy*s)*scale)*f.im.width/1280,(y+(dx*s+dy*c)*scale)*f.im.width/1280))
    f.a.d.polygon(points,fill=color)


def along(points,u):
    lengths=[math.dist(a,b) for a,b in zip(points,points[1:])];pos=u*sum(lengths)
    for a,b,length in zip(points,points[1:],lengths):
        if pos<=length:
            q=pos/length
            return a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q,math.atan2(b[1]-a[1],b[0]-a[0])
        pos-=length
    a,b=points[-2:];return b[0],b[1],math.atan2(b[1]-a[1],b[0]-a[0])


def city(f,t,x=0,y=0,w=1280,h=620):
    p=f.p;a=f.a
    a.rect((x,y,x+w,y+h),p['background'],fill=True)
    # Quiet city blocks let the road model feel spatial without competing with it.
    for ix in range(7):
        for iy in range(4):
            bx=92+ix*115;by=206+iy*92
            a.rect((bx,by,bx+70,by+51),p['grid'],width=.7,r=3)
            a.rect((bx+6,by+7,bx+64,by+43),p['grid'],width=.5,r=1)
    f.text('SYSTEM / 城市里的选择',70,48,17,p['accent'],anchor='left')
    f.text('MODEL · NOT A REAL CITY',1210,48,14,p['muted'],anchor='right',latin=True)
    f.line([(70,72),(1210,72)],p['grid'])


def road_map(f,d,t,state,box=(130,245,730,480),labels=True):
    p,a=f.p,f.a;m=metrics(d);x0,y0,x1,y1=box;xm=(x0+x1)/2;ym=(y0+y1)/2
    nodes=[(x0,ym),(xm,y0),(xm,y1),(x1,ym)]
    edges=[(0,1),(1,3),(0,2),(2,3)]
    final=state in ('equilibrium','compare_after');open_link=state in ('shortcut','equilibrium','compare_after')
    for i,(u,v) in enumerate(edges):
        color=p['grid'] if final and i in (1,2) else p['muted']
        a.line([nodes[u],nodes[v]],p['grid'],19)
        a.line([nodes[u],nodes[v]],color,1)
        mid=((nodes[u][0]+nodes[v][0])/2,(nodes[u][1]+nodes[v][1])/2)
        if labels:
            value=num(m['full'] if final else m['half'])+' 分' if i in (0,3) and state!='rules' else ('流量 / '+num(d['flow_divisor']) if i in (0,3) else num(d['fixed_time'])+' 分')
            if state=='shortcut' and i in (0,3):value='最多 '+num(m['full'])+' 分'
            f.text(value,mid[0],mid[1]+(-31 if i in (0,1) else 31),18,p['accent'] if i in (0,3) else p['muted'],max_width=190)
    if open_link:
        grow=ease(t/1.4) if state=='shortcut' else 1
        endpoint=(xm,y0+(y1-y0)*grow)
        a.line([nodes[1],endpoint],p['grid'],21)
        a.arrow(nodes[1],endpoint,p['secondary'],3)
        if labels:f.text(num(d['shortcut_time'])+' 分',xm+48,ym,24,p['secondary'],anchor='left')
    paths=([[0,1,2,3]] if final else [[0,1,3],[0,2,3]])
    for pi,path in enumerate(paths):
        points=[nodes[n] for n in path]
        if final:color=p['secondary'];count=24
        else:color=p['accent'] if pi==0 else p['secondary'];count=11
        for j in range(count):
            xx,yy,angle=along(points,(t*.075+j/count)%1)
            car(f,xx,yy,angle,color,.78 if x1-x0<500 else 1)
    for i,(x,y) in enumerate(nodes):
        a.ellipse(x,y,23,color=p['background'],fill=True)
        a.ellipse(x,y,23,color=p['ink'],width=1.5)
        f.text(d['node_labels'][i],x,y,18,p['ink'],max_width=85)


def info(f,small,big,detail,y=260,color=None):
    p=f.p;c=color or p['accent']
    f.text(small,1040,y,21,p['muted'],max_width=300)
    f.text(big,1040,y+68,65,c,latin=True,max_width=300)
    f.text(detail,1040,y+123,21,p['ink'],max_width=300)


def system_city(f,s,t):
    d=s['data'];p=f.p;m=metrics(d);mode=d['mode'];city(f,t)
    f.text(s['heading'],70,123,41,p['ink'],anchor='left',max_width=1120)
    if mode in ('hook','compare'):
        # Compare the same geometry and same population; the extra edge is the only change.
        f.line([(640,220),(640,558)],p['grid'])
        road_map(f,d,t,'baseline',(120,275,530,460),False)
        road_map(f,d,t,'compare_after',(750,275,1160,460),False)
        f.text(d.get('before_label','原来的网络'),325,220,24,p['accent'])
        f.text(d.get('after_label','增加一条连接'),955,220,24,p['secondary'])
        f.text(num(m['before'])+' 分钟',325,530,48,p['accent'],latin=True)
        f.text(num(m['after'])+' 分钟',955,530,48,p['secondary'],latin=True)
        f.text('同样 '+num(d['total_flow'])+' 辆车 · 只改变一条连接',640,590,21,p['muted'])
    else:
        road_map(f,d,t,mode)
        f.line([(858,215),(858,565)],p['grid'])
        if mode=='rules':
            info(f,'同一个起点与终点',num(d['total_flow']),'辆车同时选择路线')
            f.text('两段随流量变化，两段用时固定。',1040,505,19,p['muted'],max_width=300)
        elif mode=='baseline':
            info(f,'每条路线分到一半车辆',num(m['before'])+' min',num(m['half'])+' + '+num(d['fixed_time'])+' = '+num(m['before']))
            f.text(num(d['total_flow']/2)+' 辆 / 路线',1040,505,24,p['accent'])
        elif mode=='shortcut':
            info(f,'新增连接耗时',num(d['shortcut_time'])+' min','每个人都想走捷径',color=p['secondary'])
            f.text(num(m['full']+d['shortcut_time'])+' < '+num(d['fixed_time']),1040,495,34,p['secondary'],latin=True)
            f.text('即使全挤上来，也比固定段快。',1040,545,18,p['muted'],max_width=300)
        elif mode=='equilibrium':
            info(f,'所有车辆改走中间',num(m['after'])+' min',num(m['full'])+' + '+num(d['shortcut_time'])+' + '+num(m['full']),color=p['secondary'])
            f.text('单独退出：约 '+num(m['deviation'])+' 分钟',1040,510,23,p['muted'],max_width=300)
        f.text(d.get('note','示意车辆仅表示方向与密度，不代表真实车速。'),440,582,18,p['muted'],max_width=760)


DRAWERS={'system_city':system_city}
