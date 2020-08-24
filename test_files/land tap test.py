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
from Player import *
import pandas as pd
from itertools import product
from itertools import permutations

deck= [copy.deepcopy(Forest) for i in range(2)] + \
    [copy.deepcopy(Taiga) for i in range(2)] + \
    [copy.deepcopy(Mountain) for i in range(2)] + \
    [copy.deepcopy(Cryptic_Caves) for i in range(2)] + \
    [copy.deepcopy(Grizzly_Bears) for i in range(2)]

plyr=Player('plyr',deck)
plyr.shuffle_lib()
plyr.draw_card(num=10)
[i for i in plyr.hand if i.name=='Forest'][0].play_card()
[i for i in plyr.hand if i.name=='Taiga'][0].play_card()
[i for i in plyr.hand if i.name=='Mountain'][0].play_card()
[i for i in plyr.hand if i.name=='Forest'][0].play_card()
# [i for i in plyr.hand if i.name=='Unknown Shores'][0].play_card()
[i for i in plyr.hand if i.name=='Cryptic Caves'][0].play_card()

plyr.tap_sources_for_cost({'C':1,'G':1})

print(time.process_time())
