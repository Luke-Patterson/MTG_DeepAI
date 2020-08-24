import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
import copy
import time
import inspect
import numpy as np
from Exceptions import *
from Cards import *
from Card_types import *
from game import *
from Player import *
import pandas as pd
from itertools import product
from itertools import permutations

deck= [copy.deepcopy(Hill_Giant) for i in range(20)] + \
    [copy.deepcopy(Horned_Turtle) for i in range(20)] + \
    [copy.deepcopy(Grizzly_Bears) for i in range(20)]
plyr1=Player('plyr1',copy.deepcopy(deck))
for i in plyr1.lib:
    i.controller=plyr1
plyr2=Player('plyr2',copy.deepcopy(deck))
for i in plyr2.lib:
    i.controller=plyr2
    
plyr1.opponent=plyr2
plyr2.opponent=plyr1
g=Game(plyr1,plyr2,verbose=2)

plyr1.field.append([i for i in plyr1.lib if i.name=='Hill Giant'][0])
plyr1.field.append([i for i in plyr1.lib if i.name=='Horned Turtle'][0])
plyr1.field.append([i for i in plyr1.lib if i.name=='Grizzly Bears'][0])
plyr2.field.append([i for i in plyr2.lib if i.name=='Hill Giant'][0])
plyr2.field.append([i for i in plyr2.lib if i.name=='Horned Turtle'][0])
plyr2.field.append([i for i in plyr2.lib if i.name=='Grizzly Bears'][0])

for i in plyr1.field+plyr2.field:
    i.summoning_sick=False

g.act_plyr=plyr1
g.na_plyr=plyr2
g.act_plyr.declare_attackers()
g.na_plyr.declare_blockers()
print('Attackers:',g.act_plyr.get_attackers())
print('Blockers:',g.na_plyr.get_blockers())
for i in g.na_plyr.get_blockers():
    print(i, 'is blocking', i.is_blocking_attacker)
g.resolve_combat_damage()
g.check_state_effects()
