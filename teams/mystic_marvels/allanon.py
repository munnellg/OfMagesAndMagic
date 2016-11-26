class Mage:
    def __init__(self):
        self.name     = "Allanon"

        self.health   = 50
        self.attack   = 25
        self.defense  = 15
        self.speed    = 10

        self.element  = "Earth"

        self.spells   = [
            "Bassault",
            "Landslide",
            "Quicksand",
            "Kinetic Blast"
        ]

        # Remember base stats for reference later
        self.max_health    = self.health
        self.base_attack   = self.attack
        self.base_defense  = self.defense
        self.base_speed    = self.speed

        # Be aware of strengths and weaknesses
        self.strengths  = [ "Thunder", "Fire" ]
        self.weaknesses = [ "Ice", "Water" ]

    def find_weak_foes(self, enemies):
        # A weak foe is anyone who is alive and whose element is in our strengths list
        return [ enemy for enemy in enemies if enemy.element in self.strengths and enemy.health > 0]

    def find_living_foes(self, enemies):
        # Just find a living target
        return [ enemy for enemy in enemies if enemy.health > 0]

    def find_living_allies(self, allies):
        return [ ally for ally in allies if ally.health > 0]

    # Try to figure out what our allies will do on their next turn
    def anticipate_ally_moves(self, allies, enemies):
        # Find out what our allies are planning to do
        moves = [(ally, ally.anticipate(allies, enemies)) for ally in allies if ally != self and ally.health > 0]
        # Figure out what order our allies will go in, so we can try
        # to help the next person in the move chain
        moves.sort(key=lambda ally: -ally[0].speed)
        # Send back the moves
        return moves

    def anticipate(self, allies, enemies):
        # Identify any targets that we're strong against
        weak_targets = self.find_weak_foes(enemies)

        if len(weak_targets) > 2:
            # If we're strong against more than one enemy,
            # Do a group attack to hit as many enemies as possible
            return (self.spells[1], enemies)
        elif len(weak_targets) > 0:
            # if there is only one enemy we're strong against, target
            # them specifically
            return (self.spells[0], weak_targets[0])
        else:
            # By default, say we're not sure what we'll do. It's too
            # early to tell
            return (None, None)

    def make_move(self, allies, enemies):
        # Identify any targets that we're strong against
        weak_targets = self.find_weak_foes(enemies)

        if len(weak_targets) > 2:
            # If we're strong against more than one enemy,
            # Do a group attack to hit as many enemies as possible
            return (self.spells[1], enemies)
        elif len(weak_targets) > 0:
            # if there is only one enemy we're strong against, target
            # them specifically
            return (self.spells[0], weak_targets[0])
        else:
            # We're weak against remaining enemies. What we should do
            # depends on the state of our allies

            # Find out what our allies are planning to do
            moves = self.anticipate_ally_moves(allies, enemies)

            # If any of our allies are targeting a specific enemy,
            # attack that enemy's defense
            for move in moves:
                if move[1] in enemies:
                    return (self.spells[2], move[1])

            # If none of our allies are alive or none of them know who
            # they're going to attack, then we'll just attack someone
            # random
            living = self.find_living_foes(enemies)

            # See how many of our remaining allies are actually
            # targeting an enemy or are simply uncertain (it's
            # possible that the only allies left are us and a healer,
            # so we should attack in that case)
            targeting_enemy = [ move for move in moves if move[1] == enemies or move[1] == None]

            if len(targeting_enemy) == 0:
                # Nobody else is targeting an enemy (or else they're
                # all dead) We should just hit someone
                return (self.spells[3], living[0])
            else:
                # Enemies are being targeted, but we don't know
                # exactly who will be hit. Lower the defense of the
                # enemy with the highest defense
                target = max(living, key=lambda enemy: enemy.speed)
                return (self.spells[2], target)
