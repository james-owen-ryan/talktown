import random


class BasicConfig(object):
    """Configuration parameters related to basic aspects of the simulation."""
    # Seed for the psuedorandom number generator; if a given seed is held constant
    # across simulation instances, and if the codebase hasn't changed, the towns
    # generated for the simulation instances will be identical
    # seed = int(random.random()*9999999)
    seed = 8
    random.seed(seed)
    # Date that town generation starts
    year_worldgen_begins = 1839
    month_worldgen_begins = 8
    day_of_month_worldgen_begins = 19
    date_worldgen_begins = (  # Do not alter
        year_worldgen_begins,
        month_worldgen_begins,
        day_of_month_worldgen_begins
    )
    # Date that town generation ends
    year_worldgen_ends = 1979
    month_worldgen_ends = 8
    day_of_month_worldgen_ends = 19
    date_worldgen_ends = (  # Do not alter
        year_worldgen_ends,
        month_worldgen_ends,
        day_of_month_worldgen_ends
    )
    # Number of timesteps to simulate each year during world generation (each day in that span will
    # have two timesteps -- day, night -- and this parameter specifies how many will actually be simulated)
    number_of_timesteps_to_simulate_a_year = 10.0  # Setting for Bad News: 3.6
    chance_of_a_timestep_being_simulated = number_of_timesteps_to_simulate_a_year / (365 * 2.0)  # Do not alter
    # -- LEVERS FOR ADJUSTING POPULATIONS --
    # The primary driver of population growth is new businesses, which may cause new people
    # to enter the simulation to begin working there, or at the least may prevent unemployed
    # people from leaving town (and thus the simulation) for work; the primary drivers of population
    # decrease are businesses shutting down (which cause people to become unemployed, which may
    # compel them to leave town) and, more directly, the explicit probabilities of unemployed people
    # and new adults leaving town (which are adjustable below)
    # --
    # Chance of a business opening on any timestep (businesses may be opened on timesteps
    # that aren't actually being simulated)
    chance_a_business_opens_some_timestep = (1 / 730.) * 0.7  # Thus, 0.7 will open a year
    # Chance a business shuts down some timestep
    chance_a_business_closes_some_timestep = (1 / 730.) / 60  # Thus, average business will last 60 years
    # Chance an unemployed person leaves the town on a simulated timestep
    chance_an_unemployed_person_departs_on_a_simulated_timestep = (
        # Currently set so that an unemployed person would be expected to leave the
        # town after four years of being unemployed (so change the 4.0 to change this); I
        # have it set at four so that characters in times where people start working at
        # 18 may get a college degree (which currently happens automatically when someone
        # is 22 and unemployed)
        1.0 / (chance_of_a_timestep_being_simulated * 730 * 4.0)
    )
    # Chance that a character will leave town (and thus the simulation) upon the birthday
    # that represents them reaching adulthood (which birthday this is differs by era)
    chance_a_new_adult_decides_to_leave_town = 0.1
