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
      town = sim.town
      return town
  except KeyboardInterrupt:  # Enter "ctrl+C" (a keyboard interrupt) to end worldgen early
      # In the case of keyboard interrupt, we need to tie up a few loose ends
      sys.stdout.write('\r{}'.format(' ' * 94))  # Clear out the last sampled event written to stdout
      sys.stdout.write('\rWrapping up...')
      sim.advance_time()
      for person in list(sim.town.residents):
          person.routine.enact()

def dictionary_to_json(career_trajectory_dictionary):
  json_data = json.dumps(career_trajectory_dictionary)
  output_file = open('sifting_heuristic/career_trajectory_dictionary_m.json', 'w')
  output_file.write(json_data)
  output_file.close()

def create_career_trajectory_dictionary():
  #career_trajectory_dictionary = {}
  #json_file = open('sifting_heuristic/career_trajectory_dictionary.json', 'r')
  #career_trajectory_dictionary = json.loads(json_file.read())
  career_trajectory_dictionary = {}
  town = create_simulation()
  all_time_residents = town.all_time_residents
  for resident in all_time_residents:
    occupations = []
    occupations_levels = []
    previous = "occupation"
    for occupation in resident.occupations:
      if occupation.vocation == previous:
        continue
      occupations.append(occupation.vocation)
      previous = occupation.vocation
      occupations_levels.append(occupation.level)
    if 1 in occupations_levels:
      continue
    occupations_tuple = tuple(occupations)
    if str(occupations_tuple) in career_trajectory_dictionary.keys():
      career_trajectory_dictionary[str(occupations_tuple)] += 1 
    else:
      career_trajectory_dictionary[str(occupations_tuple)] = 1  
  #json_file.close()
  dictionary_to_json(career_trajectory_dictionary)
  print(sorted(career_trajectory_dictionary.items(), key=lambda x:x[1]))

'''
for i in range(100):
  try:
    create_career_trajectory_dictionary()
  except Exception as e:
    create_career_trajectory_dictionary()
'''

def calculate_trajectory_percentages():
  input_json_file = open('sifting_heuristic/career_trajectory_dictionary.json', 'r')
  career_trajectory_dictionary = json.loads(input_json_file.read())
  career_trajectory_percentages_dictionary = {}
  all_trajectories_count = 0.0
  for career in career_trajectory_dictionary:
    all_trajectories_count += career_trajectory_dictionary[career]
  for career in career_trajectory_dictionary:
    current_career_likelihood = float(career_trajectory_dictionary[career]) / all_trajectories_count
    if career_trajectory_dictionary[career] == 1:
      career_trajectory_percentages_dictionary[career] = current_career_likelihood
  print("Unemployed: " + str(career_trajectory_dictionary['()']))
  print("Unemployed percentage: " + str(career_trajectory_dictionary['()']/all_trajectories_count))
  json_data = json.dumps(career_trajectory_percentages_dictionary)
  input_json_file.close()
  output_json_file = open('sifting_heuristic/career_trajectory_percentages.json', 'w')
  output_json_file.write(json_data)
  output_json_file.close()

#calculate_trajectory_percentages()
create_career_trajectory_dictionary()





