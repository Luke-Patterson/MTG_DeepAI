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
import os

# set up the decks
df=pd.read_csv('C:/Users/lsp52/AnacondaProjects/card_sim/cards/M20_index.csv')
white_cards=df.loc[df.colors.apply(lambda x: 'W' in x),'object_name']
blue_cards=df.loc[df.colors.apply(lambda x: 'U' in x),'object_name']
nn_logic=NN_Logic()
nn_logic.load_models(['attackers'])
nn_logic.test=True

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

Rand=Player("Rand", deckA, ignore_pass=False)
Robo=Player("Robo", deckB, nn_logic, ignore_pass=False)

for _ in range(1000):
    g=MTG_Game(Rand,Robo,verbose=2,stop_at_end=False, logged=True)
    g.play_game()
    print(nn_logic.game_log.value_counts())
