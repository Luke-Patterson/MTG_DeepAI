# define class of players
import random
import numpy as np
import pandas as pd
import time
import inspect
import sys
from itertools import combinations
from itertools import permutations
from itertools import product
from collections import Counter
from Exceptions import *
#from Cards import *
from Card_types import *
from Abilities_Effects import *
from Zones import *
from copy import deepcopy
from collections import Counter
from ai_sim.combat_logic import Combat_Logic

class Player:
    def __init__(self, name, deck, sideboard=[], logic=None, mana_shorthand=False,ignore_pass=True):
        self.name=name
        self.deck=deck
        self.game=None
        self.owner=self
        self.controller=self
        # assign deck
        self.lib=Library(self)
        self.deck=deck
        # sb -> list of sideboard cards
        self.sb=sideboard
        # sideboard -> sideboard zone
        self.sideboard=Sideboard(self)
        # starting game characteristics
        self.combat_logic=Combat_Logic(player=self)

        self.life=20
        self.hand=Hand(self)
        self.yard=Graveyard(self)
        self.field=Battlefield(self)
        self.exile=Exile(self)
        self.zones=[self.lib,self.hand,self.yard,self.field,self.exile]
        self.opponent=None
        self.mana_pool={"C":0, "W":0, "U":0, "B":0, "R":0, "G":0}
        # whether to use shorthand method for quickly excluding possible plays
        # shorthand is count up untapped mana sources, and exclude those with
        # CMC > untapped sources
        self.mana_shorthand=mana_shorthand
        self.land_drops=1
        self.lose_game=False
        self.Pass=False
        self.max_hand_size=7
        self.counters=[]
        # list of available activated abilities
        self.yard_abil=[]
        self.hand_abil=[]
        self.field_abil=[]
        # decision making
        self.logic=logic
        if logic!=None:
            self.logic.plyr=self
        # place to store hexproof and other (?) player-level abils
        self.keyword_static_abils=[]
        # keywords to expire at end of turn
        self.EOT_keywords=[]
        # other EOT effects to reverse
        self.EOT_reverse_effects=[]
        # place to store triggered_abils granted to a player
        self.triggered_abils=[]
        # place to store applied effects to players
        self.applied_effects=[]
        # logic assignment
        if logic != None:
            self.logic.plyr=self
        # whether to consider passing as an option or not
        self.ignore_pass=ignore_pass
        # temporary storage for player-level decisions
        self.target=None
        # place to store a cost
        self.cost_to_pay={"C":0, "W":0, "U":0, "B":0, "R":0, "G":0}
        # objects to track potential mana permutations, and whether it pays the cost
        self.potential_mana=[]
        self.potential_mana_permutes=[]
        self.pmana_can_pay=[]
        # type recognition as a player
        self.types=['player']
        # spell count/colors in turn
        self.turn_spell_count=0
        self.turn_spell_colors=[]
        # life lost this turn
        self.life_lost_this_turn=0
        # limit on number of spells player can cast in a turn
        self.spell_cap=[]
        # list to store cost modification objects
        self.cost_mods=[]
        # dataframe of revealed private info to store
        self.known_info=pd.DataFrame()
        # zones with known info not usually known
        self.known_zones=[]
        # emblems
        self.emblems=[]
        # protection effects
        self.protection_effects=[]
        # track misc clean up effects
        self.EOT_effects_cleanup={'objs':[],'effects':[]}
        # trigger to check graveyard for castable spells
        self.check_yard_for_cast=False
        self.check_exile_for_cast=False
        # trigger for checking if top of lib can be cast
        self.top_lib_cast_condition=[]

    #==========================================================================
    # Game Procedure Functions
    #==========================================================================

    # enter the game
    def enter_game(self, game):
        self.game=game
        self.verbose=self.game.verbose
        for i in self.zones:
            i.game=game
        self.check_yard_for_cast=False
        self.check_exile_for_cast=False

    # reset self for in between games
    def reset_self(self):
        self.__init__(name=self.name,deck=self.deck,sideboard=self.sb,logic=self.logic)

    # shuffle library
    def shuffle_lib(self):
        return(random.shuffle(self.lib))

    # mulligan at beginning of game
    def take_mulligans(self):
        hand_num=7
        open_keep=self.input_bool(label="mulligan")
        while hand_num>0 and open_keep==False:
            hand_num-=1
            for i in self.hand:
                self.hand.leave_zone(i)
                self.lib.enter_zone(i)
            self.shuffle_lib()
            self.draw_card(num=hand_num)
            open_keep=self.input_bool(label="mulligan")
            if self.game.verbose>=2:
                print(self,'mulligans to',hand_num)

    # draw card
    def draw_card(self, num=1):
        for i in range(num):
            if len(self.lib)<1:
                self.lose_game=True
                self.game.end_game(self,'Player drew from empty deck')
            top_card=self.lib[0]
            self.lib.leave_zone(top_card)
            self.hand.enter_zone(top_card)
        if self.game.verbose>=2:
            print(self,'draws',num,'card')

    # scrying
    def scry(self,num):
        top=[]
        bottom=[]
        for i in self.lib[0:num]:
            # decide whether to put the card on the bottom of the lib
            keep=self.input_bool(label='scry')
            if keep:
                top.append(i)
            else:
                bottom.append(i)
        # order the cards put on top and bottom
        top=self.input_order(top,label='scry_top')
        bottom=self.input_order(bottom,label='scry_bottom')
        for i in top:
            self.lib.remove(i)
            self.lib.insert(0, i)
        for i in bottom:
            self.lib.remove(i)
            self.lib.insert(-1, i)

    def mill_card(self,num=1):
        for i in range(num):
            if len(self.lib)<1:
                self.yard.append(self.lib.pop())
        if self.game.verbose>=2:
            print(self,'mills',num,'card')

    def sacrifice_permanent(self, types=[], subtypes=[], num=1):
        if types!=[]:
            perms=[i for i in self.field if any([j in i.types for j in types])]
        else:
            perms =[i for i in self.field]
        if subtypes!=[]:
            perms=[i for i in perms if any([j in i.subtypes for j in subtypes])]
        chosen=self.input_choose(perms, n=num)
        if num>1:
            for i in chosen:
                i.sacrifice()
        else:
            chosen.sacrifice()

    def pay_life(self, num):
        self.change_life(-1*num, dealing_damage=False)

    def change_life(self,num, dealing_damage=True, combat=False):
        # if positive life change, then set combat and damge indicator = False
        if num>0:
            dealing_damage=False
            combat=False
        # first check replacement effects
        # store num as attribute for the sake of modifiying with replace effects
        self.life_chg_num=num
        if num>0:
            if 'lifegain' in self.game.replace_points:
                self.game.check_replace_effects('lifegain',effect_kwargs={'player':self,
                    'num':num},condition_kwargs={'player':self,
                        'num':num})
        # apply life change
        self.life+=self.life_chg_num
        num=self.life_chg_num
        if num>0:
            self.game.triggers('lifegain',player=self,num=num)
            if self.game.verbose>=2:
                print(self,'gains',num,'life')
        if num<0:
            self.game.triggers('lifeloss',player=self,num=num,dealing_damage=dealing_damage,
                combat=combat)
            self.life_lost_this_turn-=num
            if self.game.verbose>=2:
                print(self,'loses',num*-1,'life')

    def take_damage(self,num,source,deathtouch=False, combat=True):
        protect=False
        for j in self.protection_effects:
            if j.hexproof_from==False and j.check_protect(source):
                protect=True
                if self.controller.game.verbose>=2:
                    print(self, 'prevented damage from',source,'due to protection',
                    inspect.getsource(i.condition))
                break
        if protect==False:
            if self.check_keyword('lifelink') and num>0:
                source.controller.change_life(num)
            if combat and num>0:
                source.controller.game.triggers('combat damage dealt',
                    source=source, receiver=self, num=num)
            self.change_life(-1*num)

    # create a token
    def create_token(self,token, is_attacking=False, is_tapped=False):
        token.assign_ownership(self)
        token.assign_sources()
        token.summoning_sick=True
        token.controller=self
        token.owner=self
        self.field.enter_zone(token)
        if is_tapped:
            token.tap(for_cost=False)
        if is_attacking:
            atk_targets=[self.opponent]
            for i in self.opponent.field:
                if 'planeswalker' in i.types:
                    atk_targets.append(i)
            self.attacking=True
            self.atk_target=self.input_choose(atk_targets, label='attack target')

    # search library
    def search_library(self,elig_condition, select_effect, select_num=1,shuffle=True):
        cands=[i for i in self.lib if elig_condition(i)]
        if cands==[]:
            if self.game.verbose>=2:
                print('No cards found')
            selected=None
        else:
            selected=self.input_choose(cands,n=select_num)
            if isinstance(selected, list):
                if self.game.verbose>=2:
                    print('selected', selected, 'cards')
                for i in selected:
                    select_effect(i)
            else:
                if self.game.verbose>=2:
                    print('selected', selected, 'card')
                select_effect(selected)
        if shuffle:
            self.shuffle_lib()
        return(selected)

    # select cards from top of library
    def select_top_lib(self,n_cards,n_selected, non_select_func):

        # get top n cards from deck, or entire deck if cards left <= n
        if len(self.lib)>n_cards:
            cards=self.lib[0:n_cards]
        else:
            cards=self.lib

        if len(cards) != 0:
            # select n cards from them
            selected = self.input_choose(cards, n=n_selected, label='select cards')
            if isinstance(selected, list)==False:
                selected=[selected]

            # do something with the non-selected based on non_select_func
            non_selected=[i for i in cards if i not in selected]
            if non_select_func=='bottom of lib, choose order':
                # order of non_selected is [card1,card2,...,card_n] <- bottom of library
                non_selected=self.input_order(non_selected, label='non-selected order')
                for i in non_selected:
                    self.lib.remove(i)
                    self.lib.append(i)

            if non_select_func=='bottom of lib, random order':
                random.shuffle(non_selected)
                for i in non_selected:
                    self.lib.remove(i)
                    self.lib.append(i)
            return(selected)

    # function to untap a player's permanents and reset turn counters
    def untap_for_turn(self):
        self.land_drops=1
        for i in self.field:
            if 'stop_untap' not in i.keyword_static_abils and \
                'stop_next_untap' not in i.keyword_static_abils:
                i.untap()
            elif self.game.verbose>=2 and i.tapped:
                print(i, 'does not untap during untap step')

            # remove instances of stopping untap in next untap step
            if 'stop_next_untap' in i.keyword_static_abils:
                i.keyword_static_abils= [j for j in i.keyword_static_abils if
                    j!='stop_next_untap']

            i.summoning_sick=False

        if self.game.verbose>=2:
            print(self,'untaps for turn')

    # Choose a play, then pay costs and play the card/ability
    def make_play(self, flash):
        # get legal moves while having priority
        land_moves=[]
        abil_moves=[]
        spell_moves=[]

        # add playing lands to possible moves
        if flash==False and self.land_drops>0:
            for i in self.hand:
                if 'land' in i.types:
                    land_moves.append(i)

            if self.check_yard_for_cast:
                for i in self.yard:
                    if 'land' in i.types and i.check_keyword('cast_from_yard'):
                        land_moves.append(i)

            if self.check_exile_for_cast:
                for i in self.exile:
                    if 'land' in i.types and i.check_keyword('cast_from_exile'):
                        land_moves.append(i)

            if self.top_lib_cast_condition!=[]:
                if 'land' in i.types and any([f(i) for f in self.top_lib_cast_condition]):
                    land_moves.append(i)

        # Add playing spells (first checking to see if there's any spell cap
        # imposed on player)
        if self.spell_cap==[] or min(self.spell_cap)>self.turn_spell_count:
            if flash==False:
                for spell in self.hand:
                    if not 'land' in spell.types and spell.legal_req_tar_cho_costs():
                        spell_moves.append(spell)
            if flash==True:
                for spell in self.hand:
                    if spell.flash==True:
                        if not 'land' in spell.types and spell.legal_req_tar_cho_costs():
                            spell_moves.append(spell)

        # if check_yard_for_cast enabled, also check your yard for spells
        if self.check_yard_for_cast:
            if self.spell_cap==[] or min(self.spell_cap)>self.turn_spell_count:
                if flash==False:
                    for spell in self.yard:
                        if spell.check_keyword('cast_from_yard') and 'land' not in spell.types and spell.legal_req_tar_cho_costs():
                            spell_moves.append(spell)
                if flash==True:
                    for spell in self.yard:
                        if spell.flash==True:
                            if spell.check_keyword('cast_from_yard') and not 'land' in spell.types and spell.legal_req_tar_cho_costs():
                                spell_moves.append(spell)

        # if check_exile_for_cast enabled, also check your yard for spells
        if self.check_exile_for_cast:
            if self.spell_cap==[] or min(self.spell_cap)>self.turn_spell_count:
                if flash==False:
                    for spell in self.exile:
                        if spell.check_keyword('cast_from_exile') and 'land' not in spell.types and spell.legal_req_tar_cho_costs():
                            spell_moves.append(spell)
                if flash==True:
                    for spell in self.exile:
                        if spell.flash==True:
                            if spell.check_keyword('cast_from_exile') and not 'land' in spell.types and spell.legal_req_tar_cho_costs():
                                spell_moves.append(spell)

        # if check_exile_for_cast enabled, also check your yard for spells
        if self.top_lib_cast_condition!= None:
            if self.spell_cap==[] or min(self.spell_cap)>self.turn_spell_count:
                if flash==False:
                    spell = self.lib[0]
                    if any([f(spell) for f in self.top_lib_cast_condition]) and 'land' not in spell.types and spell.legal_req_tar_cho_costs():
                        spell_moves.append(spell)
                if flash==True:
                    spell = self.lib[0]
                    if spell.flash==True:
                        if any([f(spell) for f in self.top_lib_cast_condition]) and not 'land' in spell.types and spell.legal_req_tar_cho_costs():
                            spell_moves.append(spell)


        # add playing abilities
        for obj in self.field:
            for abil in obj.activated_abils:
                if abil.mana_abil==False and 'field' in abil.active_zones:
                    if ((flash==False & abil.flash==False) | abil.flash==True) and \
                        abil.legal_req_tar_cho_costs():
                            abil_moves.append(abil)

        # check for any activated abilities on cards in graveyard
        for obj in self.yard:
            for abil in obj.activated_abils:
                if 'yard' in abil.active_zones:
                    if ((flash==False & abil.flash==False) | abil.flash==True) and \
                        abil.legal_req_tar_cho_costs():
                            abil_moves.append(abil)

        moves=[land_moves, spell_moves, abil_moves]

        # flatten
        moves=[x for y in moves for x in y]

        # doing nothing as an option
        # ignore pass if we want to always make a move if possible during main phase
        if self.ignore_pass==False or flash==True:
            moves.append('Pass')
        else:
            if moves==[]:
                moves.append('Pass')

        play=self.input_choose(moves,label='make play')
        # play selected spell/activate selected ability
        if isinstance(play, Activated_Ability):
            if self.game.verbose>=1:
                print(self, 'Activating', play)
            play.activate_ability()
            self.Pass=False
        elif play=='Pass':
            if self.game.verbose>=2:
                print(self, 'Passes')
            self.Pass=True
        else:
            play.play_card()
            if 'spells_cast' in self.game.dcollect_points:
                self.game.dcollect['spells_cast'][self][play.name]+=1
            if self.game.verbose>=1:
                play.play_msg()
            self.Pass=False

    # process of discarding cards
    def discard_cards(self, num_discard):
        # if equal to or greater than hand size, discard everything
        if num_discard>=len(self.hand):
            for i in self.hand:
                i.discard_from_hand()
        else:
            discard_choices=self.input_choose(self.hand,label='discarding',n=num_discard)
            if isinstance(discard_choices,list):
                for i in discard_choices:
                    i.discard_from_hand()
            else:
                discard_choices.discard_from_hand()

    def discard_hand(self):
        self.discard_cards(num_discard = len(self.hand))

    # has certain number of cards in hand, defaults to any cards
    def has_cards_in_hand(self,num=1):
        return(len(self.hand)>=num)
    # looting
    def loot(self, num_draw=1, num_discard=1):
        self.draw_card(num_draw)
        self.discard_cards(num_discard)

    # End of turn discarding down to max hand size
    def EOT_discard(self):
        if len(self.hand)>self.max_hand_size:
            num_discard=len(self.hand)-self.max_hand_size
            self.discard_cards(num_discard)

    # check for keyword
    def check_keyword(self, keyword):
        result = keyword in self.keyword_static_abils and \
            'loses_'+keyword not in self.keyword_static_abils
        # if both are present, then whichever was applied last dominates
        if keyword in self.keyword_static_abils and 'loses_'+keyword in \
            self.keyword_static_abils:
            kword_idx= len(self.keyword_static_abils) - list_of_elems[::-1].index(keyword) - 1
            loses_idx= len(self.keyword_static_abils) - list_of_elems[::-1].index('loses_'+keyword) - 1
            if kword_idx > loses_idx:
                result=True
            else:
                result=False
        return(result)

    # add keyword
    def add_keyword(self, keyword):
        self.keyword_static_abils.append(keyword)

    # remove keyword if present
    def remove_keyword(self, keyword):
        if keyword in self.keyword_static_abils:
            self.keyword_static_abils.remove(keyword)
        elif self.game.verbose>=2:
            print('Warning:', keyword, 'not in', self, 'keyword_static_abils')

    # get legal targets for all objects that meet criteria
    def get_legal_targets(self,criteria= lambda source, obj: False,zones=['field'],
        players=None,own=True,opponent=True,source=None,different=False,self_target=True,
        stack=False):
        # zones - list of zones to check
        # criteria - a lambda function that takes an object as an input and returns
            # whether or not that object meets the criteria for a legal target
        # own - whether to check own zones
        # opponent - whether to check opponent zones
        # source - source of target for determining protection
        # different - if source has multiple targets and targets must be distinct
        # self_target - if source can target itself
        # stack - if source can target objects on stack
        legal_targets=[]
        # specify players
        if players==None:
            players=[]
        if players=='self':
            players=[self]
        if players=='opp':
            players=[self.opponent]
        if players=='both':
            players=[self, self.opponent]

        # for every type of zone in the zone list ...
        for zone in zones:
            # if own is true then check all objects in the zone
            if own:
                for i in self.__dict__[zone]:
                    # check the object against criteria
                    if criteria(source, i):
                        # check if object has shroud or hexproof
                        protect=False
                        if i.check_keyword('shroud') or \
                            (i.check_keyword('hexproof') and i.controller!=self):
                                protect=True
                        # check if object has protection
                        for j in i.protection_effects:
                            if j.check_protect(source):
                                protect=True
                        if protect==False:
                            # check if target has already been selected
                            if different==False or (different==True and i not in
                                source.get_targets(squeeze=False, check_illegal_targets=False)):
                                # check if target is self and self_target is false
                                if (self_target==False and i!=source) or self_target:
                                    legal_targets.append(i)
            # repeat for opponent's zone
            if opponent:
                for i in self.opponent.__dict__[zone]:
                    if criteria(source, i):
                        protect=False
                        if i.check_keyword('shroud') or (i.check_keyword('hexproof') \
                            and i.controller!=self):
                                protect=True
                        for j in i.protection_effects:
                            if j.check_protect(source):
                                protect=True
                        if protect==False:
                            if different==False or (different==True and i not in
                                source.get_targets(squeeze=False, check_illegal_targets=False)):
                                if (self_target==False and i!=source) or self_target:
                                    legal_targets.append(i)

        if stack:
            for i in self.game.stack:
                if criteria(source, i):
                    if different==False or (different==True and i not in
                        source.get_targets(squeeze=False, check_illegal_targets=False)):
                        if (self_target==False and i!=source) or self_target:
                            legal_targets.append(i)

        # add players that can be targeted
        for i in players:
            if (i.check_keyword('hexproof') and i==self.opponent) or \
                i.check_keyword('shroud'):
                legal_targets.append(i)

        return(legal_targets)

    # reveal cards to opponent
    def reveal_cards(self, cards, zone):
        for i in cards:
            self.opponent.known_info=self.opponent.known_info.append(
                pd.Series([i,zone]), ignore_index=True)

    #==========================================================================
    # Combat Functions
    #==========================================================================
    # declare attackers
    def declare_attackers(self):
        # get possible candidates for attackers
        atk_cand=[]
        atk_targets=[self.opponent]
        for i in self.opponent.field:
            if 'planeswalker' in i.types:
                atk_targets.append(i)
        for i in self.field:
            # TODO: making sure creatures that must attack do so
            if 'creature' in i.types and i.legal_attacker():
                atk_cand.append(i)
        # check for if there's creatures that can't attack alone
        if atk_cand!=[] and self.game.combat_eval:
            self.combat_logic.eval_attacks(atk_cand)
        attackers=[]
        alone_attackers=[]
        for i in atk_cand:
            make_atk=self.input_bool(label='make attack',obj=i)
            if make_atk:
                if 'no_atk_alone' in i.keyword_static_abils:
                    alone_attackers.append(i)
                else:
                    i.declare_as_attacker(atk_targets)
                    attackers.append(i)
        if len(alone_attackers)>=2 or len(attackers)>=1:
            for i in alone_attackers:
                i.declare_as_attacker(atk_targets)

    def declare_blockers(self):
        # get whose attacking
        attackers=[]
        for i in self.opponent.field:
            if 'creature' in i.types and i.attacking:
                attackers.append(i)
        # get possible candidates for blockers
        blck_cand=[]
        for i in self.field:
            if 'creature' in i.types and i.legal_blocker():
                blck_cand.append(i)

        # first, figure out menace attacker blocks
        menace_atkers=[i for i in attackers if i.check_keyword('menace')]
        attackers=[i for i in attackers if i not in menace_atkers]
        for atker in menace_atkers:
            legal_blockers=[]
            for blk in blck_cand:
                legal=blk.legal_block_pair(atker, other_blockers=[])
                if legal:
                    legal_blockers.append(blk)
            if len(legal_blockers)>=2:
                to_block = self.input_bool(label= 'double block menace attacker: ' + str(atker))
                if to_block:
                    num_block= self.input_choose([i for i in range(2, len(legal_blockers)+1)],
                        'num of blocks for menace attacker: ' + str(atker))
                    blockers = self.input_choose(legal_blockers, n=num_block, label=
                        'which blocker for menace attacker: ' + str(atker))
                    for i in blockers:
                        i.declare_as_blocker(atker)

        # for each candidate, get possible attackers it could block
        block_pairs=[]
        alone_blockers=[]
        for blocker in blck_cand:
            possible_blcks=[]
            for attacker in attackers:
                # first see if it's a legal block
                legal=blocker.legal_block_pair(attacker, [i[1:] for i in block_pairs if attacker in i])
                if legal:
                    possible_blcks.append(attacker)
            possible_blcks.append('None')
            # select blocker
            block_choice=self.input_choose(possible_blcks, label='choose blockers')
            if block_choice!='None':
                # if there's already a creature blocking it, append to that sublist
                if block_choice in [j[0] for j in block_pairs]:
                    idx=[i for i,j in enumerate(block_pairs) if j[0]==block_choice][0]
                    block_pairs[idx].append(blocker)

                # check if can't block alone
                elif i.check_keyword('no_blk_alone'):
                    alone_blockers.append([i,block_choice])

                # if not, add a new pair to block_pairs
                else:
                    block_pairs.append([block_choice,blocker])

            # finally, check for various restrictions on number of blockers
            #  "can't block alone"
            for i,block_choice in alone_blockers:
                if len(alone_blockers)>1 or len(block_pairs)!=0:
                    # add blockers
                    # if there's already a creature blocking it, append to that sublist
                    if block_choice in [j[0] for j in block_pairs]:
                        idx=[i for i,j in enumerate(block_pairs) if j[0]==block_choice][0]
                        block_pairs[idx].append(blocker)
                    else:
                        alone_blockers.append([i,block_choice])

        # execute the blocks
        for i in block_pairs:
            for j in i[1:]:
                j.declare_as_blocker(i[0])

        # for those with multiple blockers, attacker declares order of blocks
        for i in block_pairs:
            if len(i)>=3:
                i[1:]=self.opponent.input_order(i[1:], label='order blockers')

    def combat_cleanup(self):
        for i in self.field:
            if 'creature' in i.types:
                i.attacking=False
                i.blocking=False
                i.blocked=False
                i.is_blocking_attacker=None
    def get_attackers(self):
        return([i for i in self.field if 'creature' in i.types and i.attacking])
    def get_blockers(self):
        return([i for i in self.field if 'creature' in i.types and i.blocking])

    def EOT_cleanup(self):
        self.turn_spell_count=0
        self.turn_spell_colors=[]
        self.life_lost_this_turn=0
        if self.logic!=None and self.logic.gather_gamestate:
            self.logic.get_gamestate()

        # do clean up in other zones
        for obj, effect in zip(self.EOT_effects_cleanup['objs'],self.EOT_effects_cleanup['effects']):
            effect(obj)

        # remove temporary keywords granted
        for i in self.EOT_keywords:
            self.remove_keyword(i)
        self.EOT_keywords=[]

        # reverse applied effects
        for effect in self.EOT_reverse_effects:
            effect(self)
            self.EOT_reverse_effects.remove(effect)

    #==========================================================================
    # Making Mana Functions
    #==========================================================================
    # TODO: make mana filtering work under mana code
    # TODO: make multiple mana types/abilities work
    def reset_mana_pool(self):
        self.mana_pool={"C":0, "W":0, "U":0, "B":0, "R":0, "G":0}

    def add_mana(self, color, num=1):
        self.mana_pool[color] = self.mana_pool[color] + num

    def get_potential_mana(self,for_cost=None):
        # if there's any conditional mana in pool, check if it can be added to
        #self.potential_mana=deepcopy(self.mana_pool)
        # load all possible combinations of potential manas
        self.potential_mana=[]
        potential_mana_sets=[]
        for card in self.field:
            if card.potential_mana!=[]:
                potential_mana_sets.append(card.potential_mana)

        self.potential_mana_permutes=list(product(*potential_mana_sets))
        if len(self.potential_mana_permutes)>10000:
            print('warning: large number of potential mana permutations, disregarding treasure to bring combinations down')
            # if really large, try disregarding treasures
            potential_mana_sets=[]
            for card in self.field:
                if card.potential_mana!=[] and card.name!='Treasure':
                    potential_mana_sets.append(card.potential_mana)
            self.potential_mana_permutes=list(product(*potential_mana_sets))


        self.potential_mana_permutes=[list(i) for i in self.potential_mana_permutes]
        for n,p in enumerate(self.potential_mana_permutes):
            remove_p = []
            p_mana=deepcopy(self.mana_pool)
            for i in p:
                if i.check_condition():
                    if i.use_condition==None:
                        for key, val in i.mana.items():
                            p_mana[key]+=val
                    else:
                        if for_cost!=None and i.use_condition(for_cost):
                            for key, val in i.mana.items():
                                p_mana[key]+=val
                        # if we fail use condition, remove from abils used in
                        # this potential mana iteration
                        else:
                            remove_p.append(i)
                # if we fail check condition, remove from abils used in
                # this potential mana iteration
                else:
                    remove_p.append(i)
                # change potential mana permutation to only those who passed
                # check/use conditions
                p_mod = [i for i in p if i not in remove_p]
                self.potential_mana_permutes[n]= p_mod
            self.potential_mana.append(p_mana)

    def check_potential_mana(self,mana_cost):
        # check to see if we have enough colored mana
        self.pmana_can_pay=[]
        for p_mana in self.potential_mana:
            pay_cost=True
            for i in mana_cost.keys():
                if i!='C' and p_mana[i]<mana_cost[i]:
                    pay_cost=False
            # check to see if we have enough total mana
            if sum(mana_cost.values())>sum(p_mana.values()):
                pay_cost=False
            # also check that all permutations can be activated
            self.pmana_can_pay.append(pay_cost)
        return any(self.pmana_can_pay)

    # tap mana sources for a specific mana cost
    def tap_sources_for_cost(self,mana_cost,cost_object):
        # make a copy of the cost to keep track of source selection
        clone_cost=deepcopy(mana_cost)
        # make sure that pmana_can_pay is properly set to object
        self.get_potential_mana(cost_object.source)
        self.check_potential_mana(mana_cost)
        # reduce cost by whatever is currently in mana pool
        if sum(self.mana_pool.values())>0:
            for key in self.mana_pool.keys():
                if key in clone_cost.keys() and clone_cost[key]>0:
                    clone_cost[key]-=self.mana_pool[key]
                elif 'C' in clone_cost.keys() and clone_cost['C']>0:
                    clone_cost['C']-=self.mana_pool[key]

        # get all mana sources
        # if there are conditional mana sources, check for those
        sources=[i for i in self.field if i.mana_source and
            any([j.check_condition() for j in i.potential_mana])]
        sources=[i for i in sources if any([j.use_condition(cost_object.source)
            for j in i.potential_mana])]

        # get the permutations that can pay for the cost
        # after running get_potential_mana and check_potential_mana, we have three
        # attributes that can tell us this
        # self.potential_mana - the mana output of each permutation
        # self.pmana_can_pay - whether each permutation can pay for the cost
        # self.potential_mana_permutes - potential mana attributes corresponding to each permutation
        idx = [i for i,x in enumerate(self.pmana_can_pay) if x]
        valid_permutes= [self.potential_mana_permutes[i] for i in idx]

        # of the valid permutations, select one
        selected=self.input_choose(valid_permutes, label='select sources to pay with')
        # if any(['Gift of Paradise' in i.linked_abil.name for i in selected]):
        #     print(selected)
        # for each ability of selected permutation activate and reduce cost
        for pmana in selected:
            if pmana.source in sources:
                abil_activated=False
                for i in pmana.mana.keys():
                    if abil_activated==False:
                        # first try to pay a colored mana
                        if i in clone_cost.keys() and pmana.mana[i]>0 and clone_cost[i]>0:
                            clone_cost[i]-=pmana.mana[i]
                            pmana.linked_abil.activate_ability()
                            abil_activated=True
                        # next try to pay a colorless mana
                        elif 'C' in clone_cost.keys() and pmana.mana[i]>0 and clone_cost['C']>0:
                            clone_cost['C']-=pmana.mana[i]
                            pmana.linked_abil.activate_ability()
                            abil_activated=True

        # below can be removed, just checking in htis function that cost can be paid
        pool=deepcopy(self.mana_pool)
        self.pay_mana(mana_cost)
        self.mana_pool=pool

    # pay a cost with mana in pool
    def pay_mana(self,cost,partial=False):
        cost_to_pay=deepcopy(cost)
        # pay any colored mana first
        for i,j in self.mana_pool.items():
            if i !='C':
            # check if there's any mana left to pay with
                if j>0 and i in cost_to_pay.keys() and cost_to_pay[i]>0:
                    while cost_to_pay[i]>0 and self.mana_pool[i]>0:
                        self.mana_pool[i]-=1
                        cost_to_pay[i]-=1
        # pay for any colorless mana
        if 'C' in cost_to_pay.keys() and cost_to_pay['C']>0:
            # pay one colorless at a time
            while cost_to_pay['C']>0:
                # first identify possible ways to pay for it
                color_opts=[i for i,j in self.mana_pool.items() if j>0]
                if color_opts!=[]:
                    # then ask for input on which color to use
                    color_util=self.input_choose(color_opts)
                    # pay that type of mana
                    self.mana_pool[color_util]-=1
                    cost_to_pay['C']-=1
                else:
                    break
        if partial==False:
            # when considering permutations
            assert all(a==0 for a in cost_to_pay.values()),'%s mana cost not fully paid' %(cost_to_pay)




    #================= actions requiring player input==============
    # Yes/No input
    def input_bool(self,label=None,obj=None):
        decision=self.rand_decisions([True, False])
        if self.logic!=None:
            decision=self.logic.input_bool(player=self,obj=obj,decision=decision,label=label)
        return(decision)

    # choose from list
    def input_choose(self, choices, choose_color_cost=False,label=None, n=1,
        permit_empty_list=False, squeeze=True):
        if permit_empty_list and choices==[]:
            if self.game.verbose>=2:
                print('no choices available')
            return None
        if n == 'any':
            decision=self.rand_decisions(choices, np.random.randint(0,len(choices)+1))
        else:
            decision=self.rand_decisions(choices, n)
        if self.logic!=None:
            decision=self.logic.input_choose(player=self,decision=decision,
                choices=choices,choose_color_cost=choose_color_cost, label=label,n=n)

        if squeeze==False and isinstance(decision, list)==False:
            decision=[decision]
        return(decision)

    # specify an order of a list of objects
    def input_order(self, object_list,label=None):
        random.shuffle(object_list)
        if self.logic!=None:
            object_list=self.logic.input_order(player=self,object_list=object_list
                ,label=label)
        return(object_list)

    # placeholder decision making: random
    def rand_decisions(self,choices,n=1):
        if n==1:
            choice=random.choice(choices)
        else:
            choice=random.sample(choices,n)
        return(choice)

    def __repr__(self):
        return self.name
