"""Second visual pass: real hinge sockets, grounded rest poses, two-eyed birds,
and individual entrance, hurt and death performances. Draft ideas never ship here.
Pure standard-library data editing; called after polish.apply by gen_models.
"""
from copy import deepcopy
from collections import Counter
import math,zlib
REMOVED={'ironhide_behemoth','void_walker','fenrir'}
FREE=('orb','gem','halo','crystal','book','spark','float','aura')

def keys(duration,values):
 return [[round(duration*i/(len(values)-1),4),list(v)] for i,v in enumerate(values)]

def cube(m,b,k,center,size,tag=''):
 c={'b':b,'k':k,'f':[round(center[i]-size[i]/2,5) for i in range(3)],'t':[round(center[i]+size[i]/2,5) for i in range(3)]}
 if tag:c['g']=tag
 m['cubes'].append(c);return c

def bird(m,id):
 """An actual bird rig: low oval body, joined neck, side eyes, bill and webbed feet."""
 old=deepcopy(m);m['cubes']=[]
 pigeon=id=='puffneck';goose=id=='angry_goose';neck=7 if goose else 1.5
 m['bones']=[{'name':'root','parent':None,'pivot':[0,0,0]},
  {'name':'hips','parent':'root','pivot':[0,3,0]},
  {'name':'legL','parent':'hips','pivot':[2,3,1]}, {'name':'legR','parent':'hips','pivot':[-2,3,1]},
  {'name':'body','parent':'hips','pivot':[0,4,0]},
  {'name':'neck','parent':'body','pivot':[0,8,3]},
  {'name':'head','parent':'neck','pivot':[0,8+neck,3]},
  {'name':'jaw','parent':'head','pivot':[0,9+neck,5.4]},
  {'name':'armL','parent':'body','pivot':[4.2,8,-1]}, {'name':'armR','parent':'body','pivot':[-4.2,8,-1]},
  {'name':'tail','parent':'body','pivot':[0,6,-5]}]
 body='white_wool' if goose else 'gray_wool' if pigeon else 'light_gray_wool'
 head='white_wool' if goose else 'gray_wool' if pigeon else 'green_terracotta'
 foot='pink_terracotta' if pigeon else 'orange_terracotta'
 cube(m,'body',body,[0,6.5,-.7],[8,6,10]);cube(m,'body','white_wool' if goose else 'purple_terracotta' if pigeon else 'brown_terracotta',[0,6.5,4],[6.8,5.2,1.4])
 for side,b in [(1,'legL'),(-1,'legR')]:
  cube(m,b,foot,[side*2,1.9,1],[.8,3.4,.8]);cube(m,b,foot,[side*2,.35,2],[2.8,.7,3.6])
 for side,b in [(1,'armL'),(-1,'armR')]:
  cube(m,b,body,[side*4.05,6.5,-1],[1.3,4.3,7.8]);cube(m,b,'white_wool' if goose else 'light_gray_wool',[side*4.7,6,-1],[.18,1.4,5],'trim')
  if not goose:cube(m,b,'purple_terracotta' if pigeon else 'blue_terracotta',[side*4.78,7,-1],[.15,1.5,3.5],'trim')
 cube(m,'neck',head,[0,8+neck/2,3],[3.8,neck+1,3.8])
 if not goose and not pigeon:cube(m,'neck','white_wool',[0,8.6,3],[4.05,.7,4.05])
 cube(m,'head',head,[0,10+neck,3],[6,5,5.5])
 # Only two eye surfaces, one on each side. No second pair on the front.
 for side in [-1,1]:
  cube(m,'head','white_concrete',[side*3.06,10.6+neck,4.1],[.18,1.7,1.7],'eye_white')
  cube(m,'head','black_concrete',[side*3.17,10.6+neck,4.35],[.12,1,1],'eye_pupil')
 bill='black_terracotta' if pigeon else 'orange_terracotta' if goose else 'yellow_terracotta'
 cube(m,'head',bill,[0,9.8+neck,6.65],[2 if pigeon else 4,.8,2.5]);cube(m,'jaw',bill,[0,9.15+neck,6.45],[1.8 if pigeon else 3.8,.45,2.2])
 cube(m,'tail',body,[0,7,-6.6],[5.2,1.7,4]);
 if id=='mallard':cube(m,'tail','black_terracotta',[0,8.4,-8],[1.2,2.2,1.2])
 # A few contiguous feather plates keep low detail useful without painting extra eyes.
 for side in [-1,1]:
  for y in [5.5,7.8]:cube(m,'body',body,[side*3.94,y,-2],[.16,1.2,3],'detail')
 names={b['name'] for b in m['bones']}
 for a in m.get('anims',{}).values():a['bones']={b:c for b,c in a['bones'].items() if b in names}
 m['height']=12.5+neck;m['scale']=round((1.9 if goose else 1.65)*16/m['height'],5)
 m['hitbox']=.8
 m['zones']=[{'kind':'head','b':'head','c':[0,10+neck,3],'w':6,'h':5,'mult':1.5},{'kind':'body','b':'body','c':[0,6.5,0],'w':8,'h':6,'mult':1}]
 walk=m['anims'].get('walk',{'length':.9,'loop':True,'bones':{}})
 walk['bones']={'legL':{'rot':keys(walk['length'],[(15,0,0),(-15,0,0),(15,0,0)])},'legR':{'rot':keys(walk['length'],[(-15,0,0),(15,0,0),(-15,0,0)])},'neck':{'rot':keys(walk['length'],[(-3,0,0),(4,0,0),(-3,0,0)])}}
 m['anims']['walk']=walk

def socket_joints(m):
 """Extend a short matching socket to both sides of each actual hinge.
 A pivot covered on both branches stays covered while the branches rotate.
 No new independent bone and no floating filler is introduced.
 """
 bones={b['name']:b for b in m['bones']};count=0
 for b in m['bones']:
  name=b['name'];parent=b.get('parent')
  if not parent or not name.startswith(('leg','shin','foot','arm','fore','head','neck','jaw','tail','n1','n2','n3','n4','stem')):continue
  child=[c for c in m['cubes'] if c['b']==name and not c.get('g','').startswith('face:')]
  if not child:continue
  p=parent;parts=[c for c in m['cubes'] if c['b']==p]
  while not parts and bones.get(p,{}).get('parent'):
   p=bones[p]['parent'];parts=[c for c in m['cubes'] if c['b']==p]
  if not parts and name.startswith('leg'):
   parts=[c for c in m['cubes'] if c['b']=='body'];p=parent
  if not parts:continue
  for branch,items in [(name,child),(p,parts)]:
   plain=[c for c in items if not c.get('r') and c.get('g','') not in ('detail','trim') and not c.get('g','').startswith(('face:','eye_'))]
   if not plain:continue
   pivot=b['pivot'];point=lambda c:[max(c['f'][i],min(c['t'][i],pivot[i])) for i in range(3)]
   nearest=min(plain,key=lambda c:sum((point(c)[i]-pivot[i])**2 for i in range(3)))
   q=point(nearest);dist=math.dist(q,pivot)
   if dist<=.04:continue
   if dist>9:continue # Deliberately separate props need an explicit authored parent.
   width=min(1.8,max(.65,min(nearest['t'][i]-nearest['f'][i] for i in range(3))*.55))
   cube(m,branch,nearest['k'],[(q[i]+pivot[i])/2 for i in range(3)],[abs(q[i]-pivot[i])+width for i in range(3)],'joint')
   count+=1
 return count

def performance(id,m,rigs):
 seed=zlib.crc32(id.encode());a=deepcopy(dict(rigs[m['rig']],**m.get('anims',{})));names={b['name'] for b in m['bones']}
 # Attached bones rotate around their hinge; translation channels were pulling
 # skin/armour plates away even when the skeleton parent relation was correct.
 for name,clip in a.items():
  clip['bones']={n:c for n,c in clip['bones'].items() if n in names}
  if not name.startswith(('die','death')):
   for n,ch in clip['bones'].items():
    if n!='root' and not n.startswith(FREE):ch.pop('pos',None)
    ch.pop('scl',None)
    if n=='root' and name in ('idle','walk'):ch.pop('pos',None)
 # The root keeps a grounded silhouette while the head, jaw, wings and weapon
 # define each creature's performance. Different families have different beats.
 birdlike=id in ('mallard','puffneck','angry_goose','clucksworth')
 plant=id in ('overgrowth','old_ironroot','oakheart','mossling','mandrake','stumpy','snapjaw','moss_imp')
 quad=m['rig'] in ('quad','spider','scorpion')
 caster=any(n in names for n in ('staff','wand','book','orb')) or id in ('grand_augur','pharaoh','hollow_mage','hexmother','old_wizard','moss_spirit','ugor')
 group='bird' if birdlike else 'plant' if plant else 'beast' if quad else 'caster' if caster else 'fighter'
 duration=round(1.35+(seed%29)*.027,3);death_dur=round(1.8+(seed%31)*.031,3)
 def gesture(length,root,head,jaw,arms):
  clip={'length':length,'bones':{}}
  for bone,values in [('root',root),('head',head),('jaw',jaw),('armL',arms),('armR',[(x,-y,-z) for x,y,z in arms])]:
   if bone in names:clip['bones'][bone]={'rot':keys(length,values)}
  return clip
 tilt=2+seed%5;look=5+seed%13;side=1 if seed%2 else -1
 opening={
 'bird':([(0,0,0),(4,0,0),(-3,0,0),(0,0,0)],[(0,0,0),(-8,look,0),(5,-look,0),(0,0,0)],[(0,0,0),(12,0,0),(22,0,0),(0,0,0)],[(0,0,0),(0,0,48),(0,0,12),(0,0,0)]),
 'plant':([(0,0,0),(0,0,-tilt),(0,0,tilt),(0,0,0)],[(0,0,0),(8,look,0),(-5,-look,0),(0,0,0)],[(0,0,0),(18,0,0),(5,0,0),(0,0,0)],[(0,0,0),(-25,0,18),(-8,0,5),(0,0,0)]),
 'beast':([(0,0,0),(3,side*7,0),(-2,-side*3,0),(0,0,0)],[(0,0,0),(-12,look,0),(-7,-look,0),(0,0,0)],[(0,0,0),(25+seed%12,0,0),(15,0,0),(0,0,0)],[(0,0,0)]*4),
 'caster':([(0,0,0),(0,-side*8,0),(0,side*5,0),(0,0,0)],[(0,0,0),(-5,-look,0),(4,look,0),(0,0,0)],[(0,0,0),(7,0,0),(3,0,0),(0,0,0)],[(0,0,0),(-55,10,25),(-30,-8,12),(0,0,0)]),
 'fighter':([(0,0,0),(5,side*10,0),(-2,-side*5,0),(0,0,0)],[(0,0,0),(-7,look,tilt),(4,-look,-tilt),(0,0,0)],[(0,0,0),(17,0,0),(8,0,0),(0,0,0)],[(0,0,0),(-32,0,18),(8,0,-6),(0,0,0)])}[group]
 a['opening_'+id]=gesture(duration,*opening)
 # A brief reaction authored per creature, with no sideways limb translation.
 accent=round(seed/4294967295*9,6)
 recoil={'bird':(-3,0,side*3),'plant':(4,0,side*5),'beast':(-4,side*5,0),'caster':(-2,side*7,0),'fighter':(-tilt,side*3,0)}[group]
 guard=(0,0,26+accent) if birdlike else (-22,0,8) if caster else (8+accent,0,-tilt)
 a['hurt']=gesture(round(.28+(seed%7)*.008,3),[(0,0,0),recoil,(0,0,0)],[(0,0,0),(5+accent,side*4,0),(0,0,0)],[(0,0,0),(6+accent,0,0),(0,0,0)],[(0,0,0),guard,(0,0,0)])
 falls={'bird':(54,0,side*12),'plant':(35,side*8,side*17),'beast':(0,side*5,side*64),'caster':(-16,side*24,side*13),'fighter':(38,side*8,side*16)}
 end=falls[group];a['death_'+id]=gesture(death_dur,[(0,0,0),(end[0]*.12,0,0),(end[0]*.45,end[1]*.3,end[2]*.25),end],[(0,0,0),(12,0,0),(24,0,side*7),(28+accent,0,side*12)],[(0,0,0),(15,0,0),(10,0,0),(0,0,0)],[(0,0,0),(-8,0,8),(15,0,-8),(30+accent,0,-15)])
 m['anims']=a
 # Keep the bespoke hatch and climbing opening. Everything else presents one
 # complete silhouette and its own performance, rather than loose flying cubes.
 if id not in ('clucksworth','rotting_giant'):
  fx=next((deepcopy(s) for s in m['spawn'] if s['op']=='fx'),{'op':'fx','particle':'CLOUD','count':20})
  fx.update(at=0,count=18+seed%16,spread=.3+(seed%5)*.07,pitch=round(.82+(seed%21)*.023,3));fx.pop('ring',None)
  ticks=round(duration*20)
  m['spawn']=[{'op':'scale','at':0,'dur':0,'s':[.92,.92,.92]},fx,{'op':'pose','at':0,'dur':6},{'op':'anim','at':4,'dur':ticks,'name':'opening_'+id},{'op':'pose','at':ticks+7,'dur':3}]
 else:
  for s in m['spawn']:
   s.pop('ring',None)
   if s['op']=='anim':s.update(name='opening_'+id,dur=round(duration*20))
 # Whole-body farewell: creature-specific collapse, theme burst, fade. No
 # detached parts hang indefinitely and no universal white-flash shatter.
 oldfx=next((deepcopy(s) for s in m['death'] if s['op']=='fx'),{'op':'fx','particle':'SMOKE','count':20})
 oldfx.update(at=round(death_dur*20)-5,count=16+seed%19,spread=.4,pitch=round(.72+(seed%17)*.027,3));oldfx.pop('ring',None)
 ticks=round(death_dur*20)
 m['death']=[{'op':'anim','at':0,'dur':ticks,'name':'death_'+id},{'op':'flash','at':4+seed%5,'dur':2,'only':'lit' if any(c.get('l') for c in m['cubes']) else 'all','block':'gray_concrete'},oldfx,{'op':'shrink','at':ticks-4,'dur':12}]
 if group=='plant':m['death'].insert(-1,{'op':'scale','at':ticks-8,'dur':12,'s':[1.08,.4,1.08]})
 elif group=='caster':m['death'].insert(-1,{'op':'toward','at':ticks-5,'dur':10,'only':'lit','y':.8})
 elif id in ('slagheart','clockwork_colossus','prism_sentinel'):
  m['death'].insert(-1,{'op':'light','at':ticks-10,'dur':0,'only':'lit','on':False})
 if id=='the_unmaker':m['death'].insert(-1,{'op':'shatter','at':ticks-1,'dur':12,'power':1.2,'pieces':2})

def apply(id,m,rigs):
 if m.get('refine-revision')==2:return
 if id in ('mallard','puffneck','angry_goose'):bird(m,id)
 if id=='mossy_turtle':
  for c in m['cubes']:
   if c['b']=='head' and c['k']=='black_concrete' and c.get('g')=='detail':
    if c['t'][0]-c['f'][0]<.3:c['k']='green_terracotta'
    elif c['t'][2]-c['f'][2]<.3:c['g']='eye_pupil'
 # Props must not become the floor anchor and leave their owner's feet in air.
 # Rotate around the existing grip (never translate it out of the hand).
 for b in m['bones']:
  angle={('moss_spirit','staff'):83,('mudclub','club'):-35,('old_blindman','staff'):0}.get((id,b['name']))
  if angle is not None:b['rest']=[angle,0,0]
 if id=='horned_brute':
  for c in m['cubes']:
   if c['b']=='spear' and c['k']=='stripped_spruce_log' and c['t'][1]-c['f'][1]>30:c['f'][1]+=8
 if id=='broodmother':m['cubes']=[c for c in m['cubes'] if not(c['b']=='abdomen' and (c['k']=='white_stained_glass' and c.get('g')=='trim' or c['k']=='gray_wool' and c.get('r')==[-40,0,0]))]
 added=socket_joints(m)
 if not id.startswith('decor_'):performance(id,m,rigs)
 # All source geometry is grounded, including rotated rest limbs. Existing
 # intentional hovering/flying models retain their runtime lift setting.
 floor=min(c['f'][1] for c in m['cubes'] if not c['b'].startswith('shell') and not c.get('g','').startswith('face:'))
 if abs(floor)>.0001:
  for b in m['bones']:b['pivot'][1]=round(b['pivot'][1]-floor,5)
  for c in m['cubes']:
   c['f'][1]=round(c['f'][1]-floor,5);c['t'][1]=round(c['t'][1]-floor,5)
   if 'o' in c:c['o'][1]=round(c['o'][1]-floor,5)
  for z in m.get('zones',[]):z['c'][1]=round(z['c'][1]-floor,5)
 m['joint-sockets']=added;m['refine-revision']=2
 # Spend sockets on actual structure, retire the smallest surface flecks.
 def active(c):return not c.get('g','').startswith('face:') or c['g']=='face:idle'
 excess=sum(active(c) for c in m['cubes'])-300
 if excess>0:
  small=sorted((c for c in m['cubes'] if c.get('g')=='detail'),key=lambda c:math.prod(c['t'][i]-c['f'][i] for i in range(3)))
  remove={__import__('builtins').id(c) for c in small[:excess]};m['cubes']=[c for c in m['cubes'] if __import__('builtins').id(c) not in remove]
