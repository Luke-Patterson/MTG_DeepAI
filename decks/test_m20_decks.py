import sys
sys.path.append("..")
from cards.M20_cards import *
from Player import *
import pandas as pd
import copy
import itertools
import random

# generate decks from randomly from colors
df=pd.read_csv('C:/Users/lsp52/AnacondaProjects/card_sim/cards/M20_index.csv')
# transform some columns into python objects we will need
df['colors']=df['colors'].apply(lambda x: eval(x))
df['types']=df['types'].apply(lambda x: eval(x))
df['potential_mana_values']=df['potential_mana_values'].apply(lambda x: eval(x))

# single color cards
cards={}
# multi colored cards
for n,card in df.iterrows():
    if tuple(card.colors) not in cards.keys():
        cards[tuple(card.colors)]=[card.object_name]
    else:
        cards[tuple(card.colors)].append(card.object_name)

# colorless non land cards
cards[('C')]=df.loc[(df.colors.apply(lambda x: 'C' in x)) &
    (df.types.apply(lambda x: 'land' not in x)),'object_name'].tolist()

# lands
lands = df.loc[df.types.apply(lambda x: 'land' in x and 'basic' not in x)]
for n,card in lands.iterrows():
    mana_produced = card.potential_mana_values
    mana_produced = tuple(list(i.keys())[0] for i in mana_produced)
    if mana_produced not in cards.keys():
        cards[mana_produced]=[card.object_name]
    else:
        cards[mana_produced].append(card.object_name)

basic_lands={
    ('W',):'Plains',
    ('U',):'Island',
    ('B',):'Swamp',
    ('R',):'Mountain',
    ('G',):'Forest'
}

# randomly pick colors for decks
colors=['W','U','B','R','G']

# cards key is alpha sorted, so we'll alpha sort colors here too
# making some code easily editable for different num of colors. starting with trips
num_colors = 3
color_select = [tuple(sorted(i)) for i in itertools.combinations(colors,num_colors)]
color_select = random.sample(color_select, 1)
deckA_cols = color_select
# if 2 or more colors, add subsets within selected color combo (pairs in triple,
# single color in pair, etc.)
for n in range(num_colors-1,0,-1):
    color_sub = [tuple(sorted(i)) for i in itertools.combinations(color_select[0],n)]
    deckA_cols = deckA_cols + color_sub

# first add cards to the deck
deckA = []
for c in deckA_cols:
    if c in cards.keys():
        for name in cards[c]:
            deckA+=[copy.deepcopy(eval(name)) for _ in range(1)]

# then add lands
num_lands=round(len(deckA) / 3)
single_colors = [i for i in deckA_cols if len(i)==1]
for c in single_colors:
    deckA+=[copy.deepcopy(eval(basic_lands[c])) for _ in range(num_lands)]

# Repeat for second deck
# making some code easily editable for different num of colors. starting with trips
num_colors = 3
color_select = [tuple(sorted(i)) for i in itertools.combinations(colors,num_colors)]
color_select = random.sample(color_select, 1)
deckB_cols = color_select
# if 2 or more colors, add subsets within selected color combo (pairs in triple,
# single color in pair, etc.)
for n in range(num_colors-1,0,-1):
    color_sub = [tuple(sorted(i)) for i in itertools.combinations(color_select[0],n)]
    deckB_cols = deckB_cols + color_sub

# first add cards to the deck
deckB = []
for c in deckB_cols:
    if c in cards.keys():
        for name in cards[c]:
            deckB+=[copy.deepcopy(eval(name)) for _ in range(1)]

# then add lands
num_lands=round(len(deckB) / 3)
single_colors = [i for i in deckB_cols if len(i)==1]
for c in single_colors:
    deckB+=[copy.deepcopy(eval(basic_lands[c])) for _ in range(num_lands)]

#
# deckA=  [copy.deepcopy(Leafkin_Druid) for i in range(20)] + \
#         [copy.deepcopy(Leyline_of_Abundance) for i in range(20)] + \
#         [copy.deepcopy(Forest) for i in range(20)]
# deckB=  [copy.deepcopy(Leafkin_Druid) for i in range(20)] + \
#         [copy.deepcopy(Leyline_of_Abundance) for i in range(20)] + \
#         [copy.deepcopy(Forest) for i in range(20)]

Bob=Player("Bob", deckA)
Jim=Player("Jim", deckB)
