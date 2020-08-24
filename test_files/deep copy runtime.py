import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from cards.M20_cards import *
from copy import deepcopy
from datetime import datetime

start=datetime.now()
objs=[]
for _ in range(100):
    x=deepcopy(Ajani_SotP)
    objs.append(x)

print(datetime.now()-start)
