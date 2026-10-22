"""Choice-stage components with explicit, deterministic exhaustive outcomes.

These diagrams do not claim random simulation or measured experimental counts.
Each drawer accepts the public Frame interface and episode-owned scene data.
"""
import math


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def validate_scene(scene):
    d = scene.get('data', {})
    if scene['kind'] in ('probability_choice', 'probability_rules', 'probability_trials'):
        if not isinstance(d.get('selected', 0), int) or not 0 <= d.get('selected', 0) < 3:
            raise ValueError('probability stage requires a selected door in 0..2')
    if scene['kind'] in ('probability_choice', 'probability_rules') and 'opened' in d:
        if not isinstance(d['opened'], int) or not 0 <= d['opened'] < 3 or d['opened']==d.get('selected',0):
            raise ValueError('host opening must be a valid unselected door')
    if scene['kind'] == 'probability_trials':
        order = d.get('prize_order', [0, 1, 2])
        if sorted(order) != [0, 1, 2]:
            raise ValueError('exhaustive stage must visit all three prize positions once')
        if scene['duration'] < 18:
            raise ValueError('three exhaustive rounds require at least 18 seconds')
    if scene['kind'] == 'probability_rules' and len(d.get('rules', [])) != 3:
        raise ValueError('rules stage requires three explicit conditions')
    if scene['kind'] == 'probability_result' and not 1 <= len(d.get('lines', [])) <= 3:
        raise ValueError('result requires one to three lines')


def stage(f):
    # Perspective floor and proscenium make this a choice stage, not a dashboard.
    a, p = f.a, f.p
    for x in (140, 340, 540, 740, 940, 1140):
        f.line([(640 + (x - 640) * .3, 435), (x, 600)], p['grid'])
    for y in (460, 489, 530, 590):
        f.line([(100, y), (1180, y)], p['grid'])
    a.rect((80, 216, 1200, 602), p['grid'], width=1, r=10)


def door(f, x, y, number, opened=0, selected=False, prize=False, reveal=False, scale=1):
    a, p = f.a, f.p
    w, h = 74 * scale, 200 * scale
    col = p['accent'] if selected else p['muted']
    a.rect((x-w-7, y-7, x+w+7, y+h+7), col, width=1.5, r=4)
    a.rect((x-w, y, x+w, y+h), p['background'], fill=True)
    if opened > .4 or reveal:
        if prize:
            # An abstract prize token is deliberately not a borrowed asset.
            cy = y + h * .48
            a.line([(x,cy-28*scale),(x+26*scale,cy),(x,cy+28*scale),(x-26*scale,cy),(x,cy-28*scale)],p['accent'],3)
            f.text('奖品',x,y+h*.76,21*scale,p['accent'],max_width=w*1.8)
        else:
            f.text('空',x,y+h*.48,35*scale,p['muted'])
    # The visible panel narrows continuously as the hinge opens.
    panel = (1-opened) * 2*w
    if panel > 1:
        a.rect((x-w,y,x-w+panel,y+h),p['grid'],fill=True,r=2)
        a.rect((x-w,y,x-w+panel,y+h),col,width=1.5,r=2)
        if opened < .12:
            f.text(f'{number:02d}',x,y+h*.44,48*scale,col,latin=True)
            a.ellipse(x+w*.65,y+h*.65,3*scale,color=col,fill=True)
    if selected:
        f.text('最初选择',x,y-29*scale,19*scale,p['accent'])


def probability_choice(f, s, t):
    d, a, p = s['data'], f.a, f.p
    stage(f)
    selected = d.get('selected', 0)
    opened = d.get('opened', next(j for j in (2,1,0) if j!=selected))
    reveal_at = d.get('reveal_at', 1.4)
    for j, x in enumerate((340, 640, 940)):
        door(f,x,286,j+1,ease((t-reveal_at)/.8) if j==opened else 0,j==selected)
    if t < reveal_at:
        f.text('先记住你的选择',640,553,27,p['ink'])
    else:
        f.text('坚持',340,553,29,p['secondary'])
        f.text('换门',640,553,29,p['accent'])
        f.text('主持人排除',940,553,21,p['muted'])
        remaining = max(0, math.ceil(s['duration']-t-1))
        if remaining:
            a.ellipse(1125,262,24,color=p['secondary'],width=2)
            f.text(str(remaining),1125,262,22,p['secondary'],latin=True)


def probability_rules(f, s, t):
    d, a, p = s['data'], f.a, f.p
    stage(f)
    selected = d.get('selected', 0)
    opened = d.get('opened', next(j for j in (2,1,0) if j!=selected))
    for j,x in enumerate((235,425,615)):
        door(f,x,312,j+1,ease((t-3.3)/.7) if j==opened else 0,j==selected,scale=.7)
    f.text(d.get('setup','奖品等概率放置'),425,535,24,p['secondary'])
    for i,rule in enumerate(d['rules']):
        active=t >= i*2.4
        y=284+i*105
        col=p['accent'] if active else p['grid']
        a.ellipse(815,y,17,color=col,width=2)
        f.text(str(i+1),815,y,17,col,latin=True)
        f.text(rule,861,y,25,col,anchor='left',max_width=300)
        if active: f.line([(860,y+30),(1135,y+30)],p['grid'])


def probability_trials(f, s, t):
    d, a, p = s['data'], f.a, f.p
    order=d.get('prize_order',[0,1,2]); selected=d.get('selected',0)
    period=s['duration']/3
    round_index=min(2,int(t/period)); phase=t-round_index*period
    prize=order[round_index]
    # Tie when selected==prize: use lowest-index legal empty door. Either tie
    # choice loses on switching, so this does not alter the exhaustive result.
    host=next(j for j in range(3) if j not in (selected,prize))
    target=next(j for j in range(3) if j not in (selected,host))
    reveal_time=period*.65
    settled=phase>=reveal_time
    complete=round_index+int(settled)
    stay=sum(v==selected for v in order[:complete])
    switch=complete-stay
    stage(f)
    f.text(f'情形 {round_index+1} / 3',155,249,22,p['secondary'],anchor='left')
    f.text(f'奖品在 {prize+1} 号门',745,249,22,p['muted'],anchor='right')
    xs=(250,470,690)
    for j,x in enumerate(xs):
        opening=ease((phase-period*.23)/.5) if j==host else ease((phase-reveal_time)/.45)
        door(f,x,325,j+1,opening,j==selected,j==prize,settled,scale=.66)
        if j==host and phase>period*.23:
            f.text('主持人开空门',x,501,18,p['muted'],max_width=185)
    if phase>period*.43:
        a.arrow((xs[selected],558),(xs[target],558),p['accent'],3)
        f.text('换到剩下的门',470,588,21,p['accent'])
    f.line([(825,245),(825,585)],p['grid'])
    f.text('已揭晓情形的累计',1010,260,21,p['muted'],max_width=300)
    f.text(f'{complete} / 3',1010,303,30,p['ink'],latin=True)
    for label,value,y,col in [('坚持赢',stay,370,p['secondary']),('换门赢',switch,463,p['accent'])]:
        f.text(label,887,y,24,col,anchor='left')
        f.text(str(value),1137,y,52,col,anchor='right',latin=True)
        for j in range(3):
            a.ellipse(902+j*95,y+43,7,color=col if j<value else p['grid'],fill=True)
    f.text('等可能情形穷举',1010,563,20,p['muted'])
    f.text('不是随机实测',1010,588,17,p['muted'])


def probability_odds(f, s, t):
    a,p=f.a,f.p
    stage(f)
    labels=s['data'].get('labels',['最初选对','最初选错'])
    for group,(x,col,label) in enumerate(((330,p['secondary'],labels[0]),(850,p['accent'],labels[1]))):
        f.text(label,x,275,29,col)
        n=group+1
        for i in range(n):
            xx=x+(i-(n-1)/2)*110
            a.ellipse(xx,370,38,color=col,width=2)
            if t>1+i*.3:f.text('1 / 3',xx,370,25,col,latin=True)
        a.arrow((x,420),(x,466),col,2)
        f.text('换门输' if group==0 else '换门赢',x,510,35,col)
    if t>2.5:
        f.text('1 / 3',330,568,35,p['secondary'],latin=True)
        f.text('2 / 3',850,568,35,p['accent'],latin=True)


def probability_boundary(f,s,t):
    a,p=f.a,f.p
    stage(f)
    cols=[('标准规则',p['accent'],['知道答案','总开未选中的空门','总给换门机会']),
          ('改了规则',p['secondary'],['随机开门？','选择性给换门机会？','需要重新计算'])]
    for x,(label,col,lines) in zip((350,925),cols):
        f.text(label,x,280,32,col)
        for i,line in enumerate(lines):
            f.text(line,x,361+i*70,26,col,alpha=ease((t-i*.5)/.6),max_width=440)
    f.line([(640,265),(640,560)],p['grid'])


def probability_result(f,s,t):
    p=f.p
    for i,line in enumerate(s['data']['lines']):
        f.text(line,640,325+i*82,51,p['accent'] if i==len(s['data']['lines'])-1 else p['ink'],alpha=ease((t-i*.5)/.7))
    f.text(s['data'].get('note',''),640,558,23,p['muted'])


DRAWERS={name:globals()[name] for name in (
    'probability_choice','probability_rules','probability_trials',
    'probability_odds','probability_boundary','probability_result')}
