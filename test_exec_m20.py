
from Game import *
from decks.test_m20_decks import *
from datetime import datetime
import sys
import inspect
import time
from datetime import datetime

gs=MTG_Game_Set(playerA=Bob,playerB=Jim)
gs.execute_game_set(1000,playerA=Bob,playerB=Jim,verbose=3,stop_at_end=False)
