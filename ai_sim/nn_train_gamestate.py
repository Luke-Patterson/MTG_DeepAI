# training computer to play a game with two decks of bears
import sys
sys.path.append("..")
import numpy as np
import pickle
import datetime
import scipy
from copy import copy
from copy import deepcopy
from Game import *
from cards.M20_cards import *
from nn_input_logic import *


nn_logic=NN_Logic()
nn_logic.load_train_data(labels=['game_state'])
start=datetime.datetime.now()
nn_logic.train_bool(label='game_state',epochs=1000)
nn_logic.save_model('game_state')
print(datetime.datetime.now()-start, 'elapsed')
