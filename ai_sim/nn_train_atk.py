# training computer to play a game with two decks of bears
import sys
sys.path.append("..")
import numpy as np
import pickle
import datetime
from copy import copy
from copy import deepcopy
from Game import *
from cards.M20_cards import *
from nn_input_logic import *


nn_logic=NN_Logic()
nn_logic.load_train_data(labels=['attackers'])
start=datetime.datetime.now()
nn_logic.train_bool(label='attackers',epochs=1000)
pickle.dump( nn_logic.models['attackers'], open( "models/nn_model_attackers.p", "wb" ) )
print(datetime.datetime.now()-start, 'elapsed')
