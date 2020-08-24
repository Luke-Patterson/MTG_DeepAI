import sys
sys.path.append("..")
from cards.test_cards import *
from Player import *
import copy

deckA=  [copy.deepcopy(Grizzly_Bears) for i in range(5)] + \
        [copy.deepcopy(Hill_Giant) for i in range(6)] + \
        [copy.deepcopy(Lightning_Bolt) for i in range(6)] + \
        [copy.deepcopy(Goblin_Firechucker) for i in range(6)] + \
        [copy.deepcopy(Leonin_Scimtar) for i in range(8)] + \
        [copy.deepcopy(Mountain) for i in range(10)] + \
        [copy.deepcopy(Forest) for i in range(10)]
deckB=  [copy.deepcopy(Horned_Turtle) for i in range(5)] + \
        [copy.deepcopy(Grizzly_Bears) for i in range(6)] + \
        [copy.deepcopy(Gaeas_Anthem) for i in range(6)] + \
        [copy.deepcopy(Jace_Beleren) for i in range(6)] + \
        [copy.deepcopy(Leonin_Scimtar) for i in range(8)] + \
        [copy.deepcopy(Island) for i in range(10)] + \
        [copy.deepcopy(Forest) for i in range(10)]

Bob=Player("Bob", deckA)
Jim=Player("Jim", deckB)

#
