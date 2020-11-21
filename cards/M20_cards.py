# M20 Cards
import time
from Card_types import *
from Abilities_Effects import *
from Player import *
import inspect
import itertools





# Basic Lands
Plains= Land(
    name="Plains",
    types=['basic','land'],
    subtypes=['Plains'],
    activated_abils=[
        # T: add W
        Activated_Ability(
            name='Plains ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('W'),
            mana_abil=True,
            potential_mana=Potential_Mana({'W':1})
        )
    ],
    rarity='basic land'
)

Island= Land(
    name="Island",
    types=['basic','land'],
    subtypes=['Island'],
    activated_abils=[
        # T: add U
        Activated_Ability(
            name='Island ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('U'),
            mana_abil=True,
            potential_mana=Potential_Mana({'U':1})
        )
    ],
    rarity='basic land'
)

Swamp= Land(
    name="Swamp",
    types=['basic','land'],
    subtypes=['Swamp'],
    activated_abils=[
        # T: add B
        Activated_Ability(
            name='Swamp ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('B'),
            mana_abil=True,
            potential_mana=Potential_Mana({'B':1})
        )
    ],
    rarity='basic land'
)

Mountain= Land(
    name="Mountain",
    types=['basic','land'],
    subtypes=['Mountain'],
    activated_abils=[
        # T: add R
        Activated_Ability(
            name='Mountain ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('R'),
            mana_abil=True,
            potential_mana=Potential_Mana({'R':1})
        )
    ],
    rarity='basic land'
)

Forest= Land(
    name="Forest",
    types=['basic','land'],
    subtypes=['Forest'],
    activated_abils=[
        # T: add G
        Activated_Ability(
            name='Forest ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('G'),
            mana_abil=True,
            potential_mana=Potential_Mana({'G':1})
        )
    ],
    rarity='basic land'
)

# White
# Aerial Assault
# 2W
# Sorcery
# Destroy target tapped creature. You gain 1 life for each creature you control with flying.

def Aerial_Assault_effect(source_card):
    target=source_card.get_targets()
    target.destroy()
    nfly=len([i for i in source_card.controller.field if 'flying' in i.keyword_static_abils])
    source_card.controller.change_life(nfly)

Aerial_Assault= Sorcery(
    name='Aerial Assault',
    cost=Cost(mana={'C':2,'W':1}),
    targets=[Target(criteria= lambda source, obj: obj.tapped and 'creature' in obj.types)],
    spell_effect= Aerial_Assault_effect,
    rarity='common'
)

# Ajani, Strength of the Pride
# 2WW
# Planeswalker
#+1: You gain life equal to the number of creatures you control plus the number
# of planeswalkers you control
# -2: Create a 2/2, white Cat Soldier creature token named Ajani's Pridemate
# with "Whenever you gain life, put a +1/+1 counter on Ajani's Pridemate."
# 0: If you have at least 15 life more than your starting life total, exile
# Ajani Strength of the Pride and each artifact and creature your opponents control.
# 5

def Ajani_SotP_plus1_effect(source_abil):
    nobj=len([i for i in source_abil.source.controller.field if 'creature' in i.types or
        'planeswalker' in i.types])
    source_abil.source.controller.change_life(nobj)

def Ajani_SotP_minus2_effect(source_abil):
    source_abil.source.controller.create_token(
        Creature_Token(
            name="Ajani's Pridemate",
            colors=['W'],
            types=['creature'],
            subtypes=['cat','soldier'],
            power=2,
            toughness=2,
            triggered_abils=[
                Triggered_Ability(
                    name='Ajani Pridemate get +1/+1 counter on lifegain',
                    trigger_points=['lifegain'],
                    trigger_condition=lambda source_abil, **kwargs:
                        source_abil.source.controller==kwargs['player'],
                    abil_effect=lambda source_abil: deepcopy(plus1_plus1_counter)
                        .attach_to(source_abil.source)
                )
            ]
        )
    )

def Ajani_SotP_0_effect(source_abil):
    if source_abil.source.controller.life>=35:
        source_abil.source.exile()
        for i in source_abil.source.controller.opponent.field:
            if 'artifact' in i.types or 'creature' in i.types:
                i.exile()

Ajani_SotP=Planeswalker(
    name='Ajani, Strength of the Pride',
    subtypes=['ajani'],
    cost=Cost(mana={'C':2,'W':2}),
    loyalty=5,
    activated_abils=[
    # +1
        Activated_Ability(
            name='Ajani, Strength of the Pride +1 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(1)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False]
            ),
            abil_effect= Ajani_SotP_plus1_effect,
            flash=False
        ),
    #-2
        Activated_Ability(
            name='Ajani, Strength of the Pride -2 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(-2)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False and
                    source_abil.source.loyalty>=2]
            ),
            abil_effect= Ajani_SotP_minus2_effect,
            flash=False
        ),
    #0
        Activated_Ability(
            name='Ajani, Strength of the Pride 0 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(0)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False]
            ),
            abil_effect= Ajani_SotP_0_effect,
            flash=False
        )
    ],
    rarity='mythic'
)

# Ancestral Blade
# 1W
# Artifact - Equipment
# When Ancestral Blade enters the battlefield, create a 1/1 white Soldier
# creature token, then attach Ancestral Blade to it.
# Equipped creature gets +1/+1.
# Equip 1
def Ancestral_Blade_equip(attached_to):
    attached_to.change_power(1)
    attached_to.change_toughness(1)
def r_Ancestral_Blade_equip(attached_to):
    attached_to.change_power(-1)
    attached_to.change_toughness(-1)

def Ancestral_Blade_ETB_effect(source_abil):
    token=Creature_Token(
        name="Soldier 1/1",
        colors=['W'],
        types=['creature'],
        subtypes=['soldier'],
        power=1,
        toughness=1,
    )
    source_abil.source.attach_to(token)
    source_abil.source.controller.create_token(token)

Ancestral_Blade=Equipment(
    name='Ancestral Blade',
    cost=Cost(mana={'C':1,'W':1}),
    equip_cost=Cost(mana={'C':1}),
    equip_static_effect=Attached_Effect(
        name='Ancestral Blade Pump',
        effect_func=Ancestral_Blade_equip,
        reverse_effect_func=r_Ancestral_Blade_equip
    ),
    triggered_abils=[
        Triggered_Ability(
            name='Ancestral Blade ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Ancestral_Blade_ETB_effect
        )
    ],
    rarity='uncommon'
)

# Angel of Vitality
# 2W
# Creature - Angel
# Flying
# If you would gain life, you gain that much life plus 1 instead.
# Angel of Vitality gets +2/+2 as long as you have 25 or more life.
# 2/2
def Angel_of_Vitality_lifegain_effect(source_abil, effect_kwargs):
    source_abil.source.controller.life_chg_num+=1

def Angel_of_Vitality_pump_effect(source_abil):
    source_abil.source.change_power(2)
    source_abil.source.change_toughness(2)

def r_Angel_of_Vitality_pump_effect(source_abil):
    source_abil.source.change_power(-2)
    source_abil.source.change_toughness(-2)

Angel_of_Vitality=Creature(
    name='Angel of Vitality',
    cost=Cost(mana={'C':2,'W':1}),
    subtypes=['angel'],
    power=2,
    toughness=2,
    keyword_static_abils=['flying'],
    replace_effects=[
        Replacement_Effect(
            name='Angel of Vitality +1 Gain Life',
            replace_points=['lifegain'],
            replace_condition=lambda source_abil, **kwargs:
                source_abil.source.controller==kwargs['player'],
            replace_func= Angel_of_Vitality_lifegain_effect
        )
    ],
    nonkeyword_static_abils= [
        Local_Static_Effect(
            name='Angel of Vitality Pump Effect',
            effect_func = Angel_of_Vitality_pump_effect,
            reverse_effect_func = r_Angel_of_Vitality_pump_effect,
            effect_condition = lambda source_abil: source_abil.controller.life>=25
        )
    ],
    rarity='uncommon'
)

# Angelic Gift
# 1W
# Enchantment - Aura
# Enchant creature
# When Angelic Gift enters the battlefield, draw a card.
# Enchanted creature has flying.

def Angelic_Gift_effect(attached_to):
    attached_to.keyword_static_abils.append('flying')
def r_Angelic_Gift_effect(attached_to):
    attached_to.remove_keyword('flying')

Angelic_Gift= Aura(
    name='Angelic Gift',
    cost=Cost(mana={'C':1,'W':1}),
    aura_static_effect=Attached_Effect(
        name="Angelic Gift flying effect",
        effect_func=Angelic_Gift_effect,
        reverse_effect_func=r_Angelic_Gift_effect
    ),
    triggered_abils=[
        Triggered_Ability(
            name='Angelic Gift ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.source.controller.draw_card()
        )
    ],
    rarity='common'
)

# Apostle of Purifying Light
# 1W
# Creature - Human Cleric
# Protection from black
# {2}: Exile target card from a graveyard
# 2/1
Apostle_of_Purifying_Light= Creature(
    name='Apostle of Purifying Light',
    cost=Cost(mana={"C":1, "W":1}),
    power=2,
    toughness=1,
    subtypes=['human','cleric'],
    protection_effects=[Protection(condition=lambda obj: 'B' in obj.colors)],
    activated_abils=[
        Activated_Ability(
            name='Apostle of Purifying Light exile ability',
            cost=Cost(mana={'C':2}),
            targets=[Target(criteria= lambda source, obj: True, c_zones=['yard'])],
            abil_effect= lambda source_abil: source_abil.get_targets().exile()
        )
    ],
    rarity='uncommon'
)

# Battalion Foot Soldier
# 2W
# Creature - Human Soldier
# When Battalion Foot Soldier enters the battlefield, you may search your
# library for any number of cards named Battalion Foot Soldier, reveal them,
# put them into your hand, then shuffle your library.

def Battalion_Foot_Soldier_select_effect(card):
    card.owner.lib.leave_zone(card)
    card.owner.hand.enter_zone(card)

def Battalion_Foot_Soldier_ETB(source_abil):
    source_abil.source.controller.search_library(
        elig_condition= lambda card: card.name=="Battalion Foot Soldier",
        select_effect= Battalion_Foot_Soldier_select_effect,
        select_num='any'
    )

Battalion_Foot_Soldier=Creature(
    name='Battalion Foot Soldier',
    cost=Cost(mana={"C":2, "W":1}),
    power=2,
    toughness=2,
    subtypes=['human','soldier'],
    triggered_abils=[
        Triggered_Ability(
            name='Battalion Foot Soldier ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Battalion_Foot_Soldier_ETB
        )
    ],
    rarity='common'
)

# Bishop of Wings
# Bishop of Wings {W}{W}
# Creature — Human Cleric
# Whenever an Angel enters the battlefield under your control, you gain 4 life.
# Whenever an Angel you control dies, create a 1/1 white Spirit creature token with flying.
# 1/4

Bishop_of_Wings=Creature(
    name='Bishop of Wings',
    cost=Cost(mana={"W":2}),
    power=1,
    toughness=4,
    subtypes=['human','cleric'],
    triggered_abils=[
        Triggered_Ability(
            name='Bishop of Wings Angel ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'angel' in obj.subtypes
                and source_abil.source.controller==obj.controller,
            abil_effect= lambda source_abil: source_abil.source.controller.change_life(4)
        ),
        Triggered_Ability(
            name='Bishop of Wings Angel Dies',
            trigger_points=['dies'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'angel' in obj.subtypes
                and source_abil.source.controller==obj.controller,
            abil_effect= lambda source_abil: source_abil.source.controller.create_token(
                Creature_Token(
                    name="Spirit 1/1 Flying",
                    colors=['W'],
                    types=['creature'],
                    subtypes=['Spirit'],
                    power=1,
                    toughness=1,
                    keyword_static_abils=['flying']
                )
            )
        )
    ],
    rarity='rare'
)

# Brought Back
# WW
# Instant
# Choose up to two target permanent cards in your graveyard that were put there
# from the battlefield this turn. Return them to the battlefield tapped.
def Brought_Back_effect(source_card):
    for card in source_card.get_targets():
        if card!=None:
            card.owner.yard.leave_zone(card)
            card.controller.field.enter_zone(card, tapped=True)

Brought_Back=Instant(
    name='Brought Back',
    cost=Cost(mana={"W":2}),
    targets=[
            Target(criteria= lambda source, obj: 'instant' not in obj.types and
            'sorcery' not in obj.types and obj.zone_turn==obj.owner.game.turn_id and
            obj.prev_zone.zone_type=='field', c_opponent=False ,c_zones=['yard'],
            c_required=False),
            Target(criteria= lambda source, obj: 'instant' not in obj.types and
            'sorcery' not in obj.types and obj.zone_turn==obj.owner.game.turn_id and
            obj.prev_zone.zone_type=='field', c_opponent=False ,c_zones=['yard'],
            c_different=True,c_required=False)
        ],
    spell_effect= Brought_Back_effect,
    rarity='rare'
)

# Cavalier of Dawn
# 2WWW
# Creature - Elemental Knight
# Vigilance
# When Cavalier of Dawn enters the battlefield, destroy up to one target
# nonland permanent. Its controller creates a 3/3 colorless Golem artifact
# creature token.
# When Cavalier of Dawn dies, return target artifact or enchantment card from
# your graveyard to your hand.
# 4/6

def Cavalier_of_Dawn_ETB_effect(source_abil):
    target=source_abil.get_targets()
    if target!=None:
        target.destroy()
        target.controller.create_token(
            Creature_Token(
                name='Golem 3/3',
                colors=[],
                types=['artifact','creature'],
                subtypes=['golem'],
                power=3,
                toughness=3
            )
        )

def Cavalier_of_Dawn_dies_effect(source_abil):
    target=source_abil.get_targets()
    target.owner.yard.leave_zone(target)
    target.owner.hand.enter_zone(target)

Cavalier_of_Dawn=Creature(
    name='Cavalier of Dawn',
    cost=Cost(mana={"C":2, "W":3}),
    power=4,
    toughness=6,
    subtypes=['elemental','knight'],
    keyword_static_abils=['vigilance'],
    triggered_abils=[
        Triggered_Ability(
            name='Cavalier of Dawn ETB',
            trigger_points=['enter field'],
            targets=[Target(criteria= lambda source, obj: 'land' not in obj.types,
                c_required=False)],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Cavalier_of_Dawn_ETB_effect
        ),
        Triggered_Ability(
            name='Cavalier of Dawn Dies',
            trigger_points=['dies'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[Target(criteria= lambda source, obj: 'artifact' in obj.types or
                'enchantment' in obj.types, c_opponent=False, c_zones=['yard'])],
            abil_effect= Cavalier_of_Dawn_dies_effect
        )
    ],
    rarity='mythic'
)

# Dawning Angel
# 4W
# Creature - Angel
# flying
# When Dawning Angel enters the battlefield, you gain 4 life
# 3/2
Dawning_Angel= Creature(
    name='Dawning Angel',
    cost=Cost(mana={"C":4, "W":1}),
    power=3,
    toughness=2,
    subtypes=['angel'],
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Dawning Angel ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.source.controller.change_life(4)
        )
    ],
    rarity='common'
)

# Daybreak Chaplin
# 1W
# lifelink
# 1/3
Daybreak_Chaplin= Creature(
    name='Daybreak Chaplin',
    cost=Cost(mana={"C":1, "W":1}),
    power=1,
    toughness=3,
    subtypes=['human','cleric'],
    keyword_static_abils=['lifelink'],
    rarity='common'
)

# Devout Decree
# 1W
# Sorcery
# Exile target creature or planeswalker that’s black or red. Scry 1.
def Devout_Decree_effect(source_card):
    target=source_card.get_targets()
    target.exile()
    source_card.controller.scry(1)

Devout_Decree= Sorcery(
    name='Devout Decree',
    cost=Cost(mana={"C":1, "W":1}),
    targets=[Target(criteria= lambda source, obj: ('creature' in obj.types or
    'planeswalker' in obj.types) and ('R' in obj.colors or 'B' in obj.colors))],
    spell_effect= Devout_Decree_effect,
    rarity='uncommon'
)

# Disenchant
# 1W
# Instant
# Destroy target artifact or enchantment
def Disenchant_effect(source_card):
    target=source_card.get_targets()
    target.destroy()

Disenchant= Instant(
    name='Disenchant',
    cost=Cost(mana={"C":1, "W":1}),
    targets=[Target(criteria= lambda source, obj: 'artifact' in obj.types or
    'enchantment' in obj.types)],
    spell_effect= Disenchant_effect,
    rarity='common'
)

# Eternal Isolation
# 1W
# Sorcery
# Put target creature with power 4 or greater on the bottom of its owner’s library.
def Eternal_Isolation_effect(source_card):
    target=source_card.get_targets()
    target.controller.field.leave_zone(target)
    target.owner.lib.enter_zone(target,pos=-1)

Eternal_Isolation= Sorcery(
    name='Eternal Isolation',
    cost=Cost(mana={"C":1, "W":1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types and obj.power>=4)],
    spell_effect= Eternal_Isolation_effect,
    rarity='uncommon'
)

# Fencing Ace
# 1W
# Double Strike
# 1/1
Fencing_Ace= Creature(
    name='Fencing Ace',
    cost=Cost(mana={"C":1, "W":1}),
    power=1,
    toughness=1,
    subtypes=['human','soldier'],
    keyword_static_abils=['double strike'],
    rarity='uncommon'
)

# Gauntlets of Light
# 2W
# Enchantment - Aura
# Enchant creature
# Enchanted creature gets +0/+2 and assigns combat damage equal to its toughness
# rather than its power.
# Enchanted creature has “{2}{W}: Untap this creature.”.

def Gauntlet_of_Light_effect(attached_to):
    attached_to.change_toughness(2)
    attached_to.keyword_static_abils.append('tough_assign')
    abil=Activated_Ability(
        name='Gauntlet of Light ability',
        cost=Cost(mana={'C':2,'W':1}),
        abil_effect= lambda source_abil: source_abil.source.untap(),
    )
    abil.assign_source(attached_to)
    abil.assign_ownership(attached_to.controller)
    attached_to.activated_abils=attached_to.activated_abils+ [abil]

def r_Gauntlet_of_Light_effect(attached_to):
    attached_to.change_toughness(-2)
    attached_to.remove_keyword('tough_assign')
    # remove granted activated ability (remove only one copy in case multiples
    # of this aura are attached to the target)
    abil_instances=[i for i in attached_to.activated_abils if i.name==
        'Gauntlet of Light ability']
    attached_to.activated_abils.remove(abil_instances[0])

Gauntlet_of_Light= Aura(
    name='Gauntlet of Light',
    cost=Cost(mana={'C':2,'W':1}),
    aura_static_effect=Attached_Effect(
        name="Gauntlet of Light Aura effects",
        effect_func=Gauntlet_of_Light_effect,
        reverse_effect_func=r_Gauntlet_of_Light_effect
    ),
    rarity='uncommon'
)

# Glaring Aegis
# W
# Enchantment - Aura
# Enchant creature
# When Glaring Aegis enters the battlefield, tap target creature an opponent controls.
# Enchanted creature gets +1/+3.
def Glaring_Aegis_effect(attached_to):
    attached_to.change_power(1)
    attached_to.change_toughness(3)
def r_Glaring_Aegis_effect(attached_to):
    attached_to.change_power(-1)
    attached_to.change_toughness(-3)

Glaring_Aegis= Aura(
    name='Glaring Aegis',
    cost=Cost(mana={'W':1}),
    aura_static_effect=Attached_Effect(
        name='Glaring Aegis +1/+3 Pump Effect',
        effect_func=Glaring_Aegis_effect,
        reverse_effect_func=r_Glaring_Aegis_effect
    ),
    triggered_abils=[
        Triggered_Ability(
            name='Glaring Aegis ETB',
            trigger_points=['enter field'],
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,c_own=False)],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.get_targets().tap(for_cost=False)
        )
    ],
    rarity='common'
)

# Gods Willing
# W
# Instant
# Target creature you control gains protection from the color of your choice until
# end of turn. Scry 1.

def Gods_Willing_choose_color(source_card):
    source_card.choice_made=source_card.controller.input_choose(['W','U','B','R','G'])
def EOTr_Gods_Willing_effect(target):
    # remove the protection effect granted by Gods willing
    target.protection_effects=[i for i in target.protection_effects if
        i.source.name!='Gods Willing']
def Gods_Willing_effect(source_card):
    target=source_card.get_targets()
    color = source_card.get_choices()
    target.protection_effects.append(Protection(condition=lambda obj: color in obj.colors,
        source=source_card))
    target.EOT_reverse_effects.append(EOTr_Gods_Willing_effect)
    source_card.controller.scry(1)

Gods_Willing= Instant(
    name='Gods Willing',
    cost=Cost(mana={"W":1}),
    choices=[Choice(Gods_Willing_choose_color)],
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,c_opponent=False)],
    spell_effect= Gods_Willing_effect,
    rarity='uncommon'
)

# Griffin Protector
# 3W
# Creature-Griffin
# Flying
# Whenever another creature enters the battlefield under your control, Griffin
# Protector gets +1/+1 until end of turn.
# 2/3
def EOTr_Griffin_Protector_Creature_ETB(creature):
    creature.change_power(-1)
    creature.change_toughness(-1)
def Griffin_Protector_Creature_ETB(source_abil):
    source_abil.source.change_power(1)
    source_abil.source.change_toughness(1)
    source_abil.source.EOT_reverse_effects.append(EOTr_Griffin_Protector_Creature_ETB)

Griffin_Protector=Creature(
    name='Griffin Protector',
    cost=Cost(mana={'C':3,"W":1}),
    power=2,
    toughness=3,
    subtypes=['griffin'],
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Griffin Protector Creature ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'creature' in obj.types
                and source_abil.source.controller==obj.controller and
                obj!=source_abil.source,
            abil_effect= Griffin_Protector_Creature_ETB
        )
    ],
    rarity='common'
)

# Griffin Sentinel
# 2W
# Creature - Griffin
# Flying, Vigilance
# 1/3
Griffin_Sentinel=Creature(
    name='Griffin Sentinel',
    cost=Cost(mana={'C':2,"W":1}),
    power=1,
    toughness=3,
    subtypes=['griffin'],
    keyword_static_abils=['flying','vigilance'],
    rarity='common'
)

# Hanged Executioner
# 2W
# Creature - Spirit
# Flying
# When Hanged Executioner enters the battlefield, create a 1/1 white Spirit
# creature token with flying.
# {3}{W}, Exile Hanged Executioner: Exile target creature.
# 1/1
Hanged_Executioner=Creature(
    name='Hanged Executioner',
    cost=Cost(mana={'C':2,"W":1}),
    power=1,
    toughness=1,
    subtypes=['spirit'],
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Hanged Executioner ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.source.controller.create_token(
                Creature_Token(
                    name="Spirit 1/1 Flying",
                    colors=['W'],
                    types=['creature'],
                    subtypes=['spirit'],
                    power=1,
                    toughness=1,
                    keyword_static_abils=['flying']
                )
            )
        )
    ],
    activated_abils= [
        Activated_Ability(
            name='Hanged Executioner ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.exile()],
                mana={'C':3,'W':1}),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
            abil_effect= lambda source_abil: source_abil.get_targets().exile(),
        )
    ],
    rarity='rare'
)
# Herald of the Sun
# {4}{W}{W}
# Creature — Angel
# Flying
# {3}{W}: Put a +1/+1 counter on another target creature with flying.
# 4/4
Herald_of_the_Sun=Creature(
    name='Herald of the Sun',
    cost=Cost(mana={'C':4,"W":2}),
    power=4,
    toughness=4,
    subtypes=['angel'],
    keyword_static_abils=['flying'],
    activated_abils= [
        Activated_Ability(
            name='Herald of the Sun ability',
            cost=Cost(mana={'C':3,'W':1}),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types and 'flying'
                in obj.keyword_static_abils, c_self_target=False)],
            abil_effect= lambda source_abil: deepcopy(plus1_plus1_counter).attach_to(
                source_abil.get_targets())
        )
    ],
    rarity='uncommon'
)

# Inspired Charge
# {2}{W}{W}
# Instant
# Creatures you control get +2/+1 until end of turn.
def EOTr_Inspired_Charge_effect(creature):
    creature.change_power(-2)
    creature.change_toughness(-1)

def Inspired_Charge_effect(source_card):
    for i in source_card.controller.field:
        if 'creature' in i.types:
            i.change_power(2)
            i.change_toughness(1)
            i.EOT_reverse_effects.append(EOTr_Inspired_Charge_effect)

Inspired_Charge= Instant(
    name='Inspired Charge',
    cost=Cost(mana={'C':2,"W":2}),
    choices=[],
    spell_effect= Inspired_Charge_effect,
    rarity='common'
)

# Inspiring Captain
# {3}{W}
# Creature — Human Knight
# When Inspiring Captain enters the battlefield, creatures you control get +1/+1
# until end of turn.
# 3/3
def EOTr_Inspiring_Captain_ETB(creature):
    creature.change_power(-1)
    creature.change_toughness(-1)

def Inspiring_Captain_ETB(source_abil):
    for i in source_abil.source.controller.field:
        if 'creature' in i.types:
            i.change_power(1)
            i.change_toughness(1)
            i.EOT_reverse_effects.append(EOTr_Inspiring_Captain_ETB)

Inspiring_Captain= Creature(
    name='Inspiring Captain',
    cost=Cost(mana={'C':3,"W":1}),
    power=3,
    toughness=3,
    subtypes=['human','knight'],
    triggered_abils=[
        Triggered_Ability(
            name='Inspiring Captain Creature ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Inspiring_Captain_ETB
        )
    ],
    rarity='common'
)

# Leyline of Sanctity
# {2}{W}{W}
# Enchantment
# If Leyline of Sanctity is in your opening hand, you may begin the game with
# it on the battlefield.
# You have hexproof.

def Leyline_of_Sanctity_begin_game(source_abil):
    if source_abil.source.owner.input_bool(label='Leyline begin of game abil'):
        source_abil.source.owner.hand.leave_zone(source_abil.source)
        source_abil.source.owner.field.enter_zone(source_abil.source)
        if source_abil.source.controller.game.verbose>=2:
            print(source_abil.source.controller, 'puts Leyline of Sanctity into play at beginning of game')
    else:
        if source_abil.source.controller.game.verbose>=2:
            print(source_abil.source.controller, 'elects not to put Leyline of Sanctity into play at beginning of game')

def r_Leyline_of_Sanctity_effect(applied_obj, source_abil):
    applied_obj.remove_keyword('hexproof')

def Leyline_of_Sanctity_effect(applied_obj, source_abil):
    applied_obj.add_keyword('hexproof')

Leyline_of_Sanctity= Enchantment(
    name="Leyline of Sanctity",
    cost=Cost(mana={'W':2,'C':2}),
    triggered_abils=[
        Triggered_Ability(
            name="Leyline of Sanctity begin game effect",
            trigger_points=['begin game'],
            add_trigger_zones=['hand'],
            remove_trigger_zones=['hand'],
            abil_effect=Leyline_of_Sanctity_begin_game,
            stack=False
        )
    ],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Leyline of Sanctity hexproof effect",
            own_apply_zones=[], opp_apply_zones=[],
            players='self',
            effect_func= Leyline_of_Sanctity_effect,
            reverse_effect_func = r_Leyline_of_Sanctity_effect
        )
    ],
    rarity='rare'
)

# Loxodon Lifechanter
# {5}{W}
# Creature — Elephant Cleric
# When Loxodon Lifechanter enters the battlefield, you may have your life total
# become the total toughness of creatures you control.
# {5}{W}: Loxodon Lifechanter gets +X/+X until end of turn, where X is your life total.
# 4/6

def Loxodon_Lifechanter_ETB(source_abil):
    tot_tough=0
    for i in source_abil.source.controller.field:
        if 'creature' in i.types:
            tot_tough+= i.toughness
    if source_abil.source.controller.input_bool(label='Loxodon Lifechanter set life'):
        source_abil.source.controller.life=tot_tough
    else:
        if source_abil.source.controller.game.verbose>=2:
            print(source_abil.source.controller, 'elects not to set life with Loxodon Lifechanter')

def Loxodon_Lifechanter_pump(source_abil):
    temp_pump=source_abil.source.controller.life
    source_abil.source.change_toughness(temp_pump)
    source_abil.source.change_power(temp_pump)
    source_abil.source.EOT_power_pump+=temp_pump
    source_abil.source.EOT_toughness_pump+=temp_pump

Loxodon_Lifechanter= Creature(
    name='Loxodon Lifechanter',
    cost=Cost(mana={"C":5, "W":1}),
    power=4,
    toughness=6,
    subtypes=['elephant','cleric'],
    triggered_abils=[
        Triggered_Ability(
            name='Loxodon Lifechanter ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Loxodon_Lifechanter_ETB
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Loxodon Lifechanter ability',
            cost=Cost(mana={'C':5,'W':1}),
            abil_effect= Loxodon_Lifechanter_pump,
        )
    ],
    rarity='rare'
)

#Loyal Pegasus {W}
#Creature — Pegasus
#Flying
#Loyal Pegasus can’t attack or block alone.
#2/1

Loyal_Pegasus= Creature (
    name='Loyal Pegasus',
    cost=Cost(mana={"W":1}),
    power=2,
    toughness=1,
    subtypes=['pegasus'],
    keyword_static_abils=['no_atk_alone'],
    rarity='common'
)

# Master Splicer
# Creature - Human Artificer
# When Master Splicer enters the battlefield, create a 3/3 colorless Golem
# artifact creature token.
# Golems you control get +1/+1.
# 1/1

def Master_Splicer_pump_effect(applied_obj,source_abil):
    applied_obj.change_power(1)
    applied_obj.change_toughness(1)

def r_Master_Splicer_pump_effect(applied_obj,source_abil):
    applied_obj.change_power(-1)
    applied_obj.change_toughness(-1)

Master_Splicer= Creature(
    name='Master Splicer',
    cost=Cost(mana={'C':3,"W":1}),
    power=1,
    toughness=1,
    subtypes=['human','artificer'],
        triggered_abils=[
            Triggered_Ability(
                name='Master Splicer ETB',
                trigger_points=['enter field'],
                trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
                abil_effect= lambda source_abil: source_abil.source.controller.create_token(
                    Creature_Token(
                        name='Golem 3/3',
                        colors=[],
                        types=['artifact','creature'],
                        subtypes=['golem'],
                        power=3,
                        toughness=3
                    )
                )
            )
        ],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Master Splicer Pump effect",
            effect_condition= lambda applied_obj, source_abil: 'creature' in \
                applied_obj.types and 'golem' in applied_obj.subtypes and
                applied_obj.controller == source_abil.controller,
            effect_func= Master_Splicer_pump_effect,
            reverse_effect_func = r_Master_Splicer_pump_effect
        )
    ],
    rarity='uncommon'
)

# Moment of Heroism
# 1W
# Instant
# Target creature gets +2/+2 and lifelink until end of turn

def Moment_of_Heroism_effect(source_card):
    target=source_card.get_targets()
    target.change_power(2)
    target.change_toughness(2)
    target.keyword_static_abils.append('lifelink')
    target.EOT_reverse_effects.append(EOTr_Moment_of_Heroism_effect)

def EOTr_Moment_of_Heroism_effect(target):
    target.change_power(-2)
    target.change_toughness(-2)
    target.remove_keyword('lifelink')

Moment_of_Heroism= Instant(
    name='Moment of Heroism',
    cost=Cost(mana={"C":1, "W":1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
    spell_effect= Moment_of_Heroism_effect,
    rarity='common'
)

# Moorland Inquisitor
# 1W
# Creature - Human Soldier
# 2W: Moorland Inquisitor gets first strike until end of turn
# 2/2

def EOTr_Moorland_Inquisitor_abil(creature):
    creature.remove_keyword('first strike')

def Moorland_Inquisitor_abil(source_abil):
    source_abil.source.keyword_static_abils.append('first strike')
    source_abil.source.EOT_reverse_effects.append(EOTr_Moorland_Inquisitor_abil)

Moorland_Inquisitor= Creature(
    name='Moorland Inquisitor',
    cost=Cost(mana={'C':1,"W":1}),
    power=2,
    toughness=2,
    subtypes=['human','soldier'],
    activated_abils= [
        Activated_Ability(
            name='Moorland Inquisitor ability',
            cost=Cost(mana={'C':2,'W':1}),
            abil_effect= Moorland_Inquisitor_abil
        )
    ],
    rarity='common'
)

# Pacifism
# 1W
# Enchantment - Aura
# Enchant Creature
# Enchanted creature can't attack or block
def pacifism_effect(attached_to):
    attached_to.keyword_static_abils.append('cant_attack')
    attached_to.keyword_static_abils.append('cant_block')
def r_pacifism_effect(attached_to):
    attached_to.remove_keyword('cant_attack')
    attached_to.remove_keyword('cant_block')

Pacifism= Aura(
    name='Pacifism',
    cost=Cost(mana={'C':1,'W':1}),
    aura_static_effect=Attached_Effect(
        name="Pacifism effect",
        effect_func=pacifism_effect,
        reverse_effect_func=r_pacifism_effect
    ),
    rarity='common'
)


# Planar Cleansing
# 3WWW
# Sorcery
# Destroy all nonland permanents
def Planar_Cleansing_effect(source_card):
    for i in source_card.controller.field+source_card.controller.opponent.field:
        # confirm both land and still on field
        if 'land' not in i.types and i.zone.zone_type=='field':
            i.destroy()


Planar_Cleansing= Sorcery(
    name='Planar Cleansing',
    cost=Cost(mana={'C':3,'W':3}),
    spell_effect= Planar_Cleansing_effect,
    rarity='rare'
)

# Raise the Alarm
# 1W
# Instant
# Create two 1/1 White Soldier tokens
Raise_the_Alarm= Instant(
    name='Raise the Alarm',
    cost=Cost(mana={'C':1,'W':1}),
    spell_effect= lambda source_card: source_card.controller.create_token(
        Creature_Token(
            name="Soldier 1/1",
            colors=['W'],
            types=['creature'],
            subtypes=['Soldier'],
            power=1,
            toughness=1,
        )
    ),
    rarity='common'
)

# Rule of Law
# 2W
# Enchantment
# Each player can't cast more than one spell per turn
def Rule_of_Law_effect(applied_obj, source_abil):
    applied_obj.spell_cap.append(1)

def r_Rule_of_Law_effect(applied_obj, source_abil):
    if 1 in applied_obj.spell_cap:
        applied_obj.spell_cap.remove(1)

Rule_of_Law= Enchantment(
    name="Rule of Law",
    cost=Cost(mana={'W':1,'C':2}),
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Rule of Law effect",
            own_apply_zones=[], opp_apply_zones=[],
            players='both',
            effect_func= Rule_of_Law_effect,
            reverse_effect_func = r_Rule_of_Law_effect
        )
    ],
    rarity='uncommon'
)

# Sephara, Sky's Blade
# 4WWW
# Legendary Creature - Angel
# You may pay {W} and tap four untapped creatures you control with flying rather
# than pay this spell’s mana cost.
# Flying, lifelink
# Other creatures you control with flying have indestructible. (Damage and
# effects that say “destroy” don’t destroy them.)
# 7/7

def Sephara_Skys_Blade_effect(applied_obj, source_abil):
    applied_obj.keyword_static_abils.append('indestructible')

def r_Sephara_Skys_Blade_effect(applied_obj, source_abil):
    applied_obj.remove_keyword('indestructible')

def Sephara_Skys_Blade_alt_cost(source_abil):
    untap_fly=[]
    for obj in source_abil.controller.field:
        if obj.tapped==False and 'creature' in obj.types and 'flying' in  \
        obj.keyword_static_abils:
            untap_fly.append(obj)
    choices=source_abil.controller.input_choose(untap_fly,
        label='Sephara, Skys Blade alt cost tapping', n=4)
    for i in choices:
        i.tap(summoning_sick_ok=True)

# makes sure there's at least 4 untapped flying creatures
def Sephara_Skys_Blade_alt_cost_check(source_abil):
    untap_fly=[]
    for obj in source_abil.controller.field:
        if obj.tapped==False and 'creature' in obj.types and 'flying' in  \
        obj.keyword_static_abils:
            untap_fly.append(obj)
    if len(untap_fly)>=4:
        return True
    else:
        return False

Sephara_Skys_Blade= Creature(
    name="Sephara, Sky's Blade",
    cost=[Cost(mana={'C':4,"W":3}),Cost(
            mana={'W':1},
            non_mana=[Sephara_Skys_Blade_alt_cost],
            non_mana_check=[Sephara_Skys_Blade_alt_cost_check]
        )
    ],
    power=7,
    toughness=7,
    types=['legendary','creature'],
    subtypes=['angel'],
    keyword_static_abils=['flying','lifelink'],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Sephara, Sky's Blade indestructible effect",
            effect_condition= lambda applied_obj, source_abil: \
                'creature' in applied_obj.types and 'flying' in \
                applied_obj.keyword_static_abils and applied_obj!=source_abil.source,
            effect_func= Sephara_Skys_Blade_effect,
            reverse_effect_func = r_Sephara_Skys_Blade_effect
        )
    ],
    rarity='rare'
)

# Soulmender
# Creature - Human cleric
# Tap: You gain 1 life
# 1/1
Soulmender= Creature(
    name='Soulmender',
    cost=Cost(mana={"W":1}),
    power=1,
    toughness=1,
    subtypes=['human','cleric'],
    activated_abils=[
        Activated_Ability(
            name='Soulmender ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                    and (source_abil.source.summoning_sick==False or 'creature' not in
                    source_abil.source.types)]
            ),
            abil_effect= lambda source_abil: source_abil.source.controller.change_life(1)
        )
    ],
    rarity='common'
)


# Squad Captain
# Creature - Human Soldier
# Vigilance (Attacking doesn’t cause this creature to tap.)
# Squad Captain enters the battlefield with a +1/+1 counter on it for each
# other creature you control.
# 2/2

def Squad_Captain_ETB(source_abil):
    creature_count=0
    for i in source_abil.source.controller.field:
        if 'creature' in i.types and i!=source_abil.source:
            creature_count+=1

    for _ in range(creature_count):
        deepcopy(plus1_plus1_counter).attach_to(source_abil.source)

    if source_abil.source.controller.verbose>=2:
        print('Squad Captain enters the battlefield with '+ str(creature_count)
            +' +1/+1 counters')

Squad_Captain= Creature(
    name='Squad Captain',
    cost=Cost(mana={'C':4,"W":1}),
    power=2,
    toughness=2,
    subtypes=['human','soldier'],
    keyword_static_abils=['vigilance'],
    nonkeyword_static_abils=[
        Local_Static_Effect(
            name="Squad Captain ETB",
            effect_func= Squad_Captain_ETB,
            reverse_effect_func= lambda source_abil: True,
            effect_condition = lambda source_abil: source_abil.source.ETB_static_check==True
        )
    ],
    rarity='common'
)

# Starfield Mystic
# 1W
# Creature - Human Cleric
# Enchantment spells you cast cost {1} less to cast.
# Whenever an enchantment you control is put into a graveyard from the battlefield
# , put a +1/+1 counter on Starfield Mystic.
# 2/2
def Starfield_Mystic_cost_reduce(applied_obj, source_abil):
    source_abil.source.controller.cost_mods.append(
        Cost_Modification(
            name='Starfield Mystic cost reduction obj',
            cost_mod={'C':-1},
            cost_mod_source=source_abil.source,
            mod_condition= lambda cost_obj, cost_mod_source: \
                isinstance(cost_obj.source, Card) and 'enchantment' in cost_obj.source.types
        )
    )

def r_Starfield_Mystic_cost_reduce(applied_obj, source_abil):
    abil_instances=[i for i in source_abil.controller.cost_mods if i.name==
        'Starfield Mystic cost reduction obj']
    if abil_instances != []:
        source_abil.controller.cost_mods.remove(abil_instances[0])

Starfield_Mystic= Creature(
    name='Starfield Mystic',
    cost=Cost(mana={'C':1,"W":1}),
    power=2,
    toughness=2,
    subtypes=['human','cleric'],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Starfield Mystic cost reduction",
            own_apply_zones=[], opp_apply_zones=[],
            players='self',
            effect_func= Starfield_Mystic_cost_reduce,
            reverse_effect_func= r_Starfield_Mystic_cost_reduce,
        )
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Starfield Mystic enchantment dies ability',
            trigger_points=['to_graveyard_from_field'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'enchantment' in obj.types,
            abil_effect=  lambda source_abil: deepcopy(plus1_plus1_counter).attach_to(
                source_abil.source)
        )
    ],
    rarity='rare'
)

# Steadfast Sentry
# 2W
# Creature - Human Soldier
# Vigilance
# When Steadfast Sentry dies, put a +1/+1 counter on target creature you control.
# 3/2

def Steadfast_Sentry_dies_effect(source_abil):
    target=source_abil.get_targets()
    deepcopy(plus1_plus1_counter).attach_to(target)

Steadfast_Sentry = Creature(
    name='Steadfast Sentry',
    cost=Cost(mana={'C':2,"W":1}),
    power=3,
    toughness=2,
    subtypes=['human','soldier'],
    keyword_static_abils=['vigilance'],
    triggered_abils=[
        Triggered_Ability(
            name='Steadfast Sentry dies ability',
            trigger_points=['to_graveyard_from_field'],
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,
                c_opponent=False)],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect=Steadfast_Sentry_dies_effect

        )
    ],
    rarity='common'
)

# Yoked Ox
# W
# Creature - Ox
# 0/4
Yoked_Ox = Creature(
    name='Yoked Ox',
    cost=Cost(mana={"W":1}),
    power=0,
    toughness=4,
    subtypes=['ox'],
    rarity='common'
)

#==============================================================================
#==============================================================================
# Blue
#==============================================================================
#==============================================================================

# Aether Gust
# 1U
# Instant
# Choose target spell or permanent that’s red or green. Its owner puts it on
# the top or bottom of their library.
def Aether_Gust_effect(source_card):
    target=source_card.get_targets()
    loc_lib=target.controller.input_choose(['top','bottom'], label='Aether Gust location')
    if source_card.controller.game.verbose>=2:
        print(target, ' location in library choice:', loc_lib)

    target.zone.leave_zone(target)
    if loc_lib=='top':
        target.owner.lib.enter_zone(target, pos=0)
    if loc_lib=='bottom':
        target.owner.lib.enter_zone(target, pos=-1)

Aether_Gust= Instant(
    name='Aether Gust',
    cost=Cost(mana={'C':1,"U":1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types and isinstance(obj,Card)
        and ('G' in obj.colors or 'R' in obj.colors), c_stack=True)],
    spell_effect= Aether_Gust_effect,
    rarity='uncommon'
)

# Agent of Treachery
# 5UU
# Creature - Human Rogue
# When Agent of Treachery enters the battlefield, gain control of target permanent.
# At the beginning of your end step, if you control three or more permanents
# you don’t own, draw three cards.
# 2/3

def Agent_of_Treachery_EOT_cond(source_abil, **kwargs):
    stolen_perms=0
    for i in source_abil.controller.field:
        if i.owner!= i.controller:
            stolen_perms += 1
    if stolen_perms >= 3:
        return(True)
    else:
        return(False)

Agent_of_Treachery= Creature(
    name='Agent of Treachery',
    cost=Cost(mana={"C":5, "U":2}),
    power=2,
    toughness=3,
    subtypes=['human','rogue'],
    triggered_abils=[
        Triggered_Ability(
            name='Agent of Treachery ETB abil',
            trigger_points=['enter field'],
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.get_targets()
                .assign_controller(source_abil.controller, gain_control=True)
        ),
        Triggered_Ability(
            name='Agent of Treachery EOT abil',
            trigger_points=['end phase'],
            trigger_condition= Agent_of_Treachery_EOT_cond,
            abil_effect = lambda source_abil: source_abil.controller.draw_card(3)
        )
    ],
    rarity='rare'
)

# Air Elemental
# 3UU
# Creature - Elemental
# Flying
# 4/4

Air_Elemental = Creature(
    name='Air Elemental',
    cost=Cost(mana={'C':3,"U":2}),
    power=4,
    toughness=4,
    subtypes=['elemental'],
    keyword_static_abils=['flying'],
    rarity='uncommon'
)

# Anticipate
# 1U
# Look at the top three cards of your library. Put one of them into your hand
# and the rest on the bottom of your library in any order.

def Anticipate_effect(source_card):
    selected = source_card.controller.select_top_lib(n_cards=3,n_selected=1,
        non_select_func='bottom of lib, choose order')
    if selected != None:
        source_card.controller.lib.leave_zone(selected[0])
        source_card.controller.hand.enter_zone(selected[0])

Anticipate = Instant(
    name='Anticipate',
    cost=Cost(mana={"C":1, "U":1}),
    spell_effect= Anticipate_effect,
    rarity='common'
)

# Atemis, All-Seeing
# {3}{U}{U}{U}
# Legendary Creature — Sphinx
# Flying
# {2}{U}, {T}: Draw two cards, then discard a card.
# Whenever Atemsis, All-Seeing deals damage to an opponent, you may reveal your
# hand. If cards with at least six different converted mana costs are revealed
# this way, that player loses the game.
# 4/5

def Atemis_draw_effect(source_abil):
    source_abil.controller.draw_card(2)
    source_abil.controller.discard_cards(1)

def Atemis_trigger_cond(source_abil, **kwargs):
    player_hit=[i for i in source_abil.source.dmg_dealt if isinstance(i[0],Player) and i[1]>0]
    return
    if len(player_hit)>0:
        return True
    else:
        return False

def Atemis_trigger_effect(source_abil):
    if source_abil.controller.input_bool(label='Atemis reveal choice'):
        source_abil.controller.reveal_cards(source_abil.controller.hand, zone='hand')
        cmc_list=[]
        for i in source_abil.controller.hand:
            cmc=i.cost.get_cmc()
            if cmc not in cmc_list:
                cmc_list.append(cmc)
        if len(cmc_list)>=6:
            source_abil.controller.lose_game=True
            source_abil.controller.game.end_game(source_abil.controller.opponent,
                'Atemis win condition')

Atemis_All_Seeing = Creature(
    name='Atemis, All-Seeing',
    cost=Cost(mana={'C':3,"U":3}),
    power=4,
    toughness=5,
    types=['legendary','creature'],
    subtypes=['Sphinx'],
    keyword_static_abils=['flying'],
    activated_abils=[
        Activated_Ability(
            name='Atemis draw cards abil',
            cost=Cost(mana={'C':2,'U':1}),
            abil_effect= Atemis_draw_effect
        )
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Atemis hit opponent trigger',
            trigger_points=['combat damage'],
            trigger_condition= Atemis_trigger_cond,
            abil_effect= Atemis_trigger_effect
        )
    ],
    rarity='rare'
)

# Befuddle
# 2U
# Instant
# Target creature gets -4/-0 until end of turn.
# Draw a card.

def EOTr_Befuddle_effect(creature):
    creature.change_power(4)

def Befuddle_effect(source_card):
    target=source_card.get_targets()
    target.change_power(-4)
    target.EOT_reverse_effects.append(EOTr_Befuddle_effect)
    source_card.controller.draw_card()


Befuddle=Instant(
name='Befuddle',
cost=Cost(mana={'C':2,"U":1}),
targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
spell_effect= Befuddle_effect,
rarity='common'
)

# Bone to Ash
# 2UU
# Instant
# Counter target creature spell.
# Draw a card.

def Bone_to_Ash_effect(source_card):
    target=source_card.get_targets()
    target.counterspelled()
    source_card.controller.draw_card()

Bone_to_Ash=Instant(
    name='Bone to Ash',
    cost=Cost(mana={'C':2,"U":2}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types, c_zones=[],
        c_stack=True)],
    spell_effect= Bone_to_Ash_effect,
    rarity='common'
)

# Boreal Elemental
# 4U
# Creature - Elemental
# Flying
# Spells that your opponents cast targeting Boreal Elemental cost {2} more
# to cast
# 3/4

def Boreal_Elemental_effect(applied_obj,source_abil):
    source_card=source_abil.source
    source_abil.controller.opponent.cost_mods.append(
        Cost_Modification(
            name='Boreal Elemental Cost Mod',
            cost_mod={'C':2},
            cost_mod_source= source_card,
            mod_condition = lambda cost_obj, cost_mod_source: hasattr(cost_obj.source, 'targets')
                and cost_obj.source.targets != None
                and isinstance(cost_obj.source,Card)
                and any([i==cost_mod_source for i in cost_obj.source.get_targets(squeeze=False,
                    check_illegal_targets=False)])
        )
    )

def r_Boreal_Elemental_effect(applied_obj, source_abil):
    abil_instances=[i for i in source_abil.controller.opponent.cost_mods if
        i.cost_mod_source!=source_abil.source or i.name!='Boreal Elemental Cost Mod']
    source_abil.controller.opponent.cost_mods=abil_instances

Boreal_Elemental=Creature(
    name='Boreal Elemental',
    cost=Cost(mana={'C':4,"U":1}),
    power=3,
    toughness=4,
    subtypes=['elemental'],
    keyword_static_abils=['flying'],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name='Boreal Elemental cost increase',
            own_apply_zones=[], opp_apply_zones=[],
            players='opponent',
            effect_func= Boreal_Elemental_effect,
            reverse_effect_func = r_Boreal_Elemental_effect
        )
    ],
    rarity='common'
)

# Brineborn Cutthroat
# {1}{U}
# Creature — Merfolk Pirate
# Flash (You may cast this spell any time you could cast an instant.)
# Whenever you cast a spell during an opponent’s turn, put a +1/+1 counter on
# Brineborn Cutthroat.
# 2/1

Brineborn_Cutthroat=Creature(
    name='Brineborn Cutthroat',
    cost=Cost(mana={'C':1,"U":1}),
    power=2,
    toughness=1,
    subtypes=['Merfolk Pirate'],
    keyword_static_abils=['flash'],
    flash=True,
    triggered_abils=[
        Triggered_Ability(
            name='Brineborn Cutthroat ability',
            trigger_points=['cast spell'],
            trigger_condition=lambda source_abil, casted_spell, **kwargs:
                source_abil.controller.game.act_plyr != source_abil.controller,
            abil_effect=lambda source_abil: deepcopy(plus1_plus1_counter)
                .attach_to(source_abil.source)
        )
    ],
    rarity='uncommon'
)

# Captivating Gyre
# {4}{U}{U}
# Sorcery
# Return up to three target creatures to their owners’ hands.

def Captivating_Gyre_effect(source_card):
    targets=source_card.get_targets(check_illegal_targets=True)
    for target in targets:
        if target!= None:
            target.bounce()

Captivating_Gyre=Sorcery(
    name='Captivating Gyre',
    cost=Cost(mana={'C':4,"U":2}),
    targets=[
            Target(criteria= lambda source, obj: 'creature' in obj.types, c_different=True,
                c_required=False),
            Target(criteria= lambda source, obj: 'creature' in obj.types, c_different=True,
                c_required=False),
            Target(criteria= lambda source, obj: 'creature' in obj.types, c_different=True,
                c_required=False),
        ],
    spell_effect= Captivating_Gyre_effect,
    rarity='uncommon'
)

# Cavalier of Gales {2}{U}{U}{U}
# Creature — Elemental Knight
# Flying
# When Cavalier of Gales enters the battlefield, draw three cards, then put two cards from your hand on top of your library in any order.
# When Cavalier of Gales dies, shuffle it into its owner’s library, then scry 2.
# 5/5

def Cavalier_of_Gales_ETB_effect(source_abil):
    source_abil.controller.draw_card(3)
    put_back = source_abil.controller.input_choose(source_abil.controller.hand,
        label='Cavalier of Gales put back select',n=2)
    put_back = source_abil.controller.input_order(put_back,
        label='Cavalier of Gales put back order')
    # order will be top of lib -> [card2,card1] in put_back
    for i in put_back:
        i.put_on_top_of_lib()

def Cavalier_of_Gales_dies_effect(source_abil):
    source_abil.source.shuffle_into_lib()
    source_abil.controller.scry(2)

Cavalier_of_Gales=Creature(
    name='Cavalier of Gales',
    cost=Cost(mana={"C":2, "U":3}),
    power=5,
    toughness=5,
    subtypes=['elemental','knight'],
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Cavalier of Gales ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Cavalier_of_Gales_ETB_effect
        ),
        Triggered_Ability(
            name='Cavalier of Gales Dies',
            trigger_points=['dies'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Cavalier_of_Gales_dies_effect
        )
    ],
    rarity='mythic'
)

# Cerulean Drake
# {1}{U}
# Creature — Drake
# Flying
# Protection from red
# Sacrifice Cerulean Drake: Counter target spell that targets you.
# 1/1
Cerulean_Drake= Creature(
    name='Cerulean Drake',
    cost=Cost(mana={"C":1, "U":1}),
    power=1,
    toughness=1,
    subtypes=['drake'],
    protection_effects=[Protection(condition=lambda obj: 'R' in obj.colors)],
    activated_abils=[
        Activated_Ability(
            name='Cerulean Drake counter ability',
            cost=Cost(non_mana=[lambda source_abil: source_abil.source.sacrifice()]),
            targets=[Target(criteria= lambda source, obj: isinstance(obj, Card) and
                obj.targets!=[] and any([i.target_obj==source.controller for
                i in obj.targets]), c_zones=[], c_stack=True)],
            abil_effect= lambda source_abil: source_abil.get_targets().counterspelled()
        )
    ],
    rarity='uncommon'
)

# Cloudkin Seer
# {2}{U}
# Creature — Elemental Wizard
# Flying
# When Cloudkin Seer enters the battlefield, draw a card.
# 2/1

Cloudkin_Seer= Creature(
    name='Cloudkin Seer',
    cost=Cost(mana={"C":2, "U":1}),
    power=2,
    toughness=1,
    subtypes=['elemental','wizard'],
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Cloudkin Seer ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.draw_card()
        )
    ],
    rarity='common'
)


# Convolute
# {2}{U}
# Instant
# Counter target spell unless its controller pays {4}.

def Convolute_effect(source_card):
    target=source_card.get_targets()
    target.controller.get_potential_mana()
    if target.controller.check_potential_mana({'C':4}) and target.controller \
        .input_bool(label='pay for convolute'):
        if target.controller.game.verbose>=2:
            print(target.controller, 'pays for Convolute')
        convolute_cost_obj=Cost(mana={'C':4})
        target.controller.tap_sources_for_cost(convolute_cost_obj.mana_cost, convolute_cost_obj)
        target.controller.pay_mana({'C':4})
    else:
        if target.controller.game.verbose>=2:
            print(target.controller, 'does not pay for Convolute')
        target.counterspelled()

Convolute = Instant(
    name='Convolute',
    cost=Cost(mana={"C":2, "U":1}),
    targets=[Target(criteria= lambda source, obj: isinstance(obj, Card), c_zones=[],
        c_stack=True)],
    spell_effect= Convolute_effect,
    rarity='common'
)


# Drawn from Dreams
# {2}{U}{U}
# Sorcery
# Look at the top seven cards of your library. Put two of them into your hand
# and the rest on the bottom of your library in a random order.
def Drawn_from_Dreams_effect(source_card):
    selected = source_card.controller.select_top_lib(n_cards=7,n_selected=2,
        non_select_func='bottom of lib, random order')
    if selected != None:
        source_card.controller.lib.leave_zone(selected[0])
        source_card.controller.hand.enter_zone(selected[0])

Drawn_from_Dreams = Sorcery(
    name='Drawn from Dreams',
    cost=Cost(mana={"C":2, "U":2}),
    spell_effect= Drawn_from_Dreams_effect,
    rarity='rare'
)


# Dungeon Geists
# {2}{U}{U}
# Creature — Spirit
# Flying
# When Dungeon Geists enters the battlefield, tap target creature an opponent
# controls. That creature doesn’t untap during its controller’s untap step for
# as long as you control Dungeon Geists.
# 3/3
def Dungeon_Geists_effect(source_abil):
    target=source_abil.get_targets()
    target.tap(for_cost=False)
    # apply the don't untap effect to the target
    target.applied_effects.append(source_abil.source)
    source_abil.source.nonkeyword_static_abils[0].apply_to_card(target)

def Dungeon_Geists_static_effect(applied_obj,source_abil):
    applied_obj.keyword_static_abils.append('stop_untap')

def r_Dungeon_Geists_static_effect(applied_obj,source_abil):
    applied_obj.remove_keyword('stop_untap')
    applied_obj.applied_effects.remove(source_abil.source)

Dungeon_Geists = Creature(
    name='Dungeon Geists',
    cost=Cost(mana={'C':2,"U":2}),
    power=3,
    toughness=3,
    subtypes=['sprit'],
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Dungeon Geists ETB abil',
            trigger_points=['enter field'],
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,
                c_own=False)],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Dungeon_Geists_effect
        ),
    ],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Dungeon Geists stop untap effect",
            effect_condition= lambda applied_obj, source_abil: source_abil.source in
                applied_obj.applied_effects,
            effect_func= Dungeon_Geists_static_effect,
            reverse_effect_func = r_Dungeon_Geists_static_effect
        )
    ],
    rarity='rare'
)

# Faerie Miscreant
# {U}
# Creature — Faerie Rogue
# Flying
# When Faerie Miscreant enters the battlefield, if you control another creature
# named Faerie Miscreant, draw a card.
# 1/1
Faerie_Miscreant= Creature(
    name='Faerie Miscreant',
    cost=Cost(mana={"U":1}),
    power=1,
    toughness=1,
    subtypes=['faerie','rogue'],
    triggered_abils=[
        Triggered_Ability(
            name='Faerie Miscreant ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source
                and len([i for i in obj.controller.field if i.name=='Faerie Miscreant'])>=2,
            abil_effect= lambda source_abil: source_abil.controller.draw_card()
        )
    ],
    rarity='common'
)


# Flood of Tears {4}{U}{U}
# Sorcery
# Return all nonland permanents to their owners’ hands. If you return four or
# more nontoken permanents you control this way, you may put a permanent card
# from your hand onto the battlefield.
def Flood_of_Tears_effect(source_card):
    for i in source_card.controller.opponent.field:
        if 'land' not in i.types:
            i.bounce()

    self_bounce=0
    for i in source_card.controller.field:
        if 'land' not in i.types:
            i.bounce()
            if 'token' not in i.types:
                self_bounce+=1

    if self_bounce>=4:
        permanents = [i for i in source_card.controller.hand if i.is_permanent()]
        selected = source_card.controller.input_choose(permanents)
        source_card.controller.hand.leave_zone(selected)
        source_card.controller.field.enter_zone(selected)
        if source_card.controller.game.verbose>=2:
            print(selected, 'enters the battlefield from hand')

Flood_of_Tears=Sorcery(
    name='Flood of Tears',
    cost=Cost(mana={'C':4,"U":2}),
    spell_effect= Flood_of_Tears_effect,
    rarity='rare'
)

# Fortress Crab {3}{U}
# Creature — Crab
# 1/6
Fortress_Crab = Creature(
    name='Fortress Crab',
    cost=Cost(mana={'C':3,"U":1}),
    power=1,
    toughness=6,
    subtypes=['crab'],
    rarity='common'
)

# Frilled Sea Serpent {4}{U}{U}
# Creature — Serpent
# {5}{U}{U}: Frilled Sea Serpent can’t be blocked this turn.
# 4/6
def EOTr_Frilled_Sea_Serpent_abil(creature):
    creature.remove_keyword('unblockable')

def Frilled_Sea_Serpent_abil(source_abil):
    source_abil.source.keyword_static_abils.append('unblockable')
    source_abil.source.EOT_reverse_effects.append(EOTr_Frilled_Sea_Serpent_abil)

Frilled_Sea_Serpent = Creature(
    name='Frilled Sea Serpent',
    cost=Cost(mana={'C':4,"U":2}),
    power=4,
    toughness=6,
    subtypes=['serpent'],
    activated_abils= [
        Activated_Ability(
            name='Frilled Sea Serpent ability',
            cost=Cost(mana={'C':5,'U':2}),
            abil_effect= Frilled_Sea_Serpent_abil
        )
    ],
    rarity='common'
)

# Frost Lynx {2}{U}
# Creature — Elemental Cat
# When Frost Lynx enters the battlefield, tap target creature an opponent
# controls. That creature doesn’t untap during its controller’s next untap step.
# 2/2

def Frost_Lynx_ETB(source_abil):
    target=source_abil.get_targets()
    target.tap(for_cost=False)
    target.keyword_static_abils.append('stop_next_untap')

Frost_Lynx= Creature(
    name='Frost Lynx',
    cost=Cost(mana={'C':2,"U":1}),
    power=2,
    toughness=2,
    subtypes=['elemental','cat'],
    triggered_abils=[
        Triggered_Ability(
            name='Frost Lynx Creature ETB',
            trigger_points=['enter field'],
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,c_own=False)],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Frost_Lynx_ETB
        )
    ],
    rarity='common'
)

# Hard Cover {U}
# Enchantment — Aura
# Enchant creature
# Enchanted creature gets +0/+2 and has “{T}: Draw a card, then discard a card.”

def Hard_Cover_effect(attached_to):
    attached_to.change_toughness(2)
    abil=Activated_Ability(
        name='Hard Cover ability',
        cost=Cost(
            non_mana=[lambda source_abil: source_abil.source.tap()],
            non_mana_check=[lambda source_abil: source_abil.source.tapped==False
            and (source_abil.source.summoning_sick==False or 'creature' not in
            source_abil.source.types)]
        ),
        abil_effect= lambda source_abil: source_abil.controller.loot(),
    )
    abil.assign_source(attached_to)
    abil.assign_ownership(attached_to.controller)
    attached_to.activated_abils= attached_to.activated_abils+[abil]

def r_Hard_Cover_effect(attached_to):
    attached_to.change_toughness(-2)
    # remove granted activated ability (remove only one copy in case multiples
    # of this aura are attached to the target)
    abil_instances=[i for i in attached_to.activated_abils if i.name==
        'Hard Cover ability']
    attached_to.activated_abils.remove(abil_instances[0])

Hard_Cover = Aura(
    name='Hard Cover',
    cost=Cost(mana={'U':1}),
    aura_static_effect=Attached_Effect(
        name="Hard Cover Aura effects",
        effect_func=Hard_Cover_effect,
        reverse_effect_func=r_Hard_Cover_effect
    ),
    rarity='uncommon'
)

# TODO: Leyline of Anticipation

def Leyline_of_Anticipation_begin_game(source_abil):
    if source_abil.source.owner.input_bool(label='Leyline begin of game abil'):
        source_abil.source.owner.hand.leave_zone(source_abil.source)
        source_abil.source.owner.field.enter_zone(source_abil.source)
        if source_abil.source.controller.game.verbose>=2:
            print(source_abil.source.controller, 'puts Leyline of Anticipation into play at beginning of game')
    else:
        if source_abil.source.controller.game.verbose>=2:
            print(source_abil.source.controller, 'elects not to put Leyline of Anticipation into play at beginning of game')

Leyline_of_Anticipation= Enchantment(
    name="Leyline of Anticipation",
    cost=Cost(mana={'C':2,'U':2}),
    triggered_abils=[
        Triggered_Ability(
            name="Leyline of Anticipation begin game effect",
            trigger_points=['begin game'],
            add_trigger_zones=['hand'],
            remove_trigger_zones=['hand'],
            abil_effect=Leyline_of_Anticipation_begin_game,
            stack=False
        )
    ],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Leyline of Anticipation flash effect",
            own_apply_zones=['yard','hand','lib','exile'], opp_apply_zones=[],
            players='self',
            effect_func= lambda applied_obj, source_abil:
                applied_obj.add_keyword('flash'),
            reverse_effect_func = lambda applied_obj, source_abil:
                applied_obj.remove_keyword('flash')
        )
    ],
    rarity='rare'
)

# Masterful Replication {5}{U}
# Instant
# Choose one —
# • Create two 3/3 colorless Golem artifact creature tokens.
# • Choose target artifact you control. Each other artifact you control becomes
# a copy of that artifact until end of turn.

def Masterful_Replication_effect(source_card):
    if source_card.selected_mode==1:
        for _ in range(2):
            source_card.controller.create_token(
                Creature_Token(
                    name='Golem 3/3',
                    colors=[],
                    types=['artifact','creature'],
                    subtypes=['golem'],
                    power=3,
                    toughness=3
                )
            )
    if source_card.selected_mode==2:
        target=source_card.get_targets()
        for i in source_card.controller.field:
            if 'artifact' in i.types:
                i.become_copy(target)
                i.EOT_reverse_effects.append(lambda target: target.revert_copy())

Masterful_Replication = Instant (
    name='Masterful Replication',
    cost=Cost(mana={'C':5,'U':1}),
    moded=True,
    n_modes=2,
    mode_labels=['Create Golems', 'Copy Artifacts'],
    targets=[Target(criteria=lambda source, obj: 'artifact' in obj.types,
        c_opponent=False, mode_linked=True, mode_num=2)],
    spell_effect= Masterful_Replication_effect,
    rarity='rare'
)

# Metropolis Sprite {1}{U}
# Creature — Faerie Rogue
# Flying
# {U}: Metropolis Sprite gets +1/-1 until end of turn.
# 1/2

def EOTr_Metropolis_Sprite_effect(creature):
    creature.change_power(-1)
    creature.change_toughness(1)
def Metropolis_Sprite_effect(source_abil):
    source_abil.source.change_power(1)
    source_abil.source.change_toughness(-1)
    source_abil.source.EOT_reverse_effects.append(EOTr_Metropolis_Sprite_effect)

Metropolis_Sprite= Creature(
    name='Metropolis Sprite',
    cost=Cost(mana={'C':1,"U":1}),
    power=1,
    toughness=2,
    subtypes=['faerie','rogue'],
    keyword_static_abils=['flying'],
    activated_abils=[
        Activated_Ability(
            name='Metropolis Sprite Effect',
            cost=Cost(mana={'U':1}),
            abil_effect=Metropolis_Sprite_effect
        )
    ],
    rarity='common'
)

# Moat Piranhas {1}{U}
# Creature — Fish
# Defender (This creature can’t attack.)
# 3/3
Moat_Piranhas= Creature(
    name='Moat Piranhas',
    cost=Cost(mana={'C':1,"U":1}),
    power=3,
    toughness=3,
    subtypes=['fish'],
    keyword_static_abils=['defender'],
    rarity='common'
)

# Mu Yanling, Sky Dancer {1}{U}{U}
# Legendary Planeswalker — Yanling
# +2: Until your next turn, up to one target creature gets -2/-0 and loses flying.
# −3: Create a 4/4 blue Elemental Bird creature token with flying.
# −8: You get an emblem with “Islands you control have ‘{T}: Draw a card.’”
# Loyalty: 2

def next_turn_r_Mu_Yangling_plus2_effect(creature):
    creature.change_power(2)
    creature.remove_keyword('loses_flying')

def Mu_Yanling_plus2_effect(source_abil):
    target=source_abil.get_targets()
    if target!=None:
        target.change_power(-2)
        target.keyword_static_abils.append('loses_flying')
        target.next_turn_reverse_effects.append([source_abil.controller, next_turn_r_Mu_Yangling_plus2_effect])

def Mu_Yanling_minus3_effect(source_abil):
    source_abil.controller.create_token(
        Creature_Token(
            name='Elemental Bird 4/4 Flying',
            colors=['U'],
            subtypes=['elemental','bird'],
            keyword_static_abils=['flying'],
            power=4,
            toughness=4
        )
    )

def Mu_Yanling_minus8_reverse(applied_obj,source_abil):
    abils = [i for i in applied_obj.activated_abils if i.name=='Mu Yanling Emblem granted ability']
    applied_obj.activated_abils.remove(abils[0])

def Mu_Yanling_minus8_grant_abil(applied_obj, source_abil):
    abil= Activated_Ability(
            name='Mu Yanling Emblem granted ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect= lambda source_abil: source_abil.source.controller.draw_card()
        )
    applied_obj.activated_abils=applied_obj.activated_abils+[abil]

def Mu_Yanling_minus8_effect(source_abil):
    emblem=Emblem(
        name='Mu Yanling Emblem',
        static_abils=[
            Glob_Static_Effect(
                name="Mu Yanling Emblem effect",
                effect_condition= lambda applied_obj, source_abil: 'island' in \
                    applied_obj.subtypes,
                effect_func= Mu_Yanling_minus8_grant_abil,
                reverse_effect_func = Mu_Yanling_minus8_reverse
            )
        ]

    )
    emblem.give_player(source_abil.controller)

Mu_Yanling_Sky_Dancer=Planeswalker(
    name='Mu Yanling, Sky Dancer',
    subtypes=['Yanling'],
    cost=Cost(mana={'C':1,'U':2}),
    loyalty=2,
    activated_abils=[
        Activated_Ability(
            name='Mu Yanling +2 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(2)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False]
            ),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,
                c_required=False)],
            abil_effect= Mu_Yanling_plus2_effect,
            flash=False
        ),
        Activated_Ability(
            name='Mu Yanling -3 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(-3)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False and
                    source_abil.source.loyalty>=3]
            ),
            abil_effect= Mu_Yanling_minus3_effect,
            flash=False
        ),
        Activated_Ability(
            name='Mu Yanling -8 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(-8)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False and
                    source_abil.source.loyalty>=8]
            ),
            abil_effect= Mu_Yanling_minus8_effect,
            flash=False
        )
    ],
    rarity='mythic'
)

# Negate {1}{U}
# Instant
# Counter target noncreature spell.
def Negate_effect(source_card):
    target=source_card.get_targets()
    target.counterspelled()

Negate=Instant(
    name='Negate',
    cost=Cost(mana={'C':1,"U":1}),
    targets=[Target(criteria= lambda source, obj: 'creature' not in obj.types, c_zones=[],
        c_stack=True)],
    spell_effect= Negate_effect,
    rarity='common'
)

# Octoprophet {3}{U}
# Creature — Octopus
# When Octoprophet enters the battlefield, scry 2.
# 3/3
Octoprophet= Creature(
    name='Octoprophet',
    cost=Cost(mana={"C":3, "U":1}),
    power=3,
    toughness=3,
    subtypes=['octopus'],
    triggered_abils=[
        Triggered_Ability(
            name='Octoprophet ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.scry(2)
        )
    ],
    rarity='common'
)

# Portal of Sanctuary {2}{U}
# Artifact
# {1}, {T}: Return target creature you control and each Aura attached to it to
# their owners’ hands. Activate this ability only during your turn.

def Portal_of_Sancutary_effect(source_abil):
    target = source_abil.get_targets()
    for i in target.attached_objs:
        if 'aura' in i.subtypes:
            i.bounce()
    target.bounce()

Portal_of_Sancutary= Artifact(
    name='Portal of Sanctuary',
    cost=Cost(mana={'C':2,'U':1}),
    activated_abils=[
        Activated_Ability(
            name='Portal of Sanctuary effect',
            cost=Cost(
                mana={'C':1},
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            requirements=[Requirement(lambda source: source.controller.game.act_plyr==
                source.controller)],
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,c_opponent=False)],
            abil_effect=Portal_of_Sancutary_effect
        )
    ],
    rarity='uncommon'
)

# Renowned Weaponsmith {1}{U}
# Creature — Human Artificer
# {T}: Add {C}{C}. Spend this mana only to cast artifact spells or activate
# abilities of artifacts.
# {U}, {T}: Search your library for a card named Heart-Piercer Bow or Vial of
# Dragonfire, reveal it, put it into your hand, then shuffle your library.
# 1/3
def Renowned_Weaponsmith_select_effect(card):
    card.owner.lib.leave_zone(card)
    card.owner.hand.enter_zone(card)

Renowned_Weaponsmith= Creature(
    name='Renowned Weaponsmith',
    cost=Cost(mana={"C":1, "U":1}),
    power=1,
    toughness=3,
    subtypes=['human','artificer'],
    mana_source=True,
    activated_abils= [
        Activated_Ability(
            name='Renowned Weaponsmith mana ability',
            cost= Cost(
                    non_mana=[lambda source_abil: source_abil.source.tap()],
                    non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                    and (source_abil.source.summoning_sick==False or 'creature' not in
                    source_abil.source.types)]
                ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('C', 2),
            potential_mana=Potential_Mana({'C':2}, use_condition= lambda obj:
                obj!=None and ('artifact' in obj.types or
                (isinstance(obj, Activated_Ability) and obj.source.types=='artifact'))),
            mana_abil=True,
        ),
        Activated_Ability(
            name='Renowned Weaponsmith fetch ability',
            cost= Cost(
                mana={'U':1},
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect= lambda source_abil: source_abil.source.controller.search_library(
                elig_condition= lambda card: card.name=="Heart-Piercer Bow" or
                    card.name=='Vial of Dragonfire',
                select_effect= Renowned_Weaponsmith_select_effect,
            )
        )
    ],
    rarity='uncommon'
)

# Sage's Row Denizen {2}{U}
# Creature — Vedalken Wizard
# Whenever another blue creature enters the battlefield under your control, target
# player mills two cards.
# 2/3
Sages_Row_Denizen=Creature(
    name="Sage's Row Denizen",
    cost=Cost(mana={'C':2,"U":1}),
    power=2,
    toughness=3,
    subtypes=['vedalken','wizard'],
    triggered_abils=[
        Triggered_Ability(
            name='Sages Row Denizen Creature ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'creature' in obj.types
                and source_abil.source.controller==obj.controller and
                obj!=source_abil.source and 'U' in obj.colors,
            targets=[Target(criteria=lambda source, obj: True, c_zones=[],
                c_players='both')],
            abil_effect= lambda source_abil: source_abil.get_targets().mill_card(2)
        )
    ],
    rarity='common'
)

# Scholar of the Ages {5}{U}{U}
# Creature — Human Wizard
# When Scholar of the Ages enters the battlefield, return up to two target
# instant and/or sorcery cards from your graveyard to your hand.
# 3/3
def Scholar_of_the_Ages_effect(source_card):
    for card in source_card.get_targets(check_illegal_targets=True):
        if card!=None:
            card.owner.yard.leave_zone(card)
            card.owner.hand.enter_zone(card)
            if source_card.owner.game.verbose>=2:
                print(card, 'returned from graveyard to hand')

Scholar_of_the_Ages=Creature(
    name="Scholar of the Ages",
    cost=Cost(mana={'C':5,"U":2}),
    power=3,
    toughness=3,
    subtypes=['human','wizard'],
    triggered_abils=[
        Triggered_Ability(
            name='Scholar of the Ages ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[
                    Target(criteria= lambda source, obj: 'instant' in obj.types or
                    'sorcery' in obj.types, c_opponent=False ,c_zones=['yard'],
                    c_different=True,c_required=False),
                    Target(criteria= lambda source, obj: 'instant' in obj.types or
                    'sorcery' in obj.types, c_opponent=False ,c_zones=['yard'],
                    c_different=True,c_required=False)
                ],
            abil_effect= Scholar_of_the_Ages_effect
        )
    ],
    rarity='uncommon'
)

# Sleep Paralysis {3}{U}
# Enchantment — Aura
# Enchant creature
# When Sleep Paralysis enters the battlefield, tap enchanted creature.
# Enchanted creature doesn’t untap during its controller’s untap step.
def Sleep_Paralysis_effect(attached_to):
    attached_to.keyword_static_abils.append('stop_untap')
def r_Sleep_Paralysis_effect(attached_to):
    attached_to.remove_keyword('stop_untap')
def Sleep_Paralysis_triggered_abil(source_abil):
    if source_abil.last_known_info!=None:
        source_abil.last_known_info.tap(for_cost=False)
    elif source_abil.source.attached_to!=None:
        source_abil.attached_to.tap(for_cost=False)
Sleep_Paralysis= Aura(
    name='Sleep Paralysis',
    cost=Cost(mana={'C':3,'U':1}),
    aura_static_effect=Attached_Effect(
        name="Sleep Paralysis effect",
        effect_func=Sleep_Paralysis_effect,
        reverse_effect_func=r_Sleep_Paralysis_effect
    ),
    triggered_abils=[
        Triggered_Ability(
            name='Sleep Paralysis ETB',
            trigger_points=['enter field'],
            lki_func= lambda source_abil, effect_kwargs: source_abil.source.targets[0].target_obj,
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Sleep_Paralysis_triggered_abil
        )
    ],
    rarity='common'
)

# Spectral Sailor {U}
# Creature — Spirit Pirate
# Flash (You may cast this spell any time you could cast an instant.)
# Flying
# {3}{U}: Draw a card.
# 1/1

Spectral_Sailor=Creature(
    name='Spectral Sailor',
    cost=Cost(mana={"U":1}),
    power=1,
    toughness=1,
    subtypes=['spirit','pirate'],
    keyword_static_abils=['flying'],
    activated_abils= [
        Activated_Ability(
            name='Spectral Sailor ability',
            cost=Cost(mana={'C':3,'U':1}),
            abil_effect= lambda source_abil: source_abil.controller.draw_card()
        )
    ],
    rarity='uncommon'
)

# Tale's End {1}{U}
# Instant
# Counter target activated ability, triggered ability, or legendary spell.
def Tales_End_effect(source_card):
    target=source_card.get_targets()
    target.counterspelled()

def Tales_End_criteria(source, obj):
    result=False
    if 'legendary' in obj.types:
        result=True
    if isinstance(obj, Effect_Instance):
        result=True
    return result

Tales_End=Instant(
    name="Tale's End",
    cost=Cost(mana={'C':1,"U":1}),
    targets=[Target(criteria= Tales_End_criteria, c_zones=[],
        c_stack=True)],
    spell_effect= Tales_End_effect,
    rarity='rare'
)

# Unsummon {U}
# Instant
# Return target creature to its owner’s hand.

Unsummon=Instant(
    name='Unsummon',
    cost=Cost(mana={"U":1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
    spell_effect= lambda source_card: source_card.get_targets().bounce(),
    rarity='common'
)

# Warden of Evos Isle {2}{U}
# Creature — Bird Wizard
# Flying
# Creature spells with flying you cast cost {1} less to cast.
# 2/2
def Warden_of_Evos_Isle_cost_reduce(applied_obj, source_abil):
    source_abil.source.controller.cost_mods.append(
        Cost_Modification(
            name='Warden of Evos Isle cost reduction obj',
            cost_mod={'C':-1},
            cost_mod_source=source_abil.source,
            mod_condition= lambda cost_obj, cost_mod_source: \
                isinstance(cost_obj.source, Card) and 'creature' in cost_obj.source.types and
                'flying' in cost_obj.source.keyword_static_abils
        )
    )

def r_Warden_of_Evos_Isle_cost_reduce(applied_obj, source_abil):
    abil_instances=[i for i in source_abil.controller.cost_mods if i.name==
        'Warden of Evos Isle cost reduction obj']
    if abil_instances != []:
        source_abil.controller.cost_mods.remove(abil_instances[0])

Warden_of_Evos_Isle= Creature(
    name='Warden of Evos Isle',
    cost=Cost(mana={'C':2,"U":1}),
    power=2,
    toughness=2,
    subtypes=['bird','wizard'],
    keyword_static_abils=['flying'],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Warden of Evos Isle cost reduction",
            own_apply_zones=[], opp_apply_zones=[],
            players='self',
            effect_func= Warden_of_Evos_Isle_cost_reduce,
            reverse_effect_func= r_Warden_of_Evos_Isle_cost_reduce,
        )
    ],
    rarity='uncommon'
)


# Winged Words {2}{U}
# Sorcery
# This spell costs {1} less to cast if you control a creature with flying.
# Draw two cards.

Winged_Words=Sorcery(
    name='Winged Words',
    cost=Cost(mana={'C':2,"U":1}, cost_mods=[
        Cost_Modification(
            name='Winged Words Cost Mod',
            cost_mod={'C':-1},
            mod_condition= lambda cost_obj, cost_mod_source: any([
                'flying' in i.keyword_static_abils for i in cost_mod_source.controller.field
                if 'creature' in i.types]
            )
        )
    ]),
    spell_effect= lambda source_card: source_card.controller.draw_card(2),
    rarity='common'
)

# Yarok's Wavecrasher {3}{U}
# Creature — Elemental
# When Yarok’s Wavecrasher enters the battlefield, return another creature you
# control to its owner’s hand.
# 4/4
def Yaroks_Wavecrasher_effect(source_abil):
    creature_select=source_abil.controller.input_choose([i for i in source_abil.controller.field
        if i!=source_abil.source and 'creature' in i.types], permit_empty_list=True)
    if creature_select!=None:
        creature_select.bounce()

Yaroks_Wavecrasher = Creature(
    name="Yarok's Wavecrasher",
    cost=Cost(mana={'C':3,"U":1}),
    power=4,
    toughness=4,
    subtypes=['elemental'],
    triggered_abils=[
        Triggered_Ability(
            name="Yarok's Wavecrasher ETB effect",
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Yaroks_Wavecrasher_effect
        )
    ],
    rarity='uncommon'
)

# Zephyr Charge {1}{U}
# Enchantment
# {1}{U}: Target creature gains flying until end of turn.

def Zephyr_Charge_effect(source_abil):
    target=source_abil.get_targets()
    target.keyword_static_abils.append('flying')
    target.EOT_reverse_effects.append(lambda creature: creature.remove_keyword('flying'))

Zephyr_Charge=Enchantment(
    name='Zephyr Charge',
    cost=Cost(mana={'C':1,'U':1}),
    activated_abils=[
        Activated_Ability(
            name='Zephyr Charge ability',
            cost=Cost(mana={'C':1,'U':1}),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
            abil_effect= Zephyr_Charge_effect
        )
    ],
    rarity='common'
)

# Black
# Agonizing Syphon {3}{B}
# Sorcery
# Agonizing Syphon deals 3 damage to any target and you gain 3 life.
def Agonizing_Syphon_effect(source_card):
    source_card.get_targets().take_damage(3, source=source_card, combat=False)
    source_card.controller.change_life(3)

Agonizing_Syphon= Sorcery(
    name='Agonizing Syphon',
    cost=Cost(mana={"C":3, "B":1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types or
        'planeswalker' in obj.types, c_players='both')],
    spell_effect= Agonizing_Syphon_effect,
    rarity='common'
)

# Audacious Thief {2}{B}
# Creature — Human Rogue
# Whenever Audacious Thief attacks, you draw a card and you lose 1 life.
# 2/2
def Audacious_Thief_effect(source_abil):
    source_abil.controller.draw_card()
    source_abil.controller.change_life(-1)

Audacious_Thief= Creature(
    name='Audacious Thief',
    cost=Cost(mana={"C":2, "B":1}),
    power=2,
    toughness=2,
    triggered_abils=[
        Triggered_Ability(
            name='Audacious Thief attack trigger',
            trigger_points=['on attack'],
            trigger_condition=lambda source_abil, obj, **kwargs:
                source_abil.source==obj,
            abil_effect=Audacious_Thief_effect
        )
    ],
    subtypes=['human','rogue'],
    rarity='common'
)

# Barony Vampire
# 2B
# Creature - Vampire
# 3/2
Barony_Vampire= Creature(
    name='Barony Vampire',
    cost=Cost(mana={"C":2, "B":1}),
    power=3,
    toughness=2,
    subtypes=['vampire'],
    rarity='common'
)

# Bladebrand {1}{B}
# Instant
# Target creature gains deathtouch until end of turn.
# Draw a card.
def EOTr_Bladebrand(creature):
    creature.remove_keyword('deathtouch')

def Bladebrand_effect(source_card):
    source_card.get_targets().keyword_static_abils.append('deathtouch')
    source_card.get_targets().EOT_reverse_effects.append(EOTr_Bladebrand)
    source_card.controller.draw_card()

Bladebrand= Instant(
    name='Bladebrand',
    cost=Cost(mana={"C":1, "B":1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
    spell_effect= Bladebrand_effect,
    rarity='common'
)

# Blightbeetle {1}{B}
# Creature — Insect
# Protection from green
# Creatures your opponents control can’t have +1/+1 counters put on them.
# 1/1

def Blightbeetle_effect(applied_obj, source_abil):
    applied_obj.keyword_static_abils.append('cant_have_plus1_plus1')
def r_Blightbeetle_effect(applied_obj, source_abil):
    applied_obj.remove_keyword('cant_have_plus1_plus1')

Blightbeetle= Creature(
    name='Blightbeetle',
    cost=Cost(mana={"C":1, "B":1}),
    power=1,
    toughness=1,
    subtypes=['insect'],
    protection_effects=[Protection(condition=lambda obj: 'G' in obj.colors)],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Blightbeetle Counter effect",
            effect_condition= lambda applied_obj, source_abil: 'creature' in \
                applied_obj.types,
            effect_func= Blightbeetle_effect,
            reverse_effect_func = r_Blightbeetle_effect
        )
    ],
    rarity='uncommon'
)

# Blood Burglar {1}{B}
# Creature — Vampire Rogue
# As long as it’s your turn, Blood Burglar has lifelink.
# 2/2
def Blood_Burglar_effect(source_abil):
    source_abil.source.keyword_static_abils.append('lifelink')
def r_Blood_Burglar_effect(source_abil):
    source_abil.source.remove_keyword('lifelink')

Blood_Burglar= Creature(
    name='Blood Burglar',
    cost=Cost(mana={"C":1, "B":1}),
    power=2,
    toughness=2,
    nonkeyword_static_abils=[
        Local_Static_Effect(
            name='Blood Burglar lifelink effect',
            effect_condition = lambda source_abil: source_abil.controller==
                source_abil.controller.game.act_plyr,
            effect_func=Blood_Burglar_effect,
            reverse_effect_func=r_Blood_Burglar_effect
        )
    ],
    subtypes=['vampire'],
    rarity='common'
)

# Blood for Bones {3}{B}
# Sorcery
# As an additional cost to cast this spell, sacrifice a creature.
# Return a creature card from your graveyard to the battlefield, then return
# another creature card from your graveyard to your hand.

def Blood_for_Bones_effect(source_card):
    if len([i for i in source_card.controller.yard if 'creature' in i.types])>0:
        creature1 = source_card.controller.input_choose(
            [i for i in source_card.controller.yard if 'creature' in i.types]
        )
        source_card.controller.yard.leave_zone(creature1)
        source_card.controller.field.enter_zone(creature1)

    if len([i for i in source_card.controller.yard if 'creature' in i.types])>0:
        creature2 = source_card.controller.input_choose(
            [i for i in source_card.controller.yard if 'creature' in i.types]
        )
        source_card.controller.yard.leave_zone(creature2)
        source_card.controller.hand.enter_zone(creature2)

Blood_for_Bones= Sorcery(
    name='Blood for Bones',
    cost=Cost(
        mana={'C':3,"B":1},
        non_mana= [lambda source_abil: source_abil.controller.input_choose(
            [i for i in source_abil.controller.field if 'creature' in i.types]
        ).sacrifice()],
        non_mana_check= [lambda source_abil: len([i for i in source_abil.controller.field
            if 'creature' in i.types])>0]
    ),
    spell_effect= Blood_for_Bones_effect,
    rarity='uncommon'
)

# Bloodsoaked Altar {4}{B}{B}
# Artifact
# {T}, Pay 2 life, Discard a card, Sacrifice a creature: Create a 5/5 black Demon
#     creature token with flying. Activate this ability only any time you could
#     cast a sorcery.

Bloodsoaked_Altar= Artifact(
    name='Bloodsoaked Altar',
    cost=Cost(mana={'C':4,'B':2}),
    activated_abils=[
        Activated_Ability(
            name='Bloodsoaked Altar ability',
            flash=False,
            cost=Cost(
                non_mana=[
                    lambda source_abil: source_abil.controller.sacrifice_permanent(types=['creature']),
                    lambda source_abil: source_abil.controller.discard_cards(1),
                    lambda source_abil: source_abil.source.tap(),
                    lambda source_abil: source_abil.source.controller.pay_life(2)
                ],
                non_mana_check=[
                    lambda source_abil: len([i for i in source_abil.controller.field
                        if 'creature' in i.types])>0,
                    lambda source_abil: len([i for i in source_abil.controller.hand])>0,
                    lambda source_abil: source_abil.source.tapped==False
                    and (source_abil.source.summoning_sick==False or 'creature' not in
                    source_abil.source.types)
                ]
            ),
            abil_effect= lambda source_abil: source_abil.controller.create_token(
                Creature_Token(
                    name="Demon 5/5 flying",
                    colors=['B'],
                    types=['creature'],
                    subtypes=['demon'],
                    power=5,
                    toughness=5,
                    keyword_static_abils=['flying']
                )
            )
        )
    ],
    rarity='uncommon'
)

# Bloodthirsty Aerialist {1}{B}{B}
# Creature — Vampire Rogue
# Flying
# Whenever you gain life, put a +1/+1 counter on Bloodthirsty Aerialist.
# 2/3

Bloodthirsty_Aerialist= Creature(
    name='Bloodthirsty Aerialist',
    cost=Cost(mana={'C':1, 'B':2}),
    subtypes=['vampire','rogue'],
    power=2,
    toughness=3,
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Bloodthirst Aerialist get +1/+1 counter on lifegain',
            trigger_points=['lifegain'],
            trigger_condition=lambda source_abil, **kwargs:
                source_abil.source.controller==kwargs['player'],
            abil_effect=lambda source_abil: deepcopy(plus1_plus1_counter)
                .attach_to(source_abil.source)
        )
    ],
    rarity='uncommon'
)

# Bone Splinters {B}
# Sorcery
# As an additional cost to cast this spell, sacrifice a creature.
# Destroy target creature.
Bone_Splinters= Sorcery(
    name='Bone Splinters',
    cost=Cost(
        mana={"B":1},
        non_mana= [lambda source_abil: source_abil.controller.input_choose(
            [i for i in source_abil.controller.field if 'creature' in i.types and
            i!=source_abil.targets[0].target_obj]
        ).sacrifice()],
        non_mana_check= [lambda source_abil: len([i for i in source_abil.controller.field
            if 'creature' in i.types and i!=source_abil.targets[0].target_obj])>0]
    ),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
    spell_effect= lambda source_card: source_card.get_targets().destroy(),
    rarity='common'
)

# Boneclad Necromancer {3}{B}{B}
# Creature — Human Wizard
# When Boneclad Necromancer enters the battlefield, you may exile target creature
# card from a graveyard. If you do, create a 2/2 black Zombie creature token.
# 3/3
def Boneclad_Necromancer_effect(source_abil):
    target=source_abil.get_targets()
    if target!=None:
        target.exile()
        source_abil.controller.create_token(
            Creature_Token(
                name='Zombie 2/2',
                colors=['B'],
                subtypes=['zombie'],
                power=2,
                toughness=2
            )
        )

Boneclad_Necromancer= Creature(
    name='Boneclad Necromancer',
    cost=Cost(mana={"C":3, "B":2}),
    power=3,
    toughness=3,
    subtypes=['human','wizard'],
    triggered_abils=[
        Triggered_Ability(
            name='Boneclad_Necromancer ETB ability',
            choices=[Choice(lambda source_card: source_card.controller.input_bool(
                label='use Boneclad Necromancer ETB'))],
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,
                c_zones=['yard'])],
            abil_effect= Boneclad_Necromancer_effect
        )
    ],
    rarity='common'
)

# Cavalier of Night {2}{B}{B}{B}
# Creature — Elemental Knight
# Lifelink
# When Cavalier of Night enters the battlefield, you may sacrifice another creature.
# When you do, destroy target creature an opponent controls.
# When Cavalier of Night dies, return target creature card with converted mana
# cost 3 or less from your graveyard to the battlefield.
# 4/5

def Cavalier_of_Night_ETB_effect(source_abil):
    oth_creatures=[i for i in source_abil.controller.field if i!=source_abil.source
        and 'creature' in i.types]
    if source_abil.controller.input_bool(label='use Cavalier of Night ETB') and \
        oth_creatures!=[]:
        source_abil.controller.input_choose(oth_creatures).sacrifice()
        # place reflexive trigger on stack
        effect=Effect_Instance(
            name='Cavalier of Knight destroy',
            source=source_abil.source,
            abil_effect=lambda source_abil: source_abil.get_targets().destroy(),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,
                c_own=False)],
            controller=source_abil.controller,
            types=source_abil.types,
            choices=source_abil.choices,
            requirements=source_abil.requirements,
            colors=source_abil.source.colors,
            trigger_points=source_abil.trigger_points,
            trigger_condition=source_abil.trigger_condition)
        effect.assign_source(source_abil.source)
        effect.assign_controller(source_abil.controller)
        try:
            effect.set_targets()
            source_abil.controller.game.stack.enter_zone(effect)
        except GameActionError:
            if source_abil.controller.game.verbose>=2:
                print('Cavalier of Knight ETB encountered no legal targets')

def Cavalier_of_Night_dies_effect(source_abil):
    target=source_abil.get_targets()
    source_abil.controller.yard.leave_zone(target)
    source_abil.controller.field.enter_zone(target)

Cavalier_of_Night=Creature(
    name='Cavalier of Night',
    cost=Cost(mana={'C':2,'B':3}),
    subtypes=['elemental','knight'],
    power=4,
    toughness=5,
    keyword_static_abils=['lifelink'],
    triggered_abils=[
        Triggered_Ability(
            name='Cavalier of Night ETB ability',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Cavalier_of_Night_ETB_effect
        ),
        Triggered_Ability(
            name='Cavalier of Night Dies ability',
            trigger_points=['dies'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[Target(criteria= lambda source, obj: obj.cmc<=3, c_zones=['yard'],
                c_opponent=False)],
            abil_effect= Cavalier_of_Night_dies_effect
        )
    ],
    rarity='mythic'
)
# Disfigure {B}
# Instant
# Target creature gets -2/-2 until end of turn.

def EOTr_Disfigure_effect(target):
    target.change_power(2)
    target.change_toughness(2)

def Disfigure_effect(source_card):
    target=source_card.get_targets()
    target.change_power(-2)
    target.change_toughness(-2)
    target.EOT_reverse_effects.append(EOTr_Disfigure_effect)

Disfigure = Instant(
    name='Disfigure',
    cost=Cost(mana={'B':1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
    spell_effect=Disfigure_effect,
    rarity='common'
)

# Dread Presence {3}{B}
# Creature — Nightmare
# Whenever a Swamp enters the battlefield under your control, choose one —
# • You draw a card and you lose 1 life.
# • Dread Presence deals 2 damage to any target and you gain 2 life.
# 3/3

def Dread_Presence_effect(source_abil):
    if source_abil.selected_mode==1:
        source_abil.controller.draw_card()
        source_abil.change_life(-1)
    if source_abil.selected_mode==2:
        target=source_abil.get_targets()
        target.take_damage(2, source=source_abil.source, combat=False)
        source_abil.controller.change_life(2)

Dread_Presence=Creature(
    name='Dread Presence',
    cost=Cost(mana={'C':3, 'B':1}),
    subtypes=['nightmare'],
    power=3,
    toughness=3,
    triggered_abils=[
        Triggered_Ability(
            name='Dread Presence Swamp ETB ability',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'swamp' in obj.subtypes,
            moded=True,
            n_modes=2,
            mode_labels=['Draw Card -1 Life', 'Deal 2 Gain 2'],
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types or
                'planeswalker' in obj.types, c_players='both', mode_linked=True,mode_num=2)],
            abil_effect= Dread_Presence_effect
        )
    ],
    rarity='rare'
)

# Duress {B}
# Sorcery
# Target opponent reveals their hand. You choose a noncreature, nonland card
# from it. That player discards that card.

def Duress_effect(source_card):
    target=source_card.get_targets()
    target.reveal_cards(target.hand, zone='hand')
    cands= [i for i in target.hand if 'land' not in i.types and 'creature' not in i.types]
    if cands!=[]:
        source_card.controller.input_choose(cands, label='Duress select').discard_from_hand()

Duress= Sorcery(
    name='Duress',
    cost=Cost(mana={'B':1}),
    targets=[Target(criteria= lambda source, obj: False, c_players='opp')],
    spell_effect= Duress_effect,
    rarity='common'
)

# Embodiment of Agonies {1}{B}{B}
# Creature — Demon
# Flying, deathtouch
# Embodiment of Agonies enters the battlefield with a +1/+1 counter on it for each
# different mana cost among nonland cards in your graveyard.
# 0/0

def Embodiment_of_Agonies_ETB(source_abil):
    yard= [i for i in source_abil.controller.yard if 'land' not in i.types]
    costs=[str(i.cost[0].mana_cost) for i in yard]
    cost_set=list(set(costs))
    for _ in range(len(cost_set)):
        deepcopy(plus1_plus1_counter).attach_to(source_abil.source)

Embodiment_of_Agonies= Creature(
    name='Embodiment of Agonies',
    cost=Cost(mana={'C':1, 'B':2}),
    subtypes=['demon'],
    power=0,
    toughness=0,
    keyword_static_abils=['flying','deathtouch'],
    nonkeyword_static_abils=[
        Local_Static_Effect(
            name="Embodiment of Agonies ETB",
            effect_func= Embodiment_of_Agonies_ETB,
            reverse_effect_func= lambda source_abil: True,
            effect_condition = lambda source_abil: source_abil.source.ETB_static_check==True
        )
    ],
    rarity='rare'
)

# Epicure of Blood {4}{B}
# Creature — Vampire
# Whenever you gain life, each opponent loses 1 life.
# 4/4
Epicure_of_Blood= Creature(
    name='Epicure of Blood',
    cost=Cost(mana={"C":4, "B":1}),
    power=4,
    toughness=4,
    subtypes=['vampire'],
    triggered_abils=[
        Triggered_Ability(
            name='Epicure of Blood Gain Life effect',
            trigger_points=['lifegain'],
            trigger_condition=lambda source_abil, **kwargs:
                source_abil.source.controller==kwargs['player'],
            abil_effect= lambda source_abil: source_abil.controller.opponent.change_life(-1)
        )
    ],
    rarity='common'
)

# Fathom Fleet Cutthroat {3}{B}
# Creature — Human Pirate
# When Fathom Fleet Cutthroat enters the battlefield, destroy target creature an
# opponent controls that was dealt damage this turn.
# 3/3
Fathom_Fleet_Cutthroat=Creature(
    name='Fathom Fleet Cutthroat',
    cost=Cost(mana={"C":3, "B":1}),
    power=3,
    toughness=3,
    subtypes=['human','pirate'],
    triggered_abils=[
        Triggered_Ability(
            name='Fathom Fleet Cutthroat ETB effect',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[Target(criteria= lambda source_abil, obj: 'creature' in obj.types and
                obj.damage_received>0, c_own=False)],
            abil_effect= lambda source_abil: source_abil.get_targets().destroy()
        )
    ],
    rarity='common'
)


# Feral Abomination {5}{B}
# Creature — Thrull
# Deathtouch
# 5/5
Feral_Abomination= Creature(
    name='Feral Abomination',
    cost=Cost(mana={"C":5, "B":1}),
    power=5,
    toughness=5,
    subtypes=['thrull'],
    keyword_static_abils=['deathtouch'],
    rarity='common'
)

# Gorging Vulture {2}{B}
# Creature — Bird
# Flying
# When Gorging Vulture enters the battlefield, mill four cards. You gain 1 life
# for each creature card put into your graveyard this way.
# 2/2

def Gorging_Vulture_effect(source_abil):
    check_cards=min(len(source_abil.controller.lib),4)
    source_abil.controller.mill_card(4)
    creatures= [i for i in source_abil.controller.yard[-1*check_cards:] if
        'creature' in i.types]
    source_abil.controller.change_life(len(creatures))

Gorging_Vulture= Creature(
    name='Gorging Vulture',
    cost=Cost(mana={"C":2, "B":1}),
    power=2,
    toughness=2,
    subtypes=['bird'],
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Gorging Vulture ETB ability',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Gorging_Vulture_effect
        )
    ],
    rarity='common'
)

# Gravedigger {3}{B}
# Creature — Zombie
# When Gravedigger enters the battlefield, you may return target creature card
# from your graveyard to your hand.
# 2/2
def Gravedigger_effect(source_abil):
    target=source_abil.get_targets()
    source_abil.controller.yard.leave_zone(target)
    source_abil.controller.hand.enter_zone(target)

Gravedigger= Creature(
    name='Gravedigger',
    cost=Cost(mana={"C":3, "B":1}),
    power=2,
    toughness=2,
    subtypes=['zombie'],
    triggered_abils=[
        Triggered_Ability(
            name='Gravedigger ETB ability',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,
                c_zones=['yard'], c_opponent=False)],
            abil_effect= Gravedigger_effect
        )
    ],
    rarity='common'
)

# Gruesome Scourger {3}{B}{B}
# Creature — Orc Warrior
# When Gruesome Scourger enters the battlefield, it deals damage to target
# opponent or planeswalker equal to the number of creatures you control.
# 3/3

def Gruesome_Scourger_effect(source_abil):
    target=source_abil.get_targets()
    creatures=len([i for i in source_abil.controller.field if 'creature' in i.types])
    target.take_damage(creatures, source=source_abil.source, combat=False)

Gruesome_Scourger= Creature(
    name='Gruesome Scourger',
    cost=Cost(mana={"C":3, "B":2}),
    power=3,
    toughness=3,
    subtypes=['orc','warrior'],
    triggered_abils=[
        Triggered_Ability(
            name='Gruesome Scourger ETB ability',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[Target(criteria= lambda source, obj: 'planeswalker' in obj.types,
                c_players='opp')],
            abil_effect= Gruesome_Scourger_effect
        )
    ],
    rarity='uncommon'
)

# Knight of the Ebon Legion {B}
# Creature — Vampire Knight
# {2}{B}: Knight of the Ebon Legion gets +3/+3 and gains deathtouch until end of turn.
# At the beginning of your end step, if a player lost 4 or more life this turn,
# put a +1/+1 counter on Knight of the Ebon Legion.
# 1/2

def EOTr_Knight_of_the_Ebon_Legion_ETB(creature):
    creature.change_power(-3)
    creature.change_toughness(-3)
    creature.remove_keyword('deathtouch')
def Knight_of_the_Ebon_Legion_effect(source_abil):
    source_abil.source.change_power(3)
    source_abil.source.change_toughness(3)
    source_abil.source.keyword_static_abils.append('deathtouch')
    source_abil.source.EOT_reverse_effects.append(EOTr_Knight_of_the_Ebon_Legion_ETB)


Knight_of_the_Ebon_Legion= Creature(
    name='Knight of the Ebon Legion',
    cost=Cost(mana={'B':1}),
    subtypes=['knight','vampire'],
    power=1,
    toughness=2,
    activated_abils=[Activated_Ability(
            name='Knight of the Ebon Legion activated ability',
            cost=Cost(mana={'C':2,'B':1}),
            abil_effect= Knight_of_the_Ebon_Legion_effect
        )
    ],
    triggered_abils=[Triggered_Ability(
            name='Knight of the Ebon Legion triggered ability',
            trigger_points=['end phase'],
            trigger_condition= lambda source_abil, act_plyr, **kwargs:
                act_plyr==source_abil.controller and (act_plyr.life_lost_this_turn>4
                or act_plyr.opponent.life_lost_this_turn>4),
            abil_effect= lambda source_abil: deepcopy(plus1_plus1_counter)
                .attach_to(source_abil.source)
        )
    ],
    rarity='rare'
)

# Legion's End {1}{B}
# Sorcery
# Exile target creature an opponent controls with converted mana cost 2 or less
# and all other creatures that player controls with the same name as that creature.
# Then that player reveals their hand and exiles all cards with that name from their
# hand and graveyard.

def Legions_End_effect(source_card):
    target=source_card.get_targets()
    target.exile()
    target.controller.reveal_cards(target.controller.hand, zone='hand')
    for i in target.controller.hand:
        if i.name==target.name:
            i.exile()
    for i in target.controller.yard:
        if i.name==target.name:
            i.exile()

Legions_End=Sorcery(
    name="Legion's End",
    cost=Cost(mana={'B':1,'C':1}),
    targets=[Target(criteria= lambda source_card, obj: 'creature' in obj.types and
        obj.cmc<=2, c_own=False)],
    spell_effect= Legions_End_effect,
    rarity='rare'
)

# Leyline of the Void {2}{B}{B}
# Enchantment
# If Leyline of the Void is in your opening hand, you may begin the game with it on the battlefield.
# If a card would be put into an opponent’s graveyard from anywhere, exile it instead.
def Leyline_of_the_Void_begin_game(source_abil):
    if source_abil.source.owner.input_bool(label='Leyline begin of game abil'):
        source_abil.source.owner.hand.leave_zone(source_abil.source)
        source_abil.source.owner.field.enter_zone(source_abil.source)
        if source_abil.source.controller.game.verbose>=2:
            print(source_abil.source.controller, 'puts Leyline of the Void into play at beginning of game')
    else:
        if source_abil.source.controller.game.verbose>=2:
            print(source_abil.source.controller, 'elects not to put Leyline of the Void into play at beginning of game')

Leyline_of_the_Void= Enchantment(
    name="Leyline of the Void",
    cost=Cost(mana={'B':2,'C':2}),
    triggered_abils=[
        Triggered_Ability(
            name="Leyline of the Void begin game effect",
            trigger_points=['begin game'],
            add_trigger_zones=['hand'],
            remove_trigger_zones=['hand'],
            abil_effect=Leyline_of_the_Void_begin_game,
            stack=False
        )
    ],
    nonkeyword_static_abils=[
        Replacement_Effect(
            name="Leyline of the Void graveyard exile effect",
            replace_points=['graveyard_from_anywhere'],
            replace_condition=lambda source_abil, **kwargs: True,
            replace_func = lambda source_abil, effect_kwargs: effect_kwargs['obj'].exile()
        )
    ],
    rarity='rare'
)

# Mind Rot {2}{B}
# Sorcery
# Target player discards two cards.
Mind_Rot=Sorcery(
    name='Mind Rot',
    cost=Cost(mana={'C':2, 'B':1}),
    targets=[Target(criteria= lambda source_card, obj: True, c_zones=[], c_players='both')],
    spell_effect= lambda source_card: source_card.get_targets().discard_cards(2),
    rarity='common'
)

# Murder
# 1BB
# Instant
# Destroy target creature
def Murder_effect(source_card):
    target=source_card.get_targets()
    target.destroy()

Murder= Instant(
    name='Murder',
    cost=Cost(mana={"C":1, "B":2}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
    spell_effect= Murder_effect,
    rarity='common'
)

# Noxious Grasp {1}{B}
# Instant
# Destroy target creature or planeswalker that’s green or white. You gain 1 life.
def Noxious_Grasp_effect(source_card):
    target=source_card.get_targets()
    target.destroy()
    source_card.controller.change_life(1)

Noxious_Grasp= Instant(
    name='Noxious Grasp',
    cost=Cost(mana={"C":1, "B":1}),
    targets=[Target(criteria= lambda source, obj: ('creature' in obj.types or
        'planeswalker' in obj.types) and ('W' in obj.colors or 'G' in obj.colors))],
    spell_effect= Noxious_Grasp_effect,
    rarity='uncommon'
)

# Rotting Regisaur {2}{B}
# Creature — Zombie Dinosaur
# At the beginning of your upkeep, discard a card.
# 7/6
Rotting_Regisaur=Creature(
    name='Rotting Regisaur',
    cost=Cost(mana={'C':2,'B':1}),
    subtypes=['zombie','dinosaur'],
    power=7,
    toughness=6,
    triggered_abils=[Triggered_Ability(
            name='Rotting Regisaur upkeep ability',
            trigger_points=['upkeep'],
            trigger_condition=lambda source_abil, **kwargs: True,
            abil_effect= lambda source_abil: source_abil.controller.discard_cards(1)
        )
    ],
    rarity='rare'
)

# Sanitarium Skeleton {B}
# Creature — Skeleton
# {2}{B}: Return Sanitarium Skeleton from your graveyard to your hand.
# 1/2
def Sanitarium_Skeleton_effect(source_abil):
    source_abil.controller.yard.leave_zone(source_abil.source)
    source_abil.controller.hand.enter_zone(source_abil.source)

Sanitarium_Skeleton=Creature(
    name='Sanitarium Skeleton',
    cost=Cost(mana={'B':1}),
    subtypes=['skeleton'],
    power=1,
    toughness=2,
    activated_abils=[Activated_Ability(
        name='Sanitarium Skeleton ability',
        cost=Cost(mana={'C':2, 'B':1}),
        active_zones=['yard'],
        abil_effect= lambda source_abil: Sanitarium_Skeleton_effect
        )
    ],
    rarity='common'
)

# Scheming Symmetry {B}
# Sorcery
# Choose two target players. Each of them searches their library for a card,
# then shuffles their library and puts that card on top of it.
def Scheming_Symmetry_select_effect(card):
    card.owner.lib.leave_zone(card)
    card.owner.shuffle_lib()
    card.owner.lib.enter_zone(card, pos=0)

def Scheming_Symmetry_effect(source_card):
    for player in [source_card.controller,source_card.controller.opponent]:
        player.search_library(
            elig_condition= lambda card: True,
            select_effect= Scheming_Symmetry_select_effect,
            shuffle=False
        )

Scheming_Symmetry= Sorcery(
    name='Scheming Symmetry',
    cost=Cost(mana={'B':1}),
    spell_effect=Scheming_Symmetry_effect,
    rarity='rare'
)

# Sorcerer of the Fang {1}{B}
# Creature — Human Wizard
# {5}{B}, {T}: Sorcerer of the Fang deals 2 damage to target opponent or planeswalker.
# 1/3
Sorcerer_of_the_Fang=Creature(
    name='Sorcerer of the Fang',
    cost=Cost(mana={'C':1,"B":1}),
    power=1,
    toughness=3,
    subtypes=['human','wizard'],
    activated_abils= [
        Activated_Ability(
            name='Sorcerer of the Fang ability',
            cost=Cost(mana={'C':5,'B':1}),
            targets=[Target(lambda source_abil, obj: 'planeswalker' in obj.types, c_players='opp')],
            abil_effect= lambda source_abil: source_abil.get_targets().take_damage(2,
                source=source_abil.source, combat=False)
        )
    ],
    rarity='common'
)

# Sorin, Imperious Bloodlord {2}{B}
# Legendary Planeswalker — Sorin
# +1: Target creature you control gains deathtouch and lifelink until end of turn.
#     If it’s a Vampire, put a +1/+1 counter on it.
# +1: You may sacrifice a Vampire. When you do, Sorin, Imperious Bloodlord deals
#     3 damage to any target and you gain 3 life.
# −3: You may put a Vampire creature card from your hand onto the battlefield.
# Loyalty: 4

# first +1 effect
def EOTr_Sorin_IB_plus1_dt_ll_effect(creature):
    creature.remove_keyword('deathtouch')
    creature.remove_keyword('lifelink')

def Sorin_IB_plus1_dt_ll_effect(source_abil):
    target=source_abil.get_targets()
    target.keyword_static_abils.append('deathtouch')
    target.keyword_static_abils.append('lifelink')
    target.EOT_reverse_effects.append(EOTr_Sorin_IB_plus1_dt_ll_effect)
    if 'vampire' in target.subtypes:
        deepcopy(plus1_plus1_counter).attach_to(target)

# 2nd +1 ability
def Sorin_IB_plus1_sac_drn_effect_rflx_trigger(source_abil):
    source_abil.get_targets().take_damage(3, source=source_abil.source)
    source_abil.controller.change_life(3)

def Sorin_IB_plus1_sac_drn_effect(source_abil):
    vamps = [i for i in source_abil.controller.field if 'vampire' in i.subtypes]
    if vamps != [] and source_abil.controller.input_bool(label='sac vampire for Sorin'):
        source_abil.controller.input_choose(vamps).sacrifice()
        # place reflexive trigger on stack
        effect=Effect_Instance(
            name='Sorin IB drain effect',
            source=source_abil.source,
            abil_effect=Sorin_IB_plus1_sac_drn_effect_rflx_trigger,
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types or
                'planeswalker' in obj.types, c_players='both')],
            controller=source_abil.controller,
            types=source_abil.types,
            choices=source_abil.choices,
            requirements=source_abil.requirements,
            colors=source_abil.source.colors,
            trigger_points=source_abil.trigger_points,
            trigger_condition=source_abil.trigger_condition)
        effect.assign_source(source_abil.source)
        effect.assign_controller(source_abil.controller)
        try:
            effect.set_targets()
            source_abil.controller.game.stack.enter_zone(effect)
        except GameActionError:
            if source_abil.controller.game.verbose>=2:
                print('Sorin IB +1 drain effect encountered no legal targets')

# -3 ability
def Sorin_IB_minus3_effect(source_abil):
    vamps = [i for i in source_abil.controller.hand if 'vampire' in i.subtypes]
    if vamps != [] and source_abil.controller.input_bool(label='Sorin puts vampire onto field'):
        selected = source_abil.controller.input_choose(vamps)
        selected.owner.hand.leave_zone(selected)
        selected.owner.field.enter_zone(selected)

Sorin_Imperious_Bloodlord = Planeswalker(
    name='Sorin, Imperious Bloodlord',
    subtypes=['sorin'],
    cost=Cost(mana={'C':2,'B':1}),
    loyalty=4,
    activated_abils=[
        Activated_Ability(
            name='Sorin, Imperious Bloodlord +1 deathtouch/lifelink ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(1)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False]
            ),
            targets=[Target(criteria=lambda source_abil, obj: 'creature' in obj.types,
                c_opponent=False)],
            abil_effect= Sorin_IB_plus1_dt_ll_effect,
            flash=False
        ),
        Activated_Ability(
            name='Sorin, Imperious Bloodlord +1 sacrifice/drain ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(1)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False]
            ),
            abil_effect= Sorin_IB_plus1_sac_drn_effect,
            flash=False
        ),
        Activated_Ability(
            name='Sorin, Imperious Bloodlord -3 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(-3)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False
                    and source_abil.source.loyalty>=3]
            ),
            abil_effect= Sorin_IB_minus3_effect,
            flash=False
        )
    ],
    rarity='mythic'
)

# Soul Salvage {2}{B}
# Sorcery
# Return up to two target creature cards from your graveyard to your hand.
def Soul_Salvage_effect(source_card):
    for card in source_card.get_targets():
        if card!=None:
            card.owner.yard.leave_zone(card)
            card.owner.hand.enter_zone(card)

Soul_Salvage=Sorcery(
    name='Soul Salvage',
    cost=Cost(mana={"C":2,'B':2}),
    targets=[
            Target(criteria= lambda source, obj: 'creature' in obj.types,
            c_opponent=False ,c_zones=['yard'], c_required=False),
            Target(criteria= lambda source, obj: 'creature' in obj.types,
            c_opponent=False ,c_zones=['yard'], c_required=False, c_different=True)
        ],
    spell_effect= Soul_Salvage_effect,
    rarity='common'
)

# Thought Distortion {4}{B}{B}
# Sorcery
# This spell can’t be countered.
# Target opponent reveals their hand. Exile all noncreature, nonland cards from
# that player’s hand and graveyard.

def Thought_Distortion_effect(source_card):
    opp=source_card.get_targets()
    opp.reveal_cards(opp.hand, zone='hand')
    noncreats_yard = [i for i in opp.yard if 'land' not in i.types and 'creature'
        not in i.types]
    noncreats_hand = [i for i in opp.hand if 'land' not in i.types and 'creature'
        not in i.types]
    for i in noncreats_yard:
        i.exile()
    for i in noncreats_hand:
        i.exile()

Thought_Distortion = Sorcery(
    name='Thought Distortion',
    cost=Cost(mana={'C':4,'B':2}),
    targets=[Target(criteria=lambda source_card, obj: True, c_zones=[],c_players='opp')],
    spell_effect=Thought_Distortion_effect,
    rarity='uncommon'
)

# Undead Servant {3}{B}
# Creature — Zombie
# When Undead Servant enters the battlefield, create a 2/2 black Zombie creature
# token for each card named Undead Servant in your graveyard.
# 3/2

def Undead_Servant_ETB_effect(source_abil):
    servants = len([i for i in source_abil.controller.yard if i.name=='Undead Servant'])
    for _ in range(servants):
        source_abil.controller.create_token(
            Creature_Token(
                name='Zombie 2/2',
                colors=['B'],
                subtypes=['zombie'],
                power=2,
                toughness=2
            )
        )

Undead_Servant = Creature(
    name='Undead Servant',
    cost=Cost(mana={'C':3,'B':1}),
    subtypes=['zombie'],
    power=3,
    toughness=2,
    triggered_abils=[Triggered_Ability(
            name='Undead Servant ETB ability',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Undead_Servant_ETB_effect
        )
    ],
    rarity='common'
)

# Unholy Indenture {2}{B}
# Enchantment — Aura
# Enchant creature
# When enchanted creature dies, return that card to the battlefield under your
# control with a +1/+1 counter on it.

def Unholy_Indenture_effect(source_abil):
    attached_to=source_abil.last_known_info
    if attached_to!=None and isinstance(attached_to.zone, Graveyard):
        attached_to.owner.yard.leave_zone(attached_to)
        attached_to.source_abil.controller.field.enter_zone(attached_to)
        deepcopy(plus1_plus1_counter).attach_to(attached_to)

Unholy_Indenture= Aura(
    name='Unholy Indenture',
    cost=Cost(mana={'C':2, 'B':1}),
    aura_static_effect=Attached_Effect(
        name='Unholy Indenture aura effect',
        effect_func= lambda attached_to: True,
        reverse_effect_func= lambda attached_to: True
    ),
    triggered_abils=[
        Triggered_Ability(
            name='Unholy Indenture dies effect',
            trigger_points=['dies'],
            lki_func= lambda source_abil, effect_kwargs: source_abil.source.attached_to,
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.last_known_info,
            abil_effect= Unholy_Indenture_effect
        )
    ],
    rarity='common'
)

# Vampire of the Dire Moon {B}
# Creature — Vampire
# Deathtouch (Any amount of damage this deals to a creature is enough to destroy it.)
# Lifelink (Damage dealt by this creature also causes you to gain that much life.)
# 1/1

Vampire_of_the_Dire_Moon=Creature(
    name='Vampire of the Dire Moon',
    cost=Cost(mana={"B":1}),
    power=1,
    toughness=1,
    subtypes=['vampire'],
    keyword_static_abils=['deathtouch','lifelink'],
    rarity='common'
)

# Vengeful Warchief {4}{B}
# Creature — Orc Warrior
# Whenever you lose life for the first time each turn, put a +1/+1 counter on Vengeful Warchief.
# 4/4

Vengeful_Warchief=Creature(
    name='Vengeful Warchief',
    cost=Cost(mana={'C':4,"B":1}),
    power=4,
    toughness=4,
    subtypes=['orc','warrior'],
    triggered_abils=[Triggered_Ability(
            name='Vengeful Warchief triggered ability',
            trigger_points=['lifeloss'],
            trigger_condition= lambda source_abil, player, num, **kwargs: player.life_lost_this_turn==0
                and player==source_abil.controller,
            abil_effect=lambda source_abil: deepcopy(plus1_plus1_counter)
                .attach_to(source_abil.source)
        )
    ],
    rarity='uncommon'
)

# Vilis, Broker of Blood {5}{B}{B}{B}
# Legendary Creature — Demon
# Flying
# {B}, Pay 2 life: Target creature gets -1/-1 until end of turn.
# Whenever you lose life, draw that many cards. (Damage causes loss of life.)
# 8/8
def EOTr_Vilis_Broker_of_Blood_activated_effect(target):
    target.change_power(1)
    target.change_toughness(1)

def Vilis_Broker_of_Blood_activated_effect(source_abil):
    target=source_abil.get_targets()
    target.change_power(-1)
    target.change_toughness(-1)
    target.EOT_reverse_effects.append(EOTr_Vilis_Broker_of_Blood_activated_effect)

Vilis_Broker_of_Blood=Creature(
    name='Vilis, Broker of Blood',
    cost=Cost(mana={'C':5,'B':3}),
    power=8,
    toughness=8,
    subtypes=['demon'],
    keyword_static_abils=['flying'],
    activated_abils=[
        Activated_Ability(
            name='Vilis, Broker of Blood activated abil',
            cost=Cost(
                mana={'B':1},
                non_mana= [lambda source_abil: source_abil.controller.pay_life(2)]
            ),
            targets=[Target(lambda source_abil, obj: 'creature' in obj.types)],
            abil_effect=Vilis_Broker_of_Blood_activated_effect
        )
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Vilis, Broker of Blood triggered ability',
            trigger_points=['lifeloss'],
            trigger_condition= lambda source_abil, player, num, **kwargs: player==source_abil.controller,
            abil_effect=lambda source_abil: source_abil.controller.draw_card(
                source_abil.controller.life_chg_num*-1)
        )
    ],
    rarity='rare'
)

# Yarok's Fenlurker {B}{B}
# Creature — Horror
# When Yarok’s Fenlurker enters the battlefield, each opponent exiles a card from their hand.
# {2}{B}: Yarok’s Fenlurker gets +1/+1 until end of turn.
# 1/1
def Yaroks_Fenlurker_ETB_effect(source_abil):
    if len(source_abil.controller.opponent.hand)>=1:
        selected= source_abil.controller.opponent.input_choose(source_abil.controller.opponent.hand, label='Exiling from hand')
        selected.exile()

def EOTr_Yaroks_Fenlurker_activated_effect(source):
    source.change_power(-1)
    source.change_toughness(-1)

def Yaroks_Fenlurker_activated_effect(source_abil):
    source_abil.source.change_power(1)
    source_abil.source.change_toughness(1)
    source_abil.source.EOT_reverse_effects.append(EOTr_Yaroks_Fenlurker_activated_effect)

Yaroks_Fenlurker=Creature(
    name="Yarok's Fenlurker",
    cost=Cost(mana={'B':2}),
    subtypes=['horror'],
    power=1,
    toughness=1,
    triggered_abils=[
        Triggered_Ability(
            name="Yarok's Fenlurker ETB ability",
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Yaroks_Fenlurker_ETB_effect
        )
    ],
    activated_abils=[
        Activated_Ability(
            name="Yarok's Fenlurker activated ability",
            cost=Cost(mana={'C':2,'B':1}),
            abil_effect=Yaroks_Fenlurker_activated_effect
        )
    ],
    rarity='uncommon'
)

# Act of Treason {2}{R}
# Sorcery
# Gain control of target creature until end of turn. Untap that creature.
# It gains haste until end of turn. (It can attack and {T} this turn.)

def EOTr_Act_of_Treason_effect(target):
    target.remove_keyword('haste')
    # only revert controller if card is still on the battlefield
    if target.controller!=target.orig_controller and isinstance(target.zone, Battlefield) \
        and target in target.zone:
        target.assign_controller(target.orig_controller, gain_control=True)

def Act_of_Treason_effect(source_card):
    target=source_card.get_targets()
    target.orig_controller=target.controller
    if target.controller!=source_card.controller:
        target.assign_controller(source_card.controller, gain_control=True)
    target.untap()
    target.add_keyword('haste')
    target.EOT_reverse_effects.append(EOTr_Act_of_Treason_effect)

Act_of_Treason=Sorcery(
    name='Act of Treason',
    cost=Cost(mana={'C':2,'R':1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
    spell_effect=Act_of_Treason_effect,
    rarity='common'
)


# Cavalier of Flame {2}{R}{R}{R}
# Creature — Elemental Knight
# {1}{R}: Creatures you control get +1/+0 and gain haste until end of turn.
# When Cavalier of Flame enters the battlefield, discard any number of cards,
# then draw that many cards.
# When Cavalier of Flame dies, it deals X damage to each opponent and each
# planeswalker they control, where X is the number of land cards in your graveyard.
# 6/5

def EOTr_Cavalier_of_Flame_activated_effect(creature):
    creature.change_power(-1)
    creature.remove_keyword('haste')

def Cavalier_of_Flame_activated_effect(source_abil):
    for creature in [i for i in source_abil.controller.field if 'creature' in i.types]:
        creature.change_power(1)
        creature.add_keyword('haste')
        creature.EOT_reverse_effects.append(EOTr_Cavalier_of_Flame_activated_effect)

def Cavalier_of_Flame_ETB_effect(source_abil):
    selected= source_abil.controller.input_choose(source_abil.controller.hand,n='any',
        squeeze=False)
    for i in selected:
        i.discard_from_hand()
    source_abil.controller.draw_card(len(selected))

def Cavalier_of_Flame_dies_effect(source_abil):
    pwalkers = [i for i in source_abil.controller.opponent.field if 'planeswalker' in i.types]
    dmg = len([i for i in source_abil.controller.yard if 'land' in i.types])
    for i in pwalkers:
        i.take_damage(dmg, source=source_abil.source)
    source_abil.controller.opponent.take_damage(dmg, source=source_abil.source)

Cavalier_of_Flame = Creature(
    name='Cavalier of Flame',
    cost=Cost(mana={'C':2,'R':3}),
    subtypes=['elemental','knight'],
    power=6,
    toughness=5,
    activated_abils=[
        Activated_Ability(
            name='Cavalier of Flame activated abil',
            cost=Cost(mana={'C':1,'R':1}),
            abil_effect= Cavalier_of_Flame_activated_effect
        )
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Cavalier of Flame ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Cavalier_of_Flame_ETB_effect
        ),
        Triggered_Ability(
            name='Cavalier of Flame Dies',
            trigger_points=['dies'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Cavalier_of_Flame_dies_effect
        )
    ],
    rarity='mythic'
)

# Chandra, Acolyte of Flame {1}{R}{R}
# Legendary Planeswalker — Chandra
# 0: Put a loyalty counter on each red planeswalker you control.
# 0: Create two 1/1 red Elemental creature tokens. They gain haste. Sacrifice them
# at the beginning of the next end step.
# −2: You may cast target instant or sorcery card with converted mana cost 3 or
# less from your graveyard. If that spell would be put into your graveyard this
# turn, exile it instead.
# Loyalty: 4

def Chandra_AoF_0_add_loyalty_effect(source_abil):
    red_walkers=[i for i in source_abil.controller.field if 'planeswalker' in i.types
        and 'R' in i.colors]
    for i in red_walkers:
        i.change_loyalty(1)

def Chandra_AoF_0_create_token_effect(source_abil):
    for _ in range(2):
        source_abil.controller.create_token(
            Creature_Token(
                name='Elemental 1/1',
                colors=['R'],
                subtypes=['elemental'],
                power=1,
                toughness=1,
                keyword_static_abils=['haste'],
                triggered_abils=[
                    Triggered_Ability(
                        name='Elemental sacrifice trigger',
                        trigger_points=['end phase'],
                        trigger_condition = lambda source_abil, **kwargs: True,
                        abil_effect= lambda source_abil: source_abil.source.sacrifice()
                    )
                ]
            )
        )
def Chandra_AoF_minus2_effect(source_abil):
    target=source_abil.get_targets()
    if source_abil.controller.input_bool(label='Chandra AoF yard cast'):
        try:
            target.play_card(from_zone='yard',exile_on_resolve=True,pay_mana_cost=False)
        except:
            if source_abil.controller.game.verbose>=2:
                print('Not legal to cast Chandra AoF target:', target)

Chandra_Acolyte_of_Flame = Planeswalker(
    name='Chandra, Acolyte of Flame',
    subtypes=['chandra'],
    loyalty=4,
    activated_abils=[
        Activated_Ability(
            name='Chandra AoF +0 loyalty ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(0)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False]
            ),
            abil_effect=Chandra_AoF_0_add_loyalty_effect,
            flash=False
        ),
        Activated_Ability(
            name='Chandra AoF +0 create token ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(0)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False]
            ),
            abil_effect=Chandra_AoF_0_create_token_effect,
            flash=False
        ),
        Activated_Ability(
            name='Chandra AoF -2 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(-2)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False
                    and source_abil.source.loyalty>=2]
            ),
            targets=[Target(criteria= lambda source_abil, obj: ('instant' in obj.types
                or 'sorcery' in obj.types) and obj.cmc<=3, c_zones=['yard'],
                c_opponent=False)],
            abil_effect=Chandra_AoF_minus2_effect,
            flash=False
        )
    ],
    rarity='rare'
)

# Chandra, Awakened Inferno {4}{R}{R}
# Legendary Planeswalker — Chandra
# This spell can’t be countered.
# +2: Each opponent gets an emblem with “At the beginning of your upkeep, this
# emblem deals 1 damage to you.”
# −3: Chandra, Awakened Inferno deals 3 damage to each non-Elemental creature.
# −X: Chandra, Awakened Inferno deals X damage to target creature or planeswalker.
# If a permanent dealt damage this way would die this turn, exile it instead.
# Loyalty: 6

def Chandra_AI_plus2_effect(source_abil):
    emblem = Emblem(
        name= 'Chandra, Awakened Inferno emblem',
        triggered_abils=[
            Triggered_Ability(
                name='Chandra, Awakened Inferno emblem trigger',
                trigger_points=['upkeep'],
                trigger_condition= lambda source_abil, act_plyr, **kwargs:
                    act_plyr==source_abil.source.controller,
                abil_effect= lambda source_abil: source_abil.controller.take_damage(1,
                    source=source_abil.source)
            )
        ]
    )
    emblem.give_player(source_abil.controller.opponent)

def Chandra_AI_minus3_effect(source_abil):
    for i in source_abil.controller.field + source_abil.controller.opponent.field:
        if 'elemental' not in i.subtypes and 'creature' in i.types:
            i.take_damage(3, source=source_abil.source)

def EOTr_Chandra_AI_minusX_effect(target):
    target.remove_keyword('exile_on_death')

def Chandra_AI_minusX_effect(source_abil):
    target=source_abil.get_targets()
    x=source_abil.source.cost[0].x_value
    target.take_damage(x, source=source_abil.source)
    target.add_keyword('exile_on_death')
    target.EOT_reverse_effects.append(EOTr_Chandra_AI_minusX_effect)

Chandra_Awakened_Inferno = Planeswalker(
    name='Chandra, Awakened Inferno',
    cost=Cost(mana={'C':4, 'R':2}),
    subtypes=['chandra'],
    loyalty=6,
    keyword_static_abils=['uncounterable'],
    activated_abils=[
        Activated_Ability(
            name='Chandra AI +2 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(2)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False]
            ),
            abil_effect=Chandra_AI_plus2_effect,
            flash=False
        ),
        Activated_Ability(
            name='Chandra AI -3 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(-3)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False
                    and source_abil.source.loyalty>=3]
            ),
            abil_effect=Chandra_AI_minus3_effect,
            flash=False
        ),
        Activated_Ability(
            name='Chandra AI -X ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(
                    source_abil.cost[0].x_value*-1)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False],
                nonmana_x_value=True,
                xrange_func=lambda source_abil: [i for i in range(0,
                    source_abil.source.loyalty+1)]
                ),
            targets=[Target(criteria= lambda source_abil, obj: ('planeswalker' in obj.types
                or 'creature' in obj.types))],
            abil_effect=Chandra_AI_minusX_effect,
            flash=False
        )
    ],
    rarity='mythic'
)

# Chandra, Novice Pyromancer {3}{R}
# Legendary Planeswalker — Chandra
# +1: Elementals you control get +2/+0 until end of turn.
# −1: Add {R}{R}.
# −2: Chandra, Novice Pyromancer deals 2 damage to any target.
# Loyalty: 5
def EOTr_Chandra_NP_plus1_effect(target):
    target.change_power(-2)

def Chandra_NP_plus1_effect(source_abil):
    for elemental in [i for i in source_abil.controller.field if 'elemental'
        in i.subtypes]:
        elemental.change_power(2)
        elemental.EOT_reverse_effects.append(EOTr_Chandra_NP_plus1_effect)

def Chandra_NP_minus1_effect(source_abil):
    source_abil.controller.add_mana(color='R', num=2)

def Chandra_NP_minus2_effect(source_abil):
    target=source_abil.get_targets()
    target.take_damage(2, source=source_abil.source)

Chandra_Novice_Pyromancer= Planeswalker(
    name='Chandra, Novice Pyromancer',
    cost= Cost(mana={'C':3,'R':1}),
    subtypes=['chandra'],
    loyalty=5,
    activated_abils=[
        Activated_Ability(
            name='Chandra, Novice Pyromancer +1 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(1)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False]
            ),
            abil_effect=Chandra_NP_plus1_effect,
            flash=False
        ),
        Activated_Ability(
            name='Chandra, Novice Pyromancer -1 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(-1)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False]
            ),
            abil_effect=Chandra_NP_minus1_effect,
            flash=False
        ),
        Activated_Ability(
            name='Chandra, Novice Pyromancer -2 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(-2)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False
                    and source_abil.source.loyalty>=2]
            ),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types or
                'planeswalker' in obj.types, c_players='both')],
            abil_effect=Chandra_NP_minus2_effect,
            flash=False
        ),
    ],
    rarity='uncommon'
)

# Chandra's Embercat {1}{R}
# Creature — Elemental Cat
# {T}: Add {R}. Spend this mana only to cast an Elemental spell or a Chandra
# planeswalker spell.
# 2/2

Chandras_Embercat=Creature(
    name="Chandra's Embercat",
    cost=Cost(mana={'C':1,'R':1}),
    subtypes=['elemental','cat'],
    power=2,
    toughness=2,
    mana_source=True,
    activated_abils= [
        Activated_Ability(
            name="Chandra's Embercat mana ability",
            cost= Cost(
                    non_mana=[lambda source_abil: source_abil.source.tap()],
                    non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                    and (source_abil.source.summoning_sick==False or 'creature' not in
                    source_abil.source.types)]
                ),
            potential_mana=Potential_Mana({'R':1}, use_condition= lambda obj:
                isinstance(obj, Card) and ('elemental' in obj.subtypes or 'chandra' in obj.subtypes)),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('R', 1),
            mana_abil=True,
        )
    ],
    rarity='common'
)

# Chandra's Outrage {2}{R}{R}
# Instant
# Chandra’s Outrage deals 4 damage to target creature and 2 damage to that
# creature’s controller.

def Chandras_Outrage_effect(source_card):
    target=source_card.get_targets()
    target.take_damage(4, source=source_card)
    target.controller.take_damage(2, source=source_card)

Chandras_Outrage = Instant(
    name="Chandra's Outrage",
    cost=Cost(mana={'C':2,'R':2}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
    spell_effect=Chandras_Outrage_effect,
    rarity='common'
)

# Chandra's Regulator {1}{R}
# Legendary Artifact
# Whenever you activate a loyalty ability of a Chandra planeswalker, you may pay {1}.
# If you do, copy that ability. You may choose new targets for the copy.
# {1}, {T}, Discard a Mountain card or a red card: Draw a card.

def Chandras_Regulator_triggered_effect(source_abil):
    source_abil.last_known_info.make_copy()

def Chandras_Regulator_activated_cost(source_abil):
    source_abil.source.tap()
    elig_cards=[i for i in source_abil.controller.hand if 'Mountain' in i.types or
        'R' in i.colors]
    selected=source_abil.controller.input_choose(elig_cards,
        label="Chandra's Regulator discard")
    selected.discard_from_hand()

def Chandras_Regulator_activated_cost_check(source_abil):
    result = False
    if source_abil.source.tapped==False \
        and (source_abil.source.summoning_sick==False or 'creature' not in
        source_abil.source.types):
        elig_cards=[i for i in source_abil.controller.hand if 'Mountain' in i.types or
            'R' in i.colors]
        if len(elig_cards)>0:
            result = True
    return result

Chandras_Regulator= Artifact(
    name="Chandra's Regulator",
    cost=Cost(mana={'C':1,'R':1}),
    types=['legendary','artifact'],
    triggered_abils=[
        Triggered_Ability(
            name="Chandra's Regulator triggered abil",
            cost=Cost(mana={'C':1}),
            trigger_points=['abil activated'],
            trigger_condition=lambda source_abil, activated_abil, **kwargs:
                activated_abil.controller==source_abil.controller and
                'chandra' in activated_abil.source.subtypes,
            lki_func= lambda source_abil, effect_kwargs: effect_kwargs['activated_abil'],
            abil_effect = Chandras_Regulator_triggered_effect
        )
    ],
    activated_abils=[
        Activated_Ability(
            name="Chandra's Regulator activated abil",
            cost=Cost(
                mana={'C':1},
                non_mana=[Chandras_Regulator_activated_cost],
                non_mana_check=[Chandras_Regulator_activated_cost_check]
            ),
            abil_effect=lambda source_abil: source_abil.controller.draw_card()
        )
    ],
    rarity='rare'
)

# Chandra's Spitfire {2}{R}
# Creature — Elemental
# Flying
# Whenever an opponent is dealt noncombat damage, Chandra’s Spitfire gets +3/+0 until end of turn.
# 1/3

def EOTr_Chandras_Spitfire_effect(creature):
    creature.change_power(-3)

def Chandras_Spitfire_effect(source_abil):
    source_abil.source.change_power(3)
    source_abil.source.EOT_reverse_effects.append(EOTr_Chandras_Spitfire_effect)

Chandras_Spitfire= Creature(
    name="Chandra's Spitfire",
    cost=Cost(mana={"C":2, "R":1}),
    power=1,
    toughness=3,
    subtypes=['elemental'],
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name="Chandra's Spitfire triggered abil",
            trigger_points=['lifeloss'],
            trigger_condition= lambda source_abil, player, dealing_damage, combat, **kwargs:
                player==source_abil.controller.opponent and dealing_damage and combat==False,
            abil_effect= Chandras_Spitfire_effect
        )
    ],
    rarity='uncommon'
)

# Daggersail Aeronaut {3}{R}
# Creature — Goblin
# As long as it’s your turn, Daggersail Aeronaut has flying.
# 3/2
def Daggersail_Aeronaut_effect(source_abil):
    source_abil.source.add_keyword('flying')

def r_Daggersail_Aeronaut_effect(source_abil):
    source_abil.source.add_keyword('loses_flying')

Daggersail_Aeronaut= Creature(
    name="Daggersail Aeronaut",
    cost=Cost(mana={"C":3, "R":1}),
    power=3,
    toughness=2,
    subtypes=['goblin'],
    keyword_static_abils=[],
    nonkeyword_static_abils=[
        Local_Static_Effect(
            name="Daggersail Aeronaut flying effect",
            effect_func= Daggersail_Aeronaut_effect,
            reverse_effect_func = r_Daggersail_Aeronaut_effect,
            effect_condition= lambda source_abil:
                source_abil.controller.game.act_plyr == source_abil.controller
        )
    ],
    rarity='common'
)


# Destructive Digger {2}{R}
# Creature — Goblin
# {3}, {T}, Sacrifice an artifact or land: Draw a card.
# 3/2
Destructive_Digger= Creature(
    name="Destructive Digger",
    cost=Cost(mana={"C":2, "R":1}),
    power=3,
    toughness=2,
    subtypes=['goblin'],
    activated_abils=[
        Activated_Ability(
            name='Destructive Digger abil',
            cost=Cost(
                mana={'C':3},
                non_mana=[
                    lambda source_abil: source_abil.controller.sacrifice_permanent(
                        types=['creature','artifact']),
                    lambda source_abil: source_abil.source.tap(),
                ],
                non_mana_check=[
                    lambda source_abil: source_abil.source.tapped==False and
                    (source_abil.source.summoning_sick==False or 'creature' not in
                    source_abil.source.types),
                    lambda source_abil: len([i for i in source_abil.controller.field
                        if 'creature' in i.types or 'artifact' in i.types])>0,
                ],
            ),
            abil_effect= lambda source_abil: source_abil.controller.draw_card()
        )
    ],
    rarity='common'
)

# Dragon Mage {5}{R}{R}
# Creature — Dragon Wizard
# Flying
# Whenever Dragon Mage deals combat damage to a player, each player discards their
# hand, then draws seven cards.
# 5/5
def Dragon_Mage_effect(source_abil):
    for p in [source_abil.controller,source_abil.controller.opponent]:
        p.discard_hand()
        p.draw_card(7)

Dragon_Mage = Creature(
    name='Dragon Mage',
    cost=Cost(mana={'C':5, 'R':2}),
    power=5,
    toughness=5,
    subtypes=['dragon'],
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Dragon Mage triggered abil',
            trigger_points=['combat damage dealt'],
            trigger_condition = lambda source_abil, source, receiver, num, **kwargs:
                source == source_abil.source and receiver == source_abil.controller.opponent,
            abil_effect = Dragon_Mage_effect
        )
    ],
    rarity='uncommon'
)

# Drakuseth, Maw of Flames {4}{R}{R}{R}
# Legendary Creature — Dragon
# Flying
# Whenever Drakuseth, Maw of Flames attacks, it deals 4 damage to any target and
# 3 damage to each of up to two other targets.
# 7/7
def Drakuseth_Maw_of_Flames_effect(source_abil):
    targets = source_abil.get_targets()
    if len(targets)>0 and targets[0]!=None:
        targets[0].take_damage(4, source=source_abil.source, combat=False)
    if len(targets)>1 and targets[1]!=None:
        targets[1].take_damage(3, source=source_abil.source, combat=False)
    if len(targets)>2 and targets[2]!=None:
        targets[2].take_damage(3, source=source_abil.source, combat=False)

Drakuseth_Maw_of_Flames = Creature(
    name='Drakuseth, Maw of Flames',
    cost=Cost(mana={'C':4, 'R':3}),
    power=7,
    toughness=7,
    subtypes=['dragon'],
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Drakuseth, Maw of Flames triggered abil',
            trigger_points=['on attack'],
            trigger_condition=lambda source_abil, obj, **kwargs:
                source_abil.source==obj,
            targets=[
                Target(criteria= lambda source, obj: 'creature' in obj.types or
                    'planeswalker' in obj.types, c_players='both', c_different=True),
                Target(criteria= lambda source, obj: 'creature' in obj.types or
                    'planeswalker' in obj.types, c_players='both', c_different=True,
                    c_required=False),
                Target(criteria= lambda source, obj: 'creature' in obj.types or
                    'planeswalker' in obj.types, c_players='both', c_different=True,
                    c_required=False),
            ],
            abil_effect = Drakuseth_Maw_of_Flames_effect
        )
    ],
    rarity='rare'
)

# Ember Hauler {R}{R}
# Creature — Goblin
# {1}, Sacrifice Ember Hauler: It deals 2 damage to any target.
# 2/2

Ember_Hauler = Creature(
    name= 'Ember Hauler',
    cost = Cost(mana={'R':2}),
    power=2,
    toughness=2,
    subtypes=['goblin'],
    activated_abils=[
        Activated_Ability(
            name='Ember Hauler abil',
            cost=Cost(
                mana={'C':1},
                non_mana=[lambda source_abil: source_abil.source.sacrifice()],
            ),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types or
                'planeswalker' in obj.types, c_players='both')],
            abil_effect = lambda source_abil:
                source_abil.get_targets().take_damage(2,source=source_abil.source,
                    combat=False)
        )
    ],
    rarity='uncommon'
)


# Fire Elemental
# 3RR
# Creature - Elemental
# 5/4
Fire_Elemental= Creature(
    name='Fire Elemental',
    cost=Cost(mana={"C":3, "R":2}),
    power=5,
    toughness=4,
    subtypes=['elemental'],
    rarity='common'
)

# Flame Sweep {2}{R}
# Instant
# Flame Sweep deals 2 damage to each creature except for creatures you control with flying.
def Flame_Sweep_effect(source_card):
    for i in source_card.controller.opponent.field:
        if 'creature' in i.types:
            i.take_damage(2,source=source_card,combat=False)
    for i in source_card.controller.field:
        if i.check_keyword('flying')==False and 'creature' in i.types:
            i.take_damage(2,source=source_card,combat=False)

Flame_Sweep=Instant(
    name='Flame Sweep',
    cost=Cost(mana={'C':2,'R':1}),
    spell_effect=Flame_Sweep_effect,
    rarity='uncommon'
)

# Fry {1}{R}
# Instant
# This spell can’t be countered.
# Fry deals 5 damage to target creature or planeswalker that’s white or blue.
Fry = Instant(
    name='Fry',
    cost=Cost(mana={'C':1,'R':1}),
    targets=[Target(criteria= lambda source, obj: ('creature' in obj.types or
        'planeswalker' in obj.types) and ('W' in obj.colors or 'U' in obj.colors))],
    keyword_static_abils=['uncounterable'],
    spell_effect = lambda source_card: source_card.get_targets().take_damage(5,
        source=source_card,combat=False),
    rarity='uncommon'
)

# Glint-Horn Buccaneer {1}{R}{R}
# Creature — Minotaur Pirate
# Haste
# Whenever you discard a card, Glint-Horn Buccaneer deals 1 damage to each opponent.
# {1}{R}, Discard a card: Draw a card. Activate this ability only if Glint-Horn
# Buccaneer is attacking.
# 2/4

Glint_Horn_Buccaneer = Creature(
    name='Glint-Horn Buccaneer',
    cost=Cost(mana={'C':1,'R':2}),
    power=2,
    toughness=4,
    subtypes=['minotaur','pirate'],
    keyword_static_abils=['haste'],
    triggered_abils=[
        Triggered_Ability(
            name='Glint-Horn Buccaneer triggered abil',
            trigger_points=['discard'],
            trigger_condition= lambda source_abil, discarded_obj, **kwargs:
                source_abil.controller == discarded_obj.owner,
            abil_effect = lambda source_abil: source_abil.controller.opponent.take_damage(1, source=
                source_abil.source, combat=False)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Glint-Horn Buccaneer activated abil',
            cost=Cost(
                mana={'C':1,'R':1},
                non_mana=[lambda source_abil: source_abil.controller.discard_cards(1)],
                non_mana_check=[lambda source_abil: source_abil.controller.has_cards_in_hand()]
            ),
            requirements=[Requirement(lambda source_abil: source_abil.source.attacking)],
            abil_effect = lambda source_abil: source_abil.controller.draw_card()
        )
    ],
    rarity='rare'
)

# Goblin Bird-Grabber {1}{R}
# Creature — Goblin
# {R}: Goblin Bird-Grabber gains flying until end of turn. Activate this ability
# only if you control a creature with flying.
# 2/1
def EOTr_Goblin_Bird_Grabber_effect(creature):
    creature.remove_keyword('flying')
def Goblin_Bird_Grabber_effect(source_abil):
    source_abil.source.add_keyword('flying')
    source_abil.source.EOT_reverse_effects.append(EOTr_Goblin_Bird_Grabber_effect)
Goblin_Bird_Grabber = Creature(
    name = 'Goblin Bird-Grabber',
    cost=Cost(mana={'C':1,'R':1}),
    power=2,
    toughness=1,
    subtypes=['goblin'],
    rarity='common',
    activated_abils=[
        Activated_Ability(
            name='Goblin Bird-Grabber activated abil',
            cost=Cost(mana={'R':1}),
            requirements=[Requirement(lambda source:
            any([i.check_keyword('flying') for i in source.controller.field if
                'creature' in i.types]))],
            abil_effect= Goblin_Bird_Grabber_effect
        )
    ]
)

# Goblin Ringleader {3}{R}
# Creature — Goblin
# Haste (This creature can attack and {T} as soon as it comes under your control.)
# When Goblin Ringleader enters the battlefield, reveal the top four cards of your
# library. Put all Goblin cards revealed this way into your hand and the rest on
# the bottom of your library in any order.
# 2/2
def Goblin_Ringleader_effect(source_abil):
    top_cards = source_abil.controller.lib[0:4]
    selected = [i for i in top_cards if 'goblin' in i.subtypes]
    non_selected = [i for i in top_cards if i not in selected]
    source_abil.controller.reveal_cards(selected, zone='hand')
    for i in selected:
        source_abil.controller.lib.leave_zone(i)
        source_abil.controller.hand.enter_zone(i)
    # order of non_selected is [card1,card2,...,card_n] <- bottom of library
    non_selected=source_abil.controller.input_order(non_selected, label='non-selected order')
    for i in non_selected:
        source_abil.controller.lib.remove(i)
        source_abil.controller.lib.append(i)

Goblin_Ringleader = Creature(
    name = 'Goblin Ringleader',
    cost=Cost(mana={'C':3,'R':1}),
    power=2,
    toughness=2,
    subtypes=['goblin'],
    rarity='uncommon',
    keyword_static_abils=['haste'],
    triggered_abils=[
        Triggered_Ability(
            name='Goblin Ringleader triggered abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Goblin_Ringleader_effect
        )
    ]
)

# Goblin Smuggler {2}{R}
# Creature — Goblin Rogue
# Haste (This creature can attack and {T} as soon as it comes under your control.)
# {T}: Another target creature with power 2 or less can’t be blocked this turn.
# 2/2
def EOTr_Goblin_Smuggler_effect(creature):
    creature.remove_keyword('unblockable')

def Goblin_Smuggler_effect(source_abil):
    source_abil.get_targets().add_keyword('unblockable')
    source_abil.get_targets().EOT_reverse_effects.append(EOTr_Goblin_Smuggler_effect)

Goblin_Smuggler = Creature(
    name = 'Goblin Smuggler',
    cost=Cost(mana={'C':2,'R':1}),
    power=2,
    toughness=2,
    subtypes=['goblin'],
    rarity='common',
    keyword_static_abils=['haste'],
    activated_abils=[
        Activated_Ability(
            name='Goblin Smuggler',
            cost= Cost(
                non_mana= [lambda source_abil: source_abil.source.tap()],
                non_mana_check = [lambda source_abil: source_abil.source.tapped==False and
                    (source_abil.source.summoning_sick==False or 'creature' not in
                    source_abil.source.types)]
            ),
            targets= [Target(criteria=lambda source, obj: 'creature' in obj.types
                and obj.power<=2, c_self_target=False)],
            abil_effect=Goblin_Smuggler_effect
        )
    ]
)

# Infuriate {R}
# Instant
# Target creature gets +3/+2 until end of turn.
def EOTr_Infuriate_effect(creature):
    creature.change_power(-3)
    creature.change_toughness(-2)

def Infuriate_effect(source_card):
    target=source_card.get_targets()
    target.change_power(3)
    target.change_toughness(2)
    target.EOT_reverse_effects.append(EOTr_Infuriate_effect)

Infuriate=Instant(
    name='Infuriate',
    cost=Cost(mana={'R':1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
    spell_effect= Infuriate_effect,
    rarity='common'
)

# Keldon Raider {2}{R}{R}
# Creature — Human Warrior
# When Keldon Raider enters the battlefield, you may discard a card. If you do, draw a card.
# 4/3
def Keldon_Raider_effect(source_abil):
    if source_abil.controller.input_bool(label='Keldon Raider effect') and \
        source_abil.controller.has_cards_in_hand():
        source_abil.controller.discard_cards(1)
        source_abil.controller.draw_card()

Keldon_Raider = Creature(
    name='Keldon Raider',
    cost=Cost(mana={'R':2,'C':2}),
    subtypes=['human','warrior'],
    power=4,
    toughness=3,
    rarity='common',
    triggered_abils=[
        Triggered_Ability(
            name='Keldon Marauder triggered abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Keldon_Raider_effect
        )
    ]
)
# Lavakin Brawler {3}{R}
# Creature — Elemental Warrior
# Whenever Lavakin Brawler attacks, it gets +1/+0 until end of turn for each
# Elemental you control.
# 2/4

def Lavakin_Brawler_effect(source_abil):
    elems = len([i for i in source_abil.controller.field if 'elemental' in i.subtypes])
    source_abil.source.change_power(elems)
    source_abil.source.EOT_power_pump+=elems

Lavakin_Brawler = Creature(
    name='Lavakin Brawler',
    cost=Cost(mana={'R':1,'C':3}),
    subtypes=['elemental','warrior'],
    power=2,
    toughness=4,
    rarity='common',
    triggered_abils=[
        Triggered_Ability(
            name='Lavakin Brawler triggered abil',
            trigger_points=['on attack'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Lavakin_Brawler_effect
        )
    ]
)

# Leyline of Combustion {2}{R}{R}
# Enchantment
# If Leyline of Combustion is in your opening hand, you may begin the game with it
# on the battlefield.
# Whenever you and/or at least one permanent you control becomes the target of a
# spell or ability an opponent controls, Leyline of Combustion deals 2 damage to
# that player.

def Leyline_of_Combustion_begin_game(source_abil):
    if source_abil.source.owner.input_bool(label='Leyline begin of game abil'):
        source_abil.source.owner.hand.leave_zone(source_abil.source)
        source_abil.source.owner.field.enter_zone(source_abil.source)
        if source_abil.source.controller.game.verbose>=2:
            print(source_abil.source.controller, 'puts Leyline of Combustion into play at beginning of game')
    else:
        if source_abil.source.controller.game.verbose>=2:
            print(source_abil.source.controller, 'elects not to put Leyline of Combustion into play at beginning of game')

Leyline_of_Combustion= Enchantment(
    name="Leyline of Combustion",
    cost=Cost(mana={'R':2,'C':2}),
    triggered_abils=[
        Triggered_Ability(
            name="Leyline of Combustion begin game effect",
            trigger_points=['begin game'],
            add_trigger_zones=['hand'],
            remove_trigger_zones=['hand'],
            abil_effect=Leyline_of_Combustion_begin_game,
            stack=False
        ),
        Triggered_Ability(
            name="Leyline of Combustion",
            trigger_points=['on target'],
            trigger_condition= lambda source_abil, target_source, targeted_obj:
                target_source.controller==source_abil.controller.opponent and
                targeted_obj.controller==source_abil.controller,
            abil_effect= lambda source_abil: source_abil.controller.opponent.
                take_damage(2, source= source_abil.source, combat=False)
        )
    ],
    rarity='rare'
)


# Maniacal Rage {1}{R}
# Enchantment — Aura
# Enchant creature
# Enchanted creature gets +2/+2 and can’t block.

def Manical_Rage_effect(attached_to):
    attached_to.change_power(2)
    attached_to.change_toughness(2)
    attached_to.add_keyword('cant_block')

def r_Manical_Rage_effect(attached_to):
    attached_to.change_power(-2)
    attached_to.change_toughness(-2)
    attached_to.remove_keyword('cant_block')

Maniacal_Rage= Aura(
    name='Maniacal Rage',
    cost=Cost(mana={'C':1,'R':1}),
    rarity='common',
    aura_static_effect=Attached_Effect(
        name="Manical Rage aura effect",
        effect_func=Manical_Rage_effect,
        reverse_effect_func=r_Manical_Rage_effect
    )
)

# Marauding Raptor {1}{R}
# Creature — Dinosaur
# Creature spells you cast cost {1} less to cast.
# Whenever another creature enters the battlefield under your control, Marauding
# Raptor deals 2 damage to it. If a Dinosaur is dealt damage this way, Marauding
# Raptor gets +2/+0 until end of turn.
# 2/3
def Marauding_Raptor_cost_reduce(applied_obj, source_abil):
    source_abil.source.controller.cost_mods.append(
        Cost_Modification(
            name='Marauding_Raptor cost reduction obj',
            cost_mod={'C':-1},
            cost_mod_source=source_abil.source,
            mod_condition= lambda cost_obj, cost_mod_source: \
                isinstance(cost_obj.source, Card) and 'creature' in cost_obj.source.types
        )
    )

def r_Marauding_Raptor_cost_reduce(applied_obj, source_abil):
    abil_instances=[i for i in source_abil.controller.cost_mods if i.name==
        'Marauding Raptor cost reduction obj']
    if abil_instances != []:
        source_abil.controller.cost_mods.remove(abil_instances[0])

def Marauding_Raptor_ETB_effect(source_abil):
    success=source_abil.last_known_info.take_damage(2, source=source_abil.source, combat=False)
    if 'dinosaur' in source_abil.last_known_info.subtypes and success:
        source_abil.source.change_power(2)
        source_abil.source.EOT_reverse_effects.append(EOTr_Marauding_Raptor_ETB_effect)

def EOTr_Marauding_Raptor_ETB_effect(creature):
    creature.change_power(-2)


Marauding_Raptor= Creature(
    name='Marauding Raptor',
    cost=Cost(mana={'C':1,"R":1}),
    power=2,
    toughness=3,
    subtypes=['dinosaur'],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Marauding Raptor cost reduction",
            own_apply_zones=[], opp_apply_zones=[],
            players='self',
            effect_func= Marauding_Raptor_cost_reduce,
            reverse_effect_func= r_Marauding_Raptor_cost_reduce,
        )
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Marauding Raptor creature ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj!=source_abil.source
                and 'creature' in obj.types and obj.controller==source_abil.controller,
            lki_func= lambda source_abil, effect_kwargs: effect_kwargs['obj'],
            abil_effect = Marauding_Raptor_ETB_effect
        )
    ],
    rarity='rare'
)

# Mask of Immolation {1}{R}
# Artifact — Equipment
# When Mask of Immolation enters the battlefield, create a 1/1 red Elemental
# creature token, then attach Mask of Immolation to it.
# Equipped creature has “Sacrifice this creature: It deals 1 damage to any target.”
# Equip {2} ({2}: Attach to target creature you control. Equip only as a sorcery.)
def Mask_of_Immolation_equip(attached_to):
    abil=Activated_Ability(
        name='Mask of Immolation ability',
        cost=Cost(non_mana=[lambda source_abil: source_abil.source.sacrifice()]),
        targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
        abil_effect= lambda source_abil: source_abil.get_targets().take_damage(
            1, source=source_abil.source, combat=False
        ),
    )
    abil.assign_source(attached_to)
    abil.assign_ownership(attached_to.controller)
    attached_to.activated_abils=attached_to.activated_abils+[abil]

def r_Mask_of_Immolation_equip(attached_to):
    # remove granted activated ability (remove only one copy in case multiples
    # of this aura are attached to the target)
    abil_instances=[i for i in attached_to.activated_abils if i.name==
        'Mask of Immolation ability']
    attached_to.activated_abils.remove(abil_instances[0])

def Mask_of_Immolation_ETB_effect(source_abil):
    token=Creature_Token(
        name="Elemental 1/1",
        colors=['R'],
        types=['creature'],
        subtypes=['elemental'],
        power=1,
        toughness=1,
    )
    source_abil.source.attach_to(token)
    source_abil.source.controller.create_token(token)

Mask_of_Immolation=Equipment(
    name='Mask of Immolation',
    cost=Cost(mana={'C':1,'R':1}),
    equip_cost=Cost(mana={'C':2}),
    equip_static_effect=Attached_Effect(
        name='Mask of Immolation equip abil',
        effect_func=Mask_of_Immolation_equip,
        reverse_effect_func=r_Mask_of_Immolation_equip
    ),
    triggered_abils=[
        Triggered_Ability(
            name='Mask of Immolation ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Mask_of_Immolation_ETB_effect
        )
    ],
    rarity='uncommon'
)

# Pack Mastiff {1}{R}
# Creature — Dog
# {1}{R}: Each creature you control named Pack Mastiff gets +1/+0 until end of turn.
# 2/2
def EOTr_Pack_Mastiff_effect(creature):
    creature.change_power(-1)

def Pack_Mastiff_effect(source_abil):
    for i in source_abil.controller.field:
        if i.name=='Pack Mastiff':
            i.change_power(1)
            i.EOT_reverse_effects.append(EOTr_Pack_Mastiff_effect)

Pack_Mastiff= Creature(
    name='Pack Mastiff',
    cost=Cost(mana={"C":1, "R":1}),
    power=2,
    toughness=2,
    subtypes=['dog'],
    activated_abils=[
        Activated_Ability(
            name='Pack Mastiff abil',
            cost=Cost(mana={'C':1,'R':1}),
            abil_effect= Pack_Mastiff_effect
        )
    ],
    rarity='common'
)

# Rapacious Dragon {4}{R}
# Creature — Dragon
# Flying
# When Rapacious Dragon enters the battlefield, create two Treasure tokens.
# (They’re artifacts with “{T}, Sacrifice this artifact: Add one mana of any color.”)
# 3/3

def Rapacious_Dragon_ETB_effect(source_abil):
    for _ in range(2):
        token = Artifact_Token(
            name='Treasure',
            mana_source=True,
            activated_abils=[
                Activated_Ability(
                    name='Treasure add W abil',
                    cost=Cost(
                        non_mana=[lambda source_abil: source_abil.source.tap(),
                            lambda source_abil: source_abil.source.sacrifice()],
                        non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                        and (source_abil.source.summoning_sick==False or 'creature' not in
                        source_abil.source.types)]
                    ),
                    abil_effect=lambda source_abil: source_abil.source.controller.add_mana('W'),
                    mana_abil=True,
                    potential_mana=Potential_Mana({'W':1})
                ),
                Activated_Ability(
                    name='Treasure add U abil',
                    cost=Cost(
                        non_mana=[lambda source_abil: source_abil.source.tap(),
                            lambda source_abil: source_abil.source.sacrifice()],
                        non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                        and (source_abil.source.summoning_sick==False or 'creature' not in
                        source_abil.source.types)]
                    ),
                    abil_effect=lambda source_abil: source_abil.source.controller.add_mana('U'),
                    mana_abil=True,
                    potential_mana=Potential_Mana({'U':1})
                ),
                Activated_Ability(
                    name='Treasure add B abil',
                    cost=Cost(
                        non_mana=[lambda source_abil: source_abil.source.tap(),
                            lambda source_abil: source_abil.source.sacrifice()],
                        non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                        and (source_abil.source.summoning_sick==False or 'creature' not in
                        source_abil.source.types)],
                    ),
                    abil_effect=lambda source_abil: source_abil.source.controller.add_mana('B'),
                    mana_abil=True,
                    potential_mana=Potential_Mana({'B':1})
                ),
                Activated_Ability(
                    name='Treasure add R abil',
                    cost=Cost(
                        non_mana=[lambda source_abil: source_abil.source.tap(),
                            lambda source_abil: source_abil.source.sacrifice()],
                        non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                        and (source_abil.source.summoning_sick==False or 'creature' not in
                        source_abil.source.types)]
                    ),
                    abil_effect=lambda source_abil: source_abil.source.controller.add_mana('R'),
                    mana_abil=True,
                    potential_mana=Potential_Mana({'R':1})
                ),
                Activated_Ability(
                    name='Treasure add G abil',
                    cost=Cost(
                        non_mana=[lambda source_abil: source_abil.source.tap(),
                            lambda source_abil: source_abil.source.sacrifice()],
                        non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                        and (source_abil.source.summoning_sick==False or 'creature' not in
                        source_abil.source.types)]
                    ),
                    abil_effect=lambda source_abil: source_abil.source.controller.add_mana('G'),
                    mana_abil=True,
                    potential_mana=Potential_Mana({'G':1})
                ),
            ]
        )
        source_abil.controller.create_token(token)

Rapacious_Dragon= Creature(
    name='Rapacious Dragon',
    cost=Cost(mana={'C':4,'R':1}),
    power=3,
    toughness=3,
    subtypes=['dragon'],
    rarity='uncommon',
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Rapacious Dragon triggered abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Rapacious_Dragon_ETB_effect
        )
    ]
)

# Reckless Air Strike {R}
# Sorcery
# Choose one —
# • Reckless Air Strike deals 3 damage to target creature with flying.
# • Destroy target artifact.

def Reckless_Air_Strike_effect(source_card):
    target=source_card.get_targets()
    if source_card.selected_mode==1:
        target.take_damage(3, source=source_card, combat=False)
    if source_card.selected_mode==2:
        if source_card.targets[1].check_target_zones():
            target.destroy()

Reckless_Air_Strike = Instant (
    name='Reckless Air Strike',
    cost=Cost(mana={'R':1}),
    moded=True,
    n_modes=2,
    mode_labels=['Flying creature damage', 'Destroy artifact'],
    targets=[
        Target(criteria=lambda source, obj: 'flying' in obj.keyword_static_abils,
            mode_linked=True, mode_num=1),
        Target(criteria=lambda source, obj: 'artifact' in obj.types,
            mode_linked=True, mode_num=2)
        ],
    spell_effect= Reckless_Air_Strike_effect,
    rarity='common'
)

# Reduce to Ashes {4}{R}
# Sorcery
# Reduce to Ashes deals 5 damage to target creature. If that creature would die
# this turn, exile it instead.
def EOTr_Reduce_to_Ashes(creature):
    creature.remove_keyword('exile_on_death')

def Reduce_to_Ashes_effect(source_card):
    target=source_card.get_targets()
    target.take_damage(5, source=source_card, combat=False)
    target.add_keyword('exile_on_death')
    target.EOT_reverse_effects.append(EOTr_Reduce_to_Ashes)

Reduce_to_Ashes = Sorcery(
    name='Reduce to Ashes',
    cost=Cost(mana={'C':4,'R':1}),
    targets=[Target(criteria=lambda source, obj: 'creature' in obj.types)],
    spell_effect= Reduce_to_Ashes_effect,
    rarity='common'
)

# Repeated Reverberation {2}{R}{R}
# Instant
# When you next cast an instant spell, cast a sorcery spell, or activate a loyalty
#  ability this turn, copy that spell or ability twice. You may choose new targets
#  for the copies.

# store the casted ability or spell in last known info
def Repeated_Reverberation_lki(source_abil, effect_kwargs):
    if 'casted_spell' in effect_kwargs.keys():
        return(effect_kwargs['casted_spell'])
    if 'activated_abil' in effect_kwargs.keys():
        return(effect_kwargs['activated_abil'])

def Repeated_Reverberation_trigger_effect(source_abil):
    for _ in range(2):
        source_abil.last_known_info.make_copy()

def EOTr_Repeated_Reverberation_effect(player):
    abils= [i for i in player.triggered_abils if i.name==
        'Repeated Reverberation trigger']
    for abil in abils:
        abil.remove_trigger_points()
    player.triggered_abils = [i for i in player.triggered_abils if i.name!=
        'Repeated Reverberation trigger']

def Repeated_Reverberation_effect(source_card):
    abil = Triggered_Ability(
        name='Repeated Reverberation trigger',
        trigger_points=['abil activated','cast spell'],
        trigger_condition = lambda source_abil, **kwargs:
            # check if we're in an abil_activated trigger by looking for activated abils
            ('activated_abil' in locals() and
            # then check if it's a loyalty ability
            activated_abil.controller==source_abil.controller and 'planeswalker'
            in activated_abil.source.types)
            # then check if we're dealing with a 'cast spell' trigger by looking for casted_spell
            or ('casted_spell' in locals() and
            # finally, check if casted spell is an instant or sorcery
            ('instant' in casted_spell.types or 'sorcery' in casted_spell.types)),
        lki_func=  Repeated_Reverberation_lki,
        abil_effect= Repeated_Reverberation_trigger_effect
    )
    abil.assign_source(source_card.controller)
    abil.assign_controller(source_card.controller)
    abil.add_trigger_points()
    source_card.controller.triggered_abils=source_card.controller.triggered_abils+[abil]
    source_card.controller.EOT_reverse_effects.append(EOTr_Repeated_Reverberation_effect)

Repeated_Reverberation = Instant(
    name='Repeated Reverberation',
    cost=Cost(mana={'C':2,'R':2}),
    spell_effect=Repeated_Reverberation_effect,
    rarity='rare'
)

# Ripscale Predator {4}{R}{R}
# Creature — Dinosaur
# Menace (This creature can’t be blocked except by two or more creatures.)
# 6/5
Ripscale_Predator= Creature(
    name='Ripscale Predator',
    cost=Cost(mana={"C":4, "R":2}),
    power=6,
    toughness=5,
    subtypes=['dinosaur'],
    keyword_static_abils=['menace'],
    rarity='common'
)

# Scampering Scorcher {3}{R}
# Creature — Elemental
# When Scampering Scorcher enters the battlefield, create two 1/1 red Elemental
# creature tokens. Elementals you control gain haste until end of turn.
# 1/1
def EOTr_Scampering_Scorcher(creature):
    creature.remove_keyword('haste')

def Scampering_Scorcher_effect(source_abil):
    for _ in range(2):
        source_abil.controller.create_token(
            Creature_Token(
                name='Elemental 1/1',
                colors=['R'],
                subtypes=['elemental'],
                power=1,
                toughness=1
            )
        )

    for obj in [i for i in source_abil.controller.field if 'elemental' in i.subtypes]:
        obj.add_keyword('haste')
        obj.EOT_reverse_effects.append(EOTr_Scampering_Scorcher)

Scampering_Scorcher= Creature(
    name='Scampering Scorcher',
    cost=Cost(mana={"C":3, "R":1}),
    power=1,
    toughness=1,
    subtypes=['elemental'],
    triggered_abils=[
        Triggered_Ability(
            name='Scampering Scorcher ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Scampering_Scorcher_effect
        )
    ],
    rarity='uncommon'
)

# Scorch Spitter {R}
# Creature — Elemental Lizard
# Whenever Scorch Spitter attacks, it deals 1 damage to the player or planeswalker
# it’s attacking.
# 1/1
Scorch_Spitter= Creature(
    name='Scorch Spitter',
    cost=Cost(mana={"R":1}),
    power=1,
    toughness=1,
    subtypes=['elemental'],
    triggered_abils=[
        Triggered_Ability(
            name='Scorch Spitter atk abil',
            trigger_points=['on attack'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.source.atk_target
                .take_damage(1, source=source_abil.source, combat=False)
        )
    ],
    rarity='common'
)

# Shock {R}
# Instant
# Shock deals 2 damage to any target.
Shock= Instant(
    name='Shock',
    cost=Cost(mana={"R":1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types or
        'planeswalker' in obj.types, c_players='both')],
    spell_effect= lambda source_card: source_card.get_targets().take_damage(2,
        source=source_card, combat=False),
    rarity='common'
)

# Tectonic Rift {3}{R}
# Sorcery
# Destroy target land. Creatures without flying can’t block this turn.
def EOTr_Tectonic_Rift_effect(creature):
    creature.remove_keyword('cant_block')
def Tectonic_Rift_effect(source_card):
    source_card.get_targets().destroy()
    for i in source_card.owner.field:
        if 'creature' in i.types:
            i.add_keyword('cant_block')
            i.EOT_reverse_effects.append(EOTr_Tectonic_Rift_effect)
    for i in source_card.owner.opponent.field:
        if 'creature' in i.types:
            i.add_keyword('cant_block')
            i.EOT_reverse_effects.append(EOTr_Tectonic_Rift_effect)

Tectonic_Rift= Sorcery(
    name='Tectonic Rift',
    cost=Cost(mana={'C':3,"R":1}),
    targets=[Target(criteria= lambda source, obj: 'land' in obj.types)],
    spell_effect= Tectonic_Rift_effect,
    rarity='common'
)

# Thunderkin Awakener {1}{R}
# Creature — Elemental Shaman
# Haste
# Whenever Thunderkin Awakener attacks, choose target Elemental creature card in
# your graveyard with toughness less than Thunderkin Awakener’s toughness.
# Return that card to the battlefield tapped and attacking. Sacrifice it at the
# beginning of the next end step.
# 1/2

def Thunderkin_Awakener_effect(source_abil):
    target=source_abil.get_targets()
    # target leaves yard
    target.owner.yard.leave_zone(target)
    # assign sac abil to card
    sac_abil= Triggered_Ability(
        name='Thunderkin Awakener sacrifice trigger',
        trigger_points=['end phase'],
        trigger_condition = lambda source_abil, **kwargs: True,
        abil_effect= lambda source_abil: source_abil.source.sacrifice(),
        remove_on_leave_zone=True
    )
    sac_abil.assign_source(target)
    sac_abil.assign_controller(target.controller)
    target.triggered_abils= target.triggered_abils + [sac_abil]

    # target enters play
    source_abil.controller.field.enter_zone(target)

Thunderkin_Awakener=Creature(
    name='Thunderkin Awakener',
    cost=Cost(mana={'C':1,'R':1}),
    subtypes=['elemental'],
    power=1,
    toughness=2,
    rarity='rare',
    triggered_abils=[
        Triggered_Ability(
            name='Thunderkin Awakener attack abil',
            trigger_points=['on attack'],
            trigger_condition=lambda source_abil, obj, **kwargs:
                source_abil.source==obj,
            targets=[Target(criteria=lambda source, obj: 'elemental' in obj.subtypes
                and obj.toughness<source.source.toughness, c_zones=['yard'],
                c_opponent=False)],
            abil_effect=Thunderkin_Awakener_effect
        )
    ]
)

# Uncaged Fury {2}{R}
# Instant
# Target creature gets +1/+1 and gains double strike until end of turn.
# (It deals both first-strike and regular combat damage.)

def Uncaged_Fury_effect(source_card):
    target=source_card.get_targets()
    target.change_power(1)
    target.change_toughness(1)
    target.add_keyword('double strike')
    target.EOT_reverse_effects.append(EOTr_Uncaged_Fury_effect)

def EOTr_Uncaged_Fury_effect(creature):
    creature.change_power(-1)
    creature.change_toughness(-1)
    creature.remove_keyword('double strike')

Uncaged_Fury=Instant(
    name='Uncaged Fury',
    cost=Cost(mana={'C':2,'R':1}),
    rarity='uncommon',
    targets=[Target(criteria=lambda source, obj: 'creature' in obj.types)],
    spell_effect=Uncaged_Fury_effect
)

# Unchained Berserker {1}{R}
# Creature — Human Berserker
# Protection from white
# Unchained Berserker gets +2/+0 as long as it’s attacking.
# 1/1

Unchained_Berserker= Creature(
    name='Unchained Berserker',
    cost=Cost(mana={"C":1, "R":1}),
    power=1,
    toughness=1,
    subtypes=['human','berserker'],
    protection_effects=[Protection(condition=lambda obj: 'W' in obj.colors)],
    rarity='uncommon',
    nonkeyword_static_abils=[
        Local_Static_Effect(
            name='Unchained Berserker pump effect',
            effect_condition = lambda source_abil: source_abil.source.attacking,
            effect_func=lambda source_abil: source_abil.source.change_power(2),
            reverse_effect_func=lambda source_abil: source_abil.source.change_power(-2)
        )
    ]
)

# Barkhide Troll {G}{G}
# Creature — Troll
# Barkhide Troll enters the battlefield with a +1/+1 counter on it.
# {1}, Remove a +1/+1 counter from Barkhide Troll: Barkhide Troll gains hexproof
# until end of turn. (It can’t be the target of spells or abilities your opponents control.)
# 2/2
def EOTr_Barkhide_Troll_effect(creature):
    creature.remove_keyword('hexproof')

def Barkhide_Troll_effect(source_abil):
    source_abil.source.add_keyword('hexproof')
    source_abil.source.EOT_reverse_effects.append(EOTr_Barkhide_Troll_effect)

def Barkhide_Troll_abil_nonmana_cost(source_abil):
    plus1_counters= [i for i in source_abil.source.attached_objs if i.name=='+1/+1 counter']
    source_abil.source.attached_objs.remove(plus1_counters[0])

Barkhide_Troll= Creature(
    name='Barkhide Troll',
    cost=Cost(mana={'G':2}),
    power=2,
    toughness=2,
    subtypes=['troll'],
    rarity='uncommon',
    nonkeyword_static_abils=[
        Local_Static_Effect(
            name="Barkhide Troll ETB",
            effect_func= lambda source_abil: deepcopy(plus1_plus1_counter)
                .attach_to(source_abil.source),
            reverse_effect_func= lambda source_abil: True,
            effect_condition = lambda source_abil: source_abil.source.ETB_static_check==True
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Barkhide Troll activated abil',
            cost=Cost(
                mana={'C':1},
                non_mana=[Barkhide_Troll_abil_nonmana_cost],
                non_mana_check=[lambda source_abil: any([i.name=='+1/+1 counter' for
                    i in source_abil.source.attached_objs])],
                ),
            abil_effect=Barkhide_Troll_effect
        )
    ]
)

# Brightwood Tracker {3}{G}
# Creature — Elf Scout
# {5}{G}, {T}: Look at the top four cards of your library. You may reveal a
# creature card from among them and put it into your hand. Put the rest on the
# bottom of your library in a random order.
# 2/4

def Brightwood_Tracker_effect(source_abil):
    top_cards = source_abil.controller.lib[0:4]
    cands = [i for i in top_cards if 'creature' in i.types]
    selected = source_abil.controller.input_choose(cands,
        label='Brightwood Tracker abil select', permit_empty_list=True,squeeze=False)
    if selected!=None:
        source_abil.controller.lib.leave_zone(selected[0])
        source_abil.controller.hand.enter_zone(selected[0])
        source_abil.controller.reveal_cards(selected, zone='hand')
        non_selected = [i for i in top_cards if i not in selected]
    else:
        non_selected=top_cards
    random.shuffle(non_selected)
    for i in non_selected:
        source_abil.controller.lib.remove(i)
        source_abil.controller.lib.append(i)

Brightwood_Tracker = Creature(
    name='Brightwood Tracker',
    cost=Cost(mana={'C':3,'G':1}),
    subtypes=['elf','scout'],
    power=2,
    toughness=4,
    rarity='common',
    activated_abils=[
        Activated_Ability(
            name='Brightwood Tracker abil',
            cost=Cost(
                mana={'C':5,'G':1},
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect= Brightwood_Tracker_effect
        )
    ]
)

# Cavalier of Thorns {2}{G}{G}{G}
# Creature — Elemental Knight
# Reach
# When Cavalier of Thorns enters the battlefield, reveal the top five cards of your
# library. Put a land card from among them onto the battlefield and the rest into
# your graveyard.
# When Cavalier of Thorns dies, you may exile it. If you do, put another target
# card from your graveyard on top of your library.
# 5/6

def Cavalier_of_Thorns_ETB_effect(source_abil):
    top_cards = source_abil.controller.lib[0:5]
    cands = [i for i in top_cards if 'land' in i.types]
    selected = source_abil.controller.input_choose(cands,
        label='Cavalier of thorns ETB abil select', permit_empty_list=True,squeeze=False)
    if selected!=None:
        source_abil.controller.lib.leave_zone(selected[0])
        source_abil.controller.field.enter_zone(selected[0])
        selected[0].tap(for_cost=False, summoning_sick_ok=True)
        source_abil.controller.reveal_cards(selected, zone='hand')
        non_selected = [i for i in top_cards if i not in selected]
    else:
        non_selected=top_cards
    for i in non_selected:
        source_abil.controller.lib.leave_zone(i)
        source_abil.controller.yard.enter_zone(i)

def Cavalier_of_Thorns_dies_effect(source_abil):
    target=source_abil.get_targets()
    if source_abil.controller.input_bool('exile Cavalier_of_Thorns'):
        source_abil.source.exile()
        target.owner.yard.leave_zone(target)
        target.owner.lib.enter_zone(target,pos=0)

Cavalier_of_Thorns=Creature(
    name='Cavalier of Thorns',
    cost=Cost(mana={"C":2, "G":3}),
    power=5,
    toughness=6,
    subtypes=['elemental','knight'],
    keyword_static_abils=['reach'],
    triggered_abils=[
        Triggered_Ability(
            name='Cavalier of Thorns ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Cavalier_of_Thorns_ETB_effect
        ),
        Triggered_Ability(
            name='Cavalier of Thorns Dies',
            trigger_points=['dies'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[Target(criteria=lambda source, obj: True, c_zones=['yard'],
                c_opponent=False, c_self_target=False)],
            abil_effect= Cavalier_of_Thorns_dies_effect
        )
    ],
    rarity='mythic'
)


# Centaur Courser {2}{G}
# Creature — Centaur Warrior
# 3/3
Centaur_Courser= Creature(
    name='Centaur Courser',
    cost=Cost(mana={"C":2, "G":1}),
    power=3,
    toughness=3,
    subtypes=['centaur','warrior'],
    rarity='common'
)

# Elvish Reclaimer {G}
# Creature — Elf Warrior
# Elvish Reclaimer gets +2/+2 as long as there are three or more land cards in your graveyard.
# {2}, {T}, Sacrifice a land: Search your library for a land card, put it onto the battlefield tapped, then shuffle your library.
# 1/2
def Elvish_Reclaimer_pump_effect(source_abil):
    source_abil.source.change_power(2)
    source_abil.source.change_toughness(2)

def r_Elvish_Reclaimer_pump_effect(source_abil):
    source_abil.source.change_power(-2)
    source_abil.source.change_toughness(-2)

def Elvish_Reclaimer_select_effect(card):
    card.owner.lib.leave_zone(card)
    card.owner.field.enter_zone(card)
    card.tap(for_cost=False, summoning_sick_ok=True)

def Elvish_Reclaimer_activated_effect(source_abil):
    source_abil.controller.search_library(
        elig_condition= lambda card: 'land' in card.types,
        select_effect= Elvish_Reclaimer_select_effect,
        shuffle=True
    )

Elvish_Reclaimer= Creature(
    name='Elvish Reclaimer',
    cost=Cost(mana={"G":1}),
    power=1,
    toughness=2,
    subtypes=['elf','warrior'],
    rarity='rare',
    nonkeyword_static_abils=[
        Local_Static_Effect(
            name='Elvish Reclaimer Pump Effect',
            effect_func = Elvish_Reclaimer_pump_effect,
            reverse_effect_func = r_Elvish_Reclaimer_pump_effect,
            effect_condition = lambda source_abil: len([i for i in source_abil.controller.yard
                if 'land' in i.types])>=3
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Elvish Reclaimer activated abil',
            cost=Cost(
                mana={'C':2},
                non_mana=[lambda source_abil: source_abil.source.tap(),
                    lambda source_abil: source_abil.controller.sacrifice_permanent(
                    types=['land'])],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                    and (source_abil.source.summoning_sick==False or 'creature' not in
                    source_abil.source.types),
                    lambda source_abil: len([i for i in source_abil.controller.field
                        if 'land' in i.types])>0]
            ),
            abil_effect= Elvish_Reclaimer_activated_effect
        )
    ]
)

# Feral Invocation {2}{G}
# Enchantment — Aura
# Flash (You may cast this spell any time you could cast an instant.)
# Enchant creature
# Enchanted creature gets +2/+2.
def Feral_Invocation_effect(attached_to):
    attached_to.change_power(2)
    attached_to.change_toughness(2)

def r_Feral_Invocation_effect(attached_to):
    attached_to.change_power(-2)
    attached_to.change_toughness(-2)

Feral_Invocation= Aura(
    name='Feral_Invocation',
    cost=Cost(mana={'C':2,'G':1}),
    aura_static_effect=Attached_Effect(
        name="Feral Invocation Aura effects",
        effect_func=Feral_Invocation_effect,
        reverse_effect_func=r_Feral_Invocation_effect
    ),
    keyword_static_abils=['flash'],
    rarity='common'
)

# Ferocious Pup {2}{G}
# Creature — Wolf
# When Ferocious Pup enters the battlefield, create a 2/2 green Wolf creature token.
# 0/1

Ferocious_Pup= Creature(
    name='Ferocious Pup',
    cost=Cost(mana={'C':2,'G':1}),
    power=0,
    toughness=1,
    subtypes=['wolf'],
    rarity='common',
    triggered_abils=[
        Triggered_Ability(
            name='Ferocious Pup ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect = lambda source_abil: source_abil.source.controller.create_token(
                Creature_Token(
                    name="Wolf 2/2",
                    colors=['G'],
                    types=['creature'],
                    subtypes=['wolf'],
                    power=2,
                    toughness=2
                )
            )
        )
    ]
)

# Gargos, Vicious Watcher {3}{G}{G}{G}
# Legendary Creature — Hydra
# Vigilance
# Hydra spells you cast cost {4} less to cast.
# Whenever a creature you control becomes the target of a spell, Gargos, Vicious
# Watcher fights up to one target creature you don’t control.
# 8/7

def Gargos_Vicious_Watcher_cost_reduce(applied_obj, source_abil):
    source_abil.source.controller.cost_mods.append(
        Cost_Modification(
            name='Gargos, Vicious Watcher cost reduction obj',
            cost_mod={'C':-4},
            cost_mod_source=source_abil.source,
            mod_condition= lambda cost_obj, cost_mod_source: \
                isinstance(cost_obj.source, Card) and 'creature' in cost_obj.source.types and
                'hydra' in cost_obj.source.subtypes
        )
    )

def r_Gargos_Vicious_Watcher_cost_reduce(applied_obj, source_abil):
    abil_instances=[i for i in source_abil.controller.cost_mods if i.name==
        'Gargos, Vicious Watcher cost reduction obj']
    if abil_instances != []:
        source_abil.controller.cost_mods.remove(abil_instances[0])

def Gargos_Vicious_Watcher_fight_abil(source_abil):
    target=source_abil.get_targets()
    source_abil.source.fight(target)

Gargos_Vicious_Watcher= Creature(
    name="Gargos, Vicious Watcher",
    cost=Cost(mana={'C':3,"G":3}),
    power=8,
    toughness=7,
    types=['legendary','creature'],
    subtypes=['hydra'],
    keyword_static_abils=['vigilance'],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Gargos, Vicious Watcher cost reduction",
            own_apply_zones=[], opp_apply_zones=[],
            players='self',
            effect_func= Gargos_Vicious_Watcher_cost_reduce,
            reverse_effect_func= r_Gargos_Vicious_Watcher_cost_reduce,
        )
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Gargos, Vicious Watcher on target abil',
            trigger_points=['on target'],
            trigger_condition= lambda source_abil, target_source, targeted_obj:
                targeted_obj.controller==source_abil.controller and
                'creature' in targeted_obj.types and
                isinstance(target_source, Card),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,
                c_own=False, c_required=False)],
            abil_effect= Gargos_Vicious_Watcher_fight_abil
        )
    ],
    rarity='rare'
)


# Gift of Paradise {2}{G}
# Enchantment — Aura
# Enchant land
# When Gift of Paradise enters the battlefield, you gain 3 life.
# Enchanted land has “{T}: Add two mana of any one color.”

def Gift_of_Paradise_effect(attached_to):
    abil={}
    abil['W']=Activated_Ability(
            name='Gift of Paradise '+ 'W'+ ' ability',
            mana_abil=True,
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect= lambda source_abil: source_abil.source.controller.add_mana('W',2),
            potential_mana=Potential_Mana({'W':2})
        )
    abil['U']=Activated_Ability(
            name='Gift of Paradise '+ 'U'+ ' ability',
            mana_abil=True,
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect= lambda source_abil: source_abil.source.controller.add_mana('U',2),
            potential_mana=Potential_Mana({'U':2})
        )
    abil['B']=Activated_Ability(
            name='Gift of Paradise '+ 'B'+ ' ability',
            mana_abil=True,
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect= lambda source_abil: source_abil.source.controller.add_mana('B',2),
            potential_mana=Potential_Mana({'B':2})
        )
    abil['R']=Activated_Ability(
            name='Gift of Paradise '+ 'R'+ ' ability',
            mana_abil=True,
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect= lambda source_abil: source_abil.source.controller.add_mana('R',2),
            potential_mana=Potential_Mana({'R':2})
        )
    abil['G']=Activated_Ability(
            name='Gift of Paradise '+ 'G'+ ' ability',
            mana_abil=True,
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect= lambda source_abil: source_abil.source.controller.add_mana('G',2),
            potential_mana=Potential_Mana({'G':2})
        )

    for c in ['W','U','B','R','G']:
        attached_to.activated_abils=attached_to.activated_abils+[abil[c]]
        abil[c].assign_source(attached_to)
        abil[c].assign_ownership(attached_to.controller)

def r_Gift_of_Paradise_effect(attached_to):
    # remove granted activated ability (remove only one copy in case multiples
    # of this aura are attached to the target)
    abil_instances=[i for i in attached_to.activated_abils if 'Gift of Paradise' in i.name]
    attached_to.activated_abils.remove(abil_instances[0])

Gift_of_Paradise= Aura(
    name='Gift of Paradise',
    cost=Cost(mana={'C':2,'G':1}),
    target_types=['land'],
    aura_static_effect= Attached_Effect(
        name= 'Gift of Paradise Aura effect',
        effect_func=Gift_of_Paradise_effect,
        reverse_effect_func= r_Gift_of_Paradise_effect
    ),
    triggered_abils=[
        Triggered_Ability(
            name='Gift of Paradise triggered abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: source_abil.source==obj,
            abil_effect = lambda source_abil: source_abil.controller.change_life(3)
        )
    ],
    rarity='common'
)

# Greenwood Sentinel {1}{G}
# Creature — Elf Scout
# Vigilance (Attacking doesn’t cause this creature to tap.)
# 2/2
Greenwood_Sentinel= Creature(
    name='Greenwood Sentinel',
    cost=Cost(mana={"C":1, "G":1}),
    power=2,
    toughness=2,
    subtypes=['elf','scout'],
    keyword_static_abils=['vigilance'],
    rarity='common'
)


# Growth Cycle {1}{G}
# Instant
# Target creature gets +3/+3 until end of turn. It gets an additional +2/+2 until
# end of turn for each card named Growth Cycle in your graveyard.

def Growth_Cycle_effect(source_abil):
    pump=3 + 2*len([i for i in source_abil.controller.yard if i.name=='Growth Cycle'])
    target=source_abil.get_targets()
    target.change_power(pump)
    target.change_toughness(pump)
    target.EOT_power_pump+=pump
    target.EOT_toughness_pump+=pump

Growth_Cycle = Instant(
    name='Growth Cycle',
    cost=Cost(mana={'C':1,'G':1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
    spell_effect=Growth_Cycle_effect,
    rarity='common'
)

# Healer of the Glade {G}
# Creature — Elemental
# When Healer of the Glade enters the battlefield, you gain 3 life.
# 1/2
Healer_of_the_Glade= Creature(
    name='Healer of the Glade',
    cost=Cost(mana={"G":1}),
    power=1,
    toughness=2,
    subtypes=['elemental'],
        triggered_abils=[
            Triggered_Ability(
                name='Healer of the Glade ETB',
                trigger_points=['enter field'],
                trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
                abil_effect= lambda source_abil: source_abil.source.controller.change_life(3)
            )
        ],
    rarity='common'
)

# Howling Giant {5}{G}{G}
# Creature — Giant Druid
# Reach (This creature can block creatures with flying.)
# When Howling Giant enters the battlefield, create two 2/2 green Wolf creature tokens.
# 5/5

def Howling_Giant_ETB(source_abil):
    for _ in range(2):
         source_abil.source.controller.create_token(
            Creature_Token(
                name='Wolf 2/2',
                colors=[],
                subtypes=['wolf'],
                power=2,
                toughness=2
            )
        )
Howling_Giant= Creature(
    name='Howling Giant',
    cost=Cost(mana={'C':5,"G":2}),
    power=5,
    toughness=5,
    subtypes=['giant','druid'],
    keyword_static_abils=['reach'],
    triggered_abils=[
        Triggered_Ability(
            name='Howling Giant ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Howling_Giant_ETB
        )
    ],
    rarity='uncommon'
)

# Leafkin Druid {1}{G}
# Creature — Elemental Druid
# {T}: Add {G}. If you control four or more creatures, add {G}{G} instead.
# 0/3

def Leafkin_Druid_2_mana_effect(source_abil):
    source_abil.controller.add_mana('G', 2)

Leafkin_Druid=Creature(
    name='Leafkin Druid',
    cost=Cost(mana={'C':1,'G':1}),
    subtypes=['elemental','druid'],
    power=0,
    toughness=3,
    rarity='common',
    mana_source=True,
    activated_abils=[
        Activated_Ability(
            name='Leafkin Druid normal abil',
            cost= Cost(
                    non_mana=[lambda source_abil: source_abil.source.tap()],
                    non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                    and (source_abil.source.summoning_sick==False or 'creature' not in
                    source_abil.source.types)]
                ),
            potential_mana= Potential_Mana({'G':1}),
            abil_effect= lambda source_abil: source_abil.controller.add_mana('G'),
            mana_abil=True
        ),
        Activated_Ability(
            name='Leafkin Druid buffed abil',
            cost= Cost(
                    non_mana=[lambda source_abil: source_abil.source.tap()],
                    non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                    and (source_abil.source.summoning_sick==False or 'creature' not in
                    source_abil.source.types) and len([i for i in source_abil
                        .controller.field if 'creature' in i.types])>=4]
                ),
            requirements=[Requirement(lambda source: len([i for i in source.controller
                .field if 'creature' in i.types])>=4)],
            potential_mana= Potential_Mana({'G':2}, condition = lambda source:
                source.tapped==False and (source.summoning_sick==False or 'creature' not in
                source.types) and len([i for i in source.controller.field if 'creature' in i.types])>=4),
            abil_effect= Leafkin_Druid_2_mana_effect,
            mana_abil=True
        )
    ]
)

# Leyline of Abundance {2}{G}{G}
# Enchantment
# If Leyline of Abundance is in your opening hand, you may begin the game with
# it on the battlefield.
# Whenever you tap a creature for mana, add an additional {G}.
# {6}{G}{G}: Put a +1/+1 counter on each creature you control.
def Leyline_of_Abundance_begin_game(source_abil):
    if source_abil.source.owner.input_bool(label='Leyline begin of game abil'):
        source_abil.source.owner.hand.leave_zone(source_abil.source)
        source_abil.source.owner.field.enter_zone(source_abil.source)
        if source_abil.source.controller.game.verbose>=2:
            print(source_abil.source.controller, 'puts Leyline of Abundance into play at beginning of game')
    else:
        if source_abil.source.controller.game.verbose>=2:
            print(source_abil.source.controller, 'elects not to put Leyline of Abundance into play at beginning of game')

def Leyline_of_Abundance_activated_effect(source_abil):
    for i in source_abil.controller.field:
        if 'creature' in i.types:
            deepcopy(plus1_plus1_counter).attach_to(i)

def Leyline_of_Abundance_pot_mana_effect(applied_obj,source_abil):
    for abil in applied_obj.activated_abils:
        if abil.mana_abil and any(['source_abil.source.tap()' in inspect.getsource(i) for i in
        abil.cost[0].non_mana_cost]):
            if 'G' in abil.potential_mana.mana.keys():
                abil.potential_mana.mana['G'] += 1
            else:
                abil.potential_mana.mana['G'] = 1

def r_Leyline_of_Abundance_pot_mana_effect(applied_obj,source_abil):
    for abil in applied_obj.activated_abils:
        if abil.mana_abil and any(['source_abil.source.tap()' in inspect.getsource(i) for i in
        abil.cost[0].non_mana_cost]):
            abil.potential_mana.mana['G'] -= 1

Leyline_of_Abundance= Enchantment(
    name="Leyline of Abundance",
    cost=Cost(mana={'G':2,'C':2}),
    triggered_abils=[
        Triggered_Ability(
            name="Leyline of Abundance begin game effect",
            trigger_points=['begin game'],
            add_trigger_zones=['hand'],
            remove_trigger_zones=['hand'],
            abil_effect=Leyline_of_Abundance_begin_game,
            stack=False
        ),
        Triggered_Ability(
            name='Leyline of Abundance add mana effect',
            trigger_points=['abil activated'],
            trigger_condition = lambda source_abil, activated_abil, **kwargs:
                activated_abil.controller==source_abil.controller and
                'creature' in activated_abil.source.types and
                activated_abil.mana_abil and
                # check if its a tap ability
                any(['source_abil.source.tap()' in inspect.getsource(i) for i in
                    activated_abil.cost[0].non_mana_cost]) ,
            stack=False,
            abil_effect =  lambda source_abil: source_abil.controller.add_mana('G')
        )
    ],
    # use a glob static effect to modify all creature's potential mana
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Leyline of Abundance potential mana mod effect",
            opp_apply_zones=[],
            effect_condition= lambda applied_obj, source_abil: 'creature' in \
                applied_obj.types and applied_obj.mana_source,
            effect_func= Leyline_of_Abundance_pot_mana_effect,
            reverse_effect_func = r_Leyline_of_Abundance_pot_mana_effect
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Leyline of Abundance activated abil',
            cost=Cost(mana={'C':6,'G':2}),
            abil_effect= Leyline_of_Abundance_activated_effect
        )
    ],
    rarity='rare'
)

# Loaming Shaman {2}{G}
# Creature — Centaur Shaman
# When Loaming Shaman enters the battlefield, target player shuffles any number
# of target cards from their graveyard into their library.
# 3/2

def Loaming_Shaman_effect(source_abil):
    player = source_abil.get_targets()
    # generate list of permutations of possible targets
    permutes=[]
    for n in range(len(player.yard)+1):
        permutes = permutes + [i for i in itertools.combinations(player.yard,n)]
    selected = source_abil.controller.input_choose(permutes, label='Loaming Shaman gyard abil')
    for i in selected:
        player.yard.leave_zone(i)
        player.lib.enter_zone(i)
    player.shuffle_lib()

Loaming_Shaman= Creature(
    name='Loaming Shaman',
    cost=Cost(mana={'C':2,'G':1}),
    subtypes=['centaur','shaman'],
    power=3,
    toughness=2,
    rarity='uncommon',
    triggered_abils=[
        Triggered_Ability(
            name='Loaming Shaman ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[Target(criteria= lambda source_card, obj: True, c_zones=[], c_players='both')],
            abil_effect= Loaming_Shaman_effect
        )
    ]
)

# Mammoth Spider {4}{G}
# Creature — Spider
# Reach (This creature can block creatures with flying.)
# 3/5
Mammoth_Spider= Creature(
    name='Mammoth Spider',
    cost=Cost(mana={"C":4, "G":1}),
    power=3,
    toughness=5,
    subtypes=['spider'],
    rarity='common',
    keyword_static_abils=['reach']
)

# Might of the Masses {G}
# Instant
# Target creature gets +1/+1 until end of turn for each creature you control.
def Might_of_the_Masses_effect(source_card):
    target=source_card.get_targets()
    temp_pump=len([i for i in source_card.controller.field if 'creature' in i.types])
    target.change_toughness(temp_pump)
    target.change_power(temp_pump)
    target.EOT_power_pump+=temp_pump
    target.EOT_toughness_pump+=temp_pump

Might_of_the_Masses= Instant(
    name='Might of the Masses',
    cost=Cost(mana={'G':1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
    spell_effect= Might_of_the_Masses_effect,
    rarity='common'
)

# Natural End {2}{G}
# Instant
# Destroy target artifact or enchantment. You gain 3 life.
def Natural_End_effect(source_card):
    source_card.get_targets().destroy()
    source_card.controller.change_life(3)

Natural_End= Instant(
    name='Might of the Masses',
    cost=Cost(mana={'C':2,'G':1}),
    targets=[Target(criteria= lambda source, obj: 'artifact' in obj.types or
        'enchantment' in obj.types)],
    spell_effect= Natural_End_effect,
    rarity='common'
)

# Netcaster Spider {2}{G}
# Creature — Spider
# Reach (This creature can block creatures with flying.)
# Whenever Netcaster Spider blocks a creature with flying, Netcaster Spider gets
#  +2/+0 until end of turn.
# 2/3

def Netcaster_Spider_effect(source_abil):
    source_abil.source.change_power(2)
    source_abil.source.EOT_power_pump+=2

Netcaster_Spider= Creature(
    name='Netcaster Spider',
    cost=Cost(mana={"C":2, "G":1}),
    power=2,
    toughness=3,
    subtypes=['spider'],
    rarity='common',
    keyword_static_abils=['reach'],
    triggered_abils=[
        Triggered_Ability(
            name='Netcaster Spider triggered abil',
            trigger_points=['on block'],
            trigger_condition= lambda source_abil, blocker, **kwargs:
                blocker==source_abil.source and
                source_abil.source.is_blocking_attacker.check_keyword('flying'),
            abil_effect = Netcaster_Spider_effect
        )
    ]
)


# Nightpack Ambusher {2}{G}{G}
# Creature — Wolf
# Flash
# Other Wolves and Werewolves you control get +1/+1.
# At the beginning of your end step, if you didn’t cast a spell this turn,
# create a 2/2 green Wolf creature token.
# 4/4

def Nightpack_Ambusher_pump_effect(applied_obj,source_abil):
    applied_obj.change_power(1)
    applied_obj.change_toughness(1)

def r_Nightpack_Ambusher_pump_effect(applied_obj,source_abil):
    applied_obj.change_power(-1)
    applied_obj.change_toughness(-1)

Nightpack_Ambusher= Creature(
    name='Nightpack Ambusher',
    cost=Cost(mana={"C":2, "G":2}),
    power=4,
    toughness=4,
    subtypes=['wolf'],
    rarity='rare',
    keyword_static_abils=['flash'],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Nightpack Ambusher Pump effect",
            effect_condition= lambda applied_obj, source_abil: 'creature' in \
                applied_obj.types and 'wolf' in applied_obj.subtypes
                and applied_obj.controller == source_abil.controller,
            effect_func= Nightpack_Ambusher_pump_effect,
            reverse_effect_func = r_Nightpack_Ambusher_pump_effect
        )
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Nightpack Ambusher triggered abil',
            trigger_points=['end phase'],
            trigger_condition= lambda source_abil, act_plyr, **kwargs:
                act_plyr==source_abil.controller and
                act_plyr.turn_spell_count==0,
            abil_effect= lambda source_abil: source_abil.source.controller.create_token(
                Creature_Token(
                    name='Wolf 2/2',
                    colors=['G'],
                    subtypes=['wolf'],
                    power=2,
                    toughness=2
                )
            )
        )
    ]
)

# Overcome {3}{G}{G}
# Sorcery
# Creatures you control get +2/+2 and gain trample until end of turn.
def EOTr_Overcome_effect(creature):
    creature.remove_keyword('trample')

def Overcome_effect(source_abil):
    for i in source_abil.controller.field:
        if 'creature' in i.types:
            i.change_power(2)
            i.change_toughness(2)
            i.EOT_power_pump+=2
            i.EOT_toughness_pump+=2
            i.add_keyword('trample')
            i.EOT_reverse_effects.append(EOTr_Overcome_effect)

Overcome=Instant(
    name='Overcome',
    cost=Cost(mana={'C':3,'G':2}),
    spell_effect=Overcome_effect,
    rarity='uncommon'
)

# Overgrowth Elemental {2}{G}
# Creature — Elemental
# When Overgrowth Elemental enters the battlefield, put a +1/+1 counter on another
# target Elemental you control.
# Whenever another creature you control dies, you gain 1 life. If that creature
# was an Elemental, put a +1/+1 counter on Overgrowth Elemental.
# 3/2

def Overgrowth_Elemental_death_effect(source_abil):
    source_abil.controller.change_life(1)
    if 'elemental' in source_abil.last_known_info.subtypes:
        deepcopy(plus1_plus1_counter).attach_to(source_abil.source)

Overgrowth_Elemental= Creature(
    name='Overgrowth Elemental',
    cost=Cost(mana={"C":2, "G":1}),
    power=3,
    toughness=2,
    subtypes=['elemental'],
    rarity='uncommon',
    triggered_abils=[
        Triggered_Ability(
            name='Overgrowth Elemental ETB triggered abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[Target(criteria= lambda source, obj: 'elemental' in obj.subtypes,
                c_self_target=False)],
            abil_effect= lambda source_abil: deepcopy(plus1_plus1_counter).attach_to(
                source_abil.get_targets())
        ),
        Triggered_Ability(
            name='Overgrowth Elemental death trigger',
            trigger_points=['dies'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'creature' in obj.types
                and obj!= source_abil.source,
            lki_func= lambda source_abil, effect_kwargs: effect_kwargs['obj'],
            abil_effect= Overgrowth_Elemental_death_effect
        )
    ]
)


# Plummet {1}{G}
# Instant
# Destroy target creature with flying.
def Plummet_effect(source_card):
    target=source_card.get_targets()
    target.destroy()

Plummet= Instant(
    name='Plummet',
    cost=Cost(mana={"C":1, "G":1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types and
        obj.check_keyword('flying'))],
    spell_effect= Plummet_effect,
    rarity='common'
)

# Pulse of Murasa {2}{G}
# Instant
# Return target creature or land card from a graveyard to its owner’s hand. You gain 6 life.
def Pulse_of_Murasa_effect(source_abil):
    target=source_abil.get_targets()
    target.owner.yard.leave_zone(target)
    target.owner.hand.enter_zone(target)
    source_abil.controller.change_life(6)

Pulse_of_Murasa= Instant(
    name='Pulse of Murasa',
    cost=Cost(mana={"C":2, "G":1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types
        or 'land' in obj.types, c_zones=['yard'])],
    spell_effect= Pulse_of_Murasa_effect,
    rarity='uncommon'
)

# Rabid Bite {1}{G}
# Sorcery
# Target creature you control deals damage equal to its power to target creature
#  you don’t control.
def Rabid_Bite_effect(source_card):
    targets= source_card.get_targets()
    if len(targets)==2:
        self_target=source_card.get_targets()[0]
        opp_target=source_card.get_targets()[1]
        opp_target.take_damage(self_target.power, source=self_target, combat=False)

Rabid_Bite= Sorcery(
    name='Rabid_Bite',
    cost=Cost(mana={"C":1, "G":1}),
    targets=[Target(criteria= lambda source, obj: 'creature' in obj.types, c_opponent=False),
        Target(criteria= lambda source, obj: 'creature' in obj.types, c_own=False)],
    spell_effect= Rabid_Bite_effect,
    rarity='common'
)

# Season of Growth {1}{G}
# Enchantment
# Whenever a creature enters the battlefield under your control, scry 1.
# Whenever you cast a spell that targets a creature you control, draw a card.
Season_of_Growth= Enchantment(
    name='Season of Growth',
    cost=Cost(mana={'C':1,'G':1}),
    rarity='uncommon',
    triggered_abils=[
        Triggered_Ability(
            name='Season of Growth ETB scry',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'creature' in obj.types and
                obj.controller==source_abil.controller,
            abil_effect = lambda source_abil: source_abil.controller.scry(1)
        ),
        Triggered_Ability(
            name='Season of Growth on target draw',
            trigger_points=['on target'],
            trigger_condition= lambda source_abil, target_source, targeted_obj:
                target_source.controller==source_abil.controller and
                targeted_obj.controller==source_abil.controller and
                'creature' in targeted_obj.types and
                isinstance(target_source, Card),
            abil_effect = lambda source_abil: source_abil.controller.draw_card(1)
        ),
    ]
)


# Sedge Scorpion {G}
# Creature — Scorpion
# Deathtouch (Any amount of damage this deals to a creature is enough to destroy it.)
# 1/1

Sedge_Scorpion= Creature(
    name='Sedge Scorpion',
    cost=Cost(mana={"G":1}),
    power=1,
    toughness=1,
    subtypes=['scorpion'],
    keyword_static_abils=['deathtouch'],
    rarity='common'
)

# Shared Summons {3}{G}{G}
# Instant
# Search your library for up to two creature cards with different names, reveal \
# them, put them into your hand, then shuffle your library.

def Shared_Summons_select_effect(card):
    card.owner.lib.leave_zone(card)
    card.owner.hand.enter_zone(card)

def Shared_Summons_effect(source_card):
    selected1=source_card.controller.search_library(
        elig_condition= lambda card: 'creature' in card.types,
        select_effect= Shared_Summons_select_effect
    )
    source_card.controller.search_library(
        elig_condition= lambda card: 'creature' in card.types and card.name!=
            selected1.name,
        select_effect= Shared_Summons_select_effect
    )

Shared_Summons = Instant(
    name='Shared Summons',
    cost=Cost(mana={'C':3,'G':2}),
    rarity='rare',
    spell_effect= Shared_Summons_effect
)

# Shifting Ceratops {2}{G}{G}
# Creature — Dinosaur
# This spell can’t be countered.
# Protection from blue (This creature can’t be blocked, targeted, dealt damage,
# enchanted, or equipped by anything blue.)
# {G}: Shifting Ceratops gains your choice of reach, trample, or haste until end of turn.
# 5/4
def Shifting_Ceratops_effect(source_abil):
    selected= source_abil.controller.input_choose(['haste','reach','trample'],
        label='Shifting Ceratops ability select')
    source_abil.source.add_keyword(selected)
    source_abil.EOT_keywords.append(selected)

Shifting_Ceratops = Creature(
    name='Shifting Ceratops',
    subtypes=['dinosaur'],
    protection_effects=[Protection(condition=lambda obj: 'U' in obj.colors)],
    power=5,
    toughness=4,
    rarity='rare',
    keyword_static_abils=['uncounterable'],
    activated_abils=[
        Activated_Ability(
            name='Shifting Ceratops',
            cost=Cost(mana={'G':1}),
            abil_effect= Shifting_Ceratops_effect
        )
    ]
)

# Silverback Shaman {3}{G}{G}
# Creature — Ape Shaman
# Trample (This creature can deal excess combat damage to the player or
# planeswalker it’s attacking.)
# When Silverback Shaman dies, draw a card.
# 5/4
Silverback_Shaman = Creature(
    name='Silverback Shaman',
    subtypes=['ape','shaman'],
    power=5,
    toughness=4,
    rarity='common',
    keyword_static_abils=['trample'],
    triggered_abils=[
        Triggered_Ability(
            name='Silverback shaman dies abil',
            trigger_points=['dies'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.draw_card()
        )
    ]
)

# Thicket Crasher {3}{G}
# Creature — Elemental Rhino
# Trample (This creature can deal excess combat damage to the player or
# planeswalker it’s attacking.)
# Other Elementals you control have trample.
# 4/3
def Thicket_Crasher_effect(applied_obj,source_abil):
    applied_obj.add_keyword('trample')

def r_Thicket_Crasher_effect(applied_obj,source_abil):
    applied_obj.remove_keyword('trample')

Thicket_Crasher= Creature(
    name='Thicket Crasher',
    cost=Cost(mana={'C':3,"G":1}),
    power=4,
    toughness=3,
    subtypes=['elemental','rhino'],
    keyword_static_abils=['trample'],
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Thicket Crasher Pump effect",
            effect_condition= lambda applied_obj, source_abil: 'creature' in \
                applied_obj.types and 'elemental' in applied_obj.subtypes
                and applied_obj.controller == source_abil.controller,
            effect_func= Thicket_Crasher_effect,
            reverse_effect_func = r_Thicket_Crasher_effect
        )
    ],
    rarity='common'
)

# Thrashing Brontodon {1}{G}{G}
# Creature — Dinosaur
# {1}, Sacrifice Thrashing Brontodon: Destroy target artifact or enchantment.
# 3/4
Thrashing_Brontodon= Creature(
    name='Thrashing Brontodon',
    cost=Cost(mana={'C':1,"G":2}),
    power=3,
    toughness=4,
    subtypes=['dinosaur'],
    rarity='uncommon',
    activated_abils=[
        Activated_Ability(
            name='Thrashing Brontodon activated abil',
            cost=Cost(
                mana={'C':1},
                non_mana=[lambda source_abil: source_abil.source.sacrifice()]
            ),
            targets=[Target(criteria= lambda source, obj: 'artifact' in obj.types or
                'enchantment' in obj.types)],
            abil_effect= lambda source_abil: source_abil.get_targets().destroy(),
        )
    ]
)

# Veil of Summer {G}
# Instant
# Draw a card if an opponent has cast a blue or black spell this turn. Spells
# you control can’t be countered this turn. You and permanents you control gain
# hexproof from blue and from black until end of turn.

def EOTr_Veil_of_Summer_effect(obj):
    obj.protection_effects=[i for i in obj.protection_effects if i.name!='Veil of Summer protect effect']

def Veil_of_Summer_effect(source_card):
    if 'U' in source_card.controller.opponent.turn_spell_colors or \
        'B' in source_card.controller.opponent.turn_spell_colors:
        source_card.controller.draw_card()

    source_card.controller.add_keyword('all_uncounterable')
    source_card.controller.EOT_keywords.append('all_uncounterable')

    hexproof_eff = Protection(condition = lambda obj: 'B' in obj.colors or
        'U' in obj.colors, name='Veil of Summer protect effect', source=source_card,
        hexproof_from=True)
    for i in source_card.controller.field + [source_card.controller]:
        copy = deepcopy(hexproof_eff)
        copy.assign_source(i)
        copy.assign_ownership(source_card.controller)
        i.protection_effects.append(hexproof_eff)
        i.EOT_reverse_effects.append(EOTr_Veil_of_Summer_effect)


Veil_of_Summer = Instant(
    name='Veil of Summer',
    cost=Cost(mana={'G':1}),
    rarity='uncommon',
    spell_effect=Veil_of_Summer_effect
)

# Vivien, Arkbow Ranger {1}{G}{G}{G}
# Legendary Planeswalker — Vivien
# +1: Distribute two +1/+1 counters among up to two target creatures. They gain trample until end of turn.
# −3: Target creature you control deals damage equal to its power to target creature or planeswalker.
# −5: You may choose a creature card you own from outside the game, reveal it, and put it into your hand.
# Loyalty: 4

def Vivien_Arkbow_Ranger_plus1_effect(source_abil):
    targets=source_abil.get_targets()
    targets=[i for i in targets if i!=None]
    if len(targets)==1:
        targets[0].add_keyword('trample')
        targets[0].EOT_keywords.append('trample')
        for _ in range(2):
            deepcopy(plus1_plus1_counter).attach_to(targets[0])

    # handle different split counters possibilities
    if len(targets)==2:
        for i in targets:
            i.add_keyword('trample')
            i.EOT_keywords.append('trample')
            deepcopy(plus1_plus1_counter).attach_to(i)


def Vivien_Arkbow_Ranger_minus3_effect(source_abil):
    targets = source_abil.get_targets()
    if len(targets) == 2:
        self_target=source_abil.get_targets()[0]
        opp_target=source_abil.get_targets()[1]
        opp_target.take_damage(self_target.power, source=self_target, combat=False)

def Vivien_Arkbow_Ranger_minus5_effect(source_abil):
    selected = source_abil.controller.input_choose(source_abil.controller.sideboard,
        permit_empty_list=True)
    if selected != None:
        source_abil.controller.sideboard.leave_zone(selected)
        source_abil.controller.hand.enter_zone(selected)

Vivien_Arkbow_Ranger = Planeswalker(
    name='Vivien, Arkbow Ranger',
    subtypes=['vivien'],
    cost=Cost(mana={'C':1,'G':3}),
    loyalty=4,
    rarity='mythic',
    activated_abils=[
        Activated_Ability(
            name='Vivien, Arkbow Ranger +1 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(1)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False]
            ),
            targets=[
                Target(criteria= lambda source, obj: 'creature' in obj.types, c_different=True,
                    c_required=False),
                Target(criteria= lambda source, obj: 'creature' in obj.types, c_different=True,
                    c_required=False),
            ],
            abil_effect= Vivien_Arkbow_Ranger_plus1_effect,
            flash=False
        ),
        Activated_Ability(
            name='Vivien, Arkbow Ranger -3 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(-3)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False
                    and source_abil.source.loyalty>=3]
            ),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types, c_opponent=False),
                Target(criteria= lambda source, obj: 'creature' in obj.types or 'planeswalker' in obj.types)],
            abil_effect= Vivien_Arkbow_Ranger_minus3_effect,
            flash=False
        ),
        Activated_Ability(
            name='Vivien, Arkbow Ranger -5 ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.change_loyalty(-5)],
                non_mana_check=[lambda source_abil: source_abil.source.activated_loyalty_abil==False
                    and source_abil.source.loyalty>=5]
            ),
            abil_effect= Vivien_Arkbow_Ranger_minus5_effect,
            flash=False
        ),
    ]
)

# Voracious Hydra {X}{G}{G}
# Creature — Hydra
# Trample
# Voracious Hydra enters the battlefield with X +1/+1 counters on it.
# When Voracious Hydra enters the battlefield, choose one —
# • Double the number of +1/+1 counters on Voracious Hydra.
# • Voracious Hydra fights target creature you don’t control.
# 0/1

def Voracious_Hydra_ETB(source_abil):
    for _ in range(source_abil.source.cost[0].x_value):
        deepcopy(plus1_plus1_counter).attach_to(source_abil.source)

def Voracious_Hydra_ETB_effect(source_abil):
    if source_abil.selected_mode==1:
        n_counters= len([i for i in source_abil.source.attached_objs if
            i.name=='+1/+1 counter'])
        for _ in range(n_counters):
            deepcopy(plus1_plus1_counter).attach_to(source_abil.source)
    if source_abil.selected_mode==2:
        target=source_abil.get_targets()
        source_abil.source.fight(target)

Voracious_Hydra = Creature(
    name='Voracious Hydra',
    cost=Cost(mana={'G':2}, mana_x_value=True),
    power=0,
    toughness=1,
    subtypes=['hydra'],
    rarity='rare',
    keyword_static_abils=['trample'],
    nonkeyword_static_abils=[
        Local_Static_Effect(
            name="Voracious Hydra get counters ETB",
            effect_func= Voracious_Hydra_ETB,
            reverse_effect_func= lambda source_abil: True,
            effect_condition = lambda source_abil: source_abil.source.ETB_static_check==True
        )
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Voracious Hydra ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: source_abil.source==obj,
            moded=True,
            n_modes=2,
            mode_labels=['Double Counters','Fight'],
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,
                c_own=False, mode_linked=True,mode_num=2)],
            abil_effect= Voracious_Hydra_ETB_effect
        )
    ]
)

# Vorstclaw {4}{G}{G}
# Creature — Elemental Horror
# 7/7
Vorstclaw= Creature(
    name='Vorstclaw',
    cost=Cost(mana={"C":4, "G":2}),
    power=7,
    toughness=7,
    subtypes=['elemental','horror'],
    rarity='common'
)


# Wakeroot Elemental {4}{G}{G}
# Creature — Elemental
# {G}{G}{G}{G}{G}: Untap target land you control. It becomes a 5/5 Elemental
# creature with haste. It’s still a land. (This effect lasts as long as that land
# remains on the battlefield.)
# 5/5

def Wakeroot_Elemental_effect(source_abil):
    target=source_abil.get_targets()
    target.untap()
    target.add_keyword('haste')
    target.types = target.types + ['creature']
    target.subtypes = target.subtypes + ['elemental']
    target.power=5
    target.toughness=5

Wakeroot_Elemental= Creature(
    name='Wakeroot Elemental',
    cost=Cost(mana={"C":4, "G":2}),
    power=5,
    toughness=5,
    subtypes=['elemental'],
    rarity='rare',
    activated_abils=[
        Activated_Ability(
            name='Wakeroot Elemental activated abil',
            cost=Cost(mana={'G':5}),
            targets=[Target(criteria= lambda source, obj: 'land' in obj.types,
                c_opponent=False)],
            abil_effect= Wakeroot_Elemental_effect
        )
    ]
)


# Wolfkin Bond {4}{G}
# Enchantment — Aura
# Enchant creature
# When Wolfkin Bond enters the battlefield, create a 2/2 green Wolf creature token.
# Enchanted creature gets +2/+2.
def Wolfkin_Bond_effect(attached_to):
    attached_to.change_power(2)
    attached_to.change_toughness(2)
def r_Wolfkin_Bond_effect(attached_to):
    attached_to.change_power(-2)
    attached_to.change_toughness(-2)

Wolfkin_Bond= Aura(
    name='Wolfkin Bond',
    cost=Cost(mana={'C':4,'G':1}),
    aura_static_effect=Attached_Effect(
        name="Wolfkin Bond pump effect",
        effect_func=Wolfkin_Bond_effect,
        reverse_effect_func=r_Wolfkin_Bond_effect
    ),
    triggered_abils=[
        Triggered_Ability(
            name='Wolfkin Bond ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.source.controller.create_token(
                Creature_Token(
                    name="Wolf 2/2",
                    colors=['G'],
                    types=['creature'],
                    subtypes=['wolf'],
                    power=2,
                    toughness=2
                )
            )
        )
    ],
    rarity='common'
)


# Wolfrider's Saddle {3}{G}
# Artifact — Equipment
# When Wolfrider’s Saddle enters the battlefield, create a 2/2 green Wolf creature
# token, then attach Wolfrider’s Saddle to it.
# Equipped creature gets +1/+1 and can’t be blocked by more than one creature.
# Equip {3} ({3}: Attach to target creature you control. Equip only as a sorcery.)
def Wolfriders_Saddle_equip(attached_to):
    attached_to.change_power(1)
    attached_to.change_toughness(1)
    attached_to.add_keyword('cant_be_double_blocked')

def r_Wolfriders_Saddle_equip(attached_to):
    attached_to.change_power(-1)
    attached_to.change_toughness(-1)
    attached_to.remove_keyword('cant_be_double_blocked')

def Wolfriders_Saddle_ETB_effect(source_abil):
    token=Creature_Token(
        name="Wolf 2/2",
        colors=['G'],
        types=['creature'],
        subtypes=['wolf'],
        power=2,
        toughness=2
    )
    source_abil.source.attach_to(token)
    source_abil.source.controller.create_token(token)

Wolfriders_Saddle=Equipment(
    name="Wolfriders Saddle",
    cost=Cost(mana={'C':3,'G':1}),
    equip_cost=Cost(mana={'C':3}),
    equip_static_effect=Attached_Effect(
        name='Wolfriders Saddle Pump',
        effect_func=Wolfriders_Saddle_equip,
        reverse_effect_func=r_Wolfriders_Saddle_equip
    ),
    triggered_abils=[
        Triggered_Ability(
            name='Wolfriders Saddle ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Wolfriders_Saddle_ETB_effect
        )
    ],
    rarity='uncommon'
)


# Woodland Champion {1}{G}
# Creature — Elf Scout
# Whenever one or more tokens enter the battlefield under your control, put
# that many +1/+1 counters on Woodland Champion.
# 2/2

Woodland_Champion= Creature(
    name='Woodland Champion',
    cost=Cost(mana={'C':1,'G':1}),
    subtypes=['elf','scout'],
    power=2,
    toughness=2,
    rarity='uncommon',
    triggered_abils=[
        Triggered_Ability(
            name='Woodland Champion ability',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'token' in obj.types,
            abil_effect=  lambda source_abil: deepcopy(plus1_plus1_counter).attach_to(
                source_abil.source)
        )
    ]
)

# Gold
# Corpse Knight {W}{B}
# Creature — Zombie Knight
#
# Whenever another creature enters the battlefield under your control, each opponent loses 1 life.
#
# 2/2

Corpse_Knight= Creature(
    name='Corpse Knight',
    cost=Cost(mana={'W':1,'B':1}),
    power=2,
    toughness=2,
    subtypes=['zombie','knight'],
    rarity='uncommon',
    triggered_abils=[
        Triggered_Ability(
            name='Corpse Knight triggered abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'creature' in obj.types
                and obj!= source_abil.source,
            abil_effect=  lambda source_abil: source_abil.controller.opponent.change_life(-1)
        )
    ]
)


# Creeping Trailblazer {R}{G}
# Creature — Elemental
#
# Other Elementals you control get +1/+0.
#
# {2}{R}{G}: Creeping Trailblazer gets +1/+1 until end of turn for each Elemental you control.
#
# 2/2

def Creeping_Trailblazer_activated_effect(source_abil):
    elems = len([i for i in source_abil.controller.field if 'elemental' in i.subtypes])
    source_abil.source.change_power(elems)
    source_abil.source.change_toughness(elems)
    source_abil.source.EOT_power_pump+=elems
    source_abil.source.EOT_toughness_pump+=elems


Creeping_Trailblazer= Creature(
    name='Creeping Trailblazer',
    subtypes=['elemental'],
    cost=Cost(mana={'R':1,'G':1}),
    power=2,
    toughness=2,
    rarity='uncommon',
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Creeping Trailblazer Pump effect",
            effect_condition= lambda applied_obj, source_abil: 'creature' in \
                applied_obj.types and 'elemental' in applied_obj.subtypes and
                source_abil.source!=applied_obj and
                applied_obj.controller == source_abil.controller,
            effect_func= lambda applied_obj, source_abil: applied_obj.change_power(1),
            reverse_effect_func = lambda applied_obj, source_abil: applied_obj.change_power(-1),
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Creeping Trailblazer activated abil',
            cost=Cost(mana={'C':2, 'R':1, 'G':1}),
            abil_effect= Creeping_Trailblazer_activated_effect
        )
    ]
)

# Empyrean Eagle {1}{W}{U}
# Creature — Bird Spirit
#
# Flying
#
# Other creatures you control with flying get +1/+1.
#
# 2/3

def Empyrean_Eagle_pump_effect(applied_obj,source_abil):
    applied_obj.change_power(1)
    applied_obj.change_toughness(1)

def r_Empyrean_Eagle_pump_effect(applied_obj,source_abil):
    applied_obj.change_power(-1)
    applied_obj.change_toughness(-1)

Empyrean_Eagle= Creature(
    name='Empyrean Eagle',
    cost=Cost(mana={'C':1,'W':1,'U':1}),
    subtypes=['bird','spirit'],
    power=2,
    toughness=3,
    keyword_static_abils=['flying'],
    rarity='uncommon',
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Empyrean Pump effect",
            effect_condition= lambda applied_obj, source_abil: 'creature' in \
                applied_obj.types and applied_obj.check_keyword('flying') and
                source_abil.source!=applied_obj and
                applied_obj.controller == source_abil.controller,
            effect_func= Empyrean_Eagle_pump_effect,
            reverse_effect_func = r_Empyrean_Eagle_pump_effect,
        )
    ],
)

# Ironroot Warlord {1}{G}{W}
# Creature — Treefolk Soldier
#
# Ironroot Warlord’s power is equal to the number of creatures you control.
#
# {3}{G}{W}: Create a 1/1 white Soldier creature token.
#
# */5

def Ironroot_Warlord_set_power_effect(source_abil):
    n_creatures= len([i for i in source_abil.controller.field if 'creature' in i.types])
    source_abil.source.power=n_creatures

Ironroot_Warlord=Creature(
    name='Ironroot Warlord',
    cost=Cost(mana={'G':1,'W':1,'C':1}),
    subtypes=['treefolk','soldier'],
    power=0,
    toughness=5,
    rarity='uncommon',
    activated_abils=[
        Activated_Ability(
            name='Ironroot Warlord activated abil',
            cost=Cost(mana={'G':1,'W':1,'C':3}),
            abil_effect= lambda source_abil: source_abil.controller.create_token(
                Creature_Token(
                    name="Soldier 1/1",
                    colors=['W'],
                    types=['creature'],
                    subtypes=['Soldier'],
                    power=1,
                    toughness=1,
                )
            )
        )
    ],
    nonkeyword_static_abils= [
        Local_Static_Effect(
            name='Ironroot Warlord set power effect',
            effect_func = Ironroot_Warlord_set_power_effect,
            variable_value=True,
            reverse_effect_func = None,
            effect_condition = lambda source_abil: True
        )
    ],
)

# Kaalia, Zenith Seeker {R}{W}{B}
# Legendary Creature — Human Cleric
#
# Flying, vigilance
#
# When Kaalia, Zenith Seeker enters the battlefield, look at the top six cards of
# your library. You may reveal an Angel card, a Demon card, and/or a Dragon card
# from among them and put them into your hand. Put the rest on the bottom of your
# library in a random order.
#
# 3/3

def Kaalia_Zenith_Seeker_effect(source_abil):
    top_cards = source_abil.controller.lib[0:6]
    selected_list = []
    for type in ['angel','dragon','demon']:
        cands = [i for i in top_cards if type in i.subtypes]
        selected = source_abil.controller.input_choose(cands,
            label='Kaalia_Zenith_Seeker abil select for type: ' + type, permit_empty_list=True)
        selected_list.append(selected)

    for selected in selected_list:
        if selected != None:
            source_abil.controller.lib.leave_zone(selected)
            source_abil.controller.hand.enter_zone(selected)
            source_abil.controller.reveal_cards(selected, zone='hand')

    non_selected= [i for i in top_cards if i not in selected_list]
    random.shuffle(non_selected)
    for i in non_selected:
        source_abil.controller.lib.remove(i)
        source_abil.controller.lib.append(i)

Kaalia_Zenith_Seeker = Creature(
    name='Kaalia, Zenith Seeker',
    cost=Cost(mana={'R':1,'W':1,'B':1}),
    types=['legendary','creature'],
    power=3,
    toughness=3,
    rarity='mythic',
    keyword_static_abils=['flying','vigilance'],
    triggered_abils=[
        Triggered_Ability(
            name='Kaalia, Zenith Seeker ETB',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Kaalia_Zenith_Seeker_effect
        )
    ]
)


# Kethis, the Hidden Hand {W}{B}{G}
# Legendary Creature — Elf Advisor
#
# Legendary spells you cast cost {1} less to cast.
#
# Exile two legendary cards from your graveyard: Until end of turn, each legendary
# card in your graveyard gains “You may play this card from your graveyard.”
#
# 3/4

def Kethis_the_Hidden_Hand_cost_reduce(applied_obj, source_abil):
    source_abil.source.controller.cost_mods.append(
        Cost_Modification(
            name='Kethis the Hidden Hand cost reduction obj',
            cost_mod={'C':-1},
            cost_mod_source=source_abil.source,
            mod_condition= lambda cost_obj, cost_mod_source: \
                isinstance(cost_obj.source, Card) and 'legendary' in cost_obj.source.types
        )
    )

def r_Kethis_the_Hidden_Hand_cost_reduce(applied_obj, source_abil):
    abil_instances=[i for i in source_abil.controller.cost_mods if i.name==
        'Kethis the Hidden Hand cost reduction obj']
    if abil_instances != []:
        source_abil.controller.cost_mods.remove(abil_instances[0])

def Kethis_activated_cost(source_abil):
    legends = [i for i in source_abil.controller.yard if 'legendary' in i.types]
    for _ in range(2):
        selected = source_abil.controller.input_choose(legends, label='exile for Kethis')
        selected.exile()

def Kethis_activated_cost_check(source_abil):
    return(len([i for i in source_abil.controller.yard if 'legendary' in i.types])>=2)

def EOTr_Kethis_activated_effect(card):
    card.remove_keyword('cast_from_yard')

def Kethis_activated_effect(source_abil):
    legends = [i for i in source_abil.controller.yard if 'legendary' in i.types]
    for i in legends:
        i.add_keyword('cast_from_yard')
        source_abil.controller.check_yard_for_cast=True
        source_abil.controller.EOT_effects_cleanup['objs'].append(i)
        source_abil.controller.EOT_effects_cleanup['effects'].append(EOTr_Kethis_activated_effect)


Kethis_the_Hidden_Hand=Creature(
    name='Kethis, the Hidden Hand',
    cost=Cost(mana={'W':1,'B':1,'G':1}),
    types=['legendary','creature'],
    subtypes=['elf','advisor'],
    power=3,
    toughness=4,
    rarity='mythic',
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Kethis the Hidden Hand cost reduction",
            own_apply_zones=[], opp_apply_zones=[],
            players='self',
            effect_func= Kethis_the_Hidden_Hand_cost_reduce,
            reverse_effect_func= r_Kethis_the_Hidden_Hand_cost_reduce,
        )
    ],
    activated_abils=[
        Activated_Ability(
            name="Kethis the Hidden Hand activated abil",
            cost=Cost(
                non_mana= [Kethis_activated_cost],
                non_mana_check= [Kethis_activated_cost_check],
            ),
            abil_effect= Kethis_activated_effect
        )
    ]
)


# Kykar, Wind's Fury {1}{U}{R}{W}
# Legendary Creature — Bird Wizard
#
# Flying
#
# Whenever you cast a noncreature spell, create a 1/1 white Spirit creature token with flying.
#
# Sacrifice a Spirit: Add {R}.
#
# 3/3
Kykar_Winds_Fury=Creature(
    name='Kykar, Winds Fury',
    cost=Cost(mana={'C':1,'U':1,'R':1,'W':1}),
    types=['legendary','creature'],
    subtypes=['bird','wizard'],
    power=3,
    toughness=3,
    rarity='mythic',
    keyword_static_abils=['flying'],
    mana_source=True,
    activated_abils=[
        Activated_Ability(
            name='Kykar, Winds Fury mana abil',
            cost=Cost(
                non_mana= [lambda source_abil: source_abil.controller.sacrifice_permanent(
                    subtypes=['spirit'])],
                non_mana_check= [lambda source_abil: len([i for i in source_abil.controller.field
                        if 'spirit' in i.subtypes])>0]
            ),
            potential_mana=Potential_Mana({'R':1}, condition=lambda source:
                len([i for i in source.controller.field if 'spirit' in i.subtypes])>0),
            abil_effect = lambda source_abil: source_abil.controller.add_mana('R')
        )
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Kykar, Winds Fury triggered abil',
            trigger_points=['cast spell'],
            trigger_condition=lambda source_abil, casted_spell, **kwargs:
                'creature' not in casted_spell.types,
            abil_effect= lambda source_abil: source_abil.source.controller.create_token(
                Creature_Token(
                    name="Spirit 1/1 Flying",
                    colors=['W'],
                    types=['creature'],
                    subtypes=['Spirit'],
                    power=1,
                    toughness=1,
                    keyword_static_abils=['flying']
                )
            )
        )
    ]
)


# Lightning Stormkin {U}{R}
# Creature — Elemental Wizard
#
# Flying
#
# Haste (This creature can attack and {T} as soon as it comes under your control.)
#
# 2/2
Lightning_Stormkin= Creature(
    name='Lightning Stormkin',
    cost=Cost(mana={"U":1, "R":1}),
    power=2,
    toughness=2,
    subtypes=['elemental','wizard'],
    rarity='uncommon',
    keyword_static_abils=['haste','flying']
)

# Moldervine Reclamation {3}{B}{G}
# Enchantment
#
# Whenever a creature you control dies, you gain 1 life and draw a card.

def Moldervine_Reclamation_effect(source_abil):
    source_abil.controller.draw_card()
    source_abil.controller.change_life(1)

Moldervine_Reclamation=Enchantment(
    name='Moldervine Reclaimation',
    cost=Cost(mana={'C':3,'B':1,'G':1}),
    triggered_abils=[
        Triggered_Ability(
            name='Moldervine Reclamation ability',
            trigger_points=['dies'],
            trigger_condition=lambda source_abil, obj, **kwargs:
                'creature' in obj.types and obj.controller==source_abil.controller,
            abil_effect= Moldervine_Reclamation_effect
        )
    ],
    rarity='uncommon'
)



# Ogre Siegebreaker {2}{B}{R}
# Creature — Ogre Berserker
#
# {2}{B}{R}: Destroy target creature that was dealt damage this turn.
#
# 4/3

Ogre_Siegebreaker=Creature(
    name='Ogre Siegebreaker',
    cost=Cost(mana={'C':2,'B':1,'R':1}),
    subtypes=['ogre','berserker'],
    power=4,
    toughness=3,
    rarity='uncommon',
    activated_abils=[
        Activated_Ability(
            name='Ogre Siegebreaker abil',
            cost=Cost(mana={'C':2,'B':1,'R':1}),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types
                and obj.damage_received>0)],
            abil_effect= lambda source_abil: source_abil.get_targets().destroy()
        )
    ]
)

# Omnath, Locus of the Roil {1}{G}{U}{R}
# Legendary Creature — Elemental
#
# When Omnath, Locus of the Roil enters the battlefield, it deals damage to any
# target equal to the number of Elementals you control.
#
# Whenever a land enters the battlefield under your control, put a +1/+1 counter
# on target Elemental you control. If you control eight or more lands, draw a card.
#
# 3/3
def Omnath_ETB_effect(source_abil):
    elems = len([i for i in source_abil.controller.field if 'elemental' in i.subtypes])
    target=source_abil.get_targets()
    target.take_damage(elems, source=source_abil.source, combat=False)

def Omnath_land_ETB_effect(source_abil):
    deepcopy(plus1_plus1_counter).attach_to(source_abil.get_targets())
    lands = len([i for i in source_abil.controller.field if 'land' in i.types])
    if lands>=8:
        source_abil.controller.draw_card()

Omnath_Locus_of_the_Roil = Creature(
    name= "Omnath, Locus of the Roil",
    cost=Cost(mana={'C':1,'G':1,'U':1,'R':1}),
    types=['legendary','creature'],
    subtypes=['elemental'],
    power=3,
    toughness=3,
    rarity='mythic',
    triggered_abils=[
        Triggered_Ability(
            name='Omnath ETB effect',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types or
                'planeswalker' in obj.types, c_players='both')],
            abil_effect=Omnath_ETB_effect
        ),
        Triggered_Ability(
            name='Omnath land ETB effect',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'land' in obj.types and
                obj.controller==source_abil.controller,
            targets=[Target(criteria= lambda source, obj: 'elemental' in obj.subtypes)],
            abil_effect= Omnath_land_ETB_effect
        )
    ]
)


#
# Risen Reef {1}{G}{U}
# Creature — Elemental
#
# Whenever Risen Reef or another Elemental enters the battlefield under your control,
# look at the top card of your library. If it’s a land card, you may put it onto
# the battlefield tapped. If you don’t put the card onto the battlefield, put it into your hand.
#
# 1/1

def Risen_Reef_ETB_effect(source_abil):
    top_card = source_abil.controller.lib[0]
    source_abil.controller.lib.leave_zone(top_card)
    if 'land' in top_card.types and source_abil.controller.input_bool('Risen Reef land ETB'):
        source_abil.controller.field.enter_zone(top_card)
        top_card.tap(for_cost=False)
    else:
        source_abil.controller.hand.enter_zone(top_card)

Risen_Reef= Creature(
    name='Risen Reef',
    cost=Cost(mana={'C':1,'G':1,'U':1}),
    subtypes=['elemental'],
    power=1,
    toughness=1,
    rarity='uncommon',
    triggered_abils=[
        Triggered_Ability(
            name='Risen Reef elemental ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: 'elemental' in obj.types,
            abil_effect= Risen_Reef_ETB_effect
        )
    ]
)


# Skyknight Vanguard {R}{W}
# Creature — Human Knight
#
# Flying
#
# Whenever Skyknight Vanguard attacks, create a 1/1 white Soldier creature token
# that’s tapped and attacking.
#
# 1/2
def Skyknight_Vanguard_effect(source_abil):
    token = Creature_Token(
        name="Soldier 1/1",
        colors=['W'],
        types=['creature'],
        subtypes=['Soldier'],
        power=1,
        toughness=1,
    )
    source_abil.controller.create_token(token, is_attacking=True, is_tapped=True)

Skyknight_Vanguard=Creature(
    name='Skyknight Vanguard',
    cost=Cost(mana={'R':1,'W':1}),
    subtypes=['human','knight'],
    power=1,
    toughness=1,
    rarity='uncommon',
    keyword_static_abils=['flying'],
    triggered_abils=[
        Triggered_Ability(
            name='Skyknight Vanguard attack trigger',
            trigger_points=['on attack'],
            trigger_condition=lambda source_abil, obj, **kwargs:
                source_abil.source==obj,
            abil_effect=Skyknight_Vanguard_effect
        )
    ]
)

# Tomebound Lich {1}{U}{B}
# Creature — Zombie Wizard
#
# Deathtouch (Any amount of damage this deals to a creature is enough to destroy it.)
#
# Lifelink (Damage dealt by this creature also causes you to gain that much life.)
#
# Whenever Tomebound Lich enters the battlefield or deals combat damage to a player,
# draw a card, then discard a card.
#
# 1/3

Tomebound_Lich = Creature(
    name='Tomebound Lich',
    cost=Cost(mana={'C':1,'U':1,'B':1}),
    subtypes=['zombie','wizard'],
    power=1,
    toughness=3,
    rarity='uncommon',
    keyword_static_abils=['deathtouch','lifelink'],
    triggered_abils=[
        Triggered_Ability(
            name='Tomebound Lich on combat damage to player',
            trigger_points=['combat damage dealt'],
            trigger_condition= lambda source_abil, source, receiver, num, **kwargs:
                receiver == source.controller.opponent and source==source_abil.source,
            abil_effect = lambda source_abil: source_abil.controller.loot()
        ),
        Triggered_Ability(
            name='Tomebound Lich ETB effect',
            trigger_points=['enter field'],
            trigger_condition= lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect = lambda source_abil: source_abil.controller.loot()
        )
    ]
)

# Yarok, the Desecrated {2}{B}{G}{U}
# Legendary Creature — Elemental Horror
#
# Deathtouch, lifelink
#
# If a permanent entering the battlefield causes a triggered ability of a permanent
# you control to trigger, that ability triggers an additional time.
#
# 3/5

# TODO: fix yarok the desecrated abil
def Yarok_the_Desecrated_effect(source_abil):
    # check for effect instances generated by triggered abils with trigger points caused by obj etb'ing
    # copies=[]
    # for obj in source_abil.controller.game.stack:
    #     if 'triggered_abil' in obj.types and 'enter field' in obj.trigger_points \
    #     and source_abil.last_known_info != None \
    #     and obj.trigger_condition(source_abil = obj.source, obj = source_abil.last_known_info) \
    #     and obj != source_abil:
    #         copies.append(obj)
    # for obj in copies:
    #     obj.make_copy(choose_new_targets=False)
    pass

Yarok_the_Desecrated= Creature(
    name='Yarok, the Desecrated',
    cost=Cost(mana={'C':2,'B':1,'G':1,'U':1}),
    types=['legendary','creature'],
    subtypes=['elemental','warrior'],
    power=3,
    toughness=5,
    rarity='mythic',
    keyword_static_abils=['deathtouch','lifelink'],
    triggered_abils=[
        Triggered_Ability(
            name= 'Yarok the Desecrated double ETB trigger',
            trigger_points=['enter field'],
            trigger_condition= lambda source_abil, obj, **kwargs: obj.controller==
                source_abil.controller,
            lki_func= lambda source_abil, effect_kwargs: effect_kwargs['obj'],
            abil_effect= Yarok_the_Desecrated_effect
        )
    ]
)

# Artifacts

# Anvilwrought Raptor {4}
# Artifact Creature — Bird
#
# Flying
#
# First strike (This creature deals combat damage before creatures without first strike.)
#
# 2/1

Anvilwrought_Raptor = Artifact(
    name='Anvilwrought_Raptor',
    cost=Cost(mana={'C':4}),
    types=['artifact','creature'],
    subtypes=['bird'],
    power=2,
    toughness=1,
    rarity='common',
    keyword_static_abils=['flying', 'first strike']
)

# Bag of Holding {1}
# Artifact
#
# Whenever you discard a card, exile that card from your graveyard.
#
# {2}, {T}: Draw a card, then discard a card.
#
# {4}, {T}, Sacrifice Bag of Holding: Return all cards exiled with Bag of Holding
# to their owner’s hand.

def Bag_of_Holding_exile(source_abil):
    source_abil.last_known_info.exile()
    # keep track of what's been exiled this way
    if source_abil.source.last_known_info==None:
        source_abil.source.last_known_info=[source_abil.last_known_info]
    else:
        source_abil.source.last_known_info.append(source_abil.last_known_info)

def Bag_of_Holding_retrieve_effect(source_abil):
    if source_abil.source.last_known_info != None:
        for i in source_abil.source.last_known_info:
            if i.zone.type == 'exile':
                i.zone.leave_zone(i)
                i.owner.hand.enter_zone(i)

Bag_of_Holding = Artifact(
    name='Bag of Holding',
    cost=Cost(mana={'C':1}),
    rarity='rare',
    triggered_abils=[
        Triggered_Ability(
            name='Bag of Holding exile discards effect',
            trigger_points=['discard'],
            trigger_condition= lambda source_abil, discarded_obj, **kwargs:
                discarded_obj.owner == source_abil.controller,
            lki_func= lambda source_abil, effect_kwargs: effect_kwargs['discarded_obj'],
            abil_effect = Bag_of_Holding_exile
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Bag of Holding loot abil',
            cost=Cost(
                mana={'C':2},
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect = lambda source_abil: source_abil.controller.loot()
        ),
        Activated_Ability(
            name='Bag of Holding retrieve from exile abil',
            cost=Cost(
                mana={'C':4},
                non_mana=[lambda source_abil: source_abil.source.tap(),
                    lambda source_abil: source_abil.source.sacrifice()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect = Bag_of_Holding_retrieve_effect
        )
    ]
)


# Colossus Hammer {1}
# Artifact — Equipment
#
# Equipped creature gets +10/+10 and loses flying.
#
# Equip {8} ({8}: Attach to target creature you control. Equip only as a sorcery.)

def Colossus_Hammer_equip(attached_to):
    attached_to.change_power(10)
    attached_to.change_toughness(10)
    attached_to.add_keyword('loses_flying')

def r_Colossus_Hammer_equip(attached_to):
    attached_to.change_power(-10)
    attached_to.change_toughness(-10)
    attached_to.remove_keyword('loses_flying')

Colossus_Hammer = Equipment(
    name='Colossus Hammer',
    cost=Cost(mana={'C':1}),
    equip_cost=Cost(mana={'C':8}),
    equip_static_effect=Attached_Effect(
        name='Colossus Hammer equip effect',
        effect_func=Colossus_Hammer_equip,
        reverse_effect_func=r_Colossus_Hammer_equip
    ),
    rarity='uncommon'
)

# Diamond Knight {3}
# Artifact Creature — Knight
#
# Vigilance (Attacking doesn’t cause this creature to tap.)
#
# As Diamond Knight enters the battlefield, choose a color.
#
# Whenever you cast a spell of the chosen color, put a +1/+1 counter on Diamond Knight.
#
# 1/1
def Diamond_Knight_ETB_effect(source_abil):
    source_abil.source.last_known_info=source_abil.controller.input_choose(
        ['W','U','B','R','G'], label='Diamond Knight ETB color choice')

Diamond_Knight = Artifact(
    name='Diamond Knight',
    types=['artifact','creature'],
    subtypes=['knight'],
    power=1,
    toughness=1,
    rarity='uncommon',
    keyword_static_abils=['vigilance'],
    nonkeyword_static_abils=[
        Local_Static_Effect(
            name="Diamond Knight ETB",
            effect_func= Diamond_Knight_ETB_effect,
            reverse_effect_func= lambda source_abil: True,
            effect_condition = lambda source_abil: source_abil.source.ETB_static_check==True
        )
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Diamond Knight cast spell abil',
            trigger_points=['cast spell'],
            trigger_condition = lambda source_abil, casted_spell, **kwargs:
                any([c == source_abil.source.last_known_info for c in
                casted_spell.colors]),
            abil_effect= lambda source_abil:
                deepcopy(plus1_plus1_counter).attach_to(source_abil.source)
        )
    ]
)


# Diviner's Lockbox {4}
# Artifact
#
# {1}, {T}: Choose a card name, then reveal the top card of your library. If that
# card has the chosen name, sacrifice Diviner’s Lockbox and draw three cards.
# Activate this ability only any time you could cast a sorcery.

def Diviners_Lockbox_effect(source_abil):
    names = list(set([i.name for i in source_abil.controller.lib]))
    selected= source_abil.controller.input_choose(names, label='Diviners Lockbox name choice')
    source_abil.controller.reveal_cards(source_abil.controller.lib[0])
    if source_abil.controller.lib[0].name == selected:
        source_abil.source.sacrifice()
        source_abil.controller.draw_card(3)

Diviners_Lockbox = Artifact(
    name="Diviner's Lockbox",
    cost=Cost(mana={'C':4}),
    rarity='uncommon',
    activated_abils=[
        Activated_Ability(
            name="Diviner's Lockbox abil",
            cost=Cost(
                mana={'C':1},
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            flash=False,
            abil_effect=Diviners_Lockbox_effect
        )
    ]
)

# Golos, Tireless Pilgrim {5}
# Legendary Artifact Creature — Scout
#
# When Golos, Tireless Pilgrim enters the battlefield, you may search your library
# for a land card, put that card onto the battlefield tapped, then shuffle your library.
#
# {2}{W}{U}{B}{R}{G}: Exile the top three cards of your library. You may play
#  them this turn without paying their mana costs.
#
# 3/5
def Golos_ETB_search_land_select_effect(card):
    card.owner.lib.leave_zone(card)
    card.owner.field.enter_zone(card)
    card.tap(for_cost=False)

def Golos_ETB_search_land(source_abil):
    player.search_library(
        elig_condition= lambda card: 'land' in card.types,
        select_effect= Golos_ETB_search_land_select_effect,
        shuffle=True
    )

def Golos_exile_cast_effect(source_abil):
    for card in source_abil.controller.lib[0:2]:
        card.exile()
        card.add_keyword('cast_from_exile')
        source_abil.controller.EOT_effects_cleanup['objs'].append(obj)
        source_abil.controller.EOT_effects_cleanup['effects'].append(lambda card: card.remove_keyword('cast_from_exile'))
    source_abil.controller.check_exile_for_cast=True

Golos_Tireless_Pilgrim = Artifact(
    name='Golos, Tireless Pilgrim',
    cost=Cost(mana={'C':5}),
    types=['legendary','artifact','creature'],
    subtypes=['scout'],
    power=3,
    toughness=5,
    rarity='rare',
    triggered_abils=[
        Triggered_Ability(
            name='Golos ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect=Golos_ETB_search_land
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Golos activated abil',
            cost=Cost(mana={'C':2, 'W':1, 'U':1, 'B':1, 'R':1,'G':1}),
            abil_effect= Golos_exile_cast_effect
        )
    ]
)


#=========================Need to complete Grafdigger==============================

# Grafdigger's Cage {1}
# Artifact
#
# Creature cards in graveyards and libraries can’t enter the battlefield.
#
# Players can’t cast spells from graveyards or libraries.

Grafdiggers_Cage = Artifact(
    name="Grafdigger's Cage",
    cost=Cost(mana={'C':1}),
    rarity='rare',
    nonkeyword_static_abils=[]
)

# Heart-Piercer Bow {2}
# Artifact — Equipment
#
# Whenever equipped creature attacks, Heart-Piercer Bow deals 1 damage to target creature defending player controls.
#
# Equip {1} ({1}: Attach to target creature you control. Equip only as a sorcery.)

Heartpiercer_Bow = Equipment(
    name='Heartpiercer Bow',
    cost=Cost(mana={'C':2}),
    equip_cost=Cost(mana={'C':1}),
    equip_static_effect=Attached_Effect(
        name='Heartpiercer Bow equip effect',
        effect_func=lambda attached_to: True,
        reverse_effect_func=lambda attached_to: True
    ),
    rarity='common',
    triggered_abils=[
        Triggered_Ability(
            name='Heartpiercer Bow triggered_abil',
            trigger_points=['on attacks'],
            trigger_condition=lambda source_abil, obj, **kwargs:
                source_abil.source.attached_to==obj,
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types,
                c_own=False)],
            abil_effect= lambda source_abil: source_abil.get_targets().take_damage(
                1, source= source_abil.source, combat=False)
        )
    ]
)


# Icon of Ancestry {3}
# Artifact
#
# As Icon of Ancestry enters the battlefield, choose a creature type.
#
# Creatures you control of the chosen type get +1/+1.
#
# {3}, {T}: Look at the top three cards of your library. You may reveal a creature
#card of the chosen type from among them and put it into your hand. Put the rest on
#the bottom of your library in a random order.

def Icon_of_Ancestry_pump_effect(applied_obj,source_abil):
    applied_obj.change_power(1)
    applied_obj.change_toughness(1)

def r_Icon_of_Ancestry_pump_effect(applied_obj,source_abil):
    applied_obj.change_power(-1)
    applied_obj.change_toughness(-1)

def Icon_of_Ancestry_ETB(source_abil):
    # get list of creature types
    types=[]
    for zone in source_abil.controller.zones:
        for card in zone:
            if 'creature' in card.types:
                for type in card.subtypes:
                    types.append(type)
    types=list(set(types))
    source_abil.source.last_known_info=source_abil.controller.input_choose(types,
        label='Icon of Ancestry creature type select')

def Icon_of_Ancestry_activated_effect(source_abil):
    top_cards = source_abil.controller.lib[0:3]
    cands = [i for i in top_cards if 'creature' in i.types and source_abil.source
        .last_known_info in i.subtypes]
    selected = source_abil.controller.input_choose(cands,
        label='Icon of Ancestry abil select', permit_empty_list=True,squeeze=False)
    if selected!=None:
        source_abil.controller.lib.leave_zone(selected[0])
        source_abil.controller.hand.enter_zone(selected[0])
        source_abil.controller.reveal_cards(selected, zone='hand')
        non_selected = [i for i in top_cards if i not in selected]
    else:
        non_selected=top_cards
    random.shuffle(non_selected)
    for i in non_selected:
        source_abil.controller.lib.remove(i)
        source_abil.controller.lib.append(i)


Icon_of_Ancestry=Artifact(
    name='Icon of Ancestry',
    cost=Cost(mana={'C':3}),
    rarity='rare',
    nonkeyword_static_abils=[
        Local_Static_Effect(
            name="Icon of Ancestry ETB",
            effect_func= Icon_of_Ancestry_ETB,
            reverse_effect_func= lambda source_abil: True,
            effect_condition = lambda source_abil: source_abil.source.ETB_static_check==True
        ),
        Glob_Static_Effect(
            name="Icon of Ancestry Pump effect",
            effect_condition= lambda applied_obj, source_abil: 'creature' in
                applied_obj.types and source_abil.source.last_known_info in applied_obj.subtypes and
                applied_obj.controller == source_abil.controller,
            effect_func= Icon_of_Ancestry_pump_effect,
            reverse_effect_func = r_Icon_of_Ancestry_pump_effect
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Icon of Ancestry library dig effect',
            cost=Cost(
                mana={'C':3},
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect= Icon_of_Ancestry_activated_effect
        )
    ]
)

# Manifold Key {1}
# Artifact
#
# {1}, {T}: Untap another target artifact.
#
# {3}, {T}: Target creature can’t be blocked this turn.

def Manifold_Key_unblockable_effect(source_abil):
    target=source_abil.get_targets()
    target.add_keyword('unblockable')
    target.EOT_keywords.append('unblockable')

Manifold_Key=Artifact(
    name='Manifold Key',
    cost=Cost(mana={'C':1}),
    rarity='uncommon',
    activated_abils=[
        Activated_Ability(
            name='Manifold Key untap abil',
            cost=Cost(
                mana={'C':1},
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            targets=[Target(criteria= lambda source, obj: 'artifact' in obj.types)],
            abil_effect= lambda source_abil: source_abil.get_targets().untap()
        ),
        Activated_Ability(
            name='Manifold Key unblockable abil',
            cost=Cost(
                mana={'C':3},
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
            abil_effect= lambda source_abil: Manifold_Key_unblockable_effect
        )
    ]
)

# Marauder's Axe {2}
# Artifact — Equipment
#
# Equipped creature gets +2/+0.
#
# Equip {2} ({2}: Attach to target creature you control. Equip only as a sorcery.)

def Marauders_Axe_equip(attached_to):
    attached_to.change_power(2)

def r_Marauders_Axe_equip(attached_to):
    attached_to.change_power(-2)

Marauders_Axe = Equipment(
    name='Marauders Axe',
    cost=Cost(mana={'C':2}),
    equip_cost=Cost(mana={'C':2}),
    equip_static_effect=Attached_Effect(
        name='Marauders Axe equip effect',
        effect_func=Marauders_Axe_equip,
        reverse_effect_func=r_Marauders_Axe_equip
    ),
    rarity='common'
)



# Meteor Golem {7}
# Artifact Creature — Golem
#
# When Meteor Golem enters the battlefield, destroy target nonland permanent an opponent controls.
#
# 3/3
Meteor_Golem = Artifact(
    name='Meteor Golem',
    cost=Cost(mana={'C':7}),
    types=['artifact','creature'],
    subtypes=['golem'],
    power=3,
    toughness=3,
    rarity='uncommon',
    triggered_abils=[
        Triggered_Ability(
            name='Meteor Golem ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets =[Target(criteria= lambda source_abil, obj: True, c_own=False)],
            abil_effect= lambda source_abil: source_abil.get_targets().destroy()
        )
    ]
)



# Mystic Forge {4}
# Artifact
#
# You may look at the top card of your library any time.
#
# You may cast artifact spells and colorless spells from the top of your library.
#
# {T}, Pay 1 life: Exile the top card of your library.

def Mystic_Forge_static_effect(source_abil, applied_obj):
    applied_obj.known_zones.append('top_of_own_lib')
    self.top_lib_cast_condition.append(
        {source_abil: lambda obj: 'artifact' in obj.types or obj.colors==['C']
            or obj.colors==[]}
    )

def r_Mystic_Forge_static_effect(source_abil, applied_obj):
    applied_obj.known_zones.remove('top_of_own_lib')
    del self.top_lib_cast_condition[source_abil]

Mystic_Forge = Artifact(
    name='Mystic Forge',
    cost=Cost(mana={'C':4}),
    rarity='rare',
    nonkeyword_static_abils=[
        Glob_Static_Effect(
            name="Mystic Forge top lib cast effect",
            own_apply_zones=[], opp_apply_zones=[],
            players='self',
            effect_func= Mystic_Forge_static_effect,
            reverse_effect_func = r_Mystic_Forge_static_effect
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Mystic Forge activated abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap(),
                    lambda source_abil: source_abil.controller.pay_life(1)],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                    and (source_abil.source.summoning_sick==False or 'creature' not in
                    source_abil.source.types)]
            ),
            abil_effect= lambda source_abil: source_abil.controller.lib[0].exile()
        )
    ]
)


# Pattern Matcher {4}
# Artifact Creature — Golem
#
# When Pattern Matcher enters the battlefield, you may search your library for a
#card with the same name as another creature you control, reveal it, put it into
# your hand, then shuffle your library.
#
# 3/3

def Pattern_Matcher_select_effect(card):
    card.owner.lib.leave_zone(card)
    card.owner.hand.enter_zone(card)

def Pattern_Matcher_ETB(source_abil):
    elig_names = [i.name for i in source_abil.controller.field if i!=source_abil.source and
        'creature' in i.types]
    source_abil.source.controller.search_library(
        elig_condition= lambda card: card.name in elig_names,
        select_effect= Pattern_Matcher_select_effect,
    )

Pattern_Matcher = Artifact(
    name='Pattern Matcher',
    cost=Cost(mana={'C':4}),
    types=['artifact','creature'],
    subtypes=['golem'],
    power=3,
    toughness=3,
    rarity='uncommon',
    triggered_abils=[
        Triggered_Ability(
            name='Pattern Matcher ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Pattern_Matcher_ETB
        )
    ]
)


#=========================Need to finish prismite activated abil================
# Prismite {2}
# Artifact Creature — Golem
#
# {2}: Add one mana of any color.
# 2/1

Prismite=Artifact(
    name='Prismite',
    cost=Cost(mana={'C':2}),
    types=['artifact','creature'],
    subtypes=['golem'],
    power=2,
    toughness=1,
    rarity='common',
)

# Retributive Wand {3}
# Artifact
#
# {3}, {T}: Retributive Wand deals 1 damage to any target.
#
# When Retributive Wand is put into a graveyard from the battlefield, it deals
# 5 damage to any target.

Retributive_Wand = Artifact(
    name='Retributive Wand',
    cost=Cost(mana={'C':3}),
    rarity='uncommon',
    activated_abils=[
        Activated_Ability(
            name='Retributive Wand activated abli',
            cost=Cost(
                mana={'C':3},
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types or
                'planeswalker' in obj.types, c_players='both')],
            abil_effect = lambda source_abil: source_abil.get_targets().take_damage(
                1, source=source_abil.source, combat=False)
        )
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Retributive Wand triggered abil',
            trigger_points=['to_graveyard_from_field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types or
                'planeswalker' in obj.types, c_players='both')],
            abil_effect = lambda source_abil: source_abil.get_targets().take_damage(
                5, source=source_abil.source, combat=False)
        )
    ]
)

# Salvager of Ruin {3}
# Artifact Creature — Construct
#
# Sacrifice Salvager of Ruin: Choose target permanent card in your graveyard that
# was put there from the battlefield this turn. Return it to your hand.
#
# 2/1

def Salvager_of_Ruin_effect(source_abil):
    target=source_abil.get_targets()
    target.owner.yard.leave_zone(target)
    target.controller.hand.enter_zone(target)

Salvager_of_Ruin = Artifact(
    name='Salvager of Ruin',
    cost=Cost(mana={'C':3}),
    types=['artifact','creature'],
    subtypes=['construct'],
    power=2,
    toughness=1,
    rarity='uncommon',
    activated_abils=[
        Activated_Ability(
            name='Salvager of Ruin activated abil',
            cost=Cost(non_mana=[lambda source_abil: source_abil.source.sacrifice()]),
            targets=[Target(criteria= lambda source, obj: 'instant' not in obj.types and
                'sorcery' not in obj.types and obj.zone_turn==obj.owner.game.turn_id and
                obj.prev_zone.zone_type=='field', c_opponent=False ,c_zones=['yard'])],
            abil_effect=Salvager_of_Ruin_effect
        )
    ]
)


# Scuttlemutt {3}
# Artifact Creature — Scarecrow
#
# {T}: Add one mana of any color.
#
# {T}: Target creature becomes the color or colors of your choice until end of turn.
# 2/2

def Scuttlemutt_change_color_effect(source_abil):
    target= source_abil.get_targets()
    ori_colors=deepcopy(target.colors)
    possible_colors=['W','U','B','R','G']
    permutes=[]
    for i in range(5):
        permutes= permutes + [c for c in itertools.combinations(possible_colors, i)]
    target.colors= source_abil.input_choose(permutes, label='Scuttlemutt change color')
    def EOTr_return_ori_colors(creature):
        creature.colors=ori_colors
    target.EOT_reverse_effects.append(EOTr_return_ori_colors)

Scuttlemutt= Artifact(
    name='Scuttlemutt',
    cost=Cost(mana={'C':3}),
    types=['artifact','creature'],
    subtypes=['scarecrow'],
    power=2,
    toughness=2,
    rarity='uncommon',
    activated_abils=[
        Activated_Ability(
            name='Scuttlemutt change color abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            targets=[Target(criteria=lambda source_abil, obj: 'creature' in obj.types)],
            abil_effect= Scuttlemutt_change_color_effect
        ),
        Activated_Ability(
            name='Scuttlemutt add W abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('W'),
            mana_abil=True,
            potential_mana=Potential_Mana({'W':1})
        ),
        Activated_Ability(
            name='Scuttlemutt add U abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('U'),
            mana_abil=True,
            potential_mana=Potential_Mana({'U':1})
        ),
        Activated_Ability(
            name='Scuttlemutt add B abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)],
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('B'),
            mana_abil=True,
            potential_mana=Potential_Mana({'B':1})
        ),
        Activated_Ability(
            name='Scuttlemutt add R abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('R'),
            mana_abil=True,
            potential_mana=Potential_Mana({'R':1})
        ),
        Activated_Ability(
            name='Scuttlemutt add G abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('G'),
            mana_abil=True,
            potential_mana=Potential_Mana({'G':1})
        )
    ]
)

# Steel Overseer {2}
# Artifact Creature — Construct
# {T}: Put a +1/+1 counter on each artifact creature you control.
# 1/1
def Steel_Overseer_effect(source_abil):
    for card in source_abil.controller.field:
        if 'artifact' in card.types and 'creature' in card.types:
            deepcopy(plus1_plus1_counter).attach_to(card)

Steel_Overseer= Artifact(
    name='Steel Overseer',
    cost=Cost(mana={'C':2}),
    types=['artifact','creature'],
    subtypes=['construct'],
    power=1,
    toughness=1,
    rarity='rare',
    activated_abils=[
        Activated_Ability(
            name='Steel Overseer abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect= Steel_Overseer_effect
        )
    ]
)


# Stone Golem {5}
# Artifact Creature — Golem
#
# 4/4
Stone_Golem= Artifact(
    name='Stone Golem',
    cost=Cost(mana={'C':5}),
    types=['artifact','creature'],
    subtypes=['golem'],
    power=4,
    toughness=4,
    rarity='common'
)


# Vial of Dragonfire {2}
# Artifact
# {2}, {T}, Sacrifice Vial of Dragonfire: It deals 2 damage to target creature.
Vial_of_Dragonfire=Artifact(
    name='Vial of Dragonfire',
    cost=Cost(mana={'C':2}),
    activated_abils=[
        Activated_Ability(
            name='Vial of Dragonfire ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.sacrifice(),
                    lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                    and (source_abil.source.summoning_sick==False or 'creature' not in
                    source_abil.source.types)],
                mana={'C':2}),
            targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
            abil_effect = lambda source_abil:
                source_abil.get_targets().take_damage(2,source=source_abil.source,
                    combat=False)
        )
    ],
    rarity='common'
)

# Nonbasic Lands
Bloodfell_Caves= Land(
    name="Bloodfell Caves",
    rarity='common',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Bloodfell Caves ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.change_life(1)
        )
    ],
    activated_abils=[
        # T: add B
        Activated_Ability(
            name='Bloodfell Caves {B} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('B'),
            mana_abil=True,
            potential_mana=Potential_Mana({'B':1})
        ),
        # T: add R
        Activated_Ability(
            name='Bloodfell Caves {R} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('R'),
            mana_abil=True,
            potential_mana=Potential_Mana({'R':1})
        )

    ]
)

# Blossoming Sands
# Land
#
# Blossoming Sands enters the battlefield tapped.
#
# When Blossoming Sands enters the battlefield, you gain 1 life.
#
# {T}: Add {G} or {W}.
Blossoming_Sands= Land(
    name="Blossoming Sands",
    rarity='common',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Blossoming Sands ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.change_life(1)
        )
    ],
    activated_abils=[
        # T: add B
        Activated_Ability(
            name='Blossoming Sands {G} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('G'),
            mana_abil=True,
            potential_mana=Potential_Mana({'G':1})
        ),
        # T: add R
        Activated_Ability(
            name='Blossoming Sands {W} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('W'),
            mana_abil=True,
            potential_mana=Potential_Mana({'W':1})
        )
    ]
)


# Cryptic Caves
# Land
#
# {T}: Add {C}.
#
# {1}, {T}, Sacrifice Cryptic Caves: Draw a card. Activate this ability only if you control five or more lands.
Cryptic_Caves= Land(
    name="Cryptic Caves",
    rarity='uncommon',
    activated_abils=[
        Activated_Ability(
            name='Cryptic Caves mana ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('C'),
            mana_abil=True,
            potential_mana=Potential_Mana({'C':1})
        ),
        Activated_Ability(
            name='Cryptic Caves draw card abil',
            cost=Cost(
                mana={'C':1},
                non_mana=[lambda source_abil: source_abil.source.tap(),
                    lambda source_abil: source_abil.source.sacrifice()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.draw_card(),
        )
    ]
)


# Dismal Backwater
# Land
#
# Dismal Backwater enters the battlefield tapped.
#
# When Dismal Backwater enters the battlefield, you gain 1 life.
#
# {T}: Add {U} or {B}.
#
Dismal_Backwater= Land(
    name="Dismal Backwater",
    rarity='common',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Dismal Backwater ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.change_life(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Dismal Backwater {B} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('B'),
            mana_abil=True,
            potential_mana=Potential_Mana({'B':1})
        ),
        Activated_Ability(
            name='Dismal Backwater {U} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('U'),
            mana_abil=True,
            potential_mana=Potential_Mana({'U':1})
        )
    ]
)

# Evolving Wilds
# Land
#
# {T}, Sacrifice Evolving Wilds: Search your library for a basic land card, put it onto the battlefield tapped, then shuffle your library.
def Evolving_Wilds_select_effect(card):
    card.owner.lib.leave_zone(card)
    card.owner.field.enter_zone(card)
    card.tap(for_cost=False, summoning_sick_ok=True)

def Evolving_Wilds_effect(source_abil):
    source_abil.controller.search_library(
        elig_condition= lambda card: 'land' in card.types and 'basic' in card.types,
        select_effect= Evolving_Wilds_select_effect,
        shuffle=True
    )

Evolving_Wilds=Land(
    name='Evolving Wilds',
    rarity='common',
    activated_abils=[
        Activated_Ability(
            name='Evolving Wilds activated abil',
                    cost=Cost(
                        non_mana=[lambda source_abil: source_abil.source.tap(),
                            lambda source_abil: source_abil.source.sacrifice()],
                        non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                        and (source_abil.source.summoning_sick==False or 'creature' not in
                        source_abil.source.types)]
                    ),
            abil_effect= Evolving_Wilds_effect
        )
    ]
)

# Field of the Dead
# Land
#
# Field of the Dead enters the battlefield tapped.
#
# {T}: Add {C}.
#
# Whenever Field of the Dead or another land enters the battlefield under your control, if you control seven or more lands with different names, create a 2/2 black Zombie creature token.

Field_of_the_Dead=Land(
    name='Field of the Dead',
    rarity='rare',
    keyword_static_abils=['etb_tapped'],
    activated_abils=[
        Activated_Ability(
            name='Field of the Dead mana ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('C'),
            mana_abil=True,
            potential_mana=Potential_Mana({'C':1})
        ),
    ],
    triggered_abils=[
        Triggered_Ability(
            name='Field of the Dead triggered abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs:
                'land' in obj.types and obj.controller==source_abil.controller and
                len(list(set([i.name for i in source_abil.controller.field if 'land' in i.types])))>=7,
            abil_effect= lambda source_abil: source_abil.controller.create_token(
                Creature_Token(
                    name='Zombie 2/2',
                    colors=['B'],
                    subtypes=['zombie'],
                    power=2,
                    toughness=2
                )
            )
        )
    ]

)


# Jungle Hollow
# Land
#
# Jungle Hollow enters the battlefield tapped.
#
# When Jungle Hollow enters the battlefield, you gain 1 life.
#
# {T}: Add {B} or {G}.

Jungle_Hollow= Land(
    name="Jungle Hollow",
    rarity='common',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Jungle Hollow ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.change_life(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Jungle Hollow {B} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('B'),
            mana_abil=True,
            potential_mana=Potential_Mana({'B':1})
        ),
        Activated_Ability(
            name='Jungle Hollow {G} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('G'),
            mana_abil=True,
            potential_mana=Potential_Mana({'G':1})
        )
    ]
)


# Lotus Field
# Land
#
# Hexproof
#
# Lotus Field enters the battlefield tapped.
#
# When Lotus Field enters the battlefield, sacrifice two lands.
#
# {T}: Add three mana of any one color.
def Lotus_Field_ETB_effect(source_abil):
    for _ in range(2):
        source_abil.controller.sacrifice_permanent(types=['land'])

Lotus_Field= Land(
    name='Lotus Field',
    rarity='rare',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Lotus Field ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= Lotus_Field_ETB_effect
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Lotus Field add W abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('W',3),
            mana_abil=True,
            potential_mana=Potential_Mana({'W':3})
        ),
        Activated_Ability(
            name='Lotus Field add U abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('U',3),
            mana_abil=True,
            potential_mana=Potential_Mana({'U':3})
        ),
        Activated_Ability(
            name='Lotus Field add B abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)],
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('B',3),
            mana_abil=True,
            potential_mana=Potential_Mana({'B':3})
        ),
        Activated_Ability(
            name='Lotus Field add R abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('R',3),
            mana_abil=True,
            potential_mana=Potential_Mana({'R':3})
        ),
        Activated_Ability(
            name='Lotus Field add G abil',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('G',3),
            mana_abil=True,
            potential_mana=Potential_Mana({'G':3})
        )
    ]
)

# Rugged Highlands
# Land
#
# Rugged Highlands enters the battlefield tapped.
#
# When Rugged Highlands enters the battlefield, you gain 1 life.
#
# {T}: Add {R} or {G}.

Rugged_Highlands= Land(
    name="Rugged Highlands",
    rarity='common',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Rugged Highlands ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.change_life(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Rugged Highlands {R} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('R'),
            mana_abil=True,
            potential_mana=Potential_Mana({'R':1})
        ),
        Activated_Ability(
            name='Rugged Highlands {G} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('G'),
            mana_abil=True,
            potential_mana=Potential_Mana({'G':1})
        )
    ]
)
# Scoured Barrens
# Land
#
# Scoured Barrens enters the battlefield tapped.
#
# When Scoured Barrens enters the battlefield, you gain 1 life.
#
# {T}: Add {W} or {B}.
Scoured_Barrens= Land(
    name="Scoured Barrens",
    rarity='common',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Scoured Barrens ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.change_life(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Scoured Barrens {B} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('B'),
            mana_abil=True,
            potential_mana=Potential_Mana({'B':1})
        ),
        Activated_Ability(
            name='Scoured Barrens {W} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('W'),
            mana_abil=True,
            potential_mana=Potential_Mana({'W':1})
        )
    ]
)



# Swiftwater Cliffs
# Land
#
# Swiftwater Cliffs enters the battlefield tapped.
#
# When Swiftwater Cliffs enters the battlefield, you gain 1 life.
#
# {T}: Add {U} or {R}.
Swiftwater_Cliffs= Land(
    name="Swiftwater Cliffs",
    rarity='common',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Swiftwater Cliffs ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.change_life(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Swiftwater Cliffs {R} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('R'),
            mana_abil=True,
            potential_mana=Potential_Mana({'R':1})
        ),
        Activated_Ability(
            name='Swiftwater Cliffs {U} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('U'),
            mana_abil=True,
            potential_mana=Potential_Mana({'U':1})
        )
    ]
)


# Temple of Epiphany
# Land
#
# Temple of Epiphany enters the battlefield tapped.
#
# When Temple of Epiphany enters the battlefield, scry 1.
#
# {T}: Add {U} or {R}.

Temple_of_Epiphany= Land(
    name="Temple of Epiphany",
    rarity='rare',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Temple of Epiphany ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.scry(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Temple of Epiphany {R} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('R'),
            mana_abil=True,
            potential_mana=Potential_Mana({'R':1})
        ),
        Activated_Ability(
            name='Temple of Epiphany {U} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('U'),
            mana_abil=True,
            potential_mana=Potential_Mana({'U':1})
        )
    ]
)


# Temple of Malady
# Land
#
# Temple of Malady enters the battlefield tapped.
#
# When Temple of Malady enters the battlefield, scry 1.
#
# {T}: Add {B} or {G}.
Temple_of_Malady= Land(
    name="Temple of Malady",
    rarity='rare',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Temple of Malady ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.scry(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Temple of Malady {B} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('B'),
            mana_abil=True,
            potential_mana=Potential_Mana({'B':1})
        ),
        Activated_Ability(
            name='Temple of Malady {G} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('G'),
            mana_abil=True,
            potential_mana=Potential_Mana({'G':1})
        )
    ]
)

# Temple of Mystery
# Land
#
# Temple of Mystery enters the battlefield tapped.
#
# When Temple of Mystery enters the battlefield, scry 1.
#
# {T}: Add {G} or {U}.
Temple_of_Mystery= Land(
    name="Temple of Mystery",
    rarity='rare',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Temple of Mystery ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.scry(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Temple of Mystery {U} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('U'),
            mana_abil=True,
            potential_mana=Potential_Mana({'U':1})
        ),
        Activated_Ability(
            name='Temple of Mystery {G} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('G'),
            mana_abil=True,
            potential_mana=Potential_Mana({'G':1})
        )
    ]
)

# Temple of Silence
# Land
#
# Temple of Silence enters the battlefield tapped.
#
# When Temple of Silence enters the battlefield, scry 1.
#
# {T}: Add {W} or {B}.
Temple_of_Silence= Land(
    name="Temple of Silence",
    rarity='rare',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Temple of Silence ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.scry(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Temple of Silence {B} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('B'),
            mana_abil=True,
            potential_mana=Potential_Mana({'B':1})
        ),
        Activated_Ability(
            name='Temple of Silence {W} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('W'),
            mana_abil=True,
            potential_mana=Potential_Mana({'W':1})
        )
    ]
)



# Temple of Triumph
# Land
#
# Temple of Triumph enters the battlefield tapped.
#
# When Temple of Triumph enters the battlefield, scry 1.
#
# {T}: Add {R} or {W}.

Temple_of_Triumph= Land(
    name="Temple of Triumph",
    rarity='rare',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Temple of Triumph ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.scry(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Temple of Triumph {R} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('R'),
            mana_abil=True,
            potential_mana=Potential_Mana({'R':1})
        ),
        Activated_Ability(
            name='Temple of Triumph {W} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('W'),
            mana_abil=True,
            potential_mana=Potential_Mana({'W':1})
        )
    ]
)



# Thornwood Falls
# Land
#
# Thornwood Falls enters the battlefield tapped.
#
# When Thornwood Falls enters the battlefield, you gain 1 life.
#
# {T}: Add {G} or {U}.

Thornwood_Falls= Land(
    name="Thornwood Falls",
    rarity='common',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Thornwood Falls ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.change_life(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Thornwood Falls {G} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('G'),
            mana_abil=True,
            potential_mana=Potential_Mana({'G':1})
        ),
        Activated_Ability(
            name='Thornwood Falls {U} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('U'),
            mana_abil=True,
            potential_mana=Potential_Mana({'U':1})
        )
    ]
)

# Tranquil Cove
# Land
#
# Tranquil Cove enters the battlefield tapped.
#
# When Tranquil Cove enters the battlefield, you gain 1 life.
#
# {T}: Add {W} or {U}.
Tranquil_Cove= Land(
    name="Tranquil Cove",
    rarity='common',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Tranquil Cove ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.change_life(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Tranquil Cove {W} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('W'),
            mana_abil=True,
            potential_mana=Potential_Mana({'W':1})
        ),
        Activated_Ability(
            name='Tranquil Cove {U} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('U'),
            mana_abil=True,
            potential_mana=Potential_Mana({'U':1})
        )
    ]
)



# Wind-Scarred Crag
# Land
#
# Wind-Scarred Crag enters the battlefield tapped.
#
# When Wind-Scarred Crag enters the battlefield, you gain 1 life.
#
# {T}: Add {R} or {W}.

Windscarred_Crag= Land(
    name="Wind-Scarred Crag",
    rarity='common',
    keyword_static_abils=['etb_tapped'],
    triggered_abils=[
        Triggered_Ability(
            name='Wind-Scarred Crag ETB abil',
            trigger_points=['enter field'],
            trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
            abil_effect= lambda source_abil: source_abil.controller.change_life(1)
        )
    ],
    activated_abils=[
        Activated_Ability(
            name='Wind-Scarred Crag {R} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('R'),
            mana_abil=True,
            potential_mana=Potential_Mana({'R':1})
        ),
        Activated_Ability(
            name='Wind-Scarred Crag {W} ability',
            cost=Cost(
                non_mana=[lambda source_abil: source_abil.source.tap()],
                non_mana_check=[lambda source_abil: source_abil.source.tapped==False
                and (source_abil.source.summoning_sick==False or 'creature' not in
                source_abil.source.types)]
            ),
            abil_effect=lambda source_abil: source_abil.source.controller.add_mana('W'),
            mana_abil=True,
            potential_mana=Potential_Mana({'W':1})
        )
    ]
)
