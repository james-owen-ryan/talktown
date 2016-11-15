import sys
import time
from simulation import Simulation


# Generate a town!
start_time = time.time()
sim = Simulation()  # Objects of the class Simulation are Talk of the Town simulations
# Simulate from the date specified as the start of town generation to the date specified
# as its terminus; both of these dates can be set in config/basic_config.py
try:
    sim.establish_setting()  # This is the worldgen procedure
    town = sim.town
except KeyboardInterrupt:  # Enter "ctrl+C" (a keyboard interrupt) to end worldgen early
    # In the case of keyboard interrupt, we need to tie up a few loose ends
    sys.stdout.write('\r{}'.format(' ' * 94))  # Clear out the last sampled event written to stdout
    sys.stdout.write('\rWrapping up...')
    sim.advance_time()
    for person in list(sim.town.residents):
        person.routine.enact()
# Town generation was successful, so print out some basic info about the town
print "\nAfter {time_elapsed}s, town generation was successful!".format(
    time_elapsed=int(time.time()-start_time)
)
# Print out the town, population, and date
print "\nIt is now the {date}, in the town of {town}, pop. {population}.\n".format(
    date=sim.date[0].lower() + sim.date[1:],
    town=sim.town.name,
    population=sim.town.population
)
# Start excavating nuggets of dramatic intrigue from the raw emergent material produced
# during the simulation of the town's history
print "Excavating nuggets of dramatic intrigue..."
sim.story_recognizer.excavate()
# Save all this material to global variables, for convenience
unrequited_love_cases = sim.story_recognizer.unrequited_love_cases
love_triangles = sim.story_recognizer.love_triangles
extramarital_romantic_interests = sim.story_recognizer.extramarital_romantic_interests
asymmetric_friendships = sim.story_recognizer.asymmetric_friendships
misanthropes = sim.story_recognizer.misanthropes
sibling_rivalries = sim.story_recognizer.sibling_rivalries
business_owner_rivalries = sim.story_recognizer.business_owner_rivalries


# Here's some quick commands that you can use to explore your generated town
def outline_businesses():
    """Outline all the businesses, past and present, in this town."""
    print '\nFormer businesses in {town}:'.format(town=sim.town.name)
    for c in sim.town.former_companies:
        print '\t{}'.format(c)
    print '\nCurrent businesses in {town}:'.format(town=sim.town.name)
    for c in sim.town.companies:
        print '\t{}'.format(c)


def outline_character_locations():
    """Outline the locations in town, and who is currently at each one."""
    for location in sim.town.companies|sim.town.dwelling_places:
        print location
        if not location.people_here_now:
            print '\tno one here'
        else:
            for character in location.people_here_now:
                if character.routine.working:
                    print "\t{} (working as {})".format(character, character.routine.occasion, character.occupation.vocation)
                else:
                    print "\t{} ({})".format(character, character.routine.occasion)


def outline_gravestones():
    """Print out all the gravestones in the town."""
    for d in sim.town.deceased:
        print d.gravestone.description
