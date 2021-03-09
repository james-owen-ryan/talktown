import json
import sys
import time
from simulation import Simulation

def create_simulation():
    # Generate a town!
    start_time = time.time()
    sim = Simulation()  # Objects of the class Simulation are Talk of the Town simulations
    # Simulate from the date specified as the start of town generation to the date specified
    # as its terminus; both of these dates can be set in config/basic_config.py
    try:
        sim.establish_setting()  # This is the worldgen procedure; it will simulate until the date specified in basic_config.py
        return sim
    except KeyboardInterrupt:  # Enter "ctrl+C" (a keyboard interrupt) to end worldgen early
        # In the case of keyboard interrupt, we need to tie up a few loose ends
        sys.stdout.write('\r{}'.format(' ' * 94))  # Clear out the last sampled event written to stdout
        sys.stdout.write('\rWrapping up...')
        sim.advance_time()
        for person in list(sim.town.residents):
            person.routine.enact()

def dictionary_to_json(career_trajectory_dictionary):
  json_data = json.dumps(career_trajectory_dictionary)
  output_file = open('sifting_heuristic/career_trajectory_dictionary.json', 'w')
  output_file.write(json_data)
  output_file.close()

def rate_chars():
    sim = create_simulation()
    story_recognizer = sim.story_recognizer
    unrequited_love_cases = story_recognizer._excavate_unrequited_love_cases()
    love_triangles = story_recognizer._excavate_love_triangles()
    misanthropes = story_recognizer._excavate_misanthropes()
    rivalries = story_recognizer._excavate_misanthropes()
    rags_to_riches = story_recognizer._excavate_rags_to_riches()
    riches_to_rags = story_recognizer._excavate_riches_to_rags()
    town = sim.town
    all_time_residents = town.all_time_residents
    character_interesting_rating = {}
    for person in all_time_residents:
        rating = 0
        enemies = person.enemies
        num_enemies = len(enemies)
        rating += num_enemies
        num_unrequited = 0
        for case in unrequited_love_cases:
            if person == case.nonreciprocator:
                rating += 1
                num_unrequited += 1
        num_love_triangles = 0
        for triangle in love_triangles:
            if person in triangle.subjects:
                rating += 3
                num_love_triangles += 1
        is_misanthrope = False;
        for misanthrope in misanthropes:
            if person == misanthrope.misanthrope:
                is_misanthrope = True
                rating += 10
        num_rivalries = 0
        for rivalry in rivalries: 
            if person in rivalry.subjects:
                num_rivalries += 1
                rating += 1
        is_rags_to_riches = False
        for case in rags_to_riches:
            if person in case.subjects:
                is_rags_to_riches = True
                rating += 30
        is_riches_to_rags = False
        for case in riches_to_rags:
            if person in case.subjects:
                is_riches_to_rags = True
                rating += 30
        if rating > 10:
          character_interesting_rating[person] = {}
          character_interesting_rating[person]['rating'] = rating
          character_interesting_rating[person]['num_enemies'] = num_enemies
          character_interesting_rating[person]['num_love_triangles'] = num_love_triangles
          character_interesting_rating[person]['num_unrequited'] = num_unrequited
          character_interesting_rating[person]['is_rags_to_riches'] = is_rags_to_riches
          character_interesting_rating[person]['is_riches_to_rags'] = is_riches_to_rags
          character_interesting_rating[person]['num_rivalries'] = num_rivalries
          character_interesting_rating[person]['is_misanthrope'] = is_misanthrope
    return character_interesting_rating

character_interesting_rating = rate_chars()

sorted_list = sorted(character_interesting_rating.items(), key=lambda x:x[1])

for i in character_interesting_rating:
  print(i.name)
  print(str(character_interesting_rating[i]) + '\n')
