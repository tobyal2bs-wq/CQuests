"""Explicitly approved additions. Review-only drafts never enter this registry."""
import json,copy
from pathlib import Path
from models import model
from build import Model
APPROVED={'millstone_monk','moonwake_manta','thorncoil_basilisk'}
INFO={'millstone_monk':dict(name='<gradient:#91b5aa:#e0d9bd><bold>Millstone Monk</bold></gradient>',title='Keeper of the Old Mill',entity='IRON_GOLEM',damage=12,armor=9,bar='GREEN',theme='earth',movement='walk',speed=.22,minion=None,minions=0,ability_seconds=8,phases=[.66,.33],hpp=.25,money=45000,top_money=135000,items=['STONE_BRICKS 32','MOSS_BLOCK 16','DIAMOND 2'],top_items=['NETHERITE_SCRAP 1'],extra=['heal'])}
def data(id):
 return json.loads((Path(__file__).parent/'approved'/(id+'.json')).read_text(encoding='utf8'))
@model
def millstone_monk():
 """An ancient stone millkeeper with a carved cyan-eyed face, moss-covered shoulders, folded robes, heavy braced hands and an axle-mounted turning millstone. The exposed glowing axle is its weak spot."""
 m=Model('millstone_monk','millstone',1)
 m.approved=data('millstone_monk')
 return m

INFO['moonwake_manta']={'name': '<gradient:#80b9b3:#e2eadb><bold>Moonwake Manta</bold></gradient>', 'title': 'Warden of the Moonlit Tide', 'entity': 'PHANTOM', 'damage': 11, 'armor': 6, 'bar': 'BLUE', 'theme': 'water', 'movement': 'fly', 'speed': 0.23, 'minion': None, 'minions': 0, 'ability_seconds': 8, 'phases': [0.66, 0.33], 'hpp': 0.25, 'money': 45000, 'top_money': 135000, 'items': ['PRISMARINE_SHARD 32', 'DIAMOND 2'], 'top_items': ['NETHERITE_SCRAP 1'], 'extra': ['pull', 'volley', 'levitate']}
@model
def moonwake_manta():
 m=Model('moonwake_manta',"studio",1)
 m.approved=data('moonwake_manta')
 return m

INFO['thorncoil_basilisk']={'name': '<gradient:#8fa36d:#e2eadb><bold>Thorncoil Basilisk</bold></gradient>', 'title': 'Fang of the Tangled Grove', 'entity': 'RAVAGER', 'damage': 13, 'armor': 8, 'bar': 'GREEN', 'theme': 'toxic', 'movement': 'walk', 'speed': 0.21, 'minion': None, 'minions': 0, 'ability_seconds': 8, 'phases': [0.66, 0.33], 'hpp': 0.25, 'money': 45000, 'top_money': 135000, 'items': ['MOSS_BLOCK 32', 'DIAMOND 2'], 'top_items': ['NETHERITE_SCRAP 1'], 'extra': ['poison', 'roar', 'quake']}
@model
def thorncoil_basilisk():
 m=Model('thorncoil_basilisk',"studio",1)
 m.approved=data('thorncoil_basilisk')
 return m
