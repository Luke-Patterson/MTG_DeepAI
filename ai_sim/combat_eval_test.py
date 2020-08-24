import os
import sys
sys.path.append("..")
from Game import *
from decks.test_m20_decks import *
import sys
from datetime import datetime
import inspect
import time
from datetime import datetime

gs=MTG_Game_Set(playerA=Bob,playerB=Jim)
gs.execute_game_set(100,playerA=Bob,playerB=Jim,verbose=3,stop_at_end=False,
    dcollect_points=['spells_cast','winner','runtime'],combat_eval=True)
