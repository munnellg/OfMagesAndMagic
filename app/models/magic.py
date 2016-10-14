import random
import xml.etree.ElementTree as ET

##########################################
#      Spell and Character Elements      #
##########################################
# Default Element class.
class Element(object):
    # Initialize a new element object
    def __init__(self, name, strong, weak, compatible):
        self.name = name
        self.strong = strong
        self.weak = weak
        self.compatible = compatible

    # Determine whether or not this element is roughly synonymous
    # With any other element.
    def is_compatible_with(self, element):
        return element.name in self.compatible

    # Return whether or not we will do extra damage to the input element
    def is_strong_against(self, element):
        return element.name in self.strong

    # Weak against does not mean elements that do extra damage to us
    # It means elements against which we do poor damage. There is a difference!
    def is_weak_against(self, element):
        return element.name in self.weak

##########################################
#             Spell Effects              #
##########################################

# How a particular spell will affect a targeted enemy
# Stats targeted, additional modifiers, etc.
class Effect(object):
    def __init__(self, element, power):
        self.power = power
        self.element = element

    def apply_effect(self, caster, target):
        raise NotImplementedError

# A spell which reduces the targets health. Damage is a function of
# attack power, caster power, target defense and some random variables
class AttackEffect(Effect):
    def __init__(self, element, power, accuracy, critical_hit_prob):
        # Call the parent Effect constructor first
        super(AttackEffect, self).__init__(element, power)

        # Store move accuracy and critical hit probability
        self.accuracy = accuracy
        self.critical_hit_prob = critical_hit_prob

    def target_evades(self, caster, target):
        # Get respective target speeds
        evasion  = target.get_stat('speed')
        accuracy = caster.get_stat('speed')

        # Compute accuracy modifier based on difference in speeds
        modifier = float(accuracy - evasion)/max(1,float(accuracy+evasion))
        modifier = int(modifier*caster.modifier_minmax)
        modifier = float(max(2, 2 + modifier))/max(2, 2 - modifier)

        # Computer overall accuracy and test for hit using random variable
        accuracy = min(100, self.accuracy * modifier)
        return random.randint(0, 100) > accuracy

    def compute_damage(self, caster, target, critical_hit=False):
        if critical_hit:
            print("Critical hit")
            # Critical hits ignore positive defense modifiers and negative attack modifiers
            attack = max(caster.get_stat('attack'), caster.get_base_stat('attack'))
            defense = min(target.get_stat('defense'), target.get_base_stat('defense'))
        else:
            attack = caster.get_stat('attack')
            defense = target.get_stat('defense')

        damage = 4 * attack * self.power//max(1,defense)
        damage = damage//50
        damage += 2

        if self.element.is_strong_against(target.element):
            print("It's super effective")
            damage *= 2
        elif self.element.is_weak_against(target.element):
            print("It's not very effective")
            damage //= 2

        if critical_hit:
            damage *= 2

        return damage

    # Simple computation of critical hit depending on critical_hit_prob of spell
    def is_critical_hit(self):
        return random.randint(0, 100) < self.critical_hit_prob

    # Override parent apply effect method for our AttachEffect
    def apply_effect(self, caster, target):
        # Test for evasion and report if target dodged
        if self.target_evades(caster, target):
            print("{} evades the attack.".format(target.name))
        else:
            # Apply damage
            damage = self.compute_damage(caster, target, self.is_critical_hit())
            target.take_damage(damage)

class BoostStatEffect(Effect):
    def __init__(self, element, power, stat):
        super(BoostStatEffect, self).__init__(element, power)
        self.stat = stat

    def apply_effect(self, caster, target):
        target.boost_stat(self.stat, self.power)

class ReduceStatEffect(Effect):
    def __init__(self, element, power, stat):
        super(ReduceStatEffect, self).__init__(element, power)
        self.stat = stat

    def apply_effect(self, caster, target):
        target.reduce_stat(self.stat, self.power)

class HealingEffect(Effect):
    def apply_effect(self, caster, target):
        target.restore_health(self.power)

##########################################
#                 Spells                 #
##########################################

class Spell(object):
    def __init__(self, name, effects, element):
        self.name    = name
        self.effects = effects
        self.element = element

    def is_castable_by(self, caster):
        return self.element.is_compatible_with(caster.element)

    def cast(self, caster, target):
        if isinstance(target, list):
            target = target[random.randint(0,len(target)-1)]

        for effect in self.effects:
            effect.apply_effect(caster, target)

class GroupSpell(Spell):
    def cast(self, caster, targets):
        for target in targets:
            for effect in self.effects:
                effect.apply_effect(caster, target)

##########################################
#                Commands                #
##########################################
class SpellCommand:
    def __init__(self, spell, caster, target):
        self.spell = spell
        self.caster = caster
        self.target = target

    def execute(self):
        raise NotImplementedError

class CastSpell(SpellCommand):
    def execute(self):
        if not self.spell.is_castable_by(self.caster):
            print("{} can't cast {}".format(self.caster.name, self.spell.name) )
        else:
            print("{} casts {}".format(self.caster.name, self.spell.name) )
            self.spell.cast(self.caster, self.target)

##########################################
#                 Invoker                #
##########################################
class Magic:
    def __init__(self):
        return

    def execute(self, command):
        command.execute()

##########################################
#                 Client                 #
##########################################
class SpellBook:
    spells   = {}
    elements = {}

    spell_constructors  = {
        'group'  : GroupSpell,
        'single' : Spell
    }

    effect_constructors = {
        'attack'      : AttackEffect,
        'stat_boost'  : BoostStatEffect,
        'stat_reduce' : ReduceStatEffect,
        'heal'        : HealingEffect
    }

    def __init__(self):
        self.magic = Magic()

    def cast_spell(self, spell, caster, target):
        spell = SpellBook.get_spell_object(spell)
        if spell != None:
            self.magic.execute(CastSpell(spell, caster, target))

    @staticmethod
    def __load_elements(xml_tree):
        elements = xml_tree.find('elements').findall('element')

        # Load element types from the XML file
        for element in elements:
            # Get the name of the element
            name = element.attrib['name']

            # Get strengths, weaknesses and compatabilities
            strong = [elem.text for elem in element.findall('strong/element')]
            weak = [elem.text for elem in element.findall('weak/element')]
            compatible = [elem.text for elem in element.findall('compatible/element')]

            # Element has to be part of its own compatibility list
            compatible.append(name)

            # Add the element to our spell book
            SpellBook.elements[name] = Element(name, strong, weak, compatible)

    @staticmethod
    def __load_spells(xml_tree):
        spells   = xml_tree.find('spells').findall('spell')

        # Load spells into our spell book
        for spell in spells:
            # Get the name of the spell
            name    = spell.attrib['name']

            # Determine the spell's element type (with error checking)
            element = spell.find('element')

            # Element tag is missing
            if element == None:
                print("{} does not have element. Skipping".format(name))
                continue

            element = element.text

            # Element tag contained invalid text
            if element not in SpellBook.elements:
                print("{} has invalid element {}. Skipping".format(name, element))
                continue

            # Get the element from the list of elements loaded
            element = SpellBook.elements[element]

            # Load the effects that the spell has
            effects = []
            for effect in spell.findall('effect'):
                # Get the effect's type and remove that entry from the dictionary
                effect_type = effect.attrib.pop('type', None)

                # Cast dictionary elements to ints where possible
                for key in effect.attrib:
                    try:
                        new_val = int(effect.attrib[key])
                        effect.attrib[key] = new_val
                    except ValueError:
                        pass

                # Create the effect and append it to our list
                effects.append(SpellBook.effect_constructors[effect_type](element, **effect.attrib))

            # Create the spell from all that we've loaded
            SpellBook.spells[name] = SpellBook.spell_constructors[spell.attrib['type']](name, effects, element)

    @staticmethod
    def load_spell_book(spell_book):
        data = ET.parse(spell_book)
        tree = data.getroot()

        SpellBook.__load_elements(tree)
        SpellBook.__load_spells(tree)

    @staticmethod
    def get_element_object(identifier):
        if identifier not in SpellBook.elements:
            print("{} is not a real element".format(identifier))
        else:
            return SpellBook.elements[identifier]

    @staticmethod
    def get_spell_object(identifier):
        if identifier not in SpellBook.spells:
            print("{} is not a real spell".format(identifier))
        else:
            return SpellBook.spells[identifier]
