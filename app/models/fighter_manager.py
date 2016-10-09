from app.models import magic

class FighterManager:
    class __StateConscious:
        def __init__(self, parent):
            self.parent = parent
            self.spellbook = magic.SpellBook()

        def cast_spell(self, spell, target):
            self.spellbook.cast_spell(spell, self.parent, target)

        def flatten_fighters(self, fighters):
            return [status.get_updated_fighter() for status in fighters]

        def unflatten(self, fighter, flattened1, flattened2, unflattened1, unflattened2):
            if isinstance(fighter, list):
                if fighter == flattened1:
                    return unflattened1
                if fighter == flattened2:
                    return unflattened2
            else:
                for i in range(len(flattened1)):
                    if fighter == flattened1[i]:
                        return unflattened1[i]

                for j in range(len(flattened2)):
                    if fighter == flattened2[j]:
                        return unflattened2[j]
            print("Unable to find reference")

        def make_move(self, allies, enemies):
            print("{} is planning a move".format(self.parent.name))
            flattened_allies = self.flatten_fighters(allies)
            flattened_enemies = self.flatten_fighters(enemies)

            decision = self.parent.fighter.make_move(flattened_allies, flattened_enemies)
            target = self.unflatten(decision[1], flattened_enemies, flattened_allies, enemies, allies)
            if decision[0] not in self.parent.moves:
                print("{} does not know {}".format(self.parent.name, decision[0]))
            else:
                self.cast_spell(decision[0], target)

            flattened_allies = self.flatten_fighters(allies)
            flattened_enemies = self.flatten_fighters(enemies)
            print("")

        def restore_health(self, amount):
            delta = min(amount, self.parent.max_hp - self.parent.cur_hp)
            print("{} regained {} HP".format(self.parent.name, delta))
            self.parent.cur_hp += delta

        def take_damage(self, damage):
            delta = min(damage, self.parent.cur_hp)
            print("{} lost {} HP".format(self.parent.name, delta))
            self.parent.cur_hp -= delta
            if self.parent.cur_hp == 0:
                print("{} fainted".format(self.parent.name))
                self.parent.set_state('fainted')

        def boost_stat(self, stat, amount):
            delta = min(amount, self.parent.modifier_minmax - self.parent.stat_modifiers[stat])
            if delta == 0:
                print("{}'s {} stat can't go any higher".format(self.parent.name, stat))
            else:
                print("{}'s {} {}rose".format(self.parent.name, stat, "sharply " if delta > 1 else ""))
                self.parent.stat_modifiers[stat] += delta

        def reduce_stat(self, stat, amount):
            delta = min(amount, self.parent.stat_modifiers[stat] + self.parent.modifier_minmax )
            if delta == 0:
                print("{}'s {} stat can't go any lower".format(self.parent.name, stat))
            else:
                print("{}'s {} {}fell".format(self.parent.name, stat, "sharply " if delta > 1 else ""))
                self.parent.stat_modifiers[stat] -= delta

    class __StateFainted:
        def __init__(self, parent):
            self.parent = parent
            self.name = self.parent.name

        def cast_spell(self, spell, target):
            print("{} has fainted and can't cast spells".format(self.name))

        def make_move(self, allies, enemies):
            return
            print("{} has fainted and can't make a move".format(self.name))

        def restore_health(self, amount):
            print("{} has fainted and can't be restored".format(self.name))

        def take_damage(self, damage):
            print("{} has fainted and can't take more damage".format(self.name))

        def reduce_stat(self, stat, amount):
            print("Spell has no effect on {}".format(self.parent.name))

        def boost_stat(self, stat, amount):
            print("Spell has no effect on {}".format(self.parent.name))

    def __init__(self, fighter):
        self.fighter = fighter
        self.modifier_minmax = 6

        self.name    = fighter.name
        self.element = magic.SpellBook.get_element_object(self.fighter.element)

        self.max_hp = fighter.hp
        self.cur_hp = fighter.hp

        self.moves = fighter.moves
        if len(self.moves) > 4:
            self.moves = self.moves[:4]

        self.base_stats = {
            'attack'     : fighter.attack,
            'defense'    : fighter.defense,
            'speed'      : fighter.speed
        }

        self.stat_modifiers = {
            'attack'     : 0,
            'defense'    : 0,
            'speed'      : 0,
            'evasion'    : 0,
            'accuracy'   : 0
        }

        self.states = {
            "conscious" : FighterManager.__StateConscious,
            "fainted"   : FighterManager.__StateFainted,
        }

        self.set_state('conscious')

    def get_base_stat(self, stat):
        return self.base_stats[stat]

    def get_stat_modifier(self, stat):
        return self.stat_modifiers[stat]

    # Get the value of a stat with the modifier applied
    def get_stat(self, stat):
        # Get stat modifier
        modifier = self.stat_modifiers[stat]

        # Compute modifier effect
        modifier = float(max(2, 2 + modifier))/max(2, 2 - modifier)

        # Return modified stat (rounded down)
        return int(self.base_stats[stat] * modifier)

    def reset_fighter(self):
        # Reset fighter's hit points
        self.fighter.hp = self.max_hp

        # Reset fighter stats
        self.fighter.attack = self.base_stats['attack']
        self.fighter.defense = self.base_stats['defense']
        self.fighter.speed = self.base_stats['speed']

        # Reset stat modifiers
        for key in self.stat_modifiers:
            self.stat_modifiers[key] = 0

    def set_state(self, state_code):
        self.cur_state_code = state_code
        self.state = self.states[state_code](self)

    def cast_spell(self, spell, target):
        self.state.cast_spell(spell, target)

    def make_move(self, allies, enemies):
        self.state.make_move(allies, enemies)

    def restore_health(self, amount):
        self.state.restore_health(amount)

    def take_damage(self, damage):
        self.state.take_damage(damage)

    def reduce_stat(self, stat, amount):
        self.state.reduce_stat(stat, amount)

    def boost_stat(self, stat, amount):
        self.state.boost_stat(stat, amount)

    def get_updated_fighter(self):
        self.fighter.hp      = self.cur_hp
        self.fighter.attack  = self.get_stat('attack')
        self.fighter.defense = self.get_stat('defense')
        self.fighter.speed   = self.get_stat('speed')
        return self.fighter

    def __str__(self):
        return "{:>10} | HP: {:>3} | ATK: {:>3} | DEF: {:>3} | SPD: {:>3} | ACC: {:>3} | EVA: {:>3}".format(
                self.name,
                self.cur_hp,
                self.get_stat("attack"),
                self.get_stat("defense"),
                self.get_stat("speed"),
                self.get_stat_modifier("evasion"),
                self.get_stat_modifier("accuracy")
            )
