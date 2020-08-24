# define classes of cards and card types

from collections import Counter
import inspect
import random
from Exceptions import *
from Abilities_Effects import *

class Card:
    def __init__(self,name,rarity=None,cost=[Cost(mana={'C':0})],types=[],subtypes=[],mana_source=False,
        indep=True,flash=False,choices=[], targets=[],potential_mana=[],
        keyword_static_abils=[],nonkeyword_static_abils=[],
        activated_abils=[],triggered_abils=[],replace_effects=[],
        colors=None,protection_effects=[],requirements=[], moded=False, n_modes=1,
        mode_labels=[],lki_func=None, power=None, toughness=None):
        # print_name is what is printed on object
        self.print_name=name
        # name is an identifier of identical objects; modifying effects will change this
        self.name=name
        self.mana_source=mana_source
        # keep track of what zone they are in and what they came from
        self.zone=None
        self.zone_hash=None
        self.prev_zone=None
        # keep track of when it moved into its current zone
        self.zone_turn=None
        # indep, whether order matters when tapping as a mana source
        self.indep=indep
        self.owner=None
        self.controller=None
        self.verbose=None
        self.flash=flash
        self.keyword_static_abils=keyword_static_abils
        if self.check_keyword('flash'):
            self.flash=True
        # store protection effects
        self.protection_effects=protection_effects
        # add global static abilities
        self.add_static_zones=[]
        self.remove_static_zones=[]
        self.nonkeyword_static_abils=nonkeyword_static_abils
        # add activated abilities
        self.activated_abils=activated_abils
        self.damage_received=0
        self.moded=moded
        if moded:
            self.n_modes=n_modes
        else:
            self.n_modes=1
        self.selected_mode=None
        self.legal_modes=[]
        self.mode_labels=mode_labels

        # costs
        # if cost not passed as a list, make cost a list
        if isinstance(cost,list):
            self.cost=cost
        else:
            self.cost=[cost]
        self.cmc=sum(self.cost[0].mana_cost.values())
        # tracking which cost methods are valid if multiple
        self.valid_costs=[]
        # choices to be made on cast, make it a list if just a single object
        if isinstance(choices,list)==False:
            choices=[choices]
        self.choices=choices
        if isinstance(targets,list)==False:
            targets=[targets]
        self.targets=targets
        self.rarity=rarity
        # set types
        self.types=types
        self.subtypes=subtypes
        # trigger helper objects
        self.add_trigger_zones=[]
        self.remove_trigger_zones=[]
        self.trigger_points_added=False
        self.triggered_abils=triggered_abils
        self.add_replace_zones=[]
        self.remove_replace_zones=[]
        self.replace_points_added=False
        self.replace_effects=replace_effects
        # unless otherwise set, color is just derived from cost mana symbols
        if colors==None:
            self.colors=list(self.cost[0].mana_cost.keys())
            # remove colorless if any other color present
            if self.colors!=['C'] and 'C' in self.colors:
                self.colors.remove('C')
        else:
            self.colors=colors
        self.colors=sorted(self.colors)
        # list of attached objects (counters, auras, equipements)
        self.attached_objs=[]
        # list of attached effects (effects without objects directly associated,
        # global pump effects, etc.)
        self.applied_effects=[]
        # list to keep track of effects expiring end of turn
        self.EOT_reverse_effects=[]
        self.EOT_toughness_pump=0
        self.EOT_power_pump=0
        self.EOT_keywords=[]
        # effects expiring at next turn of a player
        self.next_turn_reverse_effects=[]
        # keep track of requirements for casting spell
        self.requirements=requirements
        # keep track of mana source could potentially produce
        self.potential_mana=potential_mana
        self.potential_mana_values=[]
        # track when we are doing ETB static abil checks
        self.ETB_static_check=False
        # object to keep track of who and how much damage is dealt
        self.dmg_dealt=[]
        # track if deathtouch damage was received
        self.deathtouch_damage=False
        # track hard coded orig stats, used when cloned
        self.orig_attribs={}
        self.copying=None
        # function for tracking last known info
        self.lki_func=lki_func
        # tracking last known info
        self.last_known_info=None
        # whether to exile on resolve
        self.exile_on_resolve=False
        # creature-specific attributes
        self.damage_received=0
        # combat status
        self.attacking=False
        self.blocking=False
        self.blocked=False
        self.is_blocking_attacker=None
        # creature chars
        self.base_power=power
        self.base_toughness=toughness
        self.power=power
        self.toughness=toughness
        self.tapped=False
        self.assign_sources()

    # for representing attached objs, we don't want them to appear separately,
    # but rather nested within their attached object
    def __repr__(self):
        pname = self.print_name
        if self.copying!=None:
            pname = pname +  ' copying ' + self.copying.print_name
        if self.attached_objs!=[]:
            pname = pname +  ' ' + str([i.print_name for i in self.attached_objs])
        return pname

    def __str__(self):
        pname = self.print_name
        if self.copying!=None:
            pname = pname +  ' copying ' + self.copying.print_name
        if self.attached_objs!=[]:
            pname = pname +  ' ' + str([i.print_name for i in self.attached_objs])
        return pname

    # =======================================================
    # Set ownership/source functions
    # =======================================================

    # change ownership of card
    def assign_ownership(self,new_owner):
        self.owner=new_owner
        self.controller=new_owner
        # make list of the abilites and attributes of the card
        attribs=['activated_abils','nonkeyword_static_abils','triggered_abils'
            ,'replace_effects', 'choices', 'targets','protection_effects',
            'applied_effects']
        # check for type-specific objects that need to be changed
        for i in ['aura_static_effect','equip_static_effect']:
            if i in self.__dict__.keys():
                attribs.append(i)
        for attrib in attribs:
            att=self.__dict__[attrib]
            if isinstance(att, list):
                for obj in att:
                    obj.assign_ownership(new_owner)
            else:
                att.assign_ownership(new_owner)

    # change control of a card
    def assign_controller(self, new_controller, gain_control=False):
        prev_controller=self.controller
        self.controller=new_controller
        # make list of the abilites and attributes of the card
        attribs=['activated_abils','nonkeyword_static_abils','triggered_abils'
            ,'replace_effects', 'choices', 'targets','protection_effects']
        # check for type-specific objects that need to be changed
        for i in ['aura_static_effect','equip_static_effect']:
            if i in self.__dict__.keys():
                attribs.append(i)
        for attrib in attribs:
            att=self.__dict__[attrib]
            if isinstance(att, list):
                for obj in att:
                    obj.assign_controller(new_controller)
            else:
                att.assign_controller(new_controller)

        # if it's on the battlefield and switching controller
        # , switch to the new_controller's zone w/o
        # triggering enter/leave effects. Also make summoning sick
        if self.zone.zone_type=='field' and self.controller!=prev_controller \
            and gain_control:
            self.zone.leave_zone(self, leave_effects=False)
            self.controller.field.enter_zone(self, enter_effects=False)
            self.summoning_sick=True

    # change attributes for copying another card
    def become_copy(self,copy_source):
        zone = self.zone.zone_type
        # remove original's ability zones/points
        if zone in self.remove_trigger_zones and self.trigger_points_added==True:
            for i in self.triggered_abils:
                if zone in i.remove_trigger_zones:
                    i.remove_trigger_points()
            self.trigger_points_added=False

        if zone in self.remove_replace_zones and self.replace_points_added==True:
            for i in self.replace_effects:
                if zone in i.remove_replace_zones:
                    i.remove_replace_points()
            self.replace_points_added=False

        if zone in self.remove_static_zones:
            for abil in self.nonkeyword_static_abils:
                if zone in abil.init_effect_zones:
                    abil.reverse_effect()

        # if a creature is becoming a non-creature, remove it from combat
        if 'creature' in self.types and 'creature' not in copy_source.types and \
            (self.attacking or self.blocking):
            self.remove_from_combat()

        # copy over attributes
        for attrib in ['name','mana_source','flash','keyword_static_abils','protection_effects',
            'add_static_zones','remove_static_zones','nonkeyword_static_abils',
            'activated_abils','cost','types','subtypes','add_trigger_zones',
            'remove_trigger_zones','trigger_points_added','triggered_abils',
            'add_replace_zones','remove_replace_zones','replace_effects',
            'potential_mana','colors','base_power','base_toughness','power',
            'toughness']:

            # store original attributes in dict
            if attrib in self.__dict__.keys():
                self.orig_attribs[attrib]=self.__dict__[attrib]

            # set copy's attributes
            if attrib in copy_source.__dict__.keys():
                self.__dict__[attrib]=copy_source.__dict__[attrib]
            elif attrib in self.__dict__.keys():
                del self.__dict__[attrib]

        self.copying= copy_source

        # apply any effects that are now added
        if zone in self.add_trigger_zones and self.trigger_points_added==False:
            for i in self.triggered_abils:
                if zone in i.add_trigger_zones:
                    i.add_trigger_points()
            self.trigger_points_added=True

        if zone in self.add_replace_zones and self.replace_points_added==False:
            for i in self.replace_effects:
                if zone in i.add_replace_zones:
                    i.add_replace_points()
            self.replace_points_added=True

        if zone in self.add_static_zones:
            for abil in self.nonkeyword_static_abils:
                if zone in abil.init_effect_zones:
                    abil.apply_effect()

    def revert_copy(self):
        zone = self.zone.zone_type

        # remove clone's ability zones/points
        if zone in self.remove_trigger_zones and self.trigger_points_added==True:
            for i in self.triggered_abils:
                if zone in i.remove_trigger_zones:
                    i.remove_trigger_points()
            self.trigger_points_added=False

        if zone in self.remove_replace_zones and self.replace_points_added==True:
            for i in self.replace_effects:
                if zone in i.remove_replace_zones:
                    i.remove_replace_points()
            self.replace_points_added=False

        if zone in self.remove_static_zones:
            for abil in self.nonkeyword_static_abils:
                if zone in abil.init_effect_zones:
                    abil.reverse_effect()

        # if a creature is becoming a non-creature, remove it from combat
        if 'creature' in self.types and 'creature' not in self.orig_attribs['types'] and \
            (self.attacking or self.blocking):
            self.remove_from_combat()

        # revert to original attributes
        for attrib in ['name','mana_source','flash','keyword_static_abils','protection_effects',
            'add_static_zones','remove_static_zones','nonkeyword_static_abils',
            'activated_abils','cost','types','subtypes','add_trigger_zones',
            'remove_trigger_zones','trigger_points_added','triggered_abils',
            'add_replace_zones','remove_replace_zones','replace_effects',
            'potential_mana','colors','base_power','base_toughness','power',
            'toughness']:
            if attrib in self.orig_attribs.keys():
                self.__dict__[attrib]=self.orig_attribs[attrib]
            elif attrib in self.__dict__.keys():
                del self.__dict__[attrib]
        self.copying= None

        # apply any effects that are now added
        if zone in self.add_trigger_zones and self.trigger_points_added==False:
            for i in self.triggered_abils:
                if zone in i.add_trigger_zones:
                    i.add_trigger_points()
            self.trigger_points_added=True

        if zone in self.add_replace_zones and self.replace_points_added==False:
            for i in self.replace_effects:
                if zone in i.add_replace_zones:
                    i.add_replace_points()
            self.replace_points_added=True

        if zone in self.add_static_zones:
            for abil in self.nonkeyword_static_abils:
                if zone in abil.init_effect_zones:
                    abil.apply_effect()


    # assign sources for child objects; done when copying a card
    def assign_sources(self):
        for i in self.cost:
            i.assign_source(self)
        # make copy of the abilites and attributes of the card
        attribs=['activated_abils','nonkeyword_static_abils','triggered_abils'
            ,'replace_effects', 'choices', 'targets','protection_effects',
            'requirements','potential_mana']
        # check for type-specific objects that need to be copied
        for i in ['aura_static_effect','equip_static_effect']:
            if i in self.__dict__.keys():
                attribs.append(i)
        for attrib in attribs:
            a=self.__dict__[attrib]
            if isinstance(a, list):
                for obj in a:
                    obj.assign_source(self)
            else:
                a.assign_source(self)

    # =======================================================
    # Creature-specific Functions
    # =======================================================
    def legal_attacker(self):
        assert('creature' in self.types)
        if self.tapped==False and self.summoning_sick==False and \
        self.check_keyword('defender')==False and self.check_keyword('cant_block')==False:
            return True
        else:
            return False

    # is the card a generally legal blocker
    def legal_blocker(self):
        assert('creature' in self.types)
        if self.tapped==False and self.check_keyword('cant_block')==False:
            return True
        else:
            return False

    # can the card block a specific attacker?
    def legal_block_pair(self,attacker, other_blockers):
        assert('creature' in self.types)
        if self.is_blocking_attacker!=None:
            return False
        if self.check_keyword('unblockable'):
            return False
        if attacker.check_keyword('flying') and self.check_keyword('flying')==False \
            and self.check_keyword('reach')==False:
            return False
        # check for other blocker if it has cant_be_double_blocked
        if attacker.check_keyword('cant_be_double_blocked') and \
            len(other_blockers)>=1:
            return False

        protect=False
        for j in attacker.protection_effects:
            if j.hexproof_from==False and j.check_protect(self):
                protect=True
        if protect:
            return False
        return True

    def declare_as_attacker(self,targets):
        assert('creature' in self.types)
        # pick a target
        self.atk_target=self.controller.input_choose(targets, label='attack target')
        if self.check_keyword('vigilance')==False:
            self.tapped=True
        self.attacking=True
        if 'on attack' in self.controller.game.trigger_points.keys():
            self.controller.game.triggers('on attack', obj=self)

    def declare_as_blocker(self,attacker):
        assert('creature' in self.types)
        self.blocking=True
        attacker.blocked=True
        self.is_blocking_attacker=attacker
        if 'on block' in self.controller.game.trigger_points.keys():
            self.controller.game.triggers('on block', blocker=self)

    def remove_from_combat(self, untap=False, attacker_remains_blocked=True):
        assert('creature' in self.types)
        self.attacking=False
        self.blocking=False
        if attacker_remains_blocked==False:
            attacker.blocked=False
        self.is_blocking_attacker=None
        if untap:
            self.untap()

    def deal_combat_damage(self, targets):
        assert('creature' in self.types)
        if self.check_keyword('tough_assign'):
            dmg=self.toughness
        else:
            dmg=self.power
        # track who received how much damage
        self.dmg_dealt=[]
        # if attacking and not blocked, deal damage to opponent
        if self.attacking and self.blocked==False and self.atk_target==self.controller.opponent:
            self.controller.opponent.change_life(-1*dmg, combat=True)
            self.dmg_dealt.append([self.atk_target, dmg])
        # if attacked and not blocked and attacking planeswalker, deal damage to planeswalker
        if self.attacking and self.blocked==False and self.atk_target!=self.controller.opponent:
            assert 'planeswalker' in self.atk_target.types, 'Error: not attacking' + \
                ' player or planeswalker'
            self.atk_target.change_loyalty(-1*dmg,pay=False)
            self.dmg_dealt.append([self.atk_target, dmg])
            if self.controller.game.verbose>=2:
                print(self.atk_target,'loses',dmg,'loyalty from combat')
        # else deal the damage
        if targets!=[]:
            dmg_deal=dmg
            for i in targets:
                # assign differently for deathtouch creatures
                if self.check_keyword('deathtouch'):
                    # deathtouch and trample means only 1 damage needs to be assigned
                    # to last creature if attacking
                    if dmg_deal>0 and (i!=targets[-1] or (self.check_keyword('trample')
                        and self.attacking)):
                        # option to assign more damage to blocker if desired.
                        # At minimum must assign 1 damage per blocker
                        dmg_assign=self.controller.input_choose(range(1,
                            dmg_deal+1), label='assigning damage')
                        dmg_deal-=dmg_assign
                        i.take_damage(dmg_assign, source=self, deathtouch=True)
                        self.dmg_dealt.append([i, dmg_assign])
                    else:
                        i.take_damage(dmg_deal, source=self)
                        self.dmg_dealt.append([i, dmg_deal])
                        dmg_deal=0
                else:
                    # check to see if there are other creatures to deal damage to,
                    # and if we can first assign lethal damage to this creature
                    # before moving on to the next.
                    # tramplers do not need to assign rest
                    if dmg_deal>(i.toughness-i.damage_received) and (i!=targets[-1]
                        or (self.check_keyword('trample') and self.attacking)):
                        # option to assign more damage to blocker if desired.
                        # At minimum must assign toughness though if possible
                        dmg_assign=self.controller.input_choose([i for i in range(
                            i.toughness-i.damage_received, dmg_deal+1)],
                            label='assigning damage')
                        i.take_damage(dmg_assign, source=self)
                        dmg_deal-=dmg_assign
                        self.dmg_dealt.append([i, dmg_assign])
                    else:
                        i.take_damage(dmg_deal, source=self)
                        self.dmg_dealt.append([i, dmg_deal])
                        dmg_deal=0
            # finally, if there's any damage left over and it's attacking,
            # opponent takes excess damage
            if dmg_deal!=0 and self.check_keyword('trample') and self.attacking:
                self.controller.opponent.take_damage(dmg_deal, source=self, combat=True)
                dmg_deal=0

    def check_lethal_damage(self):
        assert('creature' in self.types)
        if ((self.damage_received>=self.toughness) or \
            (self.damage_received>0 and self.deathtouch_damage)) and \
            self.check_keyword('indestructible')==False:
            if self.controller.game.verbose>=2:
                print(self, 'has taken lethal damage:', self.damage_received)
            self.dies()

    def fight(self, other):
        self.take_damage(other.power,source=other, deathtouch=
            other.check_keyword('deathtouch'), combat=False)
        other.take_damage(self.power,source=self, deathtouch=
            self.check_keyword('deathtouch'), combat=False)

    def take_damage(self,num,source,deathtouch=False, combat=True):
        protect=False
        # check if any protection effects conditions are met
        for j in self.protection_effects:
            if j.hexproof_from==False and j.check_protect(source):
                protect=True
                if self.controller.game.verbose>=2:
                    print(self, 'prevented damage from',source,'due to protection',
                    inspect.getsource(j.condition))
                break
        # if not, and the permanent is still on the field, deal damage
        if protect==False and self.zone.zone_type=='field':
            self.damage_received+=num
            if deathtouch:
                self.deathouch_received=True
            if self.check_keyword('lifelink') and num>0:
                source.controller.change_life(num)
            if combat and num>0:
                source.controller.game.triggers('combat damage dealt',
                    source=source, receiver=self, num=num)
            if 'planeswalker' in self.types:
                self.change_loyalty(-1*num, pay=False)

            # if we need to check whether damage successfully dealt, we'll
            # return true or false
            return(True)
        return(False)

    def dies(self):
        assert('creature' in self.types)
        if self.controller.game.verbose>=2:
            print(self, 'dies')
        self.controller.field.leave_zone(self)
        if self.check_keyword('exile_on_death'):
            self.owner.exile.enter_zone(self)
            if self.controller.game.verbose>=2:
                print(self, 'is exiled')
        else:
            self.controller.game.triggers('dies', obj=self)
            self.owner.yard.enter_zone(self)

    def change_power(self,num):
        if 'power' in self.__dict__.keys() and self.power!=None:
            self.power+=num

    def change_toughness(self,num):
        if 'toughness' in self.__dict__.keys() and self.toughness!=None:
            self.toughness+=num
    # =======================================================
    # Requirements functions
    # =======================================================

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
            return self.choices[0].choice_made
        else:
            return[i.choice_made for i in self.choices]

    # make choices required to play card
    def make_choices(self):
        for i in self.choices:
            i.make_choice()

    # make sure there are legal
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
    # Checking legality of targets, choices, and requirements
    # =======================================================
    # check to make sure it's legal to cast the card/activate ability
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
                        # investigative code
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
                    return(False)
            elif self.check_costs()==False:
                return(False)
            return(True)

    # =======================================================
    # Functions for casting and resolving card
    # =======================================================
    # put the card on the stack
    def play_card(self,from_zone=None,exile_on_resolve=False, pay_mana_cost=True):
        # from_zone parameter should just be whatever zone card is currently in
        from_zone= self.zone
        # if moded, choose mode based from legal modes
        if self.moded:
            self.selected_mode=self.controller.input_choose([i for i in self.legal_modes])
        # set targets
        self.set_targets()
        # make choices
        self.make_choices()
        # check requirements
        self.check_requirements()
        # pay costs - run check costs again to ensure we have set self.valid_costs
        self.check_costs(pay_mana_cost=pay_mana_cost)
        self.controller.input_choose(self.valid_costs, label='alt cost selection') \
            .pay_costs(pay_mana_cost=pay_mana_cost)
        from_zone.leave_zone(self)
        if self.lki_func!=None:
            self.last_known_info=self.lki_func(self)
        self.controller.game.stack.enter_zone(self)
        self.exile_on_resolve=exile_on_resolve
        self.controller.turn_spell_count+=1
        for i in self.colors:
            self.controller.turn_spell_colors.append(i)
        self.controller.game.triggers('cast spell',casted_spell=self,effect_kwargs={'casted_spell':self})

    # check to see if costs can be paid
    def check_costs(self, pay_mana_cost=True):
        possible_costs=[]
        for i,cost in enumerate(self.cost):
            if cost.check_costs(pay_mana_cost=pay_mana_cost):
                possible_costs.append(cost)
        if possible_costs==[]:
            return(False)
        else:
            self.valid_costs = possible_costs
            return(True)

    def play_msg(self):
        print(self.controller, 'Playing', self)
        if self.choices!=[]:
            print(' Choices: ',  self.choices)
        if self.targets!=[]:
            print(' Targets: ',  self.targets)
        if self.selected_mode!=None:
            print(' Mode: ',  self.mode_labels[self.selected_mode-1])

    # check to see if keyword is present and no "loses" keyword is present
    def check_keyword(self, keyword):
        result = keyword in self.keyword_static_abils and \
            'loses_'+keyword not in self.keyword_static_abils
        # if both are present, then whichever was applied last dominates
        if keyword in self.keyword_static_abils and 'loses_'+keyword in \
            self.keyword_static_abils:
            kword_idx= len(self.keyword_static_abils) - self.keyword_static_abils[::-1].index(keyword) - 1
            loses_idx= len(self.keyword_static_abils) - self.keyword_static_abils[::-1].index('loses_'+keyword) - 1
            if kword_idx > loses_idx:
                result=True
            else:
                result=False
        return(result)

    # remove keyword if present
    def remove_keyword(self, keyword):
        if keyword in self.keyword_static_abils:
            self.keyword_static_abils.remove(keyword)
        elif self.controller.game.verbose>=2:
            print('Warning:', keyword, 'not in', self, 'keyword_static_abils')

    # add keyword
    def add_keyword(self, keyword):
        self.keyword_static_abils.append(keyword)

    def resolve(self, to_zone='field'):
        self.controller.game.stack.leave_zone(self)
        self.controller.__dict__[to_zone].enter_zone(self)
        self.summoning_sick=True
        self.controller=self.controller

    def discard_from_hand(self):
        if self.controller.game.verbose>=2:
            print(self.controller,'discards',self)
        self.owner.hand.leave_zone(self)
        self.owner.yard.enter_zone(self)
        self.owner.game.triggers('discard',discarded_obj=self, effect_kwargs={'discarded_obj':self})

    def counterspelled(self):
        if self.check_keyword('uncounterable') or self.controller.check_keyword('all_uncounterable'):
            if self.controller.game.verbose>=2:
                print(self, "can't be countered")
        else:
            self.controller.game.stack.leave_zone(self)
            self.owner.yard.enter_zone(self)
            if self.owner.game.verbose>=2:
                print(self,'is countered')

    def tap(self, for_cost=True, summoning_sick_ok=False):
        if self.tapped and for_cost:
            raise GameActionError('Card already tapped')
        if for_cost and self.summoning_sick and summoning_sick_ok==False and 'creature' in self.types:
            raise GameActionError('Attempting to tap summoning sick creature')
        self.tapped=True

    def is_permanent(self):
        if 'instant' in self.types or 'sorcery' in self.types:
            return(False)
        else:
            return(True)

    def enter_zone_effects(self,zone):
        if zone in self.add_trigger_zones and self.trigger_points_added==False:
            for i in self.triggered_abils:
                if zone in i.add_trigger_zones:
                    i.add_trigger_points()
            self.trigger_points_added=True

        if zone in self.add_replace_zones and self.replace_points_added==False:
            for i in self.replace_effects:
                if zone in i.add_replace_zones:
                    i.add_replace_points()
            self.replace_points_added=True

        if zone in self.add_static_zones:
            for abil in self.nonkeyword_static_abils:
                if zone in abil.init_effect_zones:
                    abil.apply_effect()

        # moving this from beginning to end of the function so trigger points
        # for ETB effects will be added before they are checked
        if zone == 'field':

            # apply "as enters battlefield" static effects
            self.ETB_static_check=True
            self.controller.game.check_state_effects()
            self.ETB_static_check=False
            self.tapped=False
            if 'etb_tapped' in self.keyword_static_abils:
                self.tapped=True

            # check for ETB triggered abils
            if 'enter field' in self.controller.game.trigger_points.keys():
                self.controller.game.triggers('enter field', obj=self,effect_kwargs={'obj':self})


    def leave_zone_effects(self,zone):

        self.damage_received=0
        self.counters={}
        self.attacking=False
        self.blocking=False
        self.blocked=False
        self.is_blocking_attacker=None

        # remove trigger checks
        if zone in self.remove_trigger_zones and self.trigger_points_added==True:
            for i in self.triggered_abils:
                if zone in i.remove_trigger_zones:
                    i.remove_trigger_points()
            self.trigger_points_added=False

        # remove replacement effects
        if zone in self.remove_replace_zones and self.replace_points_added==True:
            for i in self.replace_effects:
                if zone in i.remove_replace_zones:
                    i.remove_replace_points()
            self.replace_points_added=False

        # remove static effects
        if zone in self.remove_static_zones:
            for abil in self.nonkeyword_static_abils:
                if zone in abil.init_effect_zones:
                    abil.reverse_effect()

        # battlefield-specific leave effects
        if zone=='field':
            self.tapped=False
            # remove all counters
            self.counters=[]
            # revert temporary power/toughness pumps
            self.change_power(-1*self.EOT_power_pump)
            self.change_toughness(-1*self.EOT_toughness_pump)
            self.EOT_power_pump=0
            self.EOT_toughness_pump=0
            # remove temporary keywords granted
            for i in self.EOT_keywords:
                self.remove_keyword(i)
            self.EOT_keywords=[]

            # remove any temporary effects applied to the card
            for i in self.EOT_reverse_effects:
                i(self)
                self.EOT_reverse_effects.remove(i)

            for i in self.next_turn_reverse_effects:
                i[1](self)
                self.next_turn_reverse_effects.remove(i)

            # revert controller to owner, if not the same
            if self.controller!=self.owner:
                self.assign_controller(self.owner)

        # check if any triggered abils are removed once they leave a zone
        rm_abils=[]
        for i in self.triggered_abils:
            if i.remove_on_leave_zone:
                rm_abils.append(i)
        for i in rm_abils:
            self.triggered_abils.remove(i)

    def EOT_cleanup(self):
        self.damage_received=0
        self.deathtouch_damage=False
        # reset dmg dealt tracking object
        self.dmg_dealt=[]

        # revert temporary power/toughness pumps
        self.change_power(-1*self.EOT_power_pump)
        self.change_toughness(-1*self.EOT_toughness_pump)
        self.EOT_power_pump=0
        self.EOT_toughness_pump=0

        # remove temporary keywords granted
        for i in self.EOT_keywords:
            self.remove_keyword(i)
        self.EOT_keywords=[]

        # reverse applied effects
        for effect in self.EOT_reverse_effects:
            effect(self)
            self.EOT_reverse_effects.remove(effect)

        # check to see if next turn effects are reversed
        # expecting objects in this list to be two length lists,
        # first is the player whose next turn the effect will expire
        # second is the reverse effect function
        for i in self.next_turn_reverse_effects:
            # check if this is the end of the turn of the player not listed.
            # if so, then we want to apply the reverse effect, as that players
            # turn is coming up
            if self.controller.game.act_plyr != i[0]:
                i[1](self)
                self.next_turn_reverse_effects.remove(i)


    def untap(self):
        self.tapped=False

    def sacrifice(self):
        self.controller.field.leave_zone(self)
        self.owner.yard.enter_zone(self)
        if self.owner.game.verbose>=2:
            print(self.controller,'sacrifices',self)

    def exile(self):
        self.zone.leave_zone(self)
        self.owner.exile.enter_zone(self)
        if self.owner.game.verbose>=2:
            print(self.controller,'exiles',self)

    def destroy(self):
        if self.check_keyword('indestructible')==False:
            self.controller.field.leave_zone(self)
            self.owner.yard.enter_zone(self)
        if self.owner.game.verbose>=2:
            print(self,'is destroyed')

    def bounce(self):
        if self.controller.game.verbose>=2:
            print(self, 'bounced')
        self.controller.field.leave_zone(self)
        self.owner.hand.enter_zone(self)

    def put_on_top_of_lib(self):
        self.zone.leave_zone(self)
        self.owner.lib.enter_zone(self, pos=0)

    def shuffle_into_lib(self):
        self.zone.leave_zone(self)
        self.owner.lib.enter_zone(self, pos=0)
        self.owner.shuffle_lib()


# Card types - subclass of Card

class Creature(Card):
    def __init__(self,types=['creature'],**kwargs):
        Card.__init__(self,types=types,**kwargs)
        super()

    def enter_zone_effects(self,zone):
        super().enter_zone_effects(zone)

    def leave_zone_effects(self,zone):
        super().leave_zone_effects(zone)

    def EOT_cleanup(self):
        super().EOT_cleanup()


class Land(Card):
    def __init__(self,name,indep=True,types=['land'],**kwargs):
        Card.__init__(self,name,types=types,**kwargs)
        super()
        self.mana_source=True
        self.tapped=False

        #indep -> lands for which all abilities are independent of the order they are tapped
        self.indep=indep

    def play_card(self):
        self.owner.hand.leave_zone(self)
        self.controller.field.enter_zone(self)
        self.controller.land_drops-=1

    def resolve(self):
        raise 'Error: trying to resolve land'

    def enter_zone_effects(self,zone):
        super().enter_zone_effects(zone)

    def leave_zone_effects(self,zone):
        super().leave_zone_effects(zone)

    def put_on_stack(self):
        raise 'Error: trying to put land on the stack'

class Sorcery(Card):
    def __init__(self,spell_effect,types=['sorcery'],**kwargs):
        Card.__init__(self,types=types,**kwargs)
        self.spell_effect=spell_effect
        super()

    def resolve(self, to_zone='yard'):
        if self.check_target_zones():
            self.spell_effect(self)
        elif self.controller.game.verbose>=2:
            print(self,'countered due to no legal targets')
        self.controller.game.stack.leave_zone(self)
        if self.exile_on_resolve:
            self.exile()
        else:
            self.controller.__dict__[to_zone].enter_zone(self)
        self.reset_choices()
        self.reset_targets()

class Instant(Sorcery):
    def __init__(self,spell_effect,types=['instant'],**kwargs):
        Sorcery.__init__(self,spell_effect,types=types,**kwargs)
        super()
        self.flash=True


class Enchantment(Card):
    def __init__(self,types=['enchantment'],**kwargs):
        Card.__init__(self,types=types,**kwargs)
        self.tapped=False
        super()

    def enter_zone_effects(self,zone):
        super().enter_zone_effects(zone)

    def leave_zone_effects(self,zone):
        super().leave_zone_effects(zone)

# Aura class not complete
class Aura(Enchantment):
    def __init__(self, aura_static_effect,target_types=['creature'], **kwargs):
        Enchantment.__init__(self,**kwargs)
        self.subtypes=['aura']
        self.target_types=target_types
        self.attached_to=None
        self.aura_static_effect=aura_static_effect
        self.aura_static_effect.assign_source(self)
        # add choosing an auras, target
        self.targets=[Target(criteria=lambda source, obj:
            any([i in obj.types for i in target_types]))]

    def resolve(self, to_zone='field'):
        if self.check_target_zones():
            self.controller.game.stack.leave_zone(self)
            self.controller.__dict__[to_zone].enter_zone(self)
            self.summoning_sick=True
            self.attach_to(self.targets[-1])
        else:
            if self.controller.game.verbose>=2:
                print(self,'countered due to no legal targets')
            self.controller.game.stack.leave_zone(self)
            self.owner.yard.enter_zone(self)

    # if an aura enters a zone without a target being set, choose a target
    def enter_zone_effects(self,zone):
        if self.get_targets()==[]:
            objs = [i for i in self.controller.field + self.controller.opponent.field]
            legal_objs=[]
            for i in objs:
                if any([i in obj.types for i in self.target_types]):
                    legal_objs.append(i)
            selected= self.controller.input_choose(legal_objs)
            if legal_objs!=[]:
                self.attach_to(selected)
            else:
                self.owner.yard.enter_zone(self)
        super().enter_zone_effects(zone)

    def leave_zone_effects(self,zone):
        super().leave_zone_effects(zone)
        # make sure to detach self from object when the aura is put into
        # the graveyard
        if zone=='field' and self.attached_to!=None:
            self.aura_static_effect.reverse_effect()
            self.attached_to.attached_objs.remove(self)
            #self.attached_to.applied_effects.remove(self)
            self.attached_to=None

    def attach_to(self,target):
        target.target_obj.attached_objs.append(self)
        self.attached_to=target.target_obj
        #target.target_obj.applied_effects.append(self)
        self.aura_static_effect.apply_effect()

    def detach_from(self):
        self.aura_static_effect.reverse_effect()
        self.attached_to.attached_objs.remove(self)
        #self.attached_to.applied_effects.remove(self)
        self.attached_to=None
        self.controller.field.leave_zone(self)
        self.owner.yard.enter_zone(self)

class Artifact(Card):
    def __init__(self,types=['artifact'],**kwargs):
        Card.__init__(self,types=types,**kwargs)
        self.tapped=False
        super()

    def enter_zone_effects(self,zone):
        super().enter_zone_effects(zone)

    def leave_zone_effects(self,zone):
        super().leave_zone_effects(zone)

class Equipment(Artifact):
    def __init__(self,equip_static_effect,equip_cost, **kwargs):
        Artifact.__init__(self,**kwargs)
        self.equip_cost=equip_cost
        self.equip_static_effect=equip_static_effect
        self.equip_static_effect.assign_source(self)
        self.attached_to=None
        self.subtypes=['equipment']
        # add activated equip costs
        self.add_equip_abil()

    @staticmethod
    def _select_target_(abil):
        target=Target(abil,criteria= lambda source, obj: abil.source not in obj.attached_objs
            and 'creature' in obj.types,
            c_opponent=False)
        target.set_possible_target()
        target.source=abil
        abil.targets=[target]

    def add_equip_abil(self):
        abil= Activated_Ability(
            name=self.name+' equip abil',
            cost=self.equip_cost,
            mana_abil=False,
            targets=[Target(criteria= lambda source, obj: self not in obj.attached_objs
                and 'creature' in obj.types, c_opponent=False)],
            abil_effect= lambda abil: abil.source.attach_to(abil.get_targets()),
            flash=False
        )
        abil.assign_source(self)
        self.activated_abils=[abil]

    # attach equipment procedure
    def attach_to(self,target):
        if self.attached_to!=None:
            self.detach_from()
        target.attached_objs.append(self)
        self.attached_to=target
        #target.target_obj.applied_effects.append(self)
        self.equip_static_effect.apply_effect()

    # detach equipment procedure
    def detach_from(self):
        self.equip_static_effect.reverse_effect()
        self.attached_to.attached_objs.remove(self)
        #self.attached_to.applied_effects.remove(self)
        self.attached_to=None

class Planeswalker(Card):
    def __init__(self,loyalty,types=['legendary','planeswalker'],activated_abils=[],**kwargs):
        Card.__init__(self,types=types,**kwargs)
        super()
        self.tapped=False
        self.starting_loyalty=loyalty
        self.loyalty=loyalty
        self.activated_abils=activated_abils
        self.activated_loyalty_abil=False
        # require that loyalty abils not be activated more than once per turn
        for i in self.activated_abils:
            i.requirements=  i.requirements + [Requirement(source=self,
                condition=lambda source_abil: source_abil.source.activated_loyalty_abil==False)]

    def enter_zone_effects(self,zone):
        super().enter_zone_effects(zone)

    def leave_zone_effects(self,zone):
        super().leave_zone_effects(zone)

    # change loyalty
    def change_loyalty(self,num,pay=True):
        self.loyalty+=num
        # if paying loyalty, make sure we have enough loyalty to do so
        if pay:
            if self.loyalty<0:
                raise GameActionError('Not enough loyalty to pay for ability')

    # check for zero loyalty
    def check_loyalty(self):
        if self.loyalty<=0:
            if self.controller.verbose>=2:
                print(self, 'has no loyalty')
            self.dies()

    def dies(self):
        if self.controller.verbose>=2:
            print(self, 'dies')
        self.controller.field.leave_zone(self)
        if self.check_keyword('exile_on_death'):
            self.owner.exile.enter_zone(self)
            if self.controller.game.verbose>=2:
                print(self, 'is exiled')
        else:
            self.controller.game.triggers('dies', obj=self)
            self.owner.yard.enter_zone(self)
        self.loyalty=self.starting_loyalty


    def EOT_cleanup(self):
        super().EOT_cleanup()
        self.activated_loyalty_abil=False

#=============================================================================
# Non-physical card types
#==============================================================================

# classes for tokens
class Creature_Token(Creature):
    def __init__(self,**kwargs):
        if 'types' in kwargs.keys():
            kwargs['types'].append('token')
        else:
            kwargs['types']=['creature','token']
        Creature.__init__(self,**kwargs)
        super()

    # delete token on leaving the field
    def leave_zone_effects(self,zone):
        super().leave_zone_effects(zone)
        del self

class Artifact_Token(Artifact):
    def __init__(self,**kwargs):
        if 'types' in kwargs.keys():
            kwargs['types'].append('token')
        else:
            kwargs['types']=['artifact','token']
        Artifact.__init__(self,**kwargs)
        super()

    # delete token on leaving the field
    def leave_zone_effects(self,zone):
        super().leave_zone_effects(zone)
        del self

# object to represent counters that go on cards
class MTG_Counter:
    def __init__(self,name,counter_static_effect):
        self.name=name
        self.print_name=name
        self.counter_static_effect=counter_static_effect
        self.counter_static_effect.assign_source(self)
        self.subtypes=['counter']
        self.types=['counter']

    def attach_to(self,card):
        if 'cant_have_plus1_plus1' in card.keyword_static_abils and \
            self.name=='+1/+1 counter':
            pass
        else:
            card.attached_objs.append(self)
            self.attached_to=card
            self.counter_static_effect.apply_effect()

    def detach_from(self):
        self.counter_static_effect.reverse_effect()
        self.attached_to.attached_objs.remove(self)
        self.attached_to=None

    def __repr__(self):
        return self.name #+ str(id(self))[-2:]

    def __str__(self):
        return self.name

# generate common kinds of counters
def plus1_plus1_counter_effect(creature):
    creature.change_power(1)
    creature.change_toughness(1)
def r_plus1_plus1_counter_effect(creature):
    creature.change_power(-1)
    creature.change_toughness(-1)

global plus1_plus1_counter
plus1_plus1_counter= MTG_Counter(
    name='+1/+1 counter',
    counter_static_effect=Attached_Effect(
        name="+1/+1 counter effect",
        effect_func= plus1_plus1_counter_effect,
        reverse_effect_func=r_plus1_plus1_counter_effect
    )
)

# Emblems
class Emblem:
    def __init__(self, name, static_abils=[], triggered_abils=[],replace_effects=[]):
        self.name=name
        self.controller=None
        self.owner=None
        self.add_static_zones=[]
        self.remove_static_zones=[]
        self.static_abils=static_abils
        self.add_trigger_zones=[]
        self.remove_trigger_zones=[]
        self.trigger_points_added=False
        self.triggered_abils=triggered_abils
        self.add_replace_zones=[]
        self.remove_replace_zones=[]
        self.replace_points_added=False
        self.replace_effects=replace_effects
        for i in self.static_abils:
            i.assign_source(self)
        for i in self.triggered_abils:
            i.assign_source(self)
        for i in self.replace_effects:
            i.assign_source(self)
        self.colors=[]
        # TODO: have not implemented choices or targets for emblems
        self.choices=[]
        self.requirements=[]
        self.targets=[]

    def give_player(self, player):
        player.emblems.append(self)
        self.controller=player
        self.owner=player
        for abil in self.static_abils:
            abil.assign_controller(player)
            abil.apply_effect()

        for i in self.triggered_abils:
            i.assign_controller(player)
            i.add_trigger_points()

        self.trigger_points_added=True

        for i in self.replace_effects:
            i.assign_controller(player)
            i.add_replace_points()
        self.replace_points_added=True

    # TODO: have not implemented choices or targets for emblems
    def reset_choices(self):
        for i in self.choices:
            i.choice_made=None

    def reset_targets(self):
        for i in self.targets:
            i.target_obj=None
            i.zone=None
            i.zone_hash=None

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
