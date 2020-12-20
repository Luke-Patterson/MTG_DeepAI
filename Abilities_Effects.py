# define classes for abilities and effects
from Exceptions import *
import inspect
import copy
from Concepts import *

# =======================================================
# Ability Classes
# =======================================================

# Activated Abilites
class Activated_Ability:
    def __init__(self,name,abil_effect,cost=[Cost(mana={'C:0'})],
            mana_abil=False,potential_mana=None,choices=[],targets=[],requirements=[],flash=True,
            moded=False, n_modes=0, mode_labels=[], lki_func=None, active_zones=['field']):
        self.name=name
        # if cost not passed as a list, make cost a list
        if isinstance(cost,list):
            self.cost=cost
        else:
            self.cost=[cost]
        # tracking which cost methods are valid if multiple
        self.valid_costs=[]
        # effect
        self.abil_effect=abil_effect
        self.mana_abil=mana_abil
        # choices - list of choice objects
        if isinstance(choices,list)==False:
            choices=[choices]
        self.choices=choices
        if isinstance(targets,list)==False:
            targets=[targets]
        self.targets=targets
        self.flash=flash
        # list of zones where source object can be in order for ability to be activated
        self.active_zones=active_zones
        # source and controller - to be assigned later
        self.source=None
        self.controller=None
        self.owner=None
        self.requirements=requirements
        self.types=['activated_abil']
        self.moded=moded
        if moded:
            self.n_modes=n_modes
        else:
            self.n_modes=1
        self.legal_modes=[]
        self.selected_mode=None
        self.mode_labels=mode_labels
        # function for tracking last known info
        self.lki_func=lki_func
        # tracking last known info
        self.last_known_info=[]
        # misc info placeholdre
        self.temp_memory=[]
        # potential mana tracking
        self.potential_mana=potential_mana
        if self.potential_mana!=None:
            self.potential_mana.linked_abil=self

    # =======================================================
    # Set ownership/source functions
    # =======================================================

    def assign_source(self,source):
        self.source=source
        for i in self.cost:
            i.source=self
        for i in self.choices:
            i.assign_source(self)
        for i in self.targets:
            i.assign_source(self)
        for i in self.requirements:
            i.assign_source(self)
        if self.potential_mana != None:
            self.potential_mana.assign_source(source)

        if self.potential_mana != None and self.potential_mana not in source.potential_mana:
            source.potential_mana=source.potential_mana+[self.potential_mana]
            source.potential_mana_values = source.potential_mana_values + [
                self.potential_mana.mana]
            # if there's more than one potential mana obj, sort so the color
            # of the potential mana is consistently ordered
            # potential mana colors get used as keys elsewhere, so we want this to
            # be consistent. As in ['W','U'] and ['U','W'] should be treated the same,
            # but if passed as keys to a dict, they will be treated differently.
            if len(source.potential_mana_values)>1:
                # only built to handle potential mana objects with one key currently
                # building an assert statement to catch this
                assert all([len(list(i.keys()))==1 for i in source.potential_mana_values]), 'Multi color potential mana not built to sort properly'
                keys = [list(i.keys())[0] for i in source.potential_mana_values]
                # not built to handle potential mana with duplicates of one mana symbol
                # as well as potential mana of another symbol [i.e. ['W','G','G']]

                #assert len(set(keys)) == len(keys) or len(set(keys))==1, 'Not built to handle sorting abils with duplicate and multiple different colors'

                # this assert statement throws an error in game when course of action
                # leads to these. To date (8/22/2020), the order only matters for
                # selecting cards pre game. This will have to be sorted out
                # if trying to a program a card with that fails this assert statement on its own,
                # or there's a reason that potential mana must be sorted in game

                # ignore sorting if potential mana is multiple of the same color
                # but can continue if not the above issue caught in an assert statement
                # i.e. ['G','G']
                if len(set(keys)) == len(keys):
                    sorted_keys = sorted(keys)
                    new_order = [sorted_keys.index(i) for i in keys]
                    source.potential_mana=[source.potential_mana[i]
                        for i in new_order]
                    source.potential_mana_values=[source.potential_mana_values[i]
                        for i in new_order]

    def assign_ownership(self,new_owner):
        self.owner=new_owner
        self.controller=new_owner
        for i in self.cost:
            i.owner=new_owner
            i.controller=new_owner
        for i in self.choices:
            i.assign_ownership(new_owner)
        for i in self.targets:
            i.assign_ownership(new_owner)
        if self.potential_mana!=None:
            self.potential_mana.assign_ownership(new_owner)

    def assign_controller(self,new_controller):
        self.controller=new_controller
        for i in self.cost:
            i.controller=new_controller
        for i in self.choices:
            i.assign_controller(new_controller)
        for i in self.targets:
            i.assign_controller(new_controller)
        if self.potential_mana!=None:
            self.potential_mana.assign_controller(new_controller)

    # =======================================================
    # Requirements functions
    # =======================================================

    # def check_requirements(self):
    #     for i in self.requirements:
    #         if i.check_requirement() == False:
    #             print(inspect.getsource(i.condition))
    #             raise GameActionError('Activate condition not met for ' + str(self))
    # check functions
    def check_requirements(self):
        legal=True
        for i in self.requirements:
            if i.check_requirement() == False:
                legal=False
        return(legal)
    # =======================================================
    # Choices functions
    # =======================================================

    def reset_choices(self):
        for i in self.choices:
            i.choice_made=None

    def get_choices(self,squeeze=True):
        if len(self.choices)==1 and squeeze:
            return self.targets[0].choice_made
        else:
            return[i.choice_made for i in self.targets]

    # make other choices required to activate ability
    def make_choices(self):
        for i in self.choices:
            i.make_choice()

    def check_choices(self):
        legal=True
        for i in self.choices:
            if i.check_choice() == False:
                legal = False
        return legal

    # =======================================================
    # Targets functions
    # =======================================================

    # select targets
    def set_targets(self):
        for i in self.targets:
            i.set_possible_target()

    # function to retrieve target object or list of target objects
    def get_targets(self,squeeze=True, check_illegal_targets=True):
        targets=[i for i in self.targets if self.selected_mode==None or
            self.selected_mode==i.mode_num]

        if len(targets)==1 and squeeze:
            target_objs=targets[0].target_obj
        else:
            if check_illegal_targets and len(targets)>1:
                # when we're checking targets right before resolution,
                # need to handle the case where there are multiple targets,
                # some of which are legal targets still, and some of which
                # are not. We'll run check_target_zones for each target
                # and if it's False, we'll remove from the targets list
                illegal_targets=[]
                for i in targets:
                    if i.target_obj!=None and i.check_target_zones()==False:
                        illegal_targets.append(i)
                for i in illegal_targets:
                    targets.remove(i)
            target_objs=[i.target_obj for i in targets]
        return target_objs


    # check to make sure targets have not changed zone
    # def check_target_zones(self):
    #     if self.targets==[]:
    #         any_legal=True
    #     else:
    #         any_legal=False
    #         for i in self.targets:
    #             if i.check_target_zones():
    #                 any_legal=True
    #     return(any_legal)

    # check that there are legal targets
    def check_for_legal_targets(self):
        legal=True
        if self.targets!=[]:
            for i in self.targets:
                if i.c_required and i.get_possible_targets()==[]:
                    if i.mode_linked and self.selected_mode==i.mode_num:
                        legal=False
        return(legal)

    def reset_targets(self):
        for i in self.targets:
            i.target_obj=None
            i.zone=None
            i.zone_hash=None

    # =======================================================
    # Checking legality of targets, choices, and requirements
    # =======================================================

    def check_costs(self,pay_mana_cost=True):
        possible_costs=[]
        for i,cost in enumerate(self.cost):
            if cost.check_costs(pay_mana_cost=pay_mana_cost):
                possible_costs.append(cost)
        if possible_costs==[]:
            return(False)
        else:
            self.valid_costs = possible_costs
            return(True)

    # check to make sure it's legal to activate ability
    def legal_req_tar_cho_costs(self):
        if self.moded:
            self.legal_modes=[]
            for i in [n+1 for n in range(self.n_modes)]:
                self.selected_mode=i
                if self.perform_legal_check():
                    self.legal_modes.append(i)
            return(self.legal_modes!=[])
        else:
            return(self.perform_legal_check())

    # interior function to legal_req_tar_cho_costs
    def perform_legal_check(self):
        # get potential mana
        self.controller.get_potential_mana(for_cost=self)
        legal_target=self.check_for_legal_targets()
        # first check if there are legal targets/choices/requirements
        if  legal_target == False or \
            self.check_requirements() == False or \
            self.check_choices() == False:
            return(False)
        else:
            # check that legal choices/requirements/targets can be made and
            # the spell's costs still paid
            all_targets_present=True
            # if targets are required, check there's a legal target with payable cost
            if any([t.c_required for t in self.targets]):
                all_targets_present=True
                for i in self.targets:
                    if i.c_required:
                        legal_target_present=False
                        target_cands=i.get_possible_targets()
                        for j in target_cands:
                            i.target_obj=j
                            if self.check_costs() and self.check_choices() and \
                                self.check_requirements():
                                legal_target_present=True
                                i.target_obj=None
                                break
                        if legal_target_present==False:
                            all_targets_present=False
                    i.target_obj=None
                if all_targets_present==False:
                    self.reset_targets()
                    return(False)
            elif self.check_costs()==False:
                self.reset_targets()
                return(False)
            self.reset_targets()
            return(True)


            # TODO: may need to include requirements and choices in above check too
            #for i in self.requirements:
            # for i in self.choices:

    # =======================================================
    # Functions for activating and resolving ability
    # =======================================================
    def activate_ability(self, effect_kwargs={}):
        # choose targets
        self.set_targets()
        # make choices for effect
        self.make_choices()
        # check requirements
        self.check_requirements()
        # pay costs - run check costs again to ensure we have set self.valid_costs
        self.check_costs()
        selected=self.controller.input_choose(self.valid_costs, label='alt cost selection')
        # make sure that check_potential_mana is up against the right cost
        if len(self.valid_costs)>1:
            self.controller.check_potential_mana(mana_cost=selected.mana_cost)

        selected.pay_costs()
        if 'planeswalker' in self.source.types:
            self.source.activated_loyalty_abil=True

        if self.source.owner.verbose>=2:
            if self.choices!=[]:
                print(' Choices: ',  self.choices)
            if self.targets!=[]:
                print(' Targets: ',  self.targets)
            if self.selected_mode!=None:
                print(' Mode: ',  self.mode_labels[self.selected_mode-1])



        # if a mana abil, just resolve directly
        if self.mana_abil:
            if self.source.controller.game.verbose>=2:
                print('Activating', self.source, 'mana ability')
            self.apply_effect()
            # check for triggerd abils
            self.controller.game.triggers('abil activated',activated_abil=self,
                effect_kwargs={'activated_abil':self})
        # pass choices to effect and put the effect on stack
        else:
            effect=Effect_Instance(name=self.name,source=self.source,
                abil_effect=self.abil_effect,targets=self.targets,
                controller=self.controller,types=self.types,
                choices=self.choices, requirements=self.requirements,
                colors=self.source.colors, mode=self.selected_mode,
                mana_abil=self.mana_abil)
            if self.lki_func!=None:
                effect.last_known_info=self.lki_func(self, effect_kwargs)
            self.controller.game.stack.enter_zone(effect)

            # check for triggerd abils
            self.controller.game.triggers('abil activated',activated_abil=effect,
                effect_kwargs={'activated_abil':effect})

    def apply_effect(self):
        self.abil_effect(self)

    # using Effect_Instance class to resolve so don't need these any more
    # def resolve(self):
    #     if self.check_target_zones():
    #         self.apply_effect()
    #     elif self.source.controller.game.verbose>=2:
    #         print(self,'countered due to no legal targets')
    #     self.controller.game.stack.leave_zone(self)

    def __repr__(self):
        return self.name #+ str(id(self))[-2:]

    def __str__(self):
        return self.name

class Triggered_Ability:
    def __init__(self,name,abil_effect,trigger_points,trigger_condition= lambda x:
        True, add_trigger_zones=['field'], remove_trigger_zones=['field'],
        cost=[Cost(mana={'C':0})],choices=[],targets=[],requirements=[],stack=True,
        moded=False,n_modes=0, mode_labels=[], lki_func=None, remove_on_leave_zone=False):
        self.name=name
        if isinstance(cost,list):
            self.cost=cost
        else:
            self.cost=[cost]
        # trigger points should be a list of strings of keywords in trigger_list.txt
        self.trigger_points=trigger_points
        self.trigger_condition=trigger_condition
        # add_trigger_zones - zones which entering causes the game to add trigger
        # points to. default is just the field
        self.add_trigger_zones=add_trigger_zones
        # reomve_trigger_zones - zones which entering causes the game to remove trigger
        # points to. default is just the field
        self.remove_trigger_zones=remove_trigger_zones
        self.abil_effect=abil_effect
        # choices - list of choice objects
        self.choices=choices
        self.targets=targets
        self.requirements=requirements
        # check if we need to use the stack
        self.stack=stack
        # source and controller - to be assigned later
        self.source=None
        self.controller=None
        self.owner=None
        self.types=['triggered_abil']
        self.moded=moded
        if moded:
            self.n_modes=n_modes
        else:
            self.n_modes=1
        self.legal_modes=[]
        self.selected_mode=None
        self.mode_labels=mode_labels
        # function for tracking last known info
        self.lki_func=lki_func
        # tracking last known info
        self.last_known_info=[]
        # misc info placeholdre
        self.temp_memory=[]
        # whether to remove ability once the source obj leaves current zone
        self.remove_on_leave_zone=remove_on_leave_zone

    # =======================================================
    # Set ownership/source functions
    # =======================================================

    def assign_source(self,source):
        self.source=source
        for i in self.cost:
            i.source=source
        for i in self.choices:
            i.assign_source(self)
        for i in self.targets:
            i.assign_source(self)
        for i in self.requirements:
            i.assign_source(self)
        for i in self.add_trigger_zones:
            if 'player' not in source.types:
                self.source.add_trigger_zones.append(i)
                self.source.remove_trigger_zones.append(i)

    def assign_ownership(self,new_owner):
        self.owner=new_owner
        self.controller=new_owner
        for i in self.cost:
            i.owner=new_owner
        for i in self.cost:
            i.controller=new_owner
        for i in self.choices:
            i.assign_ownership(new_owner)
        for i in self.targets:
            i.assign_ownership(new_owner)

    def assign_controller(self,new_controller):
        self.controller=new_controller
        for i in self.cost:
            i.controller=new_controller
        for i in self.choices:
            i.assign_controller(new_controller)
        for i in self.targets:
            i.assign_controller(new_controller)

    # add trigger condition checks to the game
    def add_trigger_points(self):
        for i in self.trigger_points:
            if i in self.source.controller.game.trigger_points.keys():
                self.source.controller.game.trigger_points[i].append(self)
            else:
                self.source.controller.game.trigger_points[i]=[self]

    def remove_trigger_points(self):
        for i in self.trigger_points:
            if i in self.source.controller.game.trigger_points.keys():
                if self.source.controller.game.trigger_points[i]==[self]:
                    del self.source.controller.game.trigger_points[i]
                elif self in self.source.controller.game.trigger_points[i]:
                    self.source.controller.game.trigger_points[i].remove(self)

    def check_requirements(self):
        legal=True
        for i in self.requirements:
            if i.check_requirement() == False:
                legal=False
        return(legal)

    # =======================================================
    # Targets functions
    # =======================================================

    # select targets
    def set_targets(self):
        for i in self.targets:
            i.set_possible_target()

    # function to retrieve target object or list of target objects
    def get_targets(self,squeeze=True, check_illegal_targets=True):
        targets=[i for i in self.targets if self.selected_mode==None or
            self.selected_mode==i.mode_num]

        if len(targets)==1 and squeeze:
            target_objs=targets[0].target_obj
        else:
            if check_illegal_targets and len(targets)>1:
                # when we're checking targets right before resolution,
                # need to handle the case where there are multiple targets,
                # some of which are legal targets still, and some of which
                # are not. We'll run check_target_zones for each target
                # and if it's False, we'll remove from the targets list
                illegal_targets=[]
                for i in targets:
                    if i.target_obj!=None and i.check_target_zones()==False:
                        illegal_targets.append(i)
                for i in illegal_targets:
                    targets.remove(i)
            target_objs=[i.target_obj for i in targets]
        return target_objs


    # check to make sure targets have not changed zone
    def check_target_zones(self):
        if self.targets==[]:
            any_legal=True
        else:
            any_legal=False
            for i in self.targets:
                if i.check_target_zones():
                    any_legal=True
        return(any_legal)

    # check that there are legal targets
    def check_for_legal_targets(self):
        legal=True
        if self.targets!=[]:
            for i in self.targets:
                if i.c_required and i.get_possible_targets()==[]:
                    if i.mode_linked and self.selected_mode==i.mode_num:
                        legal=False
        return(legal)

    def reset_targets(self):
        for i in self.targets:
            i.target_obj=None
            i.zone=None
            i.zone_hash=None

    # =======================================================
    # Choices functions
    # =======================================================
    # make choices required to play card
    def make_choices(self):
        for i in self.choices:
            i.make_choice()
        # if modded, select mode
        # TODO if moded triggered abils actually exist, checking for legality of modes
        if self.moded:
            self.selected_mode=self.controller.input_choose([i+1 for i in range(self.n_modes)])

    def reset_choices(self):
        for i in self.choices:
            i.choice_made=None

    def get_choices(self,squeeze=True):
        if len(self.choices)==1 and squeeze:
            return self.targets[0].choice_made
        else:
            return[i.choice_made for i in self.targets]

    def check_choices(self):
        legal=True
        for i in self.choices:
            if i.check_choice() == False:
                legal = False
        return legal

    # =======================================================
    # Functions for activating and resolving ability
    # =======================================================

    def check_costs(self, pay_mana_cost=True):
        possible_costs=[]
        for i,cost in enumerate(self.cost):
            if cost.check_costs(pay_mana_cost=pay_mana_cost):
                possible_costs.append(cost)
        if possible_costs==[]:
            return(False)
        else:
            return(True)

    # def apply_effect(self):
    #     self.abil_effect(self)

    def put_trigger_on_stack(self, effect_kwargs={}):

        # make choices for effect
        self.make_choices()

        # choose targets
        try:
            self.set_targets()
        except GameActionError:
            if self.controller.game.verbose>=2:
                print(self,'trigger not put on stack, no legal targets for trigger')
            return

        # check requirements
        self.check_requirements()
        # pay costs - run check costs again to ensure we have set self.valid_costs
        # triggered abil costs, if any, are paid on resolution. Will put these
        # costs into the abil_effect function of the card
        #self.check_costs()
        if self.source.controller.game.verbose>=2:
            if self.choices!=[]:
                print(' Choices: ',  self.choices)
            if self.targets!=[]:
                print(' Targets: ',  self.choices)
            if self.selected_mode!=None:
                print(' Mode: ',  self.mode_labels[self.selected_mode-1])

        effect=Effect_Instance(name=self.name,source=self.source,
            abil_effect=self.abil_effect,targets=self.targets,
            controller=self.controller,types=self.types,
            choices=self.choices, requirements=self.requirements,
            colors=self.source.colors, mode=self.selected_mode
            ,trigger_points=self.trigger_points, trigger_condition=self.trigger_condition)
        if self.lki_func!=None:
            effect.last_known_info=self.lki_func(self, effect_kwargs)
        self.controller.game.stack.enter_zone(effect)


    # using Effect_Instance class to resolve so don't need these any more
    # def resolve(self):
    #     if self.check_target_zones():
    #         self.apply_effect()
    #     elif self.source.controller.game.verbose>=2:
    #         print(self,'countered due to no legal targets')
    #     self.source.controller.game.stack.leave_zone(self)
    #     self.reset_targets()
    #     self.reset_choices()

    # def check_target_zones(self):
    #     if self.targets==[]:
    #         any_legal=True
    #     else:
    #         any_legal=False
    #         for i in self.targets:
    #             if i.check_target_zones():
    #                 any_legal=True
    #     return(any_legal)

    def __repr__(self):
        return self.name #+ str(id(self))[-2:]

    def __str__(self):
        return self.name

# =======================================================
# Effect Classes
# =======================================================
# class that is ability's effect on the stack
class Effect_Instance:
    def __init__(self,name,source, abil_effect,targets,controller,types,
        choices,requirements,colors,mode=None, trigger_points=None,
        trigger_condition = None, mana_abil=None):
        self.name=name
        self.source=source
        self.abil_effect=abil_effect
        self.targets=[i.make_copy() for i in targets]
        self.owner=controller
        self.controller=controller
        self.types=types
        self.zone=None
        self.zone_turn=None
        self.zone_hash=None
        self.last_known_info=None
        self.cost=[Cost(mana={'C':0})]
        self.choices=choices
        self.requirements=requirements
        self.colors=colors
        self.selected_mode=mode
        self.trigger_points=trigger_points
        self.trigger_condition= trigger_condition
        # misc info placeholdre
        self.temp_memory=[]
        self.mana_abil=mana_abil

    def assign_source(self,source):
        self.source=source
        for i in self.targets:
            i.assign_source(self)
        for i in self.cost:
            i.assign_source(self)

    # for use when spell copies an ability
    def make_copy(self, choose_new_targets=True):
        clone = Effect_Instance(name=self.name,source=self.source,
            abil_effect=self.abil_effect,targets=[i.make_copy() for i in self.targets],
            controller=self.controller,types=self.types,
            choices=self.choices, requirements=self.requirements,
            colors=self.source.colors,mode=self.selected_mode,
            trigger_points=self.trigger_points,trigger_condition=self.trigger_condition,
            mana_abil=self.mana_abil)
        if choose_new_targets:
            try:
                clone.set_targets(make_copy=True)
            except GameActionError:
                self.counterspelled()
        self.controller.game.stack.enter_zone(clone)

    def check_costs(self,pay_mana_cost=True):
        possible_costs=[]
        for i,cost in enumerate(self.cost):
            if cost.check_costs(pay_mana_cost=pay_mana_cost):
                possible_costs.append(cost)
        if possible_costs==[]:
            return(False)
        else:
            self.valid_costs = possible_costs
            return(True)

    def check_choices(self):
        legal=True
        for i in self.choices:
            if i.check_choice() == False:
                legal = False
        return legal

    def check_requirements(self):
        legal=True
        for i in self.requirements:
            if i.check_requirement() == False:
                legal=False
        return(legal)

    def assign_controller(self,new_controller):
        self.controller=new_controller
        for i in self.targets:
            i.assign_controller(new_controller)
        for i in self.cost:
            i.assign_controller(new_controller)

    def get_targets(self,squeeze=True, check_illegal_targets=True):
        if len(self.targets)==1 and squeeze:
            target_objs=self.targets[0].target_obj
        else:
            targets=[i for i in self.targets]
            if check_illegal_targets and len(self.targets)>1:
                # when we're checking targets right before resolution,
                # need to handle the case where there are multiple targets,
                # some of which are legal targets still, and some of which
                # are not. We'll run check_target_zones for each target
                # and if it's False, we'll remove from the targets list
                illegal_targets=[]
                for i in targets:
                    if i.target_obj!=None and i.check_target_zones()==False:
                        illegal_targets.append(i)
                for i in illegal_targets:
                    targets.remove(i)
            target_objs=[i.target_obj for i in targets]
        return target_objs

    # select targets
    def set_targets(self, make_copy=False):
        for i in self.targets:
            i.set_possible_target(make_copy)

    def check_target_zones(self):
        if self.targets==[]:
            any_legal=True
        else:
            any_legal=False
            for i in self.targets:
                if i.check_target_zones():
                    any_legal=True
        return(any_legal)

    def resolve(self):
        if self.check_target_zones():
            self.apply_effect()
        elif self.source.controller.game.verbose>=2:
            print(self,'countered due to no legal targets')
        self.controller.game.stack.leave_zone(self)
        self.source.reset_choices()
        self.source.reset_targets()

    def apply_effect(self,effect_kwargs={}):
        if effect_kwargs!={}:
            self.abil_effect(self,effect_kwargs)
        else:
            self.abil_effect(self)

    def counterspelled(self):
        self.controller.game.stack.leave_zone(self)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

# master effect class
class Static_Effect:
    def __init__(self,name,effect_func, reverse_effect_func,
        effect_condition=lambda obj: True, init_effect_zones=['field']):
        self.effect_func=effect_func
        self.reverse_effect_func=reverse_effect_func
        # source and controller - to be assigned later
        self.source=None
        self.controller=None
        self.owner=None
        self.name=name
        self.effect_condition=effect_condition
        # zones that when object enters the static effect is applied
        self.init_effect_zones=init_effect_zones


    def assign_source(self,source):
        self.source=source

    def assign_ownership(self,new_owner):
        self.owner=new_owner
        self.controller=new_owner

    def assign_controller(self,new_controller):
        self.controller=new_controller

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

# class representing static effects that only affect their source object
class Local_Static_Effect(Static_Effect):
    def __init__(self,variable_value=False,**kwargs):
        Static_Effect.__init__(self,**kwargs)
        super()
        self.variable_value=variable_value

    def assign_source(self,source):
        super().assign_source(source)
        for i in self.init_effect_zones:
            self.source.add_static_zones.append(i)
            self.source.remove_static_zones.append(i)

    # initially apply effect when effect source first enters the battlefield
    def apply_effect(self):
        self.controller.game.addl_state_effects.append(self)
        self.check_effect()

    # function to check whether or not the effect needs to be toggled on/off.
    # called when effect first initializes and when checking state based effects
    def check_effect(self):
        # if its a variable value, always check
        if self.variable_value:
            self.effect_func(self)
        # if its a toggle on/off effect (i.e. variable_value==False), then
        else:
            # only apply if not applied + effect_condition==True, and remove if applied + effect_condition==False.
            if self not in self.source.applied_effects and self.effect_condition(self):
                self.effect_func(self)
                self.source.applied_effects.append(self)
            if self in self.source.applied_effects and self.effect_condition(self)==False:
                self.reverse_effect_func(self)
                self.source.applied_effects.remove(self)

    # function to reverse the effect when effect source leaves the battlefield
    def reverse_effect(self):
        if self in self.source.applied_effects:
            self.reverse_effect_func(self)
            self.source.applied_effects.remove(self)
        self.controller.game.addl_state_effects.remove(self)

# class for effects given by attachments (auras, equipment, counters). Applies/
# reverses effects to the attached object
class Attached_Effect(Static_Effect):
    def __init__(self,**kwargs):
        Static_Effect.__init__(self,**kwargs)
        super()

    def apply_effect(self):
        self.effect_func(self.source.attached_to)
        self.source.attached_to.applied_effects.append(self)

    def reverse_effect(self):
        self.reverse_effect_func(self.source.attached_to)
        self.source.attached_to.applied_effects.remove(self)

# class representing global effects that affect objects other than source object
class Glob_Static_Effect(Static_Effect):
    def __init__(self, effect_condition= lambda applied_obj, source_abil: True,
        own_apply_zones=['field'],opp_apply_zones=[], players=None,**kwargs):
        Static_Effect.__init__(self,**kwargs)
        super()

        # zones that objects affected by effect can be found
        self.own_apply_zones=own_apply_zones
        self.opp_apply_zones=opp_apply_zones
        # whether and which players are affected by effect
        assert(players in ['self','opponent','both',None])
        self.players=players
        # condition which must be true to have effect applied
        self.effect_condition=effect_condition

    def assign_source(self,source):
        super().assign_source(source)
        for i in self.init_effect_zones:
            self.source.add_static_zones.append(i)
            self.source.remove_static_zones.append(i)


    # check whether to apply an effect to a card. The card must meet the apply
    # condition, and the effect condition must be true.
    def apply_to_card(self,card):
        if self not in card.applied_effects and self.effect_condition(card,self):
            self.effect_func(card,self)
            card.applied_effects.append(self)

        # if the effect has been applied and either the apply or effect
        # condition are no longer true, then we remove the effect
        if self in card.applied_effects and self.effect_condition(card,self)==False:
            self.reverse_effect_func(card,self)
            card.applied_effects.remove(self)

    # function that generally applies the the effects when initialized
    def apply_effect(self):
        # first apply to all existing objects in the relevant zones
        self.apply_zones=[]
        for zone in self.own_apply_zones:
            self.apply_zones.append(self.source.controller.__dict__[zone])
        for zone in self.opp_apply_zones:
            self.apply_zones.append(self.source.controller.opponent.__dict__[zone])
        for zone in self.apply_zones:
            # then store effect in zone for applying to future changing cards
            zone.glob_effects.append(self)

        # do initial check for effects
        self.check_effect()

        # finally, add to game state-based effects to keep checking the condition
        self.controller.game.addl_state_effects.append(self)

    # check where effect does/doesn't apply
    def check_effect(self):
        for zone in self.apply_zones:
            for card in zone:
                self.apply_to_card(card)

        # if effect is applied to players, apply accordingly
        if (self.players=='self' or self.players=='both') and self not in \
            self.controller.applied_effects:
            self.effect_func(self.controller, self)
            self.controller.applied_effects.append(self)
        if (self.players=='opponent' or self.players=='both') and self not in \
            self.controller.opponent.applied_effects:
            self.effect_func(self.controller.opponent, self)
            self.controller.opponent.applied_effects.append(self)

    # generally remove the effect from the relevant zones as part of the
    # effect source leaving one of the init_effect_zones
    def reverse_effect(self):
        # first remove effect from all existing objects in the relevant zones
        self.apply_zones=[]
        for zone in self.own_apply_zones:
            self.apply_zones.append(self.source.controller.__dict__[zone])
        for zone in self.opp_apply_zones:
            self.apply_zones.append(self.source.controller.opponent.__dict__[zone])
            getzone=self.source.controller.__dict__[zone]
        for zone in self.apply_zones:
            for card in zone:
                self.remove_from_card(card)

            # remove global effect from zone
            if self in zone.glob_effects:
                zone.glob_effects.remove(self)

        # if effect is applied to players, remove accordingly
        if (self.players=='self' or self.players=='both') and self in \
            self.controller.applied_effects:
            self.reverse_effect_func(self.controller, self)
        if (self.players=='opponent' or self.players=='both') and self in \
            self.controller.opponent.applied_effects:
            self.reverse_effect_func(self.controller.opponent, self)

        # finally remove self from checking in state based effects
        self.controller.game.addl_state_effects.remove(self)

    # remove effect from a specific card
    def remove_from_card(self,card):
        if self in card.applied_effects:
            self.reverse_effect_func(card,self)
            card.applied_effects.remove(self)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

# class for replacement effects; does not use stack
class Replacement_Effect:
    def __init__(self,name,replace_func,replace_points,replace_condition,
        add_replace_zones=['field'], remove_replace_zones=['field'],choices=[]):
        self.name=name
        # trigger points should be a list of strings of keywords in trigger_list.txt
        self.replace_points=replace_points
        self.replace_condition=replace_condition
        # add_replace_zones - zones which entering causes the game to add replace
        # points to. default is just the field
        self.add_replace_zones=add_replace_zones
        # reomve_replace_zones - zones which entering causes the game to remove replace
        # points to. default is just the field
        self.remove_replace_zones=remove_replace_zones
        self.replace_func=replace_func
        self.choices=choices

        # source and controller - to be assigned later
        self.source=None
        self.controller=None
        self.owner=None

    def assign_source(self,source):
        self.source=source
        for i in self.choices:
            i.assign_source(self)
        for i in self.add_replace_zones:
            self.source.add_replace_zones.append(i)
            self.source.remove_replace_zones.append(i)

    def assign_ownership(self,new_owner):
        self.owner=new_owner
        self.controller=new_owner
        for i in self.choices:
            i.assign_ownership(new_owner)

    def assign_controller(self,new_controller):
        self.controller=new_controller
        for i in self.choices:
            i.assign_controller(new_controller)

    # add replace condition checks to the game
    def add_replace_points(self):
        for i in self.replace_points:
            if i in self.source.controller.game.replace_points.keys():
                self.source.controller.game.replace_points[i].append(self)
            else:
                self.source.controller.game.replace_points[i]=[self]

    def remove_replace_points(self):
        for i in self.replace_points:
            if i in self.source.controller.game.replace_points.keys():
                if self.source.controller.game.replace_points[i]==[self]:
                    del self.source.controller.game.replace_points[i]
                else:
                    self.source.controller.game.replace_points[i].remove(self)

    # make choices required by ability
    def make_choices(self):
        for i in self.choices:
            i.make_choice()

    def reset_choices(self):
        for i in self.choices:
            i.choice_made=None

    def get_choices(self,squeeze=True):
        if len(self.choices)==1 and squeeze:
            return self.choices[0].choice_made
        else:
            return[i.choice_made for i in self.choices]

    # replacement effect does not require stack
    def replace_effect(self,effect_kwargs):
        self.replace_func(self,effect_kwargs)
        if self.source.controller.game.verbose>=2:
            print('applying replacement effect', self)
            if self.choices!=[]:
                print(' Choices: ',  self.choices)

    def __repr__(self):
        return self.name #+ str(id(self))[-2:]

    def __str__(self):
        return self.name
