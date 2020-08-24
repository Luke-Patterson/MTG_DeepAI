from pathos.pools import ProcessPool
import random
from datetime import datetime
from functools import partial
import time
from Player import *
from Zones import *
import sys
import collections
import copy
import gc
import time
import math

# class for running a batch of MTG games
class MTG_Game_Set:
    def __init__(self, playerA, playerB, end_of_set_stop=False,
        cards_file='C:/Users/lsp52/AnacondaProjects/card_sim/cards/M20_index.csv'):
        self.path='C:/Users/lsp52/AnacondaProjects/card_sim/'
        self.cards_file=pd.read_csv(cards_file)
        self.data_dfs={}
        self.playerA=playerA
        self.playerB=playerB
        self.end_of_set_stop=end_of_set_stop
        self.game_count=0

    # run a set of games. kwargs are game specific keyword arguments to pass
    def execute_game_set(self, num_games, multicore=False, data_collector=None,**kwargs):
        processes = []
        start=datetime.now()
        if multicore==False:
            for n in range(num_games):
                dc_wrapper = [(data_collector, 'game: '+str(n+1)+' of '+str(num_games))
                    for n in range(num_games)]
                self.execute_game(dc_wrapper=data_collector, **kwargs)
        if multicore:
            n_nodes=5
            pool = ProcessPool(nodes=n_nodes)
            #games_per_node= math.floor(num_games/n_nodes)
            dc_wrapper = [(data_collector, 'game: '+str(n+1)+' of '+str(num_games))
                for n in range(num_games)]
            results = pool.map(partial(self.execute_game,**kwargs), dc_wrapper)
            data_collector.compile_results(results)
        print('Total runtime:',datetime.now()-start)
        if self.end_of_set_stop:
            import pdb; pdb.set_trace()

    def execute_game(self,dc_wrapper=None,**kwargs):
        if dc_wrapper!=None:
            data_collector=dc_wrapper[0]
            print('Game #', dc_wrapper[1])
        else:
            data_collector=None
        g=MTG_Game(**kwargs,cards_file=self.cards_file)
        g.play_game()
        if 'dcollect_points' in kwargs.keys() and dc_wrapper!=None:
            for j in g.plyrs:
                if n==0:
                    self.data_dfs[str(j)]=pd.DataFrame()
                    self.data_dfs['runtime']=pd.Series()
                data=pd.Series(g.dcollect['spells_cast'][j])
                if g.dcollect['winner']==j:
                    data['winner']=1
                else:
                    data['winner']=0
                self.data_dfs[str(j)]=self.data_dfs[str(j)].append(data,ignore_index=True)
            self.data_dfs['runtime']=self.data_dfs['runtime'].append(pd.Series(g.dcollect['runtime'])
                , ignore_index=True)
        gc.collect()
        if data_collector!=None:
            return([data_collector.all_xtrain, data_collector.all_ytrain])

    def export_results(self):
        # export out num of spells cast and whether they won or not
        if 'spells_cast' in self.data_dfs:
            export=self.data_dfs[str(self.playerA)]
            export=export.append(self.data_dfs[str(self.playerB)])
            export.to_csv(self.path+'output/spell_counts_'+
                time.strftime("%Y_%m_%d-%H_%M_%S"+'.csv'), index=False)

        # export runtime statistics
        if 'runtime' in self.data_dfs:
            self.data_dfs['runtime'].to_csv(self.path+'output/runtime_'+
                time.strftime("%Y_%m_%d-%H_%M_%S"+'.csv'), index=False)


# object for individual game
class MTG_Game:
    def __init__(self, playerA, playerB, verbose=1,seed=None,logged=False,
        pause_at_turn=None, stop_at_end=True, save_post_game_data=False,
        dcollect_points=[], cards_file=None, combat_eval=False):

        # initialize logging and data collection
        self.path='C:/Users/lsp52/AnacondaProjects/card_sim/'
        self.logged=logged
        if self.logged:
            log_file = open(self.path+"logs/test_exec"+str(datetime.now()).replace(':','_')+".log","w")
            sys.stdout = log_file
        # dcollect - dataframe to store info about a game
        self.dcollect={}
        self.dcollect_points=dcollect_points
        self.cards_file=cards_file
        if 'spells_cast' in self.dcollect_points:
            self.dcollect['spells_cast']={}
            self.dcollect['spells_cast'][playerA]={}
            self.dcollect['spells_cast'][playerB]={}
            for i in self.cards_file.name:
                self.dcollect['spells_cast'][playerA][i]=0
                self.dcollect['spells_cast'][playerB][i]=0
        if 'winner' in self.dcollect_points:
            self.dcollect['winner']=None
        if 'runtime' in self.dcollect_points:
            self.dcollect['runtime']=None

        # evaluate combat logic -DEV TO REMOVE
        self.combat_eval=combat_eval

        # post game data save
        self.save_post_game_data=save_post_game_data
        self.stop_at_end=stop_at_end
        self.verbose=verbose
        self.start=datetime.now()

        # initialize starting set up
        self.stack=Stack(self)
        self.pause_at_turn=pause_at_turn
        self.phase=""
        self.turn_count=1
        self.turn_id=''
        self.plyrs=[playerA,playerB]
        self.plyrs[0].opponent=self.plyrs[1]
        self.plyrs[1].opponent=self.plyrs[0]

        # determine player choosing to play/draw
        choose_first=random.choice(self.plyrs)
        self.plyrs.remove(choose_first)
        if choose_first.input_bool(label="go_first"):
            self.plyr1=choose_first
            self.plyr2=self.plyrs[0]
        else:
            self.plyr1=self.plyrs[0]
            self.plyr2=choose_first

        self.plyrs=[self.plyr1,self.plyr2]
        if seed!=None:
            self.seed=seed
        else:
            self.seed=random.randint(1,10000000000)
        random.seed(self.seed)
        print('Seed:',self.seed)
        # shuffle libraries
        for p in self.plyrs:
            p.enter_game(self)
            p.lib.load_deck(p.deck)
            p.sideboard.load_sideboard(p.sb)
            p.verbose=verbose
            p.shuffle_lib()
        # store when/where to check for triggers
        self.trigger_points={}
        # store where to check for replacement effects
        self.replace_points={}
        # store additional state based effects to check
        self.addl_state_effects=[]

        # instantiate game start in logic
        for p in self.plyrs:
            if p.logic!=None:
                p.logic.game_start()

        # draw opening hand of 7 cards
        for p in self.plyrs:
            p.draw_card(num=7)

        # elect to mulligan
        for p in self.plyrs:
            p.take_mulligans()

        if 'begin game' in self.trigger_points.keys():
            self.triggers('begin game')

    # play game until someone loses
    def play_game(self):
        try:
            while True:
                if self.verbose>=1:
                    print('Turn',self.turn_count,'-',self.plyr1)
                self.turn(self.plyr1, self.plyr2)
                if self.verbose>=1:
                    print('Turn',self.turn_count,'-',self.plyr2)
                self.turn(self.plyr2, self.plyr1)
        except GameExit:
            pass

    def turn(self, act_plyr, na_plyr):
        self.act_plyr=act_plyr
        self.na_plyr=na_plyr
        if self.turn_count==1:
            first_turn=True
        else:
            first_turn=False
        # Beginning of turn set up
        if act_plyr==self.plyr1:
            self.turn_count+=1
        self.turn_id=str(act_plyr)+str(self.turn_count)
        act_plyr.land_drops=1

        # Untap phase
        if 'begin_turn' in self.trigger_points.keys():
            self.triggers("begin_turn", act_plyr=act_plyr)

        phase="Untap"
        if self.verbose>=2:
            print('Phase: Untap')
        act_plyr.untap_for_turn()
        if 'untap' in self.trigger_points.keys():
            self.triggers("untap", act_plyr=act_plyr)

        # Upkeep phase
        phase="Upkeep"
        if self.verbose>=2:
            print('Phase: Upkeep')
        if 'upkeep' in self.trigger_points.keys():
            self.triggers("upkeep", act_plyr=act_plyr)
        self.give_priority(act_plyr, na_plyr,act_flash=True)
        for p in self.plyrs:
            p.reset_mana_pool()

        # Draw phase
        phase="Draw Step"
        if self.verbose>=2:
            print('Phase: Draw Step')
        if first_turn==False:
            act_plyr.draw_card()
        if 'draw step' in self.trigger_points.keys():
            self.triggers("draw step", act_plyr=act_plyr)
        self.give_priority(act_plyr, na_plyr,act_flash=True)
        for p in self.plyrs:
            p.reset_mana_pool()

        # 1st Main phase
        phase="First Main"
        if self.verbose>=2:
            print('Phase: First Main')
        if 'first main' in self.trigger_points.keys():
            self.triggers("first main", act_plyr=act_plyr)
        self.give_priority(act_plyr, na_plyr,act_flash=False)
        if self.verbose>=3:
            print(self.basic_w_yard_out())
        elif self.verbose>=1:
            print(self.basic_out())
        for p in self.plyrs:
            p.reset_mana_pool()

        # Beginning of combat
        phase="Beginning of Combat"
        if self.verbose>=2:
            print('Phase: Beginning of Combat')
        if 'beginning of combat' in self.trigger_points.keys():
            self.triggers("beginning of combat", act_plyr=act_plyr)
        self.give_priority(act_plyr, na_plyr,act_flash=True)
        for p in self.plyrs:
            p.reset_mana_pool()

        # Declare Attackers
        phase="Declare Attackers"
        if self.verbose>=2:
            print('Phase: Declare Attackers')
        # if 'declare attackers' in self.trigger_points.keys():
        #     self.triggers("declare attackers")
        act_plyr.declare_attackers()
        if self.verbose>=1:
            print('Attackers:',act_plyr.get_attackers())
        self.give_priority(act_plyr, na_plyr,act_flash=True)
        for p in self.plyrs:
            p.reset_mana_pool()

        # Declare Blockers
        phase="Declare Blockers"
        if self.verbose>=2:
            print('Phase: Declare Blockers')
        # if 'declare blockers' in self.trigger_points.keys():
        #     self.triggers("declare blockers")
        na_plyr.declare_blockers()
        if self.verbose>=1:
            print('Blockers:',na_plyr.get_blockers())
            for i in na_plyr.get_blockers():
                print(i, 'is blocking', i.is_blocking_attacker)
        self.give_priority(act_plyr, na_plyr,act_flash=True)
        for p in self.plyrs:
            p.reset_mana_pool()

        # Combat Damage
        phase="Combat Damage"
        if self.verbose>=2:
            print('Phase: Combat Damage')
        # if 'combat damage step' in self.trigger_points.keys():
        #     self.triggers("combat damage step")
        self.resolve_combat_damage(act_plyr,na_plyr,first_strike=True)
        self.check_state_effects()
        self.resolve_combat_damage(act_plyr,na_plyr,first_strike=False)
        self.check_state_effects()
        for p in self.plyrs:
            p.reset_mana_pool()

        # End of Combat
        phase="End of Combat Step"
        if self.verbose>=2:
            print('Phase: End of Combat Step')
        if 'end of combat' in self.trigger_points.keys():
            self.triggers("end of combat", act_plyr=act_plyr)
        self.give_priority(act_plyr, na_plyr,act_flash=True)
        act_plyr.combat_cleanup()
        na_plyr.combat_cleanup()
        if self.verbose>=3:
            print(self.basic_w_yard_out())
        elif self.verbose>=1:
            print(self.basic_out())
        self.check_state_effects()
        for p in self.plyrs:
            p.reset_mana_pool()

        # 2nd Main phase
        phase="Second Main"
        if self.verbose>=2:
            print('Phase: Second Main')
        if 'second main' in self.trigger_points.keys():
            self.triggers("second main", act_plyr=act_plyr)
        self.give_priority(act_plyr, na_plyr,act_flash=False)
        for p in self.plyrs:
            p.reset_mana_pool()

        # End Phase
        phase="End Phase"
        if self.verbose>=2:
            print('Phase: End Phase')
        if 'end phase' in self.trigger_points.keys():
            self.triggers("end phase", act_plyr=act_plyr)
        self.give_priority(act_plyr, na_plyr,act_flash=True)
        for p in self.plyrs:
            p.reset_mana_pool()

        # Cleanup phase
        phase="Cleanup Phase"
        if self.verbose>=2:
            print('Phase: Cleanup Phase')
        if 'cleanup phase' in self.trigger_points.keys():
            self.triggers("cleanup phase", act_plyr=act_plyr)
        self.turn_cleanup(act_plyr)
        if self.verbose>=3:
            print(self.basic_w_yard_out())
        elif self.verbose>=1:
            print(self.basic_out())
        if self.pause_at_turn!= None and self.turn_count==self.pause_at_turn:
            import pdb; pdb.set_trace()

    # check for triggers
    # TODO: allowing players to stack simultaneous triggers in order
    def triggers(self, name,effect_kwargs={},**kwargs):
        if name in self.trigger_points.keys():
            for t in self.trigger_points[name]:
                # check to see if trigger condition is met
                if t.trigger_condition(t,**kwargs):
                    # if so, make any choices then add ability to the stack
                    if t.stack:
                        t.put_trigger_on_stack(effect_kwargs)
                    else:
                        t.abil_effect(t)

    # check for replacement effects of a certain type0
    def check_replace_effects(self,name,condition_kwargs={},effect_kwargs={}):
        if name in self.replace_points.keys():
            for t in self.replace_points[name]:
                # check to see if trigger condition is met
                if t.replace_condition(t,**condition_kwargs):
                    # if so, make any choices then resolve the replacement effect
                    t.make_choices()
                    t.replace_effect(effect_kwargs)

    # resolve top of stack
    def resolve_top_of_stack(self):
        if self.verbose>=1:
            if len(self.stack)>1:
                print('Stack:',self.stack)
                #import pdb; pdb.set_trace()
            print('Resolving',self.stack[-1])
        self.stack[-1].resolve()

    # priority opportunity for both players
    def give_priority(self, act_plyr, na_plyr, act_flash):
        while self.stack!=[] or act_plyr.Pass==False or na_plyr.Pass==False:
            if self.stack!=[]:
                act_flash_val=True
            else:
                act_flash_val=act_flash
            act_plyr.make_play(flash=act_flash_val)
            self.check_state_effects()
            if act_plyr.Pass:
                na_plyr.make_play(flash=True)
                self.check_state_effects()
            if act_plyr.Pass and na_plyr.Pass and self.stack!=[]:
                self.resolve_top_of_stack()
                self.check_state_effects()
        act_plyr.Pass=False
        na_plyr.Pass=False


    # function to check state based effects
    def check_state_effects(self):
            # perform additional checks added by cards
            for static_effect in self.addl_state_effects:
                static_effect.check_effect()
            for i in self.plyrs:
                # TODO: build in possibility of draw
                if i.life<=0:
                    self.end_game(i, 'Player has 0 or less life')

                for j in i.field:
                    # check if creatures have taken lethal damage
                    if 'creature' in j.types:
                        j.check_lethal_damage()
                    # check if planeswalkers have taken lethal damage
                    if 'planeswalker' in j.types:
                        j.check_loyalty()
                    # check if any attached objs are knocked off due to protection
                    for obj in j.attached_objs:
                        if isinstance(obj,Equipment) or isinstance(obj,Aura):
                            protect=False
                            for abil in j.protection_effects:
                                if abil.hexproof_from==False and abil.check_protect(obj):
                                    protect=True
                            if protect:
                                obj.detach_from(j)

                    # check if two legendary permanents exist
                    if 'legendary' in j.types:
                        others=[k for k in i.field if k.name==j.name]
                        if len(others)>1:
                            # player chooses one and kills the rest
                            keep=i.input_choose(others)
                            for k in others:
                                if k!=keep:
                                    i.field.leave_zone(j)
                                    i.yard.enter_zone(j)
                                    if self.verbose>=2:
                                        print(k,'legend rule applied')



    # resolve combat damage
    def resolve_combat_damage(self,act_plyr,na_plyr,first_strike):
        # identify pairs of combatants
        combat_pairs = []
        for i in act_plyr.field:
            if 'creature' in i.types and i.attacking:
                blockers=[j for j in na_plyr.field if 'creature' in j.types and
                    j.is_blocking_attacker==i]
                combat_pairs.append((i,blockers))

        # if in first strike combat step, first and double strikers deal damage
        if first_strike:
            for i in combat_pairs:
                if i[0].check_keyword('first strike') or \
                    i[0].check_keyword('double strike'):
                    i[0].deal_combat_damage(i[1])
                for j in i[1]:
                    if j.check_keyword('first strike') or \
                        j.check_keyword('double strike'):
                        j.deal_combat_damage([i[0]])
        # if in normal combat step, non-first strike and double strikers deal damage
        else:
            for i in combat_pairs:
                if i[0].check_keyword('first strike')==False or \
                    i[0].check_keyword('double strike'):
                    i[0].deal_combat_damage(i[1])
                for j in i[1]:
                    if i[0].check_keyword('first strike')==False or \
                        i[0].check_keyword('double strike'):
                        j.deal_combat_damage([i[0]])

        self.triggers('combat damage')

    # turn cleanup
    def turn_cleanup(self,act_plyr):
        # active player discards down to 7 cards
        act_plyr.EOT_discard()
        # other clean up
        # reset spell counts this turn
        # remove all damage from creatures and cease EOT effects
        for p in self.plyrs:
            p.EOT_cleanup()
            for i in p.field:
                i.EOT_cleanup()

    def end_game(self, plyr , reason):
        if self.verbose>=1:
            self.detail_out()
        print(plyr, 'loses!', reason)
        end=datetime.now()
        print('Runtime:', end-self.start)
        print('Seed:',self.seed)
        if self.logged==True:
            sys.stdout=sys.__stdout__
            print('game ended, logging complete')
            print('Runtime:', end-self.start)
            print('Seed:',self.seed)

        # save data about game in a sparse matrix
        if 'winner' in self.dcollect_points:
            self.dcollect['winner']=plyr.opponent
        if 'runtime' in self.dcollect_points:
            self.dcollect['runtime']=end-self.start
        if self.stop_at_end:
            import pdb; pdb.set_trace()
        for p in self.plyrs:
            if p.logic!=None:
                p.logic.end_game(winner=plyr.opponent)
        for p in self.plyrs:
            p.reset_self()
        raise GameExit()

    # =====================================================================
    # Output functions - functions to print out game state
    # =====================================================================
    # basic output
    def basic_out(self):
        for p in self.plyrs:
            print(p,"battlefield:", p.field)
            print(p,"hand:", p.hand)
            print(p,"life:", p.life)
            print('stack:',self.stack)

    def basic_w_yard_out(self):
        for p in self.plyrs:
            print(p,"battlefield:", p.field)
            print(p,"graveyard:", p.yard)
            print(p,"hand:", p.hand)
            print(p,"life:", p.life)
            print('stack:',self.stack)

    # detailed output
    def detail_out(self):
        for p in self.plyrs:
            print(p," battlefield:", p.field)
            print(p," hand:", p.hand)
            print(p," deck:", p.lib)
            print(p," graveyard:", p.yard)

    # combat game state
    def combat_out(self):
        for p in self.plyrs:
            attackers=p.get_attackers()
            blockers=p.get_blockers()
            if attackers!=[]:
                print(p, 'attackers:', attackers)
            if blockers!=[]:
                print(p, 'blockers:', attackers)

class GameExit(Exception):
    pass