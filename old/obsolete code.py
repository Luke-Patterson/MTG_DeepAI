# def pay_mana(self, cost):
#     # attempt to pay colored cost with any existing mana in pool
#     for i,j in self.mana_pool.items():
#         if i !='C':
#             if j>0 and i in cost.keys() and cost[i]>0:
#                 j-=1
#                 cost[i]-=1
#     # pay for any colorless mana
#     if 'C' in cost.keys() and cost['C']>0:
#         # pay one colorless at a time
#         while cost['C']>0:
#             # first identify possible ways to pay for it
#             color_opts=[i for i,j in self.mana_pool.items() if j>0]
#             # check if there's any mana left to pay with:
#             if color_opts==[]:
#                 raise GameActionError('mana cost not fully paid')
#             # then ask for input on which color to use
#             color_util=self.input_choose(color_opts)
#             # pay that type of mana
#             self.mana_pool[color_util]-=1
#             cost['C']-=1
    # untapped_lands=[i for i in self.field if \
    #     isinstance(i, Land) and i.tapped==False]
    #
    # # input on which lands to tap first
    # untapped_lands=input_order('Tapping lands', untapped_lands,logic=self.logic)
    #
    # # select lands to be tapped
    # # programming for single mana lands only for now:
    #
    # # first, select lands to pay for colored requirements
    # if untapped_lands!= None:
    #     for i in untapped_lands:
    #         if not all(a==0 for a in cost.values()):
    #             temp
    #             for j in i.abils:
    #                 if isinstance(j, Mana_Ability):
    #                     j.cost[0](i)
    #                     j.effect[0](self)
    #                     mana=j.mana_type
    #                     if mana in cost.keys() and cost[mana]>0:
    #                         cost[mana]-=1
    #                     elif 'C' in cost.keys() and cost['C']>0:
    #                         cost['C']-=1
    #                     else:
    #                         raise('Paying mana that is not needed')
    #
    #
    # assert all(a==0 for a in cost.values()), '%s mana cost not fully paid' %(cost)
        if spell_moves!=[]:
            # try to cast each spell with the sources available
            for i in spell_moves:
                attempt_clone=copy.deepcopy(self)
                card_cost=i.cost
                net_mana=Counter(mana_type)-Counter(card_cost)
                del net_mana['C']
                if sum(i.cost.values())>mana_num or not all(x >= 0 for x \
                       in net_mana.values()):
                    rm_list.append(i)
            spell_moves = [i for i in spell_moves if i not in rm_list]
            if self.game.verbose>=1:
                self.game.basic_out()
                print('spell_moves',spell_moves)

    def get_avail_mana(self):
        # get available mana
        clone=copy.deepcopy(self)
        for i in clone.field:
            i.assign_ownership(clone)
        untapped_sources=[i for i in clone.field if \
            i.mana_source==True and i.tapped==False]

        if untapped_sources!=[]:
            # create a dataframe of all sources' mana abilities
            abil_df=pd.DataFrame()
            for i in untapped_sources:
                for j in i.abils:
                    if j.mana_abil:
                        abil_df=abil_df.append(pd.Series({'ID':id(i),'Source':i,'Ability':j,
                        'Ability Text':inspect.getsource(j.cost)+' '+ inspect.getsource(
                        j.effect)}),ignore_index=True)
            # iterate through all combinations of abilities
            iter_df=pd.DataFrame()
            # generate possible combinations, accounting for not using some abilities
            all_steps=[]
            for i in range(len(abil_df)+1):
                # makes a complete list of permutations of using abilities
                all_steps+=permutations(abil_df.index,i)
            # option to treat for sources with the same name or ability as identical, and
                # disregard different orders of these
            if drop_identical:
                # pairs of duplicate objects
                dupe_pairs=[]
                # pairs to drop entirely
                drop_pairs=[]
                for i,j in permutations(abil_df.index,2):
                    # if ability text is the same, treat them as interchangable
                    if abil_df.loc[i,'Ability Text']==abil_df.loc[j,'Ability Text']:
                         dupe_pairs.append((i,j))
                    # option to assume each source can only use one mana ability (for which vast majority is true)
                    if single_use:
                        if abil_df.loc[i,'ID']==abil_df.loc[j,'ID']:
                            drop_pairs.append((i,j))
                # remove all permutations with drop_pairs from permutations list
                rm_list=[]
                for i in all_steps:
                    for j in drop_pairs:
                        if j[0] in i and j[1] in i:
                            rm_list.append(i)
                            break
                all_steps=[i for i in all_steps if i not in rm_list]
                # remove duplicate permutations based on interchangeable permutations in dupe_pairs
                rm_list=[]
                for j in dupe_pairs:
                    all_steps=[i for i in all_steps if i not in rm_list]
                    others_list=[]
                    for i in all_steps:
                        if j[0] in i and j[1] in i:
                            idx0=i.index(j[0])
                            idx1=i.index(j[1])
                            if idx1-idx0==1 | idx1-idx0==-1:
                                others=[k for k in i if k not in j]
                                if others not in others_list:
                                    others_list.append(others)
                                else:
                                    rm_list.append(i)
            all_steps=[i for i in all_steps if i not in rm_list]
            # we'll want to note result for each iteration, so we add them to the dataframe
            iter_df['Steps']=all_steps
            # subfunctions to activate the abilities
            def _activate_abils(abil_idx):
                # reset cost, clone mana pool and sources
                for i in untapped_sources:
                    i.tapped=False
                clone.reset_mana_pool()
                # try to activate the abilities in order
                for i in abil_idx:
                    try:
                        abil_df.loc[i,'Ability'].cost(abil_df.loc[i,'Source'])
                        abil_df.loc[i,'Ability'].effect(abil_df.loc[i,'Source'])
                        # TODO: fix this so multi-colored cards and multi-lands work better
                        # currently won't prioritize tapping for the scarcer color of mana,
                        # just does it randomly
                    except AssertionError:
                        if self.verbose>=1:
                            print ("Unexpected error:", sys.exc_info()[1])
                        return('illegal action')
                    except GameActionError:
                        if self.verbose>=1:
                            print ("Unexpected error:", sys.exc_info()[1])
                        return('illegal action')
                return(clone.mana_pool)
            # apply steps for all possibilities
            output=iter_df['Steps'].apply(_activate_abils)
            import pdb; pdb.set_trace()
        else:
            pass
            #return(pd.DataFrame({"C":0, "W":0, "U":0, "B":0, "R":0, "G":0}))

# see if it's possible to cast each spell
if spell_moves!=[]:
    rm_list=[]
    # try to cast each spell with the sources available
    for i in spell_moves:
        # make a clone to test out if we can play spells/activate abils
        clone=self.make_copy()
        clone.name+=' Test Clone'
        for j in clone.field:
            j.assign_ownership(clone)
            j.assign_sources()
        obj_clone=i.make_copy()
        obj_clone.assign_ownership(clone)
        obj_clone.assign_sources()
        try:
            obj_clone.cost.pay_costs(mana_shorthand=self.mana_shorthand)
        except GameActionError:
            rm_list.append(i)
    # try to make choices
        if i not in rm_list:
            try:
                obj_clone.make_choices()
                obj_clone.set_targets()
                obj_clone.check_requirements()
            except GameActionError:
                rm_list.append(i)
    spell_moves = [i for i in spell_moves if i not in rm_list]
    if self.game.verbose>=3:
        self.game.basic_out()

# assess legal abilities to play
# try to activate each ability
rm_list=[]
abil_moves_clone=[]
clone=self.make_copy()
clone.name+=' Test Clone'
for obj in clone.field:
    for abil in obj.activated_abils:
        if abil.mana_abil==False:
            if (flash==False & abil.flash==False) | abil.flash==True:
                abil_moves_clone.append(abil)
# try to pay for mana cost
for abil in abil_moves_clone:
    clone=self.make_copy()
    clone.name+=' Test Clone'
    abil.assign_ownership(clone)
    for i in clone.field:
        i.assign_ownership(clone)
        i.assign_sources()
    try:
        abil.cost.pay_costs(mana_shorthand=self.mana_shorthand)
    except GameActionError:
        rm_list.append(abil.name)
# try to make choices and set targets if we can play the card
    if abil not in rm_list:
        try:
            i.make_choices()
            i.set_targets()
            i.check_requirements()
        except GameActionError:
            rm_list.append(abil.name)
#    print([(i, i.tapped) for i in self.field])
abil_moves = [i for i in abil_moves if i.name not in rm_list]
if self.game.verbose>=3:
    self.game.basic_out()


# function for getting all possible combinations of tapping a set of sources, then executing a selected one
def tap_sources_for_cost(self,cost,sources='default',drop_identical=False,single_use=True):
    # arguments:
    # Cost: a mana dictionary object
    # sources: what sources to consider using mana for. defaults to all untapped sources
    # drop_identical: shortcut to consider duplicate sources as interchangable
    # single_use: whether to assume all lands can only use one ability when
    # considering permutations

    # make a copy of costs
    cost=deepcopy(cost)

    # don't need to proceed if cost is None
    if cost==None or sum(cost.values())==0:
        return
#        if sum(cost.values())==0:
        #raise 'Error: zero cost spells not implemented'
    if sources=='default':
        sources=[i for i in self.field if i.mana_source==True and i.tapped==False]
    if sources==[]:
        raise GameActionError('Error: no sources to tap for mana')
    # assign cost to self
    self.cost_to_pay=cost
    # pay with any existing mana
    self.pay_mana(self.cost_to_pay,partial=True)
    #preserve actual self state so will do operations on a clone
    clone=self.make_copy()
    clone.name+=' Test Cost Clone'
    clone.reset_mana_pool()
    clone_sources=[i.make_copy() for i in sources]
    # set ownership
    for i in clone_sources:
        i.assign_ownership(clone)
    # create a dataframe of all sources' mana abilities
    abil_df=pd.DataFrame(columns=['obj_id','Source','Ability','Ability Text','Independent'])
    for i in clone_sources:
        for j in i.activated_abils:
            if j.mana_abil:
                abil_df=abil_df.append(pd.Series({'obj_id':id(i),'Source':i,'Ability':j,
                'Ability Text': inspect.getsource(j.cost.non_mana_cost[0])+ ' ' + inspect.getsource(
                j.abil_effect),'Independent':i.indep}),ignore_index=True)
    abil_df['row_idx']=abil_df.index
    # create an id that identifies identical abilities
    abil_df['identical_id']=pd.factorize(abil_df['Source'].apply(lambda x: x.name)+abil_df['Ability Text'])[0]
    # iterate through all combinations of abilities
    iter_df=pd.DataFrame()
    # generate possible combinations, accounting for not using some abilities
    all_steps=[]
    all_counters=[]
    for i in range(len(abil_df)+1):
        # first list available permutations of the sources where order does
        # not matter (independent=True)
        indep_permut=list(set(j for j in combinations(abil_df.loc[abil_df['Independent']==True,'identical_id'],i)))
        # for each permutation of independent objects, assign id's corresponding to those id's
        # to add back into all_steps
        counters=[]
        for j in indep_permut:
            c=Counter()
            for k in j:
                c[k]+=1
            counters.append(c)
        # deduplicate counters list if not the last iteration
        counters_final=deepcopy(counters)
        if i != len(abil_df):
            for j in counters:
                count_temp=deepcopy(counters_final)
                count_temp.remove(j)
                if j in count_temp:
                    counters_final.remove(j)
        all_counters+=counters_final
        #TODO: implement non-independent tap lands
        assert all(abil_df['Independent']==True), 'Error: non-independent land tapping not implemented'
        # # makes a complete list of permutations of using abilities for nonindepent lands
        # all_steps+=permutations(abil_df.index,i)

    # translate each counter into ability id's
    # will double count objects with multiple abilities, but will be
    # removed with single_use
    for i in all_counters:
        step=[]
        keys, values= tuple(i.keys()), tuple(i.values())
        for key,value in zip(keys, values):
            for _ in range(value):
                step.append(abil_df.loc[(abil_df.row_idx.apply(lambda x: x not in step)) & (abil_df['identical_id']==key)].index[0])
        all_steps.append(step)
    # option to treat for sources with the same name or ability as identical, and
    # disregard different orders of these
    if drop_identical or single_use:
        # pairs of duplicate objects
        dupe_pairs=[]
        # pairs to drop entirely
        drop_pairs=[]
        for i,j in permutations(abil_df.index,2):
            # if ability text is the same, treat them as interchangable
            if drop_identical:
                if abil_df.loc[i,'Ability Text']==abil_df.loc[j,'Ability Text']:
                     dupe_pairs.append((i,j))
            # option to assume each source can only use one mana ability (for which vast majority is true)
            if single_use:
                if abil_df.loc[i,'obj_id']==abil_df.loc[j,'obj_id']:
                    drop_pairs.append((i,j))
        # remove all permutations with drop_pairs from permutations list
        rm_list=[]
        for i in all_steps:
            for j in drop_pairs:
                if j[0] in i and j[1] in i:
                    rm_list.append(i)
                    break
        all_steps=[i for i in all_steps if i not in rm_list]
        # remove duplicate permutations based on interchangeable permutations in dupe_pairs
        rm_list=[]
        for j in dupe_pairs:
            all_steps=[i for i in all_steps if i not in rm_list]
            others_list=[]
            for i in all_steps:
                if j[0] in i and j[1] in i:
                    idx0=i.index(j[0])
                    idx1=i.index(j[1])
                    if idx1-idx0==1 | idx1-idx0==-1:
                        others=[k for k in i if k not in j]
                        if others not in others_list:
                            others_list.append(others)
                        else:
                            rm_list.append(i)
    all_steps=[i for i in all_steps if i not in rm_list]
    # we'll want to note result for each iteration, so we add them to the dataframe
    iter_df['Steps']=all_steps
    # subfunctions to activate the abilities
    def _activate_abils(abil_idx):
        # reset cost, clone mana pool and sources
        for i in clone_sources:
            i.tapped=False
        clone.reset_mana_pool()
        clone.cost_to_pay=deepcopy(self.cost_to_pay)
        # try to activate the abilities in order
        for i in abil_idx:
            try:
                abil_df.loc[i,'Ability'].cost.pay_costs()
                abil_df.loc[i,'Ability'].abil_effect(abil_df.loc[i,'Ability'])
                clone.pay_mana(clone.cost_to_pay,partial=True)
                # TODO: fix this so multi-colored cards and multi-lands work better
                # currently won't prioritize tapping for the scarcer color of mana,
                # just does it randomly
            except AssertionError:
                if self.game.verbose>=1:
                    print ("Unexpected error:", sys.exc_info()[1])
                return(['illegal action','illegal action'])
            except GameActionError:
                if self.game.verbose>=1:
                    print ("Unexpected error:", sys.exc_info()[1])
                return(['illegal action','illegal action'])
        return([clone.mana_pool, clone.cost_to_pay])
    # apply steps for all possibilities
    output=iter_df['Steps'].apply(_activate_abils)
    # record excess mana
    iter_df['excess_mana']=[i[0] for i in output]
    # drop those returning an illegal action
    iter_df=iter_df.loc[iter_df['excess_mana']!='illegal action']
    # record whether cost was fully paid
    iter_df['cost_paid?']=[all(j==0 for j in i[1].values()) for i in output if i[1] != 'illegal action']
    # filter to those options that generate exactly enough mana
    iter_df=iter_df.loc[iter_df['cost_paid?']]
    iter_df=iter_df.loc[iter_df['excess_mana'].apply(lambda x:all(i==0 for i in x.values()))]
    # if iter_df is empty, it means there are no possible combinations that
    # can pay for this cost.
    if iter_df.shape[0]==0:
        raise GameActionError('Error: no possible ways to pay for cost with sources')
    # select one of these methods
    selected_steps=self.input_choose(iter_df.index)
    # execute steps on actual player
    abil_df=pd.DataFrame()
    for i in sources:
        for j in i.activated_abils:
            if j.mana_abil:
                abil_df=abil_df.append(pd.Series({'obj_id':id(i),'Source':i,'Ability':j,
                'Ability Text':inspect.getsource(j.cost.non_mana_cost[0])+' '+ inspect.getsource(
                j.abil_effect)}),ignore_index=True)
    abil_idx=iter_df.loc[selected_steps,'Steps']
    for i in abil_idx:
        abil_df.loc[i,'Ability'].cost.pay_costs()
        abil_df.loc[i,'Ability'].abil_effect(abil_df.loc[i,'Ability'])
        self.pay_mana(self.cost_to_pay, partial=True)
    if not all(a==0 for a in self.cost_to_pay.values()):
        raise GameActionError('%s mana cost not fully paid' %(self.cost_to_pay))
