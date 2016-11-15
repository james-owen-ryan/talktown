class PersonalityConfig(object):
    """Configuration parameters related to character personality."""
    # The personality representation in this framework is the famous Big Five model (also
    # called the 'five-factor model'); the appeal of using this representation is that there
    # are many papers relating Big Five personality components to various human phenomena (whose
    # findings can easily be operationalized); it's also possible to develop higher-order personality
    # traits that are derived by using the Big Five component values in higher-order functions; the
    # major source for these values is [0]
    big_five_floor = -1.0
    big_five_cap = 1.0
    # These affect the personality values that characters will take if they are not taking after
    # a parent for a particular component
    big_five_mean = {
        # These represent population means for these five traits
        'openness': 0.375,
        'conscientiousness': 0.25,
        'extroversion': 0.15,
        'agreeableness': 0.35,
        'neuroticism': 0.0
    }
    big_five_sd = {
        # A person's value for a trait is generated from a normal distribution
        # around the trait's mean, with the value listed here as standard deviation --
        # these are very high to make enmity a possibility, because that requires
        # personality discord, which requires a decent amount of variance
        'openness': 0.5,
        'conscientiousness': 0.5,
        'extroversion': 0.5,
        'agreeableness': 0.5,
        'neuroticism': 0.5
    }
    # These probabilities specify the likelihood of a character taking after a parent with
    # regard to a particular personality component
    big_five_heritability_chance = {
        'openness': 0.57,
        'conscientiousness': 0.54,
        'extroversion': 0.49,
        'agreeableness': 0.48,
        'neuroticism': 0.42
    }
    big_five_inheritance_sd = {
        # PersonMentalModel will inherit a parent's trait, but with some variance
        # according to this standard deviation
        'openness': 0.05,
        'conscientiousness': 0.05,
        'extroversion': 0.05,
        'agreeableness': 0.05,
        'neuroticism': 0.05
    }
    # These are used to derive personality component_str (see personality.py)
    threshold_for_high_binned_personality_score = 0.4
    threshold_for_low_binned_personality_score = -0.4
