import random


class Personality(object):
    """A person's personality."""

    def __init__(self, person):
        """Initialize a Personality object."""
        self.person = person
        self.openness_to_experience = self._determine_personality_feature(feature_type="openness")
        self.conscientiousness = self._determine_personality_feature(feature_type="conscientiousness")
        self.extroversion = self._determine_personality_feature(feature_type="extroversion")
        self.agreeableness = self._determine_personality_feature(feature_type="agreeableness")
        self.neuroticism = self._determine_personality_feature(feature_type="neuroticism")
        self.interest_in_history = self._determine_interest_in_history()
        # Binned scores used as convenient personality hooks during Expressionist authoring
        config = person.sim.config
        if self.openness_to_experience > config.threshold_for_high_binned_personality_score:
            self.high_o, self.low_o = True, False
        elif self.openness_to_experience < config.threshold_for_low_binned_personality_score:
            self.high_o, self.low_o = False, True
        else:
            self.high_o, self.low_o = False, False
        if self.conscientiousness > config.threshold_for_high_binned_personality_score:
            self.high_c, self.low_c = True, False
        elif self.conscientiousness < config.threshold_for_low_binned_personality_score:
            self.high_c, self.low_c = False, True
        else:
            self.high_c, self.low_c = False, False
        if self.extroversion > config.threshold_for_high_binned_personality_score:
            self.high_e, self.low_e = True, False
        elif self.extroversion < config.threshold_for_low_binned_personality_score:
            self.high_e, self.low_e = False, True
        else:
            self.high_e, self.low_e = False, False
        if self.agreeableness > config.threshold_for_high_binned_personality_score:
            self.high_a, self.low_a = True, False
        elif self.agreeableness < config.threshold_for_low_binned_personality_score:
            self.high_a, self.low_a = False, True
        else:
            self.high_a, self.low_a = False, False
        if self.neuroticism > config.threshold_for_high_binned_personality_score:
            self.high_n, self.low_n = True, False
        elif self.neuroticism < config.threshold_for_low_binned_personality_score:
            self.high_n, self.low_n = False, True
        else:
            self.high_n, self.low_n = False, False

    def __str__(self):
        """Return string representation."""
        return "Personality of {}".format(self.person.name)

    @property
    def o(self):
        """Return this person's openness to experience."""
        return self.openness_to_experience

    @property
    def c(self):
        """Return this person's conscientiousness."""
        return self.conscientiousness

    @property
    def e(self):
        """Return this person's extroversion."""
        return self.extroversion

    @property
    def a(self):
        """Return this person's agreeableness."""
        return self.agreeableness

    @property
    def n(self):
        """Return this person's neuroticism."""
        return self.neuroticism

    @property
    def gregarious(self):
        """Return whether this person has a gregarious personality, which is a E+A+N- signal."""
        return True if self.high_e and self.high_a and self.low_n else False

    @property
    def cold(self):
        """Return whether this person has a cold personality, which is a E-A+C+ signal."""
        return True if self.low_e and self.high_a and self.high_c else False

    def _determine_personality_feature(self, feature_type):
        """Determine a value for a Big Five personality trait."""
        config = self.person.sim.config
        feature_will_get_inherited = (
            self.person.biological_mother and
            random.random() < config.big_five_heritability_chance[feature_type]
        )
        if feature_will_get_inherited:
            # Inherit this trait (with slight variance)
            takes_after = random.choice([self.person.biological_father, self.person.biological_mother])
            feature_value = random.normalvariate(
                self._get_a_persons_feature_of_type(person=takes_after, feature_type=feature_type),
                config.big_five_inheritance_sd[feature_type]
            )
        else:
            takes_after = None
            # Generate from the population mean
            feature_value = random.normalvariate(
                config.big_five_mean[feature_type], config.big_five_sd[feature_type]
            )
        if feature_value < config.big_five_floor:
            feature_value = config.big_five_floor
        elif feature_value > config.big_five_cap:
            feature_value = config.big_five_cap
        feature_object = Feature(value=feature_value, inherited_from=takes_after)
        return feature_object

    def _determine_interest_in_history(self):
        """Determine this person's interest in history, given their other personality traits.

        In lieu of any actual sources (since I couldn't find any), this is entirely home-cooked
        based on my intuitions.
        """
        personality_component = (float(self.o)*2 + float(self.c)*0.5 + float(self.a))
        chance_component = random.random() * (1.0 if random.random() < 0.5 else -1.0)
        # Now divide by 4.5 to get this on the -1 to 1 scale (since -4.5 is the lowest
        # possible sum of personality_component+chance_component and 4.5 is the highest)
        interest_in_history = (personality_component + chance_component) / 4.5
        return interest_in_history

    @staticmethod
    def _get_a_persons_feature_of_type(person, feature_type):
        """Return this person's value for the given personality feature."""
        features = {
            "openness": person.personality.openness_to_experience,
            "conscientiousness": person.personality.conscientiousness,
            "extroversion": person.personality.extroversion,
            "agreeableness": person.personality.agreeableness,
            "neuroticism": person.personality.neuroticism,
        }
        return features[feature_type]

    def component_str(self, component_letter):
        """Return a short string indicating the value for a personality component."""
        component_value = eval('self.{}'.format(component_letter))
        if component_value > 0.7:
            return 'very high'
        elif component_value > 0.4:
            return 'high'
        elif component_value > 0.1:
            return 'somewhat high'
        elif component_value > -0.1:
            return 'neutral'
        elif component_value > -0.4:
            return 'somewhat low'
        elif component_value > -0.7:
            return 'low'
        else:
            return 'very low'


class Feature(float):
    """A particular personality feature, i.e., a value for a particular personality attribute."""

    def __init__(self, value, inherited_from):
        """Initialize a Feature object.

        @param value: A float representing the value, on a scale from -1 to 1, for this
                      particular personality feature.
        @param inherited_from: The parent from whom this personality feature was
                               inherited, if any.
        """
        super(Feature, self).__init__()
        self.inherited_from = inherited_from

    def __new__(cls, value, inherited_from):
        """Do float stuff."""
        return float.__new__(cls, value)