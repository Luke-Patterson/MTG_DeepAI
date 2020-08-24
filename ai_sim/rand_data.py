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
import multiprocessing

if __name__ == '__main__':
    # set up the decks
    # generate decks from all white/blue cards
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    df=pd.read_csv('C:/Users/lsp52/AnacondaProjects/card_sim/cards/M20_index.csv')
    white_cards=df.loc[df.colors.apply(lambda x: 'W' in x),'object_name']
    blue_cards=df.loc[df.colors.apply(lambda x: 'U' in x),'object_name']

    deckA=[]
    for name in white_cards:
        deckA+=[copy.deepcopy(eval(name)) for _ in range(1)]
    num_lands=len(deckA)
    deckA+=[copy.deepcopy(Plains) for _ in range(num_lands)]
    for name in blue_cards:
        deckA+=[copy.deepcopy(eval(name)) for _ in range(1)]
    deckA+=[copy.deepcopy(Island) for _ in range(num_lands)]

    deckB=[]
    for name in white_cards:
        deckB+=[copy.deepcopy(eval(name)) for _ in range(1)]
    num_lands=len(deckB)
    deckB+=[copy.deepcopy(Plains) for _ in range(num_lands)]
    for name in blue_cards:
        deckB+=[copy.deepcopy(eval(name)) for _ in range(1)]
    deckB+=[copy.deepcopy(Island) for _ in range(num_lands)]

    nn_logic=NN_Logic(gather_data_types=['game_state','attackers'])

    Rand=Player("Rand", deckA, ignore_pass=False)
    Robo=Player("Robo", deckB, nn_logic, ignore_pass=False)
    # Robo=Player("Robo", deckB, nn_logic)

    gs=MTG_Game_Set(playerA=Rand,playerB=Robo, end_of_set_stop=False)
    gs.execute_game_set(10000, playerA=Rand,playerB=Robo,verbose=0,stop_at_end=False,
        multicore=True,data_collector=nn_logic)
    nn_logic.export_results()
