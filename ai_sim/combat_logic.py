import pandas as pd
import numpy as np
import os
import copy
import itertools
import datetime
class Combat_Logic:
    def __init__(self, player):
        self.p=player
        self.runtime_df=pd.DataFrame()

    # evaluate attacks, gets passed a list of possible attackers
    def eval_attacks(self, atk_cand):
        # TODO: assessing permutations with planeswalker attacking separately
        # TODO: assessing permutations with different assigned damage
        start=datetime.datetime.now()
        # generate permutations of attacks
        atk_permutes=[]
        for n in range(len(atk_cand)+1):
            atk_permutes+=[i for i in itertools.combinations(atk_cand,n)]

        # get possible blockers
        blk_cand=[]
        for i in self.p.opponent.field:
            if 'creature' in i.types and i.legal_blocker():
                blk_cand.append(i)

        # proceed if there are possible attackers and blockers
        if len(blk_cand)>0 and len(atk_permutes)>0:

            # start by generating legal blockers for each possible attacker
            possible_blks={}
            for atk in atk_cand:
                possible_blks[atk]=[]
                for blocker in blk_cand:
                    # first see if it's a legal block
                    legal=blocker.legal_block_pair(atk)
                    if legal:
                        possible_blks[atk].append(blocker)


            # for each possible attack permutation, generate block permutations
            # we want this to end up as a dict. dict keys are
            # each possible atk permutation. dict values are lists with
            # dictionary values, with attackers/blockers keys and the opposite as values,
            # with order determining damage assignment
            # e.g. with two attackers in atk_cand and two blockers in blk_cand
            # {
            #     (atk1):[
            #         {
            #               blockers: {blk1:atk1, blk2: atk1},
            #               attackers: {atk1:(blk1, blk2)},
            #         }
            # extrapolate above structure to below...
            #         {blk1:atk1, blk2: atk1, atk1:(blk2, blk1)},
            #         {blk1:'No block', blk2: atk1, atk1:(blk2)},
            #         {blk1:atk1, blk2:'No block', atk1:(blk1)},
            #         {blk1:'No block', blk2: 'No block', atk1:()}
            #     ],
            #     (atk2):[
            #         {blk1:atk2, blk2: atk2 , atk2:(blk1, blk2)},
            #         {blk1:atk2, blk2: atk2 , atk2:(blk2, blk1)},
            #         {blk1:'No block', blk2: atk2, atk2:(blk2)},
            #         {blk1:atk2, blk2:'No block', atk2:(blk1)},
            #         {blk1:'No block', blk2: 'No block', atk2:()}
            #     ],
            #     (atk1,atk2): [
            #         {blk1:atk2, blk2: atk2, atk1: () , atk2: (blk1,blk2)},
            #         {blk1:atk2, blk2: atk2, atk1: () , atk2: (blk2,blk1)},
            #         {blk1:atk1, blk2: atk2, atk1: (blk1) , atk2: (blk2)},
            #         {blk1:atk2, blk2: atk1, atk1: (blk2) , atk2: (blk1)},
            #         {blk1:atk1, blk2: atk1, atk1: (blk1, blk2) , atk2: ()},
            #         {blk1:atk1, blk2: atk1, atk1: (blk2, blk1) , atk2: ()},
            #         {blk1:atk1, blk2: 'No block', atk1: (blk1) , atk2: ()},
            #         {blk1:atk2, blk2: 'No block', atk1: () , atk2: (blk1)},
            #         {blk1:'No block', blk2: atk1, atk1: (blk2) , atk2: ()},
            #         {blk1:'No block', blk2: atk2, atk1: () , atk2: (blk2)},
            #         {blk1:'No block', blk2: 'No block', atk1: () , atk2: ()}
            #     ]
            # }
            atk_dict = {}
            for atk_perm in atk_permutes:
                if atk_perm!=():
                    # pull the possible blockers for each attacker in the permutation
                    avail_blocks={}
                    for atk in atk_perm:
                        avail_blocks[atk]=possible_blks[atk]

                    # generate unique list of possible blockers
                    # invert avail_blocks so blockers are keys
                    avail_blocks_T={}
                    for blk in blk_cand:
                        avail_blocks_T[blk]=['No block']
                        for atk in avail_blocks.keys():
                            if blk in avail_blocks[atk]:
                                avail_blocks_T[blk].append(atk)

                    # iterate through all permutations of selections for each blocker
                    permutes=list(itertools.product(*avail_blocks_T.values()))
                    # add blocker as key and change to dicts with values
                    block_permutes=[]
                    for perm in permutes:
                        new_item={'blockers':{}, 'attackers':{}}
                        count=0
                        for blk in blk_cand:
                            new_item['blockers'][blk]=perm[count]
                            count+=1
                        # add attacker keys with corresponding blockers
                        multi_blocked=[]
                        for atk in atk_perm:
                            atk_list=[key for key, value in new_item['blockers'].items() if atk == value]
                            if len(atk_list)>1:
                                multi_blocked.append(atk)
                            new_item['attackers'][atk]=atk_list
                        block_permutes.append(new_item)

                        # if there are any multi-blocks, and separate permutations
                        # for each possible ordering of blockers
                        for atk in multi_blocked:
                            orderings = [i for i in itertools.permutations(new_item['attackers'][atk])]
                            for order in orderings[1:]:
                                new_item_alt=new_item.copy()
                                new_item_alt['attackers'][atk]=list(order)
                                block_permutes.append(new_item_alt)
                    atk_dict[atk_perm]=block_permutes

            # some code to check how it's performing
            # if len(blk_cand)==3 and len(atk_cand)==3:
            #     print('Atk cands', atk_cand)
            #     print('Blk cands', blk_cand)
            #     for x in atk_dict:
            #         for y in atk_dict[x]:
            #             if isinstance(y, list):
            #                 for z in y:
            #                     print(z)
            #             else:
            #                 print(y)
            #     import pdb; pdb.set_trace()
            # perform=pd.Series()
            # perform['runtime']=datetime.datetime.now()-start
            # perform['num_attackers']=len(atk_cand)
            # perform['num_blockers']=len(blk_cand)
            # self.runtime_df=self.runtime_df.append(perform, ignore_index=True)
            # self.runtime_df.to_csv('output/combat_eval_runtime.csv', mode='a',header=False)

            # Now assess the outcomes of each possible atk and blk permutation
            # create a dataframe that's columns are attacker and blocker candidates
            # for each permutation, we'll add results as rows
            self.atk_results=pd.DataFrame(columns=atk_cand+['unblocked_dmg','other_results'])
            self.blk_results=pd.DataFrame(columns=blk_cand+['other_results'])
            for atk in atk_dict.keys():
                blk_permutes=atk_dict[atk]
                for blk in blk_permutes:
                    self.simulate_combat(atk, blk)
                    self.atk_results=self.atk_results.append(self.result['attackers'])
                    self.blk_results=self.blk_results.append(self.result['blockers'])

            finish= datetime.datetime.now()
            import pdb; pdb.set_trace()

    def simulate_combat(self, atk, blk):
        # track what happens to each creature
        self.result={
            'attackers':pd.Series(index=self.atk_results.columns, name=(str(atk), str(blk))),
            'blockers':pd.Series(index=self.blk_results.columns, name=(str(atk), str(blk)))
        }

        # track how much damage is unblocked
        self.result['attackers']['unblocked_dmg']=0

        # track other results
        self.result['attackers']['other_results']=np.nan
        self.result['blockers']['other_results']=np.nan

        # track damage taken
        self.track_dmg= {
            'attackers':pd.Series(0,index=self.atk_results.columns, name=(str(atk), str(blk))),
            'blockers':pd.Series(0,index=self.blk_results.columns, name=(str(atk), str(blk)))
        }

        blkers=list(blk['blockers'].keys())

        atk_first_strike=[i for i in atk if i.check_keyword('first strike')
            or i.check_keyword('double strike')]
        blk_first_strike=[i for i in blkers if i.check_keyword('first strike')
            or i.check_keyword('double strike')]

        for i in atk_first_strike:
            self.simulate_combat_damage(source=i, targets=blk['attackers'][i], attacker=True)

        for i in blk_first_strike:
            if blk['blockers'][i]!='No block':
                self.simulate_combat_damage(source=i, targets=[blk['blockers'][i]], attacker=False)

        # simulate normal damage for those that didn't die in first strike step
        atk_norm=[i for i in atk if (i.check_keyword('first strike')==False \
            or i.check_keyword('double strike')) and self.result['attackers'][i]!='Dies']
        blk_norm=[i for i in blkers if (i.check_keyword('first strike')==False \
            or i.check_keyword('double strike')) and self.result['blockers'][i]!='Dies']

        for i in atk_norm:
            self.simulate_combat_damage(source=i, targets=blk['attackers'][i], attacker=True)

        for i in blk_norm:
            if blk['blockers'][i]!='No block':
                self.simulate_combat_damage(source=i, targets=[blk['blockers'][i]], attacker=False)

        for item,value in self.track_dmg['attackers'].items():
            if item!='unblocked_dmg' and item!='other_results':
                if value>=item.toughness:
                    self.result['attackers'][item]='Dies'
                else:
                    self.result['attackers'][item]=value

        for item,value in self.track_dmg['blockers'].items():
            if item!='unblocked_dmg' and item!='other_results':
                if value>=item.toughness:
                    self.result['blockers'][item]='Dies'
                else:
                    self.result['blockers'][item]=value

    def simulate_combat_damage(self, source, targets, attacker):
        # run through the combat calculations to get combat results
        # check how much damage it will deal
        if source.check_keyword('tough_assign'):
            dmg=source.toughness
        else:
            dmg=source.power

        # if unblocked, add to unblocked damage
        if attacker and targets==[]:
            self.result['attackers']['unblocked_dmg'] += dmg

        if attacker:
            source_key='attackers'
            target_key='blockers'
        else:
            source_key='blockers'
            target_key='attackers'

        # if attacker has lifelink, track as an other result
        if source.check_keyword('lifelink'):
            self.result[source_key]['other_results']=str(source.controller) + ' gains ' \
                + str(dmg) + ' life'

        # assign damage to blocker/attacker
        dmg_deal=dmg
        for target in targets:
            # first check if protection between creatures is present
            protect=False
            for j in target.protection_effects:
                if j.hexproof_from==False and j.check_protect(source):
                    protect=True
            if protect==False:
                # assign differently for deathtouch creatures
                if source.check_keyword('deathtouch'):
                    if dmg_deal>0 and (target!=targets[-1] or (source.check_keyword('trample') \
                        and attacker)):
                        dmg_deal-=1
                        self.track_dmg[target_key][target]+=1
                        if target.check_keyword('indestructible')==False:
                            self.result[target_key][target]='Dies'
                    else:
                        self.track_dmg[target_key][target]+=dmg_deal
                        if target.check_keyword('indestructible')==False:
                            self.result[target_key][target]='Dies'
                        dmg_deal=0
                else:
                    # check to see if there are other creatures to deal damage to,
                    # and if we can first assign lethal damage to this creature
                    # before moving on to the next.
                    if dmg_deal>(target.toughness-target.damage_received) and \
                        (target!=targets[-1] or (source.check_keyword('trample') \
                        and attacker)):
                        # At minimum must assign toughness though if possible
                        dmg_assign= target.toughness
                        self.track_dmg[target_key][target]+=dmg_assign
                        dmg_deal-=dmg_assign
                    else:
                        self.track_dmg[target_key][target]+=dmg_deal
                        dmg_deal=0
                if dmg_deal!=0 and source.check_keyword('trample') and attacking:
                    self.result['attackers']['unblocked_dmg']+=dmg_deal
