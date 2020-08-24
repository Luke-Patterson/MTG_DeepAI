# define classes for abilities and effects
from Exceptions import *
import inspect

# ===========================================================================
# Concept Classes
# ===========================================================================

# class to capture concept of cost
class Cost:
    def __init__(self,non_mana=[],non_mana_check=[],mana={'C':0}, alt_cost=None,
        cost_mods=[], mana_x_value=False,nonmana_x_value=False, xrange_func= None,
        mana_x_modfunc= None):
        self.non_mana_cost=non_mana
        self.non_mana_check=non_mana_check
        self.mana_cost=mana
        # card should be assigned by card/ability
        self.controller=None
        self.owner=None
        self.source=None
        self.alt_cost=alt_cost
        self.cost_mods=cost_mods
        # whether and function for determining possible xvalues
        # default xrange_func is the amount of mana available to the player
        # after paying all other mana costs
        self.mana_x_value=mana_x_value
        self.nonmana_x_value=nonmana_x_value

        # create a default X function for those spells/abils with X colorless in cost
        def _get_possible_x_mana(self_mana_cost, source):
            source.controller.get_potential_mana()
            # max X value is the largest total mana player can create minus
            # non x costs
            max_X = max([sum(i.values()) for i in source.controller.potential_mana]) - \
                sum(self.mana_cost.values())
            return([i for i in range(max_X+1)])

        def _mana_x_modfunc_default(cost, xval):
            cost['C'] += xval

        if mana_x_value and xrange_func==None:
            self.xrange_func= _get_possible_x_mana
            self.mana_x_modfunc = _mana_x_modfunc_default
        elif mana_x_value:
            self.xrange_func=xrange_func
            self.mana_x_modfunc= mana_x_modfunc
        elif nonmana_x_value:
            self.xrange_func=xrange_func
        else:
            self.xrange_func=None
            self.mana_x_modfunc=None
        self.x_value=0

    def assign_source(self,source):
        self.source=source
        for i in self.cost_mods:
            if i.cost_mod_source==None:
                i.cost_mod_source= self.source

    def assign_ownership(self,new_owner):
        self.owner=new_owner
        self.controller=new_owner

    def assign_controller(self,new_controller):
        self.controller=new_controller

    # check to make sure that non-mana costs can be paid
    def check_non_mana_cost(self):
        pass_check=True
        for i in self.non_mana_check:
            if not i(self.source):
                pass_check=False
        return pass_check

    # check if it cost can be paid
    def check_costs(self, pay_mana_cost=True):
        # pay mana cost is False if mana cost is ignored
        mod_cost=self.mana_cost
        # apply modifications to mana_cost
        for i in self.source.controller.cost_mods:
            if i.check_condition(self):
                mod_cost=i.apply_mod(mod_cost)
        for i in self.cost_mods:
            if i.check_condition(self):
                mod_cost=i.apply_mod(mod_cost)
        # if we have enough mana to do pay, return True: we can play this card,
        # False: we cannot
        if (self.source.controller.check_potential_mana(mod_cost) or pay_mana_cost==False) \
            and self.check_non_mana_cost():
            return(True)
        else:
            return(False)

    def pay_costs(self, mana_shorthand=False, pay_mana_cost=True):
        # apply cost modifications
        mod_cost=self.mana_cost
        for i in self.source.controller.cost_mods:
            if i.check_condition(self):
                mod_cost=i.apply_mod(mod_cost)
        for i in self.cost_mods:
            if i.check_condition(self):
                mod_cost=i.apply_mod(mod_cost)

        # see if cost works
        if mana_shorthand and pay_mana_cost:
            untapped_sources=len([i for i in self.source.controller.field if i.mana_source
                and i.tapped==False])
            if untapped_sources<sum(mod_cost.values()):
                raise GameActionError('mana shorthand detects not enough untapped'+
                    'sources to pay for cost')

        # pay mana costs
        if pay_mana_cost:
            # select value for X if present
            if self.mana_x_value:
                self.x_value=self.controller.input_choose(self.xrange_func(
                    self.mana_cost, self.source))
                if self.controller.game.verbose>=2:
                    print('X value set at', self.x_value)
                mod_cost= self.mana_x_modfunc(mod_cost, self)
            self.source.controller.tap_sources_for_cost(mana_cost=mod_cost,cost_object=self)
            self.source.controller.pay_mana(mod_cost)
        # paying non-mana costs
        # if there's a non-mana X to specify, select value for X
        if self.nonmana_x_value:
            self.x_value= self.controller.input_choose(self.xrange_func(self.source))
            if self.controller.game.verbose>=2:
                print('X value set at', self.x_value)
        #for each non-mana cost, call function
        for cost in self.non_mana_cost:
            cost(self.source)

# class that represents cost modification for certain costs
class Cost_Modification:
    def __init__(self, name, cost_mod, mod_condition, cost_mod_source=None):
        self.name=name
        self.cost_mod=cost_mod
        self.mod_condition=mod_condition
        # source card of cost modification
        self.cost_mod_source=cost_mod_source

    # check if cost object is an applicable cost to modify
    def check_condition(self, cost_obj):
        if self.mod_condition(cost_obj, self.cost_mod_source):
            return True
        else:
            return False

    # apply cost modification to cost
    def apply_mod(self, cost_obj):
        mod_cost=cost_obj.copy()
        for i in self.cost_mod.keys():
            if i in mod_cost.keys():
                mod_cost[i] = mod_cost[i] + self.cost_mod[i]
            else:
                mod_cost[i] = self.cost_mod[i]

            # make numbers 0 if negative
            if mod_cost[i] < 0:
                mod_cost[i] = 0
        return(mod_cost)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

# how to check for potential mana
class Potential_Mana:
    def __init__(self,mana,condition=lambda source: source.tapped==False
        and ('creature' not in source.types or source.summoning_sick==False),
        use_condition=lambda obj: True):
        self.mana=mana
        self.condition=condition
        self.use_condition=use_condition
        self.source=None
        self.linked_abil=None

    def assign_source(self, source):
        self.source=source

    def check_condition(self):
        return self.condition(self.source)


# requirement to meet
class Requirement:
    def __init__(self,condition,source=None):
        self.source=source
        # feed
        self.condition=condition

    def assign_source(self, source):
        self.source=source

    def check_requirement(self):
        return(self.condition(self.source))

# choices for cards/abilities
class Choice:
    def __init__(self,choice_func=None,required=True):
        # choice func - function that takes obj as argument
        self.choice_func=choice_func
        # whether choice is required or no choice is valid
        self.required=required
        self.choice_made=None
        self.controller=None
        self.owner=None
        self.source=None

    def assign_source(self,source):
        self.source=source

    def assign_ownership(self,new_owner):
        self.owner=new_owner
        self.controller=new_owner

    def assign_controller(self,new_controller):
        self.controller=new_controller

    def make_choice(self):
        try:
            self.choice_made=self.choice_func(self)
        except:
            if self.required==False:
                pass
            else:
                raise GameActionError('Error: mandatory choice has no valid options')

    def check_choice(self):
        if self.required:
            try:
                self.choice_func(self)
                return True
            except:
                return False
        else:
            return True

    def __repr__(self):
        if self.choice_made!=None:
            return str(self.choice_made)
        else:
            return 'choice object'

    def __str__(self):
        if self.choice_made!=None:
            return str(self.choice_made)
        else:
            return 'choice object'


# object to represent target; setting target according to condition, then
# checking on resolution
class Target:
    def __init__(self,criteria,name=None,c_zones=['field'],c_players=None,c_own=True,
        c_opponent=True,c_source=None,c_different=False,c_required=True,
        c_self_target=True,c_stack=False, mode_linked=False, mode_num=0, any_num_of_target=False):
        self.name=name
        # source and controller to be defined by source of target
        self.source=None
        self.owner=None
        self.controller=None

        # attributes that will store the target obj, and the zone it was initially in
        self.target_obj=None
        self.zone=None
        self.zone_hash=None

        # couple of different inputs for the possible targets thing
        self.criteria= criteria
        # zones that can be checked for objects
        self.c_zones=c_zones
        # whether self and/or opponent can be targeted
        self.c_players=c_players
        # whether to check self's c_zones
        self.c_own=c_own
        # whether to check opponents' c_zones
        self.c_opponent=c_opponent
        # what to note as the source of the target (for things like checking protection)
        if c_source==None:
            self.c_source=self.source
        else:
            self.c_source=c_source
        # if multiple targets need to be selected and need to be distinct
        self.c_different=c_different
        # if target has to or doesn't have to be selected
        self.c_required=c_required
        # if it can target itself
        self.c_self_target=c_self_target
        # whether it can target objects on the stack
        self.c_stack=c_stack
        # whether the target is linked to a mode, and if so what mode
        self.mode_linked=mode_linked
        self.mode_num=mode_num

    def make_copy(self):
        # not using deepcopy which would copy too much; instead create new instance
        # and set all the attributes of the original object to the new one
        clone=Target(criteria=self.criteria)
        clone.name=self.name
        clone.source=self.source
        clone.owner=self.owner
        clone.controller=self.controller
        clone.target_obj=self.target_obj
        clone.zone=self.zone
        clone.zone_hash=self.zone_hash
        clone.criteria=self.criteria
        clone.c_zones=self.c_zones
        clone.c_players=self.c_players
        clone.c_own=self.c_own
        clone.c_opponent=self.c_opponent
        clone.c_source=self.c_source
        clone.c_different=self.c_different
        clone.c_required=self.c_required
        clone.c_self_target=self.c_self_target
        return clone

    def assign_source(self,source):
        if self.c_source==self.source:
            self.c_source=source
        self.source=source

    def assign_ownership(self,new_owner):
        self.owner=new_owner
        self.controller=new_owner

    def assign_controller(self,new_controller):
        self.controller=new_controller

    def get_possible_targets(self):
        possible_targets=self.controller.get_legal_targets(
            criteria=self.criteria,
            zones=self.c_zones,
            players=self.c_players,
            own=self.c_own,
            opponent=self.c_opponent,
            source=self.c_source,
            different=self.c_different,
            self_target=self.c_self_target,
            stack=self.c_stack
        )
        return(possible_targets)

    def set_possible_target(self):

        # if mode-linked, check to see if linked mode is selected. skip setting
        # target entirely if not
        if self.mode_linked and self.source.selected_mode!=self.mode_num:
            return

        possible_targets=self.get_possible_targets()


        # check possible targets and validate whether selected target will still
        # allow valid costs/choices/requirements to be made
        legal_targets=[]
        for i in possible_targets:
            self.target_obj=i
            if self.source.check_costs() and self.source.check_choices() and \
                self.source.check_requirements():
                legal_targets.append(i)
            self.target_obj=None

        # if self.source.name=='Captivating Gyre':
        #     import pdb; pdb.set_trace()
        #
        if legal_targets==[]:
            # up to parameter; if it's from a source with "up to x targets", allow
            # no targets to be selected
            if self.c_required==False:
                return
            else:
                raise GameActionError('Error: no legal targets')

        target=self.controller.input_choose(legal_targets)
        #print(self,'legal targets', legal_targets)
        self.target_obj=target
        if self.controller.game.verbose>=2:
            print(self)
        if 'player' not in target.types:
            self.zone=target.zone
            self.zone_hash=target.zone_hash

        # trigger on target triggers
        self.controller.game.triggers('on target', target_source=self.source, targeted_obj=target)

    def check_target_zones(self):
        # if mode-linked, check to see if linked mode is selected. skip setting
        # target entirely if not
        if self.mode_linked and self.source.selected_mode!=self.mode_num:
            return True

        # if not targeting anything (due to optional "up to" targetting), just
        # return true.
        if self.target_obj==None:
            # shouldn't be checking target zones for None on required targets
            if self.c_required:
                raise GameActionError('Error: no target found when required')
            return True

        # if targeting a player, don't need to do this check
        if 'player' in self.target_obj.types:
            return True

        possible_targets=self.controller.get_legal_targets(
            criteria=self.criteria,
            zones=self.c_zones,
            players=self.c_players,
            own=self.c_own,
            opponent=self.c_opponent,
            source=self.c_source,
            #different=self.c_different,
            # since targets are already assigned, "different" no longer applicable
            different=False,
            self_target=self.c_self_target,
            stack=self.c_stack
        )
        # make sure obj still in same zone and still a legal target
        # Zone hash check should make sure "blinking" resets a target properly
        if self.target_obj.zone == self.zone and self.target_obj in possible_targets \
            and self.target_obj.zone_hash == self.zone_hash:
            return True
        else:
            return False

    def __repr__(self):
        return str(self.source) + ' targeting ' + str(self.target_obj)

    def __str__(self):
        return str(self.source) + ' targeting ' + str(self.target_obj)

# static abil trait protection from characteristic
class Protection:
    def __init__(self,condition, name=None, source=None, hexproof_from=False):
        self.condition=condition
        # modify if protection is just "hexproof_from"
        self.hexproof_from=hexproof_from
        self.source=source
        self.name=name
        if source!=None:
            self.owner=source.owner
            self.controller=source.controller
        else:
            self.owner=None
            self.controller=None

    def assign_source(self,source):
        self.source=source

    def assign_ownership(self,new_owner):
        self.owner=new_owner
        self.controller=new_owner

    def assign_controller(self,new_controller):
        self.controller=new_controller

    def check_protect(self, obj):
        from Abilities_Effects import Triggered_Ability
        from Abilities_Effects import Activated_Ability
        if isinstance(obj, Triggered_Ability) or isinstance(obj, Activated_Ability):
            return(self.condition(obj.source))
        else:
            return(self.condition(obj))
