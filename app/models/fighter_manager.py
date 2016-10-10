from app.models import magic
import time

class FighterManager:
    
    def __init__(self, fighter):
        self.fighter = fighter
        self.modifier_minmax = 6

        self.name    = fighter.name
        self.element = magic.SpellBook.get_element_object(self.fighter.element)
        self.spellbook = magic.SpellBook()

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

    # Returns requested stat without any stat modifiers being applied
    def get_base_stat(self, stat):
        return self.base_stats[stat]

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

    # Use Fighter attribute to plan and execute a move
    def make_move(self, allies, enemies):
        # Make sure we can make a move to begin with
        if not self.is_conscious():
            print("{} has fainted and cannot make a move".format(self.name))            
            return

        print("{} is planning a move".format(self.name))

        # Flatten fighter managers for the simple AI functions
        flattened_allies = [fighter.flatten() for fighter in allies]
        flattened_enemies = [fighter.flatten() for fighter in enemies]

        # Get the AI to make a choice
        decision = self.fighter.make_move(flattened_allies, flattened_enemies)

        # Test to ensure that the AI returned a tuple (valid choice)
        if type(decision) is not tuple:            
            print("{} does nothing".format(self.name))            
            return
        
        # Make sure the AI chose a valid move
        if decision[0] not in self.moves:
            print("{} does not know {}".format(self.name, decision[0]))            
            return
        
        # Uplift the target to one of the FighterManager objects.
        # Don't want to work with raw Fighter object lest cheating happen
        if decision[1] == flattened_allies:
            # Targeted all/random allies
            target = allies
        elif decision[1] == flattened_enemies:
            # Targeted all/random enemies
            target = enemies
        else:                                   
            # Last case, targeted specific fighter. Find out who
            # Search allies and enemies for target
            target = [t for t in allies+enemies if t.fighter==decision[1]]

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

        delta = min(amount, self.modifier_minmax - self.stat_modifiers[stat])
        if delta == 0:
            print("{}'s {} stat can't go any higher".format(self.name, stat))
        else:
            print("{}'s {} {}rose".format(self.name, stat, "sharply " if delta > 1 else ""))
            self.stat_modifiers[stat] += delta

    def reduce_stat(self, stat, amount):
        if not self.is_conscious():
            print("{} has fainted and is not affected".format(self.name))
            return

        delta = min(amount, self.stat_modifiers[stat] + self.modifier_minmax )
        if delta == 0:
            print("{}'s {} stat can't go any lower".format(self.name, stat))
        else:
            print("{}'s {} {}fell".format(self.name, stat, "sharply " if delta > 1 else ""))
            self.stat_modifiers[stat] -= delta

    def flatten(self):
        self.fighter.hp      = self.cur_hp
        self.fighter.attack  = self.get_stat('attack')
        self.fighter.defense = self.get_stat('defense')
        self.fighter.speed   = self.get_stat('speed')
        return self.fighter

    def is_conscious(self):
        return self.cur_hp > 0

    def __str__(self):
        return "{:>10} - {:>5} | HP: {:>3} | ATK: {:>3} | DEF: {:>3} | SPD: {:>3} | ACC: {:>3} | EVA: {:>3}".format(
                self.name,
                self.element.name,
                self.cur_hp,                
                self.get_stat("attack"),
                self.get_stat("defense"),
                self.get_stat("speed"),
                self.get_stat_modifier("evasion"),
                self.get_stat_modifier("accuracy")
            )
