class MarriageConfig(object):
    """Configuration parameters related to sex, love, marriage, and divorce."""
    # Marriage proposal
    min_mutual_spark_value_for_someone_to_propose_marriage = 10
    marriageable_age = 18  # TODO check historical data for this
    # Naming issues related to marriage
    chance_one_newlywed_takes_others_name = 0.9
    chance_newlyweds_decide_children_will_get_hyphenated_surname = 0.4
    chance_a_newlywed_keeps_former_love_interest = 0.01
    chance_stepchildren_take_stepparent_name = 0.3
    age_after_which_stepchildren_will_not_take_stepparent_name = 6
    #
    function_to_determine_chance_married_couple_are_trying_to_conceive = (
        # This is the chance they try to conceive across a given year -- it decreases
        # according to the number of kids they have
        lambda n_kids: 0.4 / (n_kids + 1)
    )
    # Divorce
    chance_a_divorce_happens_some_timestep = 0.001
    chance_a_divorcee_falls_out_of_love = 0.9
    new_raw_spark_value_for_divorcee_who_has_fallen_out_of_love = -500.0
    chance_a_male_divorcee_is_one_who_moves_out = 0.7
    function_to_derive_chance_spouse_changes_name_back = (
        lambda years_married: min(
            0.9 / ((years_married + 0.1) / 4.0),  # '+0.1' is to avoid ZeroDivisionError
            0.9
        )
    )
