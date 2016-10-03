import random

class Element:
    def is_compatible_with(self, element):
        return element.name in self.compatible

    def is_strong_against(self, element):
        return element.name in self.strong

    def is_weak_against(self, element):
        return element.name in self.weak

class LightElement(Element):
    name = 'Light'
    def __init__(self):
        self.compatible = [LightElement.name]
        self.strong     = []
        self.weak       = [LightElement.name]

class DarkElement(Element):
    name = 'Dark'
    def __init__(self):
        self.compatible = [DarkElement.name]
        self.strong     = []
        self.weak       = [DarkElement.name]

class FireElement(Element):
    name = 'Fire'
    def __init__(self):
        self.compatible = [FireElement.name]
        self.strong     = [IceElement.name]
        self.weak       = [WaterElement.name, FireElement.name]

class WaterElement(Element):
    name = 'Water'
    def __init__(self):
        self.compatible = [WaterElement.name]
        self.strong     = [FireElement.name]
        self.weak       = [IceElement.name, WaterElement.name]

class IceElement(Element):
    name = 'Ice'
    def __init__(self):
        self.compatible = [IceElement.name]
        self.strong     = [WaterElement.name]
        self.weak       = [FireElement.name, IceElement.name]

class NormalElement(Element):
    name = 'Normal'
    def __init__(self):
        self.compatible = [
                            NormalElement.name,
                            IceElement.name,
                            FireElement.name,
                            WaterElement.name,
                            LightElement.name,
                            DarkElement.name
                        ]

        self.strong     = []
        self.weak       = []

##########################################
#               Recievers                #
##########################################
class Spell:
    def apply_effect(self, caster, target):
        raise NotImplementedError

    def is_castable_by(self, caster):
        return self.element.is_compatible_with(caster.element)

    def cast(self, caster, target):
        raise NotImplementedError

class GroupEffectSpell(Spell):
    def cast(self, caster, targets):
        for target in targets:
            self.apply_effect(caster, target)

class SingleEffectSpell(Spell):
    def cast(self, caster, target):
        if isinstance(target, list):
            target = target[random.randint(0,len(target)-1)]
        self.apply_effect(caster, target)

class AttackSpell(Spell):

    def target_evades(self, caster, target):
        evasion  = target.get_stat_modifier('evasion')
        accuracy = caster.get_stat_modifier('accuracy')

        modifier = accuracy - evasion
        modifier = float(max(2, 2 + modifier))/max(2, 2 - modifier)

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

        damage = 4 * attack * self.power//defense
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

    def is_critical_hit(self):
        return random.randint(0, 100) < self.critical_hit_prob

    def apply_effect(self, caster, target):
        if self.target_evades(caster, target):
            print("{} evades the attack.".format(target.name))
        else:
            print("Hits {}".format(target.name))

            damage = self.compute_damage(caster, target, self.is_critical_hit())

            target.take_damage(damage)

class StatSpell(Spell):
    def apply_effect(self, caster, target):
        raise NotImplementedError

class BoostStatSpell(Spell):
    def apply_effect(self, caster, target):
        target.boost_stat(self.stat, self.power)

class ReduceStatSpell(Spell):
    def apply_effect(self, caster, target):
        target.reduce_stat(self.stat, self.power)

class HealingSpell(Spell):
    def apply_effect(self, caster, target):
        target.restore_health(self.power)

class KineticBlastSpell(AttackSpell, SingleEffectSpell):
    name     = "Kinetic Blast"
    element  = NormalElement()

    power             = 40
    accuracy          = 100
    critical_hit_prob = 8

class FireballSpell(AttackSpell, SingleEffectSpell):
    name    = "Fireball"
    element = FireElement()

    power             = 50
    accuracy          = 100
    critical_hit_prob = 8

class FlameWaveSpell(AttackSpell, GroupEffectSpell):
    name    = "Flame Wave"
    element = FireElement()

    power             = 20
    accuracy          = 100
    critical_hit_prob = 8

class IceBreakerSpell(AttackSpell, SingleEffectSpell):
    name    = "Ice Breaker"
    element = IceElement()

    power             = 50
    accuracy          = 100
    critical_hit_prob = 8

class WaterJetSpell(AttackSpell, SingleEffectSpell):
    name    = "Water Jet"
    element = WaterElement()

    power             = 50
    accuracy          = 100
    critical_hit_prob = 8

class GlacierSpell(AttackSpell, GroupEffectSpell):
    name    = "Glacier"
    element = IceElement()

    power             = 20
    accuracy          = 100
    critical_hit_prob = 8

class TidalWaveSpell(AttackSpell, GroupEffectSpell):
    name    = "Tidal Wave"
    element = WaterElement()

    power             = 20
    accuracy          = 100
    critical_hit_prob = 8

class FlashBangSpell(StatSpell, SingleEffectSpell):
    name = "Flashbang"
    element = LightElement()

    power = 1
    stat  = 'accuracy'

class HealingLightSpell(HealingSpell, SingleEffectSpell):
    name = "Healing Light"
    element = LightElement()

    power = 25

class HealingWaveSpell(HealingSpell, GroupEffectSpell):
    name = "Healing Wave"
    element = LightElement()

    power = 10

class EagleEyesSpell(BoostStatSpell, SingleEffectSpell):
    name = "Eagle Eyes"
    element = LightElement()

    power = 1
    stat  = 'accuracy'

class FleetFeetSpell(BoostStatSpell, SingleEffectSpell):
    name = "Fleet Feet"
    element = LightElement()

    power = 1
    stat  = 'evasion'

class SludgePuddleSpell(ReduceStatSpell, SingleEffectSpell):
    name = "Sludge Puddle"
    element = DarkElement()

    power = 1
    stat  = 'evasion'

class DisorientingMistSpell(ReduceStatSpell, SingleEffectSpell):
    name = "Disorienting Mist"
    element = DarkElement()

    power = 1
    stat  = 'accuracy'

class WitheringGlanceSpell(ReduceStatSpell, SingleEffectSpell):
    name = "Withering Glance"
    element = DarkElement()

    power = 1
    stat  = 'attack'

class FracturedArmourSpell(ReduceStatSpell, SingleEffectSpell):
    name = "Fractured Armour"
    element = DarkElement()

    power = 1
    stat  = 'defense'

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
    spells = {
        KineticBlastSpell.name : KineticBlastSpell(),
        FireballSpell.name     : FireballSpell(),
        FlameWaveSpell.name    : FlameWaveSpell(),
        WaterJetSpell.name     : WaterJetSpell(),
        TidalWaveSpell.name    : TidalWaveSpell(),
        IceBreakerSpell.name   : IceBreakerSpell(),
        GlacierSpell.name      : GlacierSpell(),
        FlashBangSpell.name    : FlashBangSpell(),
        HealingLightSpell.name : HealingLightSpell(),
        HealingWaveSpell.name  : HealingWaveSpell(),
        FracturedArmourSpell.name : FracturedArmourSpell(),
        WitheringGlanceSpell.name : WitheringGlanceSpell(),
        SludgePuddleSpell.name : SludgePuddleSpell(),
        DisorientingMistSpell.name : DisorientingMistSpell(),
    }

    elements = {
        NormalElement.name : NormalElement,
        WaterElement.name  : WaterElement,
        FireElement.name   : FireElement,
        IceElement.name    : IceElement,
        DarkElement.name   : DarkElement,
        LightElement.name  : LightElement
    }

    def __init__(self):
        self.magic = Magic()

    def cast_spell(self, spell, caster, target):
        spell = SpellBook.get_spell_object(spell)
        if spell != None:
            self.magic.execute(CastSpell(spell, caster, target))

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
