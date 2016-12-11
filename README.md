# Of Mages and Magic

A simple AI based fighting game for teaching Python

## Getting started

1. Install [python3](https://www.python.org/downloads/release/python-352/)
2. Clone the repository or [download](https://github.com/munnellg/OfMagesAndMagic/archive/master.zip) and unzip
3. Install the requirements by opening a terminal on the root of the project and typing `pip install -r requirements.txt`
4. Launch the game by typing on the terminal `python run.py`

## How to code an AI

The goal for *Of Mages and Magic* was to provide a simple programming
interface that would allow novice developers to write real,
functioning Python code while adding an interesting challenge to the
task of figuring out the language's syntax. This section of the README
will run through the basics of how this was implemented.

For every student, their task is to write a bot - a little piece of
code which will analyze the state of the game and make decisions based
on what it sees. To do this as student creates a blank python
file. We'll call ours `bot.py` for now.

Inside bot.py, the student should create a class called Mage and give
it an `__init__` function and a `make_move` function as shown below:

    class Mage:
        def __init__(self):
            return

        def make_move(self, enemies, allies):
            return

The `__init__` function will be run once per battle and should be used
to initialize the bot as desired by setting their stats, assigning
their spells, etc. The `make_move` function is called once per
turn. It takes as input a list of enemies and a list of allies. These
lists could be analysed to decide what the bot should do, but if
student's want they can program a completely introspective bot.

At a minimum, a Mage object should have the following attributes:

+ _name_ : The name to be printed on screen for the bot.
+ _attack_ : The attack power of the bot
+ _defense_ : Bot's ability to withstand damage
+ _health_ : Amount of damage bot can take before being eliminated
+ _speed_ : How fast the bot can move. Determines move order and
  evasion probability
+ _spells_ : A list of spells known by the bot. Should not be more
  than four elements long (a mage can only know four spells). Game
  will truncate longer lists
+ _element_ : The magic specialization of the bot. Should be one of
  "Fire", "Water", "Earth", "Thunder" or "Ice"

The sum of `attack`, `defense`, `health` and `speed` should not be
greater than 100. Basically, the students have 100 stat points which
they must allocate as their strategy dictates.

A spell must be included in the `spells` list before it can be used in
the `make_move` function. This is to encourage students to adopt
specific roles within their teams. One mage might learn several
high-power attack spells while another focuses on supportive, boosting
magic. A full list of spells in human readable format will be provided
elsewhere, but for now the definition for every spell in the game is
given in the `data/magic/magic.xml` file. By editing this file you can
alter the elemental strengths/weaknesses, add your own spells, add
your own elements or just play with the balance of spells already
provided.

Given these requirements, a bot's `__init__` function might look like
this:

    class Mage:
        def __init__(self):
            self.name = "Scott Sterling"
            self.element = "Fire"

            self.health  = 60
            self.attack  = 15
            self.defense = 15
            self.speed   = 10

            self.spells = [
                "Fireball",
                "Unmake"
            ]

        def make_move(self, enemies, allies):
            return

The shortest working make_move function is only a single line
long. See the sample below for a fire mage:

    def make_move(self, enemies, allies):
        return ("Fireball", enemies)

This will tell the bot to cast a fireball spell and target an enemy
from the enemies list. The bot has not chosen a specific target, so
the game will select one for them. However, the game does not guarantee
that it will pick a good (or even a living target). This is a minimum
effort bot and the quality of its behaviour reflects that.

A much better bot would attempt to scan the list of enemies to find a
target against which they are most effective. In the case of a fire
mage, fire does double damage to Ice and Thunder type enemies. Hence
we could write a for loop like this:

    def make_move( self, enemies, allies ):
        for enemy in enemies:
	        if enemy.element in ["Ice", "Thunder"] and enemy.health > 0:
                return ("Fireball", enemy)

This simple bot searches for enemies who are weak against fire and who
haven't been eliminated from the game yet (`enemy.health > 0`)

We could demonstrate list comprehensions here if we wanted to as follows:

    def make_move( self, enemies, allies ):
        living = [ enemy for enemy in enemies if enemy.health > 0]

        for enemy in living:
            if enemy.element in ["Ice", "Thunder"]:
                return ("Fireball", enemy)

A flaw in this bot is that it will not return anything if it does not
find an enemy that it is strong against. It should have some sort of
fallback behaviour. This could simply be to scan the enemies list for
anyone who is not dead and attack them:

    def make_move( self, enemies, allies ):
        living = [ enemy for enemy in enemies if enemy.health > 0]

        for enemy in living:
            if enemy.element in ["Ice", "Thunder"]:
                return ("Fireball", enemy)

        # Attack first "not dead" enemy
        return ("Fireball", living[0])

An alternative might be to fall back to a supporting role - boosting
the attack of allies or damaging the attack of enemies (a specialty
which the fire mage has). Let's go with the latter of these options
and pick an arbitrary living enemy whose attack stat we will reduce
with the "Unmake" spell:

    def make_move( self, enemies, allies ):
        living = [ enemy for enemy in enemies if enemy.health > 0]

        for enemy in living:
            if enemy.element in ["Ice", "Thunder"]:
                return ("Fireball", enemy)

        # Attack first "not dead" enemy
        return ("Unmake", living[0])

So, our complete bot would look something like this:

    class Mage:
        def __init__(self):
            self.name = "Scott Sterling"
            self.element = "Fire"

            self.health  = 60
            self.attack  = 15
            self.defense = 15
            self.speed   = 10

            self.spells = [
                "Fireball",
                "Unmake"
            ]

        def make_move(self, enemies, allies):
            living = [ enemy for enemy in enemies if enemy.health > 0]

            for enemy in living:
                if enemy.element in ["Ice", "Thunder"]:
                    return ("Fireball", enemy)

            return ("Unmake", living[0])

It is crucial to note that, once the class is called `Mage` and
provides the basic required stats and functions, the students can
extend it any way they wish. They can add more functions to the
class - e.g. a function which finds an ally with the lowest health and
returns them as a potential healing target

Students may add extra attributes to their class, like a `max_health`
attribute which can be used to determine how much health they have
lost through simple arithmetic `lost = self.max_health - self.health`

Teams of students may agree on a series of extensions to their bots
which they can use to coordinate for attacks, e.g. every bot will also
supply an analyze function which will examine the game state and
approximate the decision that will be reached by the `make_move`
function allies can ask eachother what they think they are going to do
next and work together to take down a particularly powerful opponent

Although I haven't tested it, I don't see why learning algorithms such
as genetic algorithms could not be demonstrated with the bot interface
provided, assuming the bot attributes were appropriately chosen.

## How to manage teams

On startup, Of Mages and Magic reads the `data/teams.json` file to
determine which bots it should load and how these bots are organised
into teams. The file has a simple dictionary structure as shown in the
sample below:

    {
        "Alpha Squad": [
            "teams.alpha_squad.alpha1",
            "teams.alpha_squad.alpha2",
            "teams.alpha_squad.alpha3",
            "teams.alpha_squad.alpha4",
            "teams.alpha_squad.alpha5"
        ],
        "The Mystic Marvels": [
            "teams.mystic_marvels.allanon",
            "teams.mystic_marvels.minerva",
            "teams.mystic_marvels.gandalf",
            "teams.mystic_marvels.merlin",
            "teams.mystic_marvels.morrigan"
        ]
    }

This would tell the game to load two teams - "Alpha Squad" and "The
Mystic Marvels". Each line inbetween the square brackets gives the
location of each bot to be loaded for that team.

For example, the Allanon bot is located in the file
`teams/mystic_marvels/allanon.py`. A bot can belong to many different
teams and the name of the bot's file does not have to be the same as
the name printed on screen. However, there should be no spaces in any
of the directory names leading to the file, i.e. we couldn't do this -
`teams.mystic marvels.allanon`

Note that every folder leading up to the bot (including the one
containing the bot itself) must contain an `__init__.py` file. So the
directory structure described above would look like this:

    teams/
    |
    |---- __init__.py
    |
    |---- alpha_squad/
    |     |
    |     |---- __init__.py
    |     |---- alpha1.p
    |     |---- alpha2.py
    |      |---- alpha3.py
    |      |---- alpha4.py
    |      |---- alpha5.py
    |
    |-----mystic_marvels/
          |
          |---- __init__.py
          |---- allanon.py
          |---- gandalf.py
          |---- merlin.py
          |---- minirva.py
          |---- morrigan.py

The directory structure does not affect the organization of the
teams. The following structure for `data/teams.json` is just as valid as
the previous one

    {
        "I Can Haz Team?": [
            "teams.alpha_squad.alpha1",
            "teams.mystic_marvels.morrigan"
        ],
        "One Trick Pony": [
            "teams.mystic_marvels.gandalf",
            "teams.mystic_marvels.gandalf",
            "teams.mystic_marvels.gandalf",
            "teams.mystic_marvels.gandalf"
            "teams.mystic_marvels.gandalf",      
        ]
    }

Although it's not enforced, you should not have teams that are larger
than 5 members. The current version of the graphical display just
can't handle more than that.

## How to create a tournament

If you've created the `data/teams.json` file as described above, then
the game will load it and build a league for you. So far the league
randomly pits each team against two other teams. So a team can earn a
maximum of two points in the league table. If there is a tie for a
winning position then the league will restructure itself and play out
the tie breaker between winning teams

This is not a great structure and any suggestions for an improved
league will be gratefully received
