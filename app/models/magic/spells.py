import random

##########################################
#      Spell and Character Elements      #
##########################################

# Default Element class. Treat as abstract
class Element(object):
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
        # Normal element spells can basically be cast by anyone
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
#             Spell Effects              #
##########################################

class Effect(object):
    def __init__(self, power):
        self.power = power
        return

    def apply_effect(self, caster, target):
        raise NotImplementedError

class AttackEffect(Effect):
    def __init__(self, power, accuracy, element, critical_hit_prob):
        super(AttackEffect, self).__init__(power)
        self.accuracy = accuracy
        self.element = element
        self.critical_hit_prob = critical_hit_prob

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
            damage = self.compute_damage(caster, target, self.is_critical_hit())
            target.take_damage(damage)

class BoostStatEffect(Effect):
    def __init__(self, stat, power):
        super(BoostStatEffect, self).__init__(power)
        self.stat = stat

    def apply_effect(self, caster, target):
        target.boost_stat(self.stat, self.power)

class ReduceStatEffect(Effect):
    def __init__(self, power, stat):
        super(ReduceStatEffect, self).__init__(power)
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
    def __init__(self, effect, element):
        self.effect = effect
        self.element = element

    def is_castable_by(self, caster):
        return self.element.is_compatible_with(caster.element)

    def cast(self, caster, target):
        if isinstance(target, list):
            target = target[random.randint(0,len(target)-1)]
        self.effect.apply_effect(caster, target)

class GroupEffectSpell(Spell):
    def cast(self, caster, targets):
        for target in targets:
            self.effect.apply_effect(caster, target)

class KineticBlastSpell(Spell):
    name     = "Kinetic Blast"
    element  = NormalElement()

    power             = 40
    accuracy          = 100
    critical_hit_prob = 8

    def __init__(self):
        effect = AttackEffect(
            KineticBlastSpell.power,
            KineticBlastSpell.accuracy,
            KineticBlastSpell.element,
            KineticBlastSpell.critical_hit_prob
        )

        super(KineticBlastSpell, self).__init__(
            effect,
            KineticBlastSpell.element
        )

class FireballSpell(Spell):
    name    = "Fireball"
    element = FireElement()

    power             = 50
    accuracy          = 100
    critical_hit_prob = 8

    def __init__(self):
        effect = AttackEffect(
            FireballSpell.power,
            FireballSpell.accuracy,
            FireballSpell.element,
            FireballSpell.critical_hit_prob
        )

        super(FireballSpell, self).__init__(
            effect,
            FireballSpell.element
        )

class FlameWaveSpell(GroupEffectSpell):
    name    = "Flame Wave"
    element = FireElement()

    power             = 20
    accuracy          = 100
    critical_hit_prob = 8

    def __init__(self):
        effect = AttackEffect(
            FlameWaveSpell.power,
            FlameWaveSpell.accuracy,
            FlameWaveSpell.element,
            FlameWaveSpell.critical_hit_prob
        )

        super(FlameWaveSpell, self).__init__(
            effect,
            FlameWaveSpell.element
        )

class IceBreakerSpell(Spell):
    name    = "Ice Breaker"
    element = IceElement()

    power             = 50
    accuracy          = 100
    critical_hit_prob = 8

    def __init__(self):
        effect = AttackEffect(
            IceBreakerSpell.power,
            IceBreakerSpell.accuracy,
            IceBreakerSpell.element,
            IceBreakerSpell.critical_hit_prob
        )

        super(IceBreakerSpell, self).__init__(
            effect,
            IceBreakerSpell.element
        )

class WaterJetSpell(Spell):
    name    = "Water Jet"
    element = WaterElement()

    power             = 50
    accuracy          = 100
    critical_hit_prob = 8

    def __init__(self):
        effect = AttackEffect(
            WaterJetSpell.power,
            WaterJetSpell.accuracy,
            WaterJetSpell.element,
            WaterJetSpell.critical_hit_prob
        )

        super(WaterJetSpell, self).__init__(
            effect,
            WaterJetSpell.element
        )

class GlacierSpell(GroupEffectSpell):
    name    = "Glacier"
    element = IceElement()

    power             = 20
    accuracy          = 100
    critical_hit_prob = 8

    def __init__(self):
        effect = AttackEffect(
            GlacierSpell.power,
            GlacierSpell.accuracy,
            GlacierSpell.element,
            GlacierSpell.critical_hit_prob
        )

        super(GlacierSpell, self).__init__(
            effect,
            GlacierSpell.element
        )

class TidalWaveSpell(GroupEffectSpell):
    name    = "Tidal Wave"
    element = WaterElement()

    power             = 20
    accuracy          = 100
    critical_hit_prob = 8

    def __init__(self):
        effect = AttackEffect(
            TidalWaveSpell.power,
            TidalWaveSpell.accuracy,
            TidalWaveSpell.element,
            TidalWaveSpell.critical_hit_prob
        )

        super(TidalWaveSpell, self).__init__(
            effect,
            TidalWaveSpell.element
        )

class FlashBangSpell(Spell):
    name = "Flashbang"
    element = LightElement()

    power = 1
    stat  = 'accuracy'

    def __init__(self):
        effect = ReduceStatEffect(
            FlashBangSpell.power,
            FlashBangSpell.stat
        )

        super(FlashBangSpell, self).__init__(
            effect,
            FlashBangSpell.element
        )

class HealingLightSpell(Spell):
    name = "Healing Light"
    element = LightElement()

    power = 25

    def __init__(self):
        effect = HealingEffect(
            HealingLightSpell.power
        )

        super(HealingLightSpell, self).__init__(
            effect,
            HealingLightSpell.element
        )

class HealingWaveSpell(GroupEffectSpell):
    name = "Healing Wave"
    element = LightElement()

    power = 10

    def __init__(self):
        effect = HealingEffect(
            HealingWaveSpell.power
        )

        super(HealingWaveSpell, self).__init__(
            effect,
            HealingWaveSpell.element
        )

class EagleEyesSpell(Spell):
    name = "Eagle Eyes"
    element = LightElement()

    power = 1
    stat  = 'accuracy'

    def __init__(self):
        effect = BoostStatEffect(
            EagleEyesSpell.power,
            EagleEyesSpell.stat
        )

        super(EagleEyesSpell, self).__init__(
            effect,
            EagleEyesSpell.element
        )

class FleetFeetSpell(Spell):
    name = "Fleet Feet"
    element = LightElement()

    power = 1
    stat  = 'evasion'

    def __init__(self):
        effect = BoostStatEffect(
            FleetFeetSpell.power,
            FleetFeetSpell.stat
        )

        super(FleetFeetSpell, self).__init__(
            effect,
            FleetFeetSpell.element
        )

class SludgePuddleSpell(Spell):
    name = "Sludge Puddle"
    element = DarkElement()

    power = 1
    stat  = 'evasion'

    def __init__(self):
        effect = ReduceStatEffect(
            SludgePuddleSpell.power,
            SludgePuddleSpell.stat
        )

        super(SludgePuddleSpell, self).__init__(
            effect,
            SludgePuddleSpell.element
        )

class DisorientingMistSpell(Spell):
    name = "Disorienting Mist"
    element = DarkElement()

    power = 1
    stat  = 'accuracy'

    def __init__(self):
        effect = ReduceStatEffect(
            DisorientingMistSpell.power,
            DisorientingMistSpell.stat
        )

        super(DisorientingMistSpell, self).__init__(
            effect,
            DisorientingMistSpell.element
        )

class WitheringGlanceSpell(Spell):
    name = "Withering Glance"
    element = DarkElement()

    power = 1
    stat  = 'attack'

    def __init__(self):
        effect = ReduceStatEffect(
            WitheringGlanceSpell.power,
            WitheringGlanceSpell.stat
        )

        super(WitheringGlanceSpell, self).__init__(
            effect,
            WitheringGlanceSpell.element
        )

class FracturedArmourSpell(Spell):
    name = "Fractured Armour"
    element = DarkElement()

    power = 1
    stat  = 'defense'

    def __init__(self):
        effect = ReduceStatEffect(
            FracturedArmourSpell.power,
            FracturedArmourSpell.stat
        )

        super(FracturedArmourSpell, self).__init__(
            effect,
            FracturedArmourSpell.element
        )

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
