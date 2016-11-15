class AppearanceConfig(object):
    """Configuration parameters related to character appearance."""
    # This part of the system is so fleshed out because appearance is a critical component
    # in the original framing of Talk of the Town gameplay, where two players are navigating
    # NPC knowledge structures to determine the identity (namely the appearance) of the other
    # player's character; most of the parameters specified in this file define probability
    # ranges, where the selected value will be the one whose range a random number between
    # 0.0 and 1.0 falls into (and thus ones above 1.0 -- e.g., 999 -- will never be selected)
    facial_feature_distributions_male = {
        "skin color": [
            ((0.0, 0.1), 'black'),
            ((0.1, 0.2), 'brown'),
            ((0.2, 0.4), 'beige'),
            ((0.4, 0.6), 'pink'),
            ((0.6, 1.0), 'white')
        ],
        "head size": [
            ((0.0, 0.2), 'small'),
            ((0.2, 0.5), 'medium'),
            ((0.5, 1.0), 'large'),
        ],
        "head shape": [
            ((0.0, 0.4), 'square'),
            ((0.4, 0.6), 'circle'),
            ((0.6, 0.65), 'heart'),
            ((0.65, 1.0), 'oval')
        ],
        "hair length": [
            # TODO make this depend on era
            ((0.0, 0.0), 'bald'),
            ((0.0, 0.65), 'short'),
            ((0.65, 0.95), 'medium'),
            ((0.95, 1.0), 'long')
        ],
        "hair color": [
            ((0.0, 0.4), 'black'),
            ((0.4, 0.75), 'brown'),
            ((0.75, 0.9), 'blonde'),
            ((0.9, 1.0), 'red'),
            ((999, 999), 'gray'),
            ((999, 999), 'white'),
            ((999, 999), 'green'),
            ((999, 999), 'blue'),
            ((999, 999), 'purple')
        ],
        "eyebrow size": [
            ((0.0, 0.3), 'small'),
            ((0.3, 0.7), 'medium'),
            ((0.7, 0.9), 'large'),
            ((0.9, 1.0), 'unibrow'),
        ],
        "eyebrow color": [
            ((0.0, 0.35), 'black'),
            ((0.35, 0.55), 'brown'),
            ((0.55, 0.75), 'blonde'),
            ((0.75, 0.8), 'red'),
            ((0.8, 0.875), 'gray'),
            ((0.875, 0.95), 'white'),
            ((0.95, 0.97), 'green'),
            ((0.97, 0.99), 'blue'),
            ((0.99, 1.0), 'purple')
        ],
        "mouth size": [
            ((0.0, 0.3), 'small'),
            ((0.3, 0.7), 'medium'),
            ((0.7, 1.0), 'large')
        ],
        "ear size": [
            ((0.0, 0.3), 'small'),
            ((0.3, 0.7), 'medium'),
            ((0.7, 1.0), 'large')
        ],
        "ear angle": [
            ((0.0, 0.8), 'flat'),
            ((0.8, 1.0), 'protruding')
        ],
        "nose size": [
            ((0.0, 0.3), 'small'),
            ((0.3, 0.7), 'medium'),
            ((0.7, 1.0), 'large')
        ],
        "nose shape": [
            ((0.0, 0.4), 'long'),
            ((0.4, 0.6), 'broad'),
            ((0.6, 0.8), 'upturned'),
            ((0.8, 1.0), 'pointy')
        ],
        "eye size": [
            ((0.0, 0.3), 'small'),
            ((0.3, 0.7), 'medium'),
            ((0.7, 1.0), 'large')
        ],
        "eye shape": [
            ((0.0, 0.6), 'round'),
            ((0.6, 0.7), 'almond'),
            ((0.7, 1.0), 'thin')
        ],
        "eye color": [
            ((0.0, 0.3), 'black'),
            ((0.3, 0.6), 'brown'),
            ((0.6, 0.8), 'blue'),
            ((0.8, 0.95), 'green'),
            ((0.95, 1.0), 'yellow'),
            ((999, 999), 'gray'),
            ((999, 999), 'red'),
            ((999, 999), 'purple'),
            ((999, 999), 'white'),
        ],
        "eye horizontal settedness": [
            ((0.0, 0.3), 'narrow'),
            ((0.3, 0.7), 'middle'),
            ((0.7, 1.0), 'wide'),
        ],
        "eye vertical settedness": [
            ((0.0, 0.3), 'high'),
            ((0.3, 0.7), 'middle'),
            ((0.7, 1.0), 'low'),
        ],
        "facial hair style": [
            ((0.0, 0.5), 'none'),
            ((0.5, 0.65), 'mustache'),
            ((0.65, 0.8), 'full beard'),
            ((0.8, 0.9), 'goatee'),
            ((0.9, 0.97), 'sideburns'),
            ((0.97, 1.0), 'soul patch'),
        ],
        "freckles": [
            ((0.0, 0.8), 'no'),  # These aren't booleans because Face.Feature extends str, not bool
            ((0.8, 1.0), 'yes'),
        ],
        "birthmark": [
            ((0.0, 0.85), 'no'),
            ((0.85, 1.0), 'yes'),
        ],
        "scar": [
            ((0.0, 0.85), 'no'),
            ((0.85, 1.0), 'yes'),
        ],
        "tattoo": [
            ((0.0, 0.95), 'no'),
            ((0.95, 1.0), 'yes'),
        ],
        "glasses": [
            ((0.0, 0.7), 'no'),
            ((0.7, 1.0), 'yes'),
        ],
        "sunglasses": [
            ((0.0, 0.8), 'no'),
            ((0.8, 1.0), 'yes'),
        ]
    }
    facial_feature_distributions_female = {
        "skin color": facial_feature_distributions_male["skin color"],
        "head size": [
            ((0.0, 0.6), 'small'),
            ((0.6, 0.8), 'medium'),
            ((0.8, 1.0), 'large'),
        ],
        "head shape": [
            ((0.0, 0.1), 'square'),
            ((0.1, 0.3), 'circle'),
            ((0.3, 0.8), 'heart'),
            ((0.8, 1.0), 'oval'),
        ],
        "hair length": [
            ((0.0, 0.0), 'bald'),
            ((0.0, 0.2), 'short'),
            ((0.2, 0.45), 'medium'),
            ((0.45, 1.0), 'long'),
        ],
        "hair color": facial_feature_distributions_male["hair color"],
        "eyebrow size": [
            ((0.0, 0.7), 'small'),
            ((0.7, 0.9), 'medium'),
            ((0.9, 0.95), 'large'),
            ((0.95, 1.0), 'unibrow'),
        ],
        "eyebrow color": facial_feature_distributions_male["eyebrow color"],
        "mouth size": [
            ((0.0, 0.6), 'small'),
            ((0.6, 0.85), 'medium'),
            ((0.85, 1.0), 'large'),
        ],
        "ear size": [
            ((0.0, 0.6), 'small'),
            ((0.6, 0.85), 'medium'),
            ((0.85, 1.0), 'large'),
        ],
        "ear angle": facial_feature_distributions_male["ear angle"],
        "nose size": facial_feature_distributions_male["nose size"],
        "nose shape": facial_feature_distributions_male["nose shape"],
        "eye size": facial_feature_distributions_male["eye size"],
        "eye shape": facial_feature_distributions_male["eye shape"],
        "eye color": facial_feature_distributions_male["eye color"],
        "eye horizontal settedness": facial_feature_distributions_male["eye horizontal settedness"],
        "eye vertical settedness": facial_feature_distributions_male["eye vertical settedness"],
        "facial hair style": [
            ((0.0, 1.0), 'none'),
            ((0.0, 0.0), 'mustache'),
            ((0.0, 0.0), 'full beard'),
            ((0.0, 0.0), 'goatee'),
            ((0.0, 0.0), 'sideburns'),
            ((0.0, 0.0), 'soul patch'),
        ],
        "freckles": facial_feature_distributions_male["freckles"],
        "birthmark": facial_feature_distributions_male["birthmark"],
        "scar": facial_feature_distributions_male["scar"],
        "tattoo": facial_feature_distributions_male["tattoo"],
        "glasses": facial_feature_distributions_male["glasses"],
        "sunglasses": facial_feature_distributions_male["sunglasses"],
    }
    child_skin_color_given_parents = {
        ('black', 'brown'): 'brown',
        ('brown', 'black'): 'brown',
        ('black', 'beige'): 'brown',
        ('beige', 'black'): 'brown',
        ('black', 'pink'): 'beige',
        ('pink', 'black'): 'beige',
        ('black', 'white'): 'beige',
        ('white', 'black'): 'beige',
        ('brown', 'beige'): 'beige',
        ('beige', 'brown'): 'beige',
        ('brown', 'pink'): 'beige',
        ('pink', 'brown'): 'beige',
        ('brown', 'white'): 'beige',
        ('white', 'brown'): 'beige',
        ('beige', 'pink'): 'beige',
        ('pink', 'beige'): 'beige',
        ('beige', 'white'): 'beige',
        ('white', 'beige'): 'beige',
        ('pink', 'white'): 'pink',
        ('white', 'pink'): 'pink',
    }
    facial_feature_type_heritability = {
        "skin color": 1.0,
        "head size": 0.75,
        "head shape": 0.75,
        "hair length": 0.05,  # From nurture, not nature
        "hair color": 0.75,
        "eyebrow size": 0.75,
        "eyebrow color": 0.75,
        "mouth size": 0.75,
        "ear size": 0.75,
        "ear angle": 0.75,
        "nose size": 0.75,
        "nose shape": 0.75,
        "eye size": 0.75,
        "eye shape": 0.75,
        "eye color": 0.75,
        "eye horizontal settedness": 0.75,
        "eye vertical settedness": 0.75,
        "facial hair style": 0.05,  # From nurture
        "freckles": 0.75,
        "birthmark": 0.00,
        "scar": 0.00,
        "tattoo": 0.05,  # From nurture
        "glasses": 0.6,
        "sunglasses": 0.05  # From nurture
    }
    facial_feature_variant_heritability = {
        "skin color": 1.0,
        "head size": 0.75,
        "head shape": 0.75,
        "hair length": 0.05,  # From nurture, not nature
        "hair color": 0.75,
        "eyebrow size": 0.75,
        "eyebrow color": 0.75,
        "mouth size": 0.75,
        "ear size": 0.75,
        "ear angle": 0.75,
        "nose size": 0.75,
        "nose shape": 0.75,
        "eye size": 0.75,
        "eye shape": 0.75,
        "eye color": 0.75,
        "eye horizontal settedness": 0.75,
        "eye vertical settedness": 0.75,
        "facial hair style": 0.0,
        "freckles": 0.75,
        "birthmark": 0.0,
        "scar": 0.0,
        "tattoo": 0.05,  # From nurture
        "glasses": 0.6,
        "sunglasses": 0.05  # From nurture
    }
    facial_feature_chance_inheritance_according_to_sex = {
        # The chance someone inherits only from parent/grandparent of the same sex, given
        # the dice already has them inheriting and not generating from population distribution
        "head size": 0.8,
        "head shape": 0.8,
        "hair length": 1.0,
        "hair color": 0.0,
        "eyebrow size": 0.0,
        "eyebrow color": 0.0,
        "mouth size": 0.0,
        "ear size": 0.0,
        "ear angle": 0.0,
        "nose size": 0.0,
        "nose shape": 0.0,
        "eye size": 0.0,
        "eye shape": 0.0,
        "eye color": 0.0,
        "eye horizontal settedness": 0.0,
        "eye vertical settedness": 0.0,
        "facial hair style": 1.0,
        "freckles": 0.0,
        "birthmark": 0.0,
        "scar": 0.0,
        "tattoo": 0.0,  # From nurture
        "glasses": 0.0,
        "sunglasses": 0.00  # From nurture
    }
    child_skin_color_given_parents = {
        ('black', 'brown'): 'brown',
        ('brown', 'black'): 'brown',
        ('black', 'beige'): 'brown',
        ('beige', 'black'): 'brown',
        ('black', 'pink'): 'beige',
        ('pink', 'black'): 'beige',
        ('black', 'white'): 'beige',
        ('white', 'black'): 'beige',
        ('brown', 'beige'): 'beige',
        ('beige', 'brown'): 'beige',
        ('brown', 'pink'): 'beige',
        ('pink', 'brown'): 'beige',
        ('brown', 'white'): 'beige',
        ('white', 'brown'): 'beige',
        ('beige', 'pink'): 'beige',
        ('pink', 'beige'): 'beige',
        ('beige', 'white'): 'beige',
        ('white', 'beige'): 'beige',
        ('pink', 'white'): 'pink',
        ('white', 'pink'): 'pink',
    }
    chance_eyebrows_are_same_color_as_hair = 0.8
