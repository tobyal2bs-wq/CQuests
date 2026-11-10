"""Repair joint cuts and author a compact, individual performance for each existing model.

No silhouettes, materials, IDs, ability mappings or rewards are replaced. Called by gen_models.
"""
from copy import deepcopy
import zlib

# Performances are chosen by character, rather than one roar shared by an entire rig.
PERFORMANCES = {
 'slagheart':'slam','warlord_gruk':'roar','grand_augur':'cast','crimson_ronin':'swipe',
 'thunderback':'stomp','gorehorn':'roar','abyssal_eye':'cast','overgrowth':'slam',
 'prism_sentinel':'cast','tiki_warden':'stomp','broodmother':'bite','ironhide_behemoth':'roar',
 'fenrir':'bite','tide_tyrant':'roar','void_walker':'cast','storm_herald':'cast',
 'pharaoh':'cast','executioner':'swipe','ember_queen':'cast','gravelord':'slam',
 'captain_brine':'swipe','keywarden':'stomp','bloodtusk':'roar','king_gloop':'bounce',
 'clockwork_colossus':'stomp','mossback':'roar','old_wizard':'cast','hollow_mage':'cast',
 'horned_brute':'roar','rotting_giant':'roar','dusk_scorpion':'sting','grave_marshal':'swipe',
 'mayor_grumble':'roar','old_ironroot':'slam','frost_yeti':'roar','bog_orc':'swipe',
 'the_listener':'roar','withered_tyrant':'cast','the_unmaker':'roar','killer_claus':'cast',
 'frostbottom':'stomp','old_man_winter':'cast','sunscorch':'bounce','admiral_pinchworth':'claw',
 'brain_freeze':'roar','clucksworth':'roar','killer_bunny':'bite','cocoa_colossus':'slam',
 'gourd_king':'roar','headless_horseman':'roar','hexmother':'cast','brakka':'roar',
 'gate_shade':'cast','oakheart':'slam','gnome_brothers':'cast','moss_spirit':'cast',
 'grubnose':'swipe','mudclub':'slam','ugor':'cast','bark_ape':'slam','old_blindman':'cast',
 'king_oldbeard':'cast','straw_farmer':'stomp','gilded_mimic':'bounce','mossling':'roar',
 'apple_crab':'claw','moss_imp':'roar','garden_gnome':'cast','angry_goose':'roar',
 'pack_goblin':'swipe','goblin_king':'cast','snapjaw':'bite','cap_brothers':'roar',
 'puffneck':'stomp','mallard':'stomp','piggy_farmer':'roar','ring_frog':'stomp',
 'hay_golem':'stomp','baby_minotaur':'roar','mandrake':'roar','mossy_turtle':'bite',
 'stumpy':'roar','boo_twin_b':'cast','cap_little':'roar','gnome_little':'cast',
}

def keys(length, vectors):
    return [[round(length*i/(len(vectors)-1),4),list(v)] for i,v in enumerate(vectors)]

def repair_joints(m):
    """Cut axis-aligned plates where the actual hinge crosses them; keep their union."""
    for b in m['bones']:
        if not b['name'].startswith(('fore','shin','foot')) or not b.get('parent'): continue
        parent=b['parent']; y=b['pivot'][1]; child=b['name']
        for c in list(m['cubes']):
            if c['b'] not in (parent,child) or c.get('r'): continue
            if c['f'][1]+0.02 < y < c['t'][1]-0.02:
                lower=deepcopy(c); lower['b']=child; lower['t'][1]=y
                c['b']=parent; c['f'][1]=y
                m['cubes'].append(lower)

def apply(id,m,rigs):
    if m.get('polish-revision')==1:return
    repair_joints(m)
    # Hinge cuts spend a few extra displays. Retire the smallest surface
    # flecks to keep the original 300-visible-block budget, never body boxes.
    active=lambda c:not str(c.get('g','')).startswith('face:') or c.get('g')=='face:idle'
    excess=sum(active(c) for c in m['cubes'])-300
    if excess>0:
        flecks=sorted((c for c in m['cubes'] if c.get('g')=='detail'),key=lambda c:__import__('math').prod(b-a for a,b in zip(c['f'],c['t'])))
        # Compare object identity, not dict equality (different faces may match).
        import builtins
        remove={builtins.id(c) for c in flecks[:excess]}
        m['cubes']=[c for c in m['cubes'] if builtins.id(c) not in remove]
    names={b['name'] for b in m['bones']}
    source=deepcopy(dict(rigs[m['rig']],**m.get('anims',{})))
    seed=zlib.crc32(id.encode()); pace=0.88+(seed%23)/100
    # Nonuniform animated scale shears attached limbs and can flip the SVD's
    # interpolation axes. Breathing is a small rotation, never stretched joints.
    for a in source.values():
        a['bones']={n:c for n,c in a['bones'].items() if n in names}
        for c in a['bones'].values(): c.pop('scl',None)
    idle=source.get('idle',{'length':4,'loop':True,'bones':{}})
    length=round(3.4+(seed%19)*0.11,3)
    # Keep existing model-specific gestures, then add a character's own glance
    # and breath. Small amplitude keeps facial plates and shoulders readable.
    old_length=idle['length']; idle['length']=length
    for c in idle['bones'].values():
        for channel,ks in c.items():
            for k in ks:
                k[0]=round(k[0]*length/old_length,4)
                if channel=='rot': k[1]=[round(v*0.55,3) for v in k[1]]
                if channel=='pos': k[1]=[round(v*0.3,3) for v in k[1]]
    if 'head' in names:
        look=4+(seed%9); tilt=1+(seed%3)
        idle['bones'].setdefault('head',{})['rot']=keys(length,[(0,0,0),(-2,look,tilt),(0,0,0),(2,-look,-tilt),(0,0,0)])
    if 'jaw' in names:
        idle['bones'].setdefault('jaw',{})['rot']=keys(length,[(0,0,0),(3+seed%5,0,0),(0,0,0),(1,0,0),(0,0,0)])
    source['idle']=idle
    if 'walk' in source:
        a=source['walk']; a['length']=round(a['length']*pace,4)
        for n,c in a['bones'].items():
            for channel,ks in c.items():
                for k in ks:
                    k[0]=round(k[0]*pace,4)
                    if channel=='rot': k[1]=[round(v*(0.6 if n.startswith('leg') else 0.75),3) for v in k[1]]
                    if channel=='pos': k[1]=[round(v*0.25,3) for v in k[1]]
    if not id.startswith('decor_'):
        pick=PERFORMANCES.get(id,'roar')
        if pick not in source or not source[pick]['bones']:
            pick=next((a for a in (m.get('melee'),'roar','cast','bite','slam','idle') if a in source and source[a]['bones']),'idle')
        opening=deepcopy(source[pick]); opening.pop('loop',None)
        # Each opening has authored timing and a distinct head/jaw accent.
        duration=round(1.15+(seed%17)*0.045,3); ratio=duration/opening['length'];opening['length']=duration
        if 'hit' in opening: opening['hit']*=ratio
        for c in opening['bones'].values():
            for channel,ks in c.items():
                for k in ks:
                    k[0]=round(k[0]*ratio,4)
                    if channel=='pos': k[1]=[round(v*0.3,3) for v in k[1]]
                    if channel=='rot': k[1]=[round(v*0.65,3) for v in k[1]]
        if 'jaw' in names: opening['bones']['jaw']={'rot':keys(duration,[(0,0,0),(12+seed%16,0,0),(8,0,0),(0,0,0)])}
        source['opening_'+id]=opening
        # Preserve the egg hatch and zombie climb, replacing only their gesture.
        for step in m['spawn']:
            step.pop('ring',None)
            if step['op']=='anim': step.update(name='opening_'+id,dur=round(duration*20))
        if not any(s['op']=='anim' for s in m['spawn']):
            m['spawn'].append({'op':'anim','at':16,'dur':round(duration*20),'name':'opening_'+id})
        for step in m['spawn']:
            if step['op']=='fx' and 'sound' in step: step['pitch']=round(0.82+(seed%23)*0.017,3)
    # Last pose must follow the entire opening, not cancel the final keyframes.
    pose=[s for s in m['spawn'] if s['op']=='pose']
    if pose:
        end=max((s['at']+s.get('dur',0) for s in m['spawn'] if s is not pose[-1]),default=0)
        pose[-1]['at']=end+2
    m['anims']=source
    m['polish-revision']=1
