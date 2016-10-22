from app.models import magic
import time

class MageManager:
    modifier_minmax = 6
    spell_limit     = 4
    stat_limit      = 100
    default_element = "Ice"

    def __init__(self, mage):
        self.mage = mage

        self.name    = mage.name
        self.element = magic.SpellBook.get_element_object(self.mage.element)
        if self.element is None:
            print("Invalid element choice {}. Using default {}".format(self.mage.element, MageManager.default_element))
            self.element = magic.SpellBook.get_element_object(MageManager.default_element)

        self.spellbook = magic.SpellBook()

        # Find out what spells our mage picked
        self.spells = mage.spells

        # Store our mage's stats
        self.max_hp = abs(mage.health)
        self.base_stats = {
            'attack'     : abs(mage.attack),
            'defense'    : abs(mage.defense),
            'speed'      : abs(mage.speed)
        }

        # Keep track of modifiers applied to our stats
        self.stat_modifiers = {
            'attack'     : 0,
            'defense'    : 0,
            'speed'      : 0
        }

        # Keep track of how our mage is faring healthwise
        self.cur_hp = self.max_hp

        # Make sure we don't have too many spells
        self.impose_spell_limit()

        # Make sure our stats aren't too high
        self.impose_stat_limit()

    # Returns requested stat without any stat modifiers being applied
    def get_base_stat(self, stat):
        return self.base_stats[stat]

    def impose_stat_limit(self):
        stat_total = self.max_hp + self.base_stats['attack'] + self.base_stats['defense'] + self.base_stats['speed']

        if stat_total > MageManager.stat_limit:
            print("{}'s stats are too high. Reducing".format(self.name))

            # All stats go down by a suitable ratio
            self.max_hp  = int(MageManager.stat_limit * self.max_hp/stat_total)
            self.base_stats['attack']  = int(MageManager.stat_limit * abs(self.base_stats['attack'])/stat_total)
            self.base_stats['defense'] = int(MageManager.stat_limit * abs(self.base_stats['defense'])/stat_total)
            self.base_stats['speed']   = int(MageManager.stat_limit * abs(self.base_stats['speed'])/stat_total)

    def impose_spell_limit(self):
        if len(self.spells) > MageManager.spell_limit:
            printf("{} has too many spells. Reducing to {}".format(self.name, MageManager.spell_limit))
            self.spells = self.spells[:MageManager.spell_limit]

    # Returns requested stat modifier without the base stat
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

    # Use Mage attribute to plan and execute a spell
    def make_move(self, allies, enemies):
        # Make sure we can make a spell to begin with
        if not self.is_conscious():
            print("{} has fainted and cannot make a spell".format(self.name))
            return

        print("{} is planning a spell".format(self.name))

        # Flatten mage managers for the simple AI functions
        flattened_allies = [mage.flatten() for mage in allies]
        flattened_enemies = [mage.flatten() for mage in enemies]

        # Get the AI to make a choice
        decision = self.mage.make_move(flattened_allies, flattened_enemies)

        # Test to ensure that the AI returned a tuple (valid choice)
        if type(decision) is not tuple:
            print("{} does nothing".format(self.name))
            return

        # Make sure the AI chose a valid spell
        if decision[0] not in self.spells:
            print("{} does not know {}".format(self.name, decision[0]))
            return

        # Uplift the target to one of the MageManager objects.
        # Don't want to work with raw Mage object lest cheating happen
        if decision[1] == flattened_allies:
            # Targeted all/random allies
            target = allies
        elif decision[1] == flattened_enemies:
            # Targeted all/random enemies
            target = enemies
        else:
            # Last case, targeted specific mage. Find out who
            # Search allies and enemies for target
            target = [t for t in allies+enemies if t.mage==decision[1]]

            # If we find one, great!
            if len(target) > 0:
                target = target[0]
            else:
                # Invalid target! Don't do anything
                print("Invalid target")
                print("")
                return

        # Cast the spell!
        self.cast_spell(decision[0], target)

    def cast_spell(self, spell, target):
        self.spellbook.cast_spell(spell, self, target)

    def restore_health(self, amount):
        if not self.is_conscious():
            print("{} has fainted and cannot have health restored".format(self.name))
            return

        delta = min(amount, self.max_hp - self.cur_hp)
        self.cur_hp += delta

        print("{} regained {} HP".format(self.name, delta))

    def take_damage(self, damage):
        if not self.is_conscious():
            print("{} has fainted and cannot take more damage".format(self.name))
            return

        delta = min(damage, self.cur_hp)
        self.cur_hp -= delta

        print("{} lost {} HP".format(self.name, delta))

        if self.cur_hp == 0:
            print("{} fainted".format(self.name))

    def boost_stat(self, stat, amount):
        if not self.is_conscious():
            print("{} has fainted and is not affected".format(self.name))
            return

        delta = min(amount, MageManager.modifier_minmax - self.stat_modifiers[stat])
        if delta == 0:
            print("{}'s {} stat can't go any higher".format(self.name, stat))
        else:
            print("{}'s {} {}rose".format(self.name, stat, "sharply " if delta > 1 else ""))
            self.stat_modifiers[stat] += delta

    def reduce_stat(self, stat, amount):
        if not self.is_conscious():
            print("{} has fainted and is not affected".format(self.name))
            return

        delta = min(amount, self.stat_modifiers[stat] + MageManager.modifier_minmax )
        if delta == 0:
            print("{}'s {} stat can't go any lower".format(self.name, stat))
        else:
            print("{}'s {} {}fell".format(self.name, stat, "sharply " if delta > 1 else ""))
            self.stat_modifiers[stat] -= delta

    def flatten(self):
        self.mage.health  = self.cur_hp
        self.mage.attack  = self.get_stat('attack')
        self.mage.defense = self.get_stat('defense')
        self.mage.speed   = self.get_stat('speed')
        return self.mage

    def is_conscious(self):
        return self.cur_hp > 0

    def __str__(self):
        return "{:>15} - {:7} | HP: {:>3} | ATK: {:>3} | DEF: {:>3} | SPD: {:>3}".format(
                self.name,
                self.element.name,
                self.cur_hp,
                self.get_stat("attack"),
                self.get_stat("defense"),
                self.get_stat("speed")
            )
