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

deck= [copy.deepcopy(Hill_Giant) for i in range(20)] + \
    [copy.deepcopy(Horned_Turtle) for i in range(20)] + \
    [copy.deepcopy(Grizzly_Bears) for i in range(20)] + \
    [copy.deepcopy(Volcanic_Hammer) for i in range(20)] + \
    [copy.deepcopy(Mountain) for i in range(20)]
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
plyr1.field.append([i for i in plyr1.lib if i.name=='Mountain'][0])
plyr1.field.append([i for i in plyr1.lib if i.name=='Mountain'][1])
plyr1.field.append([i for i in plyr1.lib if i.name=='Horned Turtle'][0])
plyr1.field.append([i for i in plyr1.lib if i.name=='Grizzly Bears'][0])
plyr2.field.append([i for i in plyr2.lib if i.name=='Hill Giant'][0])
plyr2.field.append([i for i in plyr2.lib if i.name=='Horned Turtle'][0])
plyr2.field.append([i for i in plyr2.lib if i.name=='Grizzly Bears'][0])

test_targets=plyr1.get_legal_targets(lambda x: 'creature' in x.types)
[i for i in plyr1.lib if i.name=='Volcanic Hammer'][0].play_card()
