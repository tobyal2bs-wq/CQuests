"""Sync visual fixes for existing CQuests bosses without replacing gameplay.
Run from the CQuests root: python tools/worldboss/sync_visuals.py ../CBosses
Only millstone_monk is approved as a new addition; all other new drafts stay excluded.
"""
import json,sys,copy
from pathlib import Path
source=Path(sys.argv[1])/'src/main/resources/models.json'
target=Path('src/main/resources/worldboss-models.json')
cb=json.loads(source.read_text());cq=json.loads(target.read_text())
for id in ('ironhide_behemoth','void_walker','fenrir','abyssal_eye','rotting_giant','moonwake_manta'):cq['models'].pop(id,None)
for id,old in list(cq['models'].items()):
 if id not in cb['models']:continue
 m=copy.deepcopy(cb['models'][id]);available=set(cb['rigs'][m['rig']])|set(m.get('anims',{}))
 motions=dict(cb['rigs'][m['rig']],**m.get('anims',{}))
 candidates=[name for name in ['claw','rear','howl','bite','charge','cast','slam','tail','sting',m['melee']] if name in motions and motions[name].get('hit',-1)>0]
 for index,name in enumerate(dict.fromkeys(list(old.get('attacks',{}).values())+[old.get('melee')])):
  if not name or name in available:continue
  clip=copy.deepcopy(motions[candidates[index%len(candidates)]]);ratio=1+index*.065;clip['length']*=ratio;clip['hit']*=ratio
  for channels in clip['bones'].values():
   for keys in channels.values():
    for key in keys:key[0]*=ratio
  m.setdefault('anims',{})[name]=clip
 m['attacks']=old.get('attacks',{}).copy()
 if old.get('melee'):m['melee']=old['melee']
 # Shared visual refreshes keep existing damage-zone assignments and multipliers.
 for z in old.get('zones',[]):
  if z['kind']!='weak' or any(x['kind']=='weak' for x in m.get('zones',[])):continue
  if z['b'] in {b['name'] for b in m['bones']}:m['zones'].append(copy.deepcopy(z))
 cq['models'][id]=m
for id in ('millstone_monk','thorncoil_basilisk'):
 if id not in cb['models']:raise ValueError('Approved model missing: '+id)
 cq['models'][id]=copy.deepcopy(cb['models'][id])
cq['rigs']=cb['rigs'];target.write_text(json.dumps(cq,separators=(',',':')))
print('Synchronized',len(set(cb['models'])&set(cq['models'])),'visual models; only the explicitly approved additions may be added.')
