class MiscellaneousCharacterDecisionMakingConfig(object):
    """Configuration parameters related to how characters make decisions."""
    # People finding new homes (these weights affect how characters will score prospective
    # vacant homes and/or lots)
    penalty_for_having_to_build_a_home_vs_buying_one = 0.1  # i.e., relative desire to build
    desire_to_live_near_family_base = 0.3  # Scale of -1 to 1; affected by personality
    desire_to_live_near_family_floor = -2
    desire_to_live_near_family_cap = 2
    pull_to_live_near_a_friend = 1.5
    pull_to_live_near_family = {
        # Arbitrary units (are just relative to each other; will also get
        # altered by the person's desire to live near family)
        'daughter': 7,
        'son': 7,
        'mother': 5,
        'father': 5,
        'granddaughter': 3,
        'grandson': 3,
        'sister': 2,
        'brother': 2,
        'grandmother': 2,
        'grandfather': 2,
        'greatgrandmother': 2,
        'greatgrandfather': 2,
        'niece': 1,
        'nephew': 1,
        'aunt': 1,
        'uncle': 1,
        'cousin': 1,
        None: 0,
    }
    pull_to_live_near_workplace = 5
    # People hiring characters to work at their companies; again, these are weights
    # that are used in a scoring procedure
    preference_to_hire_immediate_family = 15
    preference_to_hire_extended_family = 7
    preference_to_hire_from_within_company = 5
    preference_to_hire_friend = 4
    preference_to_hire_immediate_family_of_an_employee = 3
    preference_to_hire_extended_family_of_an_employee = 2
    dispreference_to_hire_enemy = -1
    preference_to_hire_acquaintance = 0.5
    unemployment_occupation_level = 0.5  # Affects scoring of job candidates
    # People contracting people (e.g., realtors, architects); again, these are weights
    # that are used in a scoring procedure
    function_to_derive_score_multiplier_bonus_for_experience = (
        lambda years_experience: years_experience ** 0.2
    )
    preference_to_contract_immediate_family = 9
    preference_to_contract_friend = 2
    dispreference_to_contract_enemy = -2
    preference_to_contract_former_contract = 2
    preference_to_contract_extended_family = 1
    preference_to_contract_acquaintance = 0.5
