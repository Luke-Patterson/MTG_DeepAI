from Game import *
from decks.test_decklists import *
from datetime import datetime
import sys
import inspect
import time
from datetime import datetime
def print_classes():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            print(obj)

for _ in range(100):
    g=MTG_Game(Bob, Jim, verbose=2,stop_at_end=False) #logged=True,seed=123
    g.play_game()
