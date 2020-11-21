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
from data_collector import *
import dill
import multiprocessing

if __name__ == '__main__':
    # set up the decks
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    decks = dill.load(open( "pickles/rand_decks.p", "rb" ))

    # load logic
    nn_logic=NN_Logic()
    #nn_logic.load_board_analyzer('models/nn_model_gamestate.p')
    dc=DataCollector(model=nn_logic, gather_data_types=['game_state'])

    Rand=Player("Rand", ignore_pass=False)
    Robo=Player("Robo", ignore_pass=False)
    Robo.assign_data_collector(dc)

    gs=MTG_Game_Set(playerA=Rand,playerB=Robo,decks=decks, end_of_set_stop=False)
    gs.execute_game_set(2, playerA=Rand,playerB=Robo,verbose=2,stop_at_end=False,
        multicore=False,gpu=False,data_collector=nn_logic.data_collector, give_random_decks=True,
        dcollect_points=['game_state','attackers','spells_cast','winner','runtime'], export_check_points=100)
    nn_logic.export_results()
