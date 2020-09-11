import sys
sys.path.append("..")
from cards.M20_cards import *
from Player import *
import pandas as pd
import copy
import itertools
import collections
import pickle
import dill
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
all_colors=['W','U','B','R','G']

decks=[]
for _ in range(100):
    print(_)
    # pick three colors and generate deck of cards
    # cards key is alpha sorted, so we'll alpha sort colors here too
    # making some code easily editable for different num of colors. starting with trips
    num_colors = 3
    #color_select = [tuple(sorted(i)) for i in itertools.combinations(colors,num_colors) if 'G' in i and 'U' in i and 'B' in i]
    color_select = [tuple(sorted(i)) for i in itertools.combinations(all_colors,num_colors)]
    color_select = random.sample(color_select, 1)
    deckA_cols = color_select
    # if 2 or more colors, add subsets within selected color combo (pairs in triple,
    # single color in pair, etc.)
    for n in range(num_colors-1,0,-1):
        color_sub = [tuple(sorted(i)) for i in itertools.combinations(color_select[0],n)]
        deckA_cols = deckA_cols + color_sub

    print(deckA_cols)

    # first add cards to pool
    pool = []
    for c in deckA_cols:
        if c in cards.keys():
            for name in cards[c]:
                pool.append(name)

    # then sample w replacement from pool
    deck = random.choices(pool,k=22)
    deck = [eval(i) for i in deck]
    # next, determine basic lands to add to the deck
    basic_lands={
        'W':'Plains',
        'U':'Island',
        'B':'Swamp',
        'R':'Mountain',
        'G':'Forest'
    }

    # count number cards of each color
    colors = [i.colors for i in deck]
    colors = [i for j in colors for i in j if i!='C']
    color_counts= collections.Counter(colors)

    # multiply by 18/22 to get number of lands
    land_counts={}
    for c in color_counts.keys():
        land_counts[c]= round(18/22 * color_counts[c])
    # in case rounding doesn't give us 18 lands, just remove/add randomly to get there
    num_lands = sum([i for i in land_counts.values()])
    if num_lands > 18:
        while num_lands > 18:
            land_counts[random.choice(list(land_counts.keys()))] -=1
            num_lands = sum([i for i in land_counts.values()])
    if num_lands < 18:
        while num_lands < 18:
            land_counts[random.choice(list(land_counts.keys()))] +=1
            num_lands = sum([i for i in land_counts.values()])

    for c in land_counts.keys():
        for _ in range(land_counts[c]):
            deck.append(eval(basic_lands[c]))
    decks.append(deck)

dill.dump( decks, open( "pickles/rand_decks.p", "wb" ) )
