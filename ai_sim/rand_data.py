# training computer to play a game with two decks of bears
import sys
sys.path.append("..")
import numpy as np
import pickle
from copy import copy
from copy import deepcopy
from Game import *
from cards.M20_cards import *
from nn_input_logic import *
import dill
import multiprocessing

if __name__ == '__main__':
    # set up the decks
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    decks = dill.load(open( "pickles/rand_decks.p", "rb" ))
    nn_logic=NN_Logic(gather_data_types=['game_state','attackers'])

    Rand=Player("Rand", ignore_pass=False)
    Robo=Player("Robo", nn_logic, ignore_pass=False)

    gs=MTG_Game_Set(playerA=Rand,playerB=Robo,decks=decks, end_of_set_stop=False)
    gs.execute_game_set(100, playerA=Rand,playerB=Robo,verbose=0,stop_at_end=False,
        multicore=False,data_collector=nn_logic, give_random_decks=True,
        dcollect_points=['game_state','attackers','spells_cast','winner','runtime'])
    nn_logic.export_results()
    import pdb; pdb.set_trace()
