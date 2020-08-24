from Card_types import *
from Abilities_Effects import *
from Player import *

# test modal card
def Choice_Bolt_effect(source_card):
    if source_card.selected_mode==1:
        target=source_card.get_targets()
        target.destroy()
    if source_card.selected_mode==2:
        source_card.controller.draw_card()

Choice_Bolt = Sorcery (
    name='Choice Bolt',
    cost=Cost(mana={'U':1}),
    moded=True,
    n_modes=2,
    mode_labels=['destroy', 'draw'],
    targets=[Target(criteria=lambda source, obj: 'creature' in obj.types,
        mode_linked=True, mode_num=1)],
    spell_effect= Choice_Bolt_effect
)

# test clone card

def Clone_ETB(source_abil):
    source_abil.source.become_copy(source_abil.get_targets())
    import pdb; pdb.set_trace()

Clone = Creature(
    name='Clone',
    cost=Cost(mana={'C':3,'U':1}),
    power=1,
    toughness=1,
    triggered_abils=[Triggered_Ability(
        name='Clone ETB',
        trigger_points=['enter field'],
        trigger_condition=lambda source_abil, obj, **kwargs: obj==source_abil.source,
        targets=[Target(criteria= lambda source, obj: 'creature' in obj.types)],
        abil_effect = Clone_ETB
    )]

)

# Creatures
Grizzly_Bears= Creature(
    name="Grizzly Bears",
    cost=Cost(mana={"C":1, "G":1}),
    power=2,
    toughness=2
)
Burly_Bears= Creature(
    name="Burly Bears",
    cost=Cost(mana={"C":1, "G":1}),
    power=5,
    toughness=5
)

Horned_Turtle= Creature(
    name="Horned Turtle",
    cost=Cost(mana={"C":2, "U":1}),
    power=1,
    toughness=4
)
Hill_Giant= Creature(
    name="Hill Giant",
    cost=Cost(mana={"C":3, "R":1}),
    power=3,
    toughness=3
)
Honor_Guard= Creature(
    name="Honor Guard",
    cost=Cost(mana={"C":1, "W":1}),
    power=2,
    toughness=2
)

# 1R
# when it ETBs, deal 2 damage to each opponent
# 2/2
Goblin_Firechucker= Creature(
    name="Goblin Firechucker",
    cost=Cost(mana={"C":1, "R":1}),
    power=2,
    toughness=2,
    triggered_abils=[
        Triggered_Ability(
            name='Goblin_Firechucker_ETB',
            trigger_points=['enter field'],
            remove_points_on_resolve=True,
            trigger_condition=lambda self: self.card.name=='Goblin Firechucker',
            effect= lambda self: self.card.controller.opponent.change_life(-2)
        )
    ]
)

# Sorceries
def Volcanic_Hammer_select_target(self):
    possible_targets=self.owner.get_legal_targets(
        criteria=lambda obj: 'creature' in obj.types or 'planeswalker' in obj.types \
            and 'hexproof' not in obj.keyword_static_abils and 'shroud' not in obj.keyword_static_abils,
        players=[self.owner,self.owner.opponent]
    )
    if possible_targets==[]:
        raise GameActionError('Error: no legal targets')
    target=self.owner.input_choose(possible_targets)
    self.choices_made['target']=target
def Volcanic_Hammer_effect(self):
    target=self.choices_made['target']
    if 'creature' in target.types:
        target.take_damage(3,source=self)
    if 'player' in target.types:
        target.change_life(-3,source=self)
    if 'planeswalker' in target.types:
        target.change_loyalty(-3)
Volcanic_Hammer= Sorcery(
    name='Volcanic Hammer',
    cost=Cost(mana={'C':1,'R':1}),
    choices= Volcanic_Hammer_select_target,
    effect= Volcanic_Hammer_effect
)

def Lightning_Bolt_select_target(self):
    possible_targets=self.owner.get_legal_targets(
        criteria=lambda obj: 'creature' in obj.types or 'planeswalker' in obj.types \
            and 'hexproof' not in obj.keyword_static_abils and 'shroud' not in obj.keyword_static_abils,
        players=[self.owner,self.owner.opponent]
    )
    if possible_targets==[]:
        raise GameActionError('Error: no legal targets')
    target=self.owner.input_choose(possible_targets)
    self.choices_made['target']=target

def Lightning_Bolt_effect(self):
    target=self.choices_made['target']
    if 'creature' in target.types:
        target.take_damage(3)
    if 'player' in target.types:
        target.change_life(-3)
    if 'planeswalker' in target.types:
        target.change_loyalty(-3)
Lightning_Bolt= Instant(
    name='Lightning Bolt',
    cost=Cost(mana={'R':1}),
    choices=Lightning_Bolt_select_target,
    effect= Lightning_Bolt_effect
)

# Enchantments
# Gaea's Anthem
def Gaeas_Anthem_Effect(creature):
    creature.power+=1
    creature.toughness+=1
def r_Gaeas_Anthem_Effect(creature):
    creature.power-=1
    creature.toughness-=1
Gaeas_Anthem= Enchantment(
    name="Gaea's Anthem",
    cost=Cost(mana={'G':2,'C':1})
)
Gaeas_Anthem.nonkeyword_static_abils.append(
    Glob_Static_Effect(
        name="Gaea's Anthem pump effect",
        obj_condition= lambda x: 'creature' in x.types,
        effect= Gaeas_Anthem_Effect,
        reverse_effect = r_Gaeas_Anthem_Effect
    )
)

# Leonin Scimtar
def Leonin_Scimtar_Effect(creature):
    creature.power+=1
    creature.toughness+=1
def r_Leonin_Scimtar_Effect(creature):
    creature.power-=1
    creature.toughness-=1
Leonin_Scimtar=Equipment(
    name='Leonin Scimtar',
    cost=Cost(mana={'C':1}),
    equip_cost=Cost(mana={'C':1}),
    equip_effect=Leonin_Scimtar_Effect,
    reverse_effect=r_Leonin_Scimtar_Effect
)


# Jace Beleren
def Jace_Beleren_plus2_effect(self):
    self.card.owner.draw_card()
    self.card.owner.opponent.draw_card()
def Jace_Beleren_minus1_effect(self):
    self.choices_made['target'].draw_card()
def Jace_Beleren_minus10_effect(self):
    self.choices_made['target'].mill_card(num=20)
def Jace_Beleren_select_target(self):
    possible_targets=self.card.owner.get_legal_targets(
        players=[self.card.owner,self.card.owner.opponent]
    )
    if possible_targets==[]:
        raise GameActionError('Error: no legal targets')
    target=self.card.owner.input_choose(possible_targets)
    self.choices_made['target']=target

Jace_Beleren=Planeswalker(
    name='Jace Beleren',
    subtypes=['Jace'],
    cost=Cost(mana={'C':1,'U':2}),
    loyalty=3,
    activated_abils=[
        #plus 2
        Activated_Ability(
            name='Jace Beleren +2 ability',
            cost=Cost(non_mana=[lambda self: self.change_loyalty(2)]),
            effect= Jace_Beleren_plus2_effect,
            flash=False
        ),
        # minus 1
        Activated_Ability(
            name='Jace Beleren -1 ability',
            cost=Cost(non_mana=[lambda self: self.change_loyalty(-1)]),
            choices=Jace_Beleren_select_target,
            effect=Jace_Beleren_minus1_effect,
            flash=False
        ),
        # minus 10
        Activated_Ability(
            name='Jace Beleren -10 ability',
            cost=Cost(non_mana=[lambda self: self.change_loyalty(-10)]),
            choices= Jace_Beleren_select_target,
            effect= Jace_Beleren_minus10_effect,
            flash=False
        )
    ]
)

# Basic Lands
Plains= Land(
    name="Plains",
    types=['basic','land'],
    subtypes=['Plains'],
    activated_abils=[
        # T: add W
        Activated_Ability(
            name='Plains ability',
            cost=Cost(non_mana=[lambda land: land.tap()]),
            effect=lambda land: land.card.owner.add_mana('W'),
            mana_abil=True
        )
    ]
)

Island= Land(
    name="Island",
    types=['basic','land'],
    subtypes=['Island'],
    activated_abils=[
        # T: add U
        Activated_Ability(
            name='Island ability',
            cost=Cost(non_mana=[lambda land: land.tap()]),
            effect=lambda land: land.card.owner.add_mana('U'),
            mana_abil=True
        )
    ]
)

Swamp= Land(
    name="Swamp",
    types=['basic','land'],
    subtypes=['Swamp'],
    activated_abils=[
        # T: add B
        Activated_Ability(
            name='Swamp ability',
            cost=Cost(non_mana=[lambda land: land.tap()]),
            effect=lambda land: land.card.owner.add_mana('B'),
            mana_abil=True
        )
    ]
)

Mountain= Land(
    name="Mountain",
    types=['basic','land'],
    subtypes=['Mountain'],
    activated_abils=[
        # T: add R
        Activated_Ability(
            name='Mountain ability',
            cost=Cost(non_mana=[lambda land: land.tap()]),
            effect=lambda land: land.card.owner.add_mana('R'),
            mana_abil=True
        )
    ]
)

Forest= Land(
    name="Forest",
    types=['basic','land'],
    subtypes=['Forest'],
    activated_abils=[
        # T: add G
        Activated_Ability(
            name='Forest ability',
            cost=Cost(non_mana=[lambda land: land.tap()]),
            effect=lambda land: land.card.owner.add_mana('G'),
            mana_abil=True
        )
    ]
)

# Nonbasics Lands
# Taiga
Taiga= Land(
    name="Taiga",
    subtypes=['Mountain','Forest'],
    activated_abils=[
        # T: add G
        Activated_Ability(
            name='Taiga G ability',
            cost=Cost(non_mana=[lambda land: land.tap()]),
            effect=lambda land: land.card.owner.add_mana('G'),
            mana_abil=True
        ),
        # T: add R
        Activated_Ability(
            name='Taiga R ability',
            cost=Cost(non_mana=[lambda land: land.tap()]),
            effect=lambda land: land.card.owner.add_mana('R'),
            mana_abil=True
        )
    ]
)

# Unknown Shores
def Unknown_Shores_abil_effect(US_obj):
    color=US_obj.owner.input_choose(['W','U','B','R','G'],choose_color_cost=True)
    US_obj.owner.add_mana(color)

Unknown_Shores= Land(
    name='Unknown Shores',
    indep=False,
    activated_abils=[
        #T: add 1
        Activated_Ability(
            name='Unknown Shores colorless ability',
            cost=Cost(non_mana=[lambda land: land.tap()]),
            effect=lambda US_obj: US_obj.owner.add_mana('C'),
            mana_abil=True
        ),
        #1,T: add 1 of any color
        Activated_Ability(
            name='Unknown Shores filtering ability',
            cost=Cost(non_mana=[lambda land: land.tap()],mana={'C':1}),
            effect=Unknown_Shores_abil_effect,
            mana_abil=True
        )
    ]
)

Cryptic_Caves= Land(
    name='Cryptic Caves',
    activated_abils=[
        #T: add 1
        Activated_Ability(
            name='Cryptic Caves colorless ability',
            cost=Cost(non_mana=[lambda land: land.tap()]),
            effect=lambda land: land.card.owner.add_mana('C'),
            mana_abil=True
        ),
        # 1, T: draw a card
        Activated_Ability(
            name='Cryptic Caves sac ability',
            cost=Cost(non_mana=[lambda land: land.tap(),lambda self: self.sacrifice()],mana={'C':1}),
            effect=lambda land: land.card.owner.draw_card(),
            mana_abil=False
        )
    ]
)
