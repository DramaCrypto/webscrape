def make_lst(s):
    return [x.strip() for x in s.split('\n')]


RARITY_ORDER = make_lst("""Prismatic Secret Rare
Extra Secret Rare
Secret Rare
Ultra Rare
Ultimate Rare
Ghost Rare
Gold Rare
Platinum Rare
Platinum Secret Rare
Ultra Parallel Rare
Normal Parallel Rare
Duel Terminal Ultra Parallel R
Duel Terminal Super Parallel R
Duel Terminal Rare Parallel Ra
Duel Terminal Normal Rare Para
Shatterfoil Rare
Mosaic Rare
Starfoil Rare
Super Rare
Rare
Common
Super Short Print
Short Print""")

TYPES_ORDER = make_lst("""Effect Monster
Flip Effect Monster
Fusion Monster
Gemini Monster
Link Monster
Normal Monster
Normal Tuner Monster
Pendulum Effect Fusion Monster
Pendulum Effect Monster
Pendulum Flip Effect Monster
Pendulum Normal Monster
Pendulum Tuner Effect Monster
Ritual Effect Monster
Ritual Monster
Spirit Monster
Synchro Monster
Synchro Pendulum Effect Monster
Synchro Tuner Monster
Token
Toon Monster
Tuner Monster
Union Effect Monster
XYZ Monster
XYZ Pendulum Effect Monster""")

RACES_ORDER = make_lst("""Pyro
Spellcaster
Fiend
Insect
Dinosaur
Plant
Winged Beast
Fairy
Zombie
Beast
Aqua
Rock
Thunder
Sea Serpent
Fish
Dragon
Psychic
Beast-Warrior
Wyrm
Reptile
Machine
Warrior
Divine-Beast
Cyberse""")

SPELLS_ORDER = make_lst("""Normal
Quick-Play
Field
Equip
Continuous
Ritual""")

TRAPS_ORDER = make_lst("""Normal
Continuous
Counter""")

SKILL_ORDER = make_lst("""Yugi
Kaiba
Weevil
Joey
Rex
Mako
Mai
Pegasus
Bonz
Keith
Ishizu""")