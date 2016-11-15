import sys
import time
from simulation import Simulation


start_time = time.time()
sim = Simulation()  # Objects of the class Simulation are Talk of the Town simulations
# Simulate from the date specified as the start of town generation to the date specified
# as its terminus; both of these dates can be set in config/basic_config.py
try:
    sim.establish_setting()  # This is the worldgen procedure
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
# Start excavating dramatic intrigue from the raw emergent material produced
# during the simulation of the town's history
print "Excavating nuggets of dramatic intrigue..."
sim.story_recognizer.excavate()
