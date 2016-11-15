import random


class MiscellaneousCharacterConfig(object):
    """Configuration parameters related to assorted aspects of characters."""
    # Infertility parameters (defined using a source that I failed to record)
    male_infertility_rate = 0.07
    female_infertility_rate = 0.11
    # Sexuality parameters (defined using a source that I failed to record)
    homosexuality_incidence = 0.045
    bisexuality_incidence = 0.01
    asexuality_incidence = 0.002
    # Memory parameters; memory is important in the full Talk of the Town framework, since
    # it affects the likelihood of misremembering knowledge -- that's been taken out here, but
    # I can imagine memory still being useful in some way, so I'm keeping that here
    memory_mean = 1.0
    memory_sd = 0.05
    memory_cap = 1.0
    memory_floor = 0.5  # After severe memory loss from aging
    memory_floor_at_birth = 0.8  # Worst possible memory of newborn
    memory_sex_diff = 0.03  # Men have worse memory, studies show
    memory_heritability = 0.6  # Couldn't quickly find a study on this -- totally made up
    memory_heritability_sd = 0.05
    # Parameters relating to the naming of children
    chance_son_inherits_fathers_exact_name = 0.03
    chance_child_inherits_first_name = 0.1
    chance_child_inherits_middle_name = 0.25
    frequency_of_naming_after_father = 12  # These are relative frequencies
    frequency_of_naming_after_grandfather = 5
    frequency_of_naming_after_greatgrandfather = 2
    frequency_of_naming_after_mother = 0
    frequency_of_naming_after_grandmother = 5
    frequency_of_naming_after_greatgrandmother = 2
    # People ex nihilo are characters who originate from outside the town (and
    # thus were born outside the simulation, which means they do not have actual parents
    # who were also characters in the simulation); see the PersonExNihilo subclass in
    # person.py for more info
    function_to_determine_person_ex_nihilo_age_given_job_level = (
        lambda job_level: 18 + random.randint(2 * job_level, 7 * job_level)
    )
    function_to_determine_chance_person_ex_nihilo_starts_with_family = (
        # The larger the town population, the lower the chance a P.E.N. moves
        # into town with a family
        lambda town_pop: (200.0 - town_pop) / 1000.0
    )
    person_ex_nihilo_age_at_marriage_mean = 23
    person_ex_nihilo_age_at_marriage_sd = 2.7
    person_ex_nihilo_age_at_marriage_floor = 17
    # Parameters related to character money -- this is a system I never quite fleshed out (initially
    # characters would be paid for working and would remunerate others for contract work, but I took
    # that out); leaving this in in case it inspires anyone to do something along economic lines
    amount_of_money_generated_people_from_outside_town_start_with = 5000
