class LifeCycleConfig(object):
    """Configuration parameters related to character life cycles (birth, life, death, sex, aging, etc.)."""
    # Sex
    chance_sexual_protection_does_not_work = 0.01
    # Pregnancy
    function_to_determine_chance_of_conception = lambda female_age: max(
        # Decreases exponentially with age (source missing)
        female_age / 10000., (100 - ((female_age ** 1.98) / 20.)) / 100
    )
    # Aging
    age_when_people_start_graying = 48
    age_when_men_start_balding = 48
    chance_someones_hair_goes_gray_or_white = 0.02
    chance_someones_loses_their_hair_some_year = 0.02
    # Death
    chance_someone_dies_some_timestep = 0.125
    function_to_derive_chance_a_widow_remarries = (
        lambda years_married: 1.0 / (int(years_married) + 4)
    )
    # Life phases
    age_children_start_going_to_school = 5
    age_people_start_working = lambda year: 14 if year < 1920 else 16 if year < 1960 else 18
    chance_mother_of_young_children_stays_home = lambda year: (
        # Determines the chance the mother of a new child will intend to
        # enter the workforce (versus staying home), given a partner who
        # is in the workforce; this changes over time according to results
        # of a study of census data by ancestry.com
        0.07 if year < 1910 else
        0.08 if year < 1920 else
        0.09 if year < 1930 else
        0.11 if year < 1941 else
        0.16 if year < 1950 else
        0.28 if year < 1960 else
        0.40 if year < 1970 else
        0.54 if year < 1980 else
        0.67 if year < 1990 else
        0.64 if year < 2000 else
        0.71
    )
    chance_employed_adult_will_move_out_of_parents_on_simulated_timestep = 0.1
