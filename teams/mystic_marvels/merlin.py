class Mage:
    def __init__(self):
        self.name     = "Merlin"

        self.health   = 50
        self.attack   = 25
        self.defense  = 15
        self.speed    = 10

        self.element  = "Water"
        
        self.spells   = [
            "Absorb",
            "Sting of Neptune",
            "Healing Wave",
            "Kinetic Blast"
        ]

        # Remember base stats for reference later
        self.max_health    = self.health
        self.base_attack   = self.attack
        self.base_defense  = self.defense
        self.base_speed    = self.speed

        # Be aware of strengths and weaknesses
        self.strengths  = [ "Earth", "Fire" ]
        self.weaknesses = [ "Ice", "Thunder" ]

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

    def play_offensive(self, allies, enemies):
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
            # By default, just attack someone random
            living = self.find_living_foes(enemies)

            return (self.spells[3], living[0])
                

    def make_move(self, allies, enemies):
        living_allies = self.find_living_allies(allies)
        living_allies.sort(key=lambda ally: (float(ally.health)/ally.max_health))
        candidate = living_allies[0]

        # If one of our allies has been injured within certain bounds,
        # then heal them
        if float(candidate.health)/candidate.max_health < 0.8:
            return ("Healing Wave", candidate)

        # Otherwise, if no one is in critical need of healing, just
        # attack like everyone else
        return self.play_offensive(allies, enemies)
