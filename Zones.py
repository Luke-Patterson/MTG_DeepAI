# define zones
from copy import deepcopy
from Abilities_Effects import *
from Card_types import *
import random
# zone of a player
class Zone(list):
    def __init__(self,owner=None):
        self.owner=owner
        self.game=None
        self.glob_effects=[]

    # add so that whenever an object is added to zone, we check global effects
    def enter_zone(self,item,pos=None):
        # pos- if position matters (mostly just for libraries)
        if pos==None:
            super().append(item)
        else:
            super().insert(pos,item)
        if isinstance(item, Card):
            item.zone=self
            item.zone_turn=self.game.turn_id

            # add a zone hash to keep track of if it has moved zones
            new_hash=random.getrandbits(128)
            while new_hash==item.zone_hash:
                new_hash=random.getrandbits(128)
            item.zone_hash=new_hash

    # likewise, when we remove an object, we are removing global effects
    def leave_zone(self,item):
        super().remove(item)
        item.prev_zone=self

# Define different zones

# Stack
class Stack(Zone):
    def __init__(self,game):
        Zone.__init__(self)
        self.game=game
        self.zone_type='stack'
        super()

    def enter_zone(self,item,pos=None):
        # pos- if position matters (mostly just for libraries)
        if pos==None:
            super().append(item)
        else:
            super().insert(pos,item)
        item.zone=self
        item.zone_turn=self.game.turn_id

        # add a zone hash to keep track of if it has moved zones
        new_hash=random.getrandbits(128)
        while new_hash==item.zone_hash:
            new_hash=random.getrandbits(128)
        item.zone_hash=new_hash

# battlefield
class Battlefield(Zone):
    def __init__(self,owner):
        Zone.__init__(self,owner)
        self.zone_type='field'

    # add so that whenever an object is added to zone, we check global effects
    def enter_zone(self,item,pos=None,enter_effects=True, tapped=False):
        super().enter_zone(item,pos)
        self.apply_glob_effects(item)
        # mostly will trigger enter effects, but a few corner cases don't,
        # like switching control of an objec
        if item.check_keyword('haste'):
            item.summoning_sick=False
        else:
            item.summoning_sick=True
        if enter_effects:
            item.enter_zone_effects('field')
        item.tapped=tapped

    # likewise, when we remove an object, we are removing global effects
    def leave_zone(self,item, leave_effects=True):
        # detach auras, equipment, and counters
        if leave_effects:
            for i in item.attached_objs:
                i.detach_from()
        super().leave_zone(item)
        # remove global effects
        self.remove_glob_effects(item)
        # mostly will trigger enter effects, but a few corner cases don't,
        # like switching control of an object
        if leave_effects:
            item.leave_zone_effects('field')
            if item.copying!=None:
                item.revert_copy()

    def apply_glob_effects(self,card):
        for effect in self.glob_effects:
            effect.apply_to_card(card)

    def remove_glob_effects(self,card):
        for effect in card.applied_effects:
            if isinstance(effect,Glob_Static_Effect):
                effect.remove_from_card(card)

# graveyard
class Graveyard(Zone):
    def __init__(self,owner):
        Zone.__init__(self,owner)
        super()
        self.zone_type='yard'

    # add so that whenever an object is added to zone, we check global effects
    def enter_zone(self,item,pos=None):
        if 'to_graveyard_from_anywhere' in self.game.replace_points:
            self.game.check_replace_effects('to_graveyard_from_anywhere',effect_kwargs={'obj':item},
                condition_kwargs={'obj':item})

        if 'token' not in item.types:
            super().enter_zone(item,pos)
            item.enter_zone_effects('yard')

        self.owner.game.triggers('to_graveyard_from_anywhere', obj = item)
        if item.prev_zone.zone_type=='field':
            self.owner.game.triggers('to_graveyard_from_field', obj = item)

        if 'token' in item.types:
            del item

    # likewise, when we remove an object, we are removing global effects
    def leave_zone(self,item):
        super().leave_zone(item)
        item.leave_zone_effects('yard')

# library
class Library(Zone):
    def __init__(self,owner):
        Zone.__init__(self,owner)
        super()
        self.zone_type='lib'

    # add so that whenever an object is added to zone, we check global effects
    def enter_zone(self,item,pos=None):
        if 'token' not in item.types:
            super().enter_zone(item,pos)
            item.enter_zone_effects('lib')
        if 'token' in item.types:
            del item

    # likewise, when we remove an object, we are removing global effects
    def leave_zone(self,item):
        super().leave_zone(item)
        item.leave_zone_effects('lib')

    def load_deck(self, deck):
        for card in deck:
            clone=deepcopy(card)
            clone.assign_ownership(self.owner)
            clone.assign_sources()
            self.enter_zone(clone)

class Sideboard(Zone):
    def __init__(self,owner):
        Zone.__init__(self,owner)
        super()
        self.zone_type='sideboard'

    # add so that whenever an object is added to zone, we check global effects
    def enter_zone(self,item,pos=None):
        if 'token' not in item.types:
            super().enter_zone(item,pos)
            item.enter_zone_effects('sideboard')
        if 'token' in item.types:
            del item

    # likewise, when we remove an object, we are removing global effects
    def leave_zone(self,item):
        super().leave_zone(item)
        item.leave_zone_effects('sideboard')

    def load_sideboard(self, sideboard):
        for card in sideboard:
            clone=deepcopy(card)
            clone.assign_ownership(self.owner)
            clone.assign_sources()
            self.enter_zone(clone)

# Exile
class Exile(Zone):
    def __init__(self,owner):
        Zone.__init__(self,owner)
        super()
        self.zone_type='exile'

    # add so that whenever an object is added to zone, we check global effects
    def enter_zone(self,item,pos=None):
        if 'token' not in item.types:
            super().enter_zone(item,pos)
            item.enter_zone_effects('exile')
        if 'token' in item.types:
            del item

    # likewise, when we remove an object, we are removing global effects
    def leave_zone(self,item):
        super().leave_zone(item)
        item.leave_zone_effects('exile')

# Hand
class Hand(Zone):
    def __init__(self,owner):
        Zone.__init__(self,owner)
        super()
        self.zone_type='hand'

    # add so that whenever an object is added to zone, we check global effects
    def enter_zone(self,item,pos=None):
        if 'token' not in item.types:
            super().enter_zone(item,pos)
            item.enter_zone_effects('hand')
        if 'token' in item.types:
            del item

    # likewise, when we remove an object, we are removing global effects
    def leave_zone(self,item):
        super().leave_zone(item)
        item.leave_zone_effects('hand')
