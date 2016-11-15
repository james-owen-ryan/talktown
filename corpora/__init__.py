import os
import pickle
import random
import math


class Names(object):
    """A class that accesses names corpora to return random names."""
    names_by_decade = pickle.load(open(
        os.getcwd()+'/corpora/american_names_by_decade_with_'
        'fitted_probability_distributions.dat', 'rb'
    )
    )
    miscellaneous_masculine_forenames = tuple(
        name[:-1] for name in
        open(os.getcwd()+'/corpora/masculine_names.txt', 'r')
    )
    miscellaneous_feminine_forenames = tuple(
        name[:-1] for name in
        open(os.getcwd()+'/corpora/feminine_names.txt', 'r')
    )
    english_surnames = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/corpora/english_surnames.txt', 'r')
    )
    french_surnames = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/corpora/french_surnames.txt', 'r')
    )
    german_surnames = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/corpora/german_surnames.txt', 'r')
    )
    irish_surnames = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/corpora/irish_surnames.txt', 'r')
    )
    scandinavian_surnames = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/corpora/scandinavian_surnames.txt', 'r')
    )
    all_surnames = (
        english_surnames + french_surnames + german_surnames +
        irish_surnames + scandinavian_surnames
    )
    place_names = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/corpora/US_settlement_names.txt', 'r')
    )
    restaurant_names = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/corpora/restaurant_names.txt', 'r')
    )
    bar_names = tuple(
        name.strip('\n') for name in
        open(os.getcwd()+'/corpora/bar_names.txt', 'r')
    )

    @classmethod
    def a_masculine_name(cls, year):
        """Return a random masculine first name befitting the in-game year."""
        if year < 1880:
            year = 1880
        decade = int(math.floor(year/10)*10)  # Determine the current decade
        x = random.random()
        if x > 0.99:
            # Choose any masculine name (allows rare ones to be used occasionally)
            name = random.choice(cls.miscellaneous_masculine_forenames)
        else:
            # Choose using the actual distribution of American names this decade
            probability_distribution_for_this_decade = cls.names_by_decade[decade]['M']
            name = next(
                name for name in probability_distribution_for_this_decade if
                probability_distribution_for_this_decade[name][0] <= x <=
                probability_distribution_for_this_decade[name][1]
            )
        return name

    @classmethod
    def a_feminine_name(cls, year):
        """Return a random feminine first name befitting the in-game year."""
        if year < 1880:
            year = 1880
        decade = int(math.floor(year/10)*10)  # Determine the current decade
        x = random.random()
        if x > 0.99:
            # Choose any masculine name (allows rare ones to be used occasionally)
            name = random.choice(cls.miscellaneous_masculine_forenames)
        else:
            # Choose using the actual distribution of American names this decade
            probability_distribution_for_this_decade = cls.names_by_decade[decade]['F']
            name = next(
                name for name in probability_distribution_for_this_decade if
                probability_distribution_for_this_decade[name][0] <= x <=
                probability_distribution_for_this_decade[name][1]
            )
        return name

    @classmethod
    def an_english_surname(cls):
        """Return a random English surname."""
        return random.choice(cls.english_surnames)

    @classmethod
    def a_french_surname(cls):
        """Return a random French surname."""
        return random.choice(cls.french_surnames)

    @classmethod
    def a_german_surname(cls):
        """Return a random German surname."""
        return random.choice(cls.german_surnames)

    @classmethod
    def an_irish_surname(cls):
        """Return a random Irish surname."""
        return random.choice(cls.irish_surnames)

    @classmethod
    def a_scandinavian_surname(cls):
        """Return a random Scandinavian surname."""
        return random.choice(cls.scandinavian_surnames)

    @classmethod
    def any_surname(cls):
        """Return a random surname of any ethnicity."""
        return random.choice(cls.all_surnames)

    @classmethod
    def a_masculine_name_starting_with(cls, letter, year):
        """Return a random masculine name starting with the given letter and befitting the given year."""
        if year < 1880:
            year = 1880
        decade = int(math.floor(year/10)*10)  # Determine the current decade
        x = random.random()
        # Choose using the actual distribution of American names this decade
        probability_distribution_for_this_decade = cls.names_by_decade[decade]['M']
        try:
            name = next(
                name for name in probability_distribution_for_this_decade if
                probability_distribution_for_this_decade[name][0] <= x <=
                probability_distribution_for_this_decade[name][1] and
                name[0].lower() == letter[0]
            )
        except StopIteration:
            if random.random() < 0.5:
                # Choose any miscellaneous name starting with the same letter
                names_that_start_with_that_letter = [
                    name for name in cls.miscellaneous_masculine_forenames if
                    name[0].lower() == letter.lower()
                ]
                name = random.choice(names_that_start_with_that_letter)
            else:
                # Choose any name befitting the era of the person's birth
                x = random.random()
                name = next(
                    name for name in probability_distribution_for_this_decade if
                    probability_distribution_for_this_decade[name][0] <= x <=
                    probability_distribution_for_this_decade[name][1]
                )
        return name

    @classmethod
    def a_feminine_name_starting_with(cls, letter, year):
        """Return a random feminine name starting with the given letter and befitting the given year."""
        if year < 1880:
            year = 1880
        decade = int(math.floor(year/10)*10)  # Determine the current decade
        x = random.random()
        # Choose using the actual distribution of American names this decade
        probability_distribution_for_this_decade = cls.names_by_decade[decade]['F']
        try:
            name = next(
                name for name in probability_distribution_for_this_decade if
                probability_distribution_for_this_decade[name][0] <= x <=
                probability_distribution_for_this_decade[name][1] and
                name[0].lower() == letter[0]
            )
        except StopIteration:
            if random.random() < 0.5:
                # Choose any miscellaneous name starting with the same letter
                names_that_start_with_that_letter = [
                    name for name in cls.miscellaneous_feminine_forenames if
                    name[0].lower() == letter.lower()
                ]
                name = random.choice(names_that_start_with_that_letter)
            else:
                # Choose any name befitting the era of the person's birth
                x = random.random()
                name = next(
                    name for name in probability_distribution_for_this_decade if
                    probability_distribution_for_this_decade[name][0] <= x <=
                    probability_distribution_for_this_decade[name][1]
                )
        return name

    @classmethod
    def a_surname_sounding_like(cls, source_name):
        """Return a random surname that sounds like the source name."""
        ethnicities = (
            cls.english_surnames, cls.french_surnames, cls.german_surnames,
            cls.irish_surnames, cls.scandinavian_surnames
        )
        if '-' in source_name:
            # ButcherShop one component of the hyphenated name
            names_derived_from = source_name.split('-')
            component_to_butcher = random.choice(names_derived_from)
            if component_to_butcher == names_derived_from[0]:
                return '{}-{}'.format(
                    cls.a_surname_sounding_like(source_name=component_to_butcher),
                    names_derived_from[1]
                )
            else:
                return '{}-{}'.format(
                    names_derived_from[0],
                    cls.a_surname_sounding_like(source_name=component_to_butcher)
                )
        names_of_the_same_ethnicity = next(
            ethnicity for ethnicity in ethnicities if str(source_name) in ethnicity
        )
        try:
            name = next(
                name for name in names_of_the_same_ethnicity if
                name[0].lower() == source_name[0].lower()
            )
        except StopIteration:
            try:
                name = random.choice(names_of_the_same_ethnicity)
            except StopIteration:
                all_surnames_that_start_with_that_letter = [
                    name for name in cls.all_surnames if name[0].lower() == source_name[0].lower()
                ]
                name = random.choice(all_surnames_that_start_with_that_letter)
        return name

    @classmethod
    def a_place_name(cls):
        """Return a random place name."""
        return random.choice(cls.place_names)

    @classmethod
    def a_restaurant_name(cls):
        """Return a random restaurant name."""
        return random.choice(cls.restaurant_names)

    @classmethod
    def a_bar_name(cls):
        """Return a random bar name."""
        return random.choice(cls.bar_names)


class GravestoneDetails(object):
    """A class that holds variants of various gravestone details, such as inscriptions."""
    headers = tuple(
        header.strip('\n') for header in
        open(os.getcwd()+'/corpora/gravestone_headers.txt', 'r')
    )
    epitaphs = tuple(
        epitaph.strip('\n') for epitaph in
        open(os.getcwd()+'/corpora/gravestone_epitaphs.txt', 'r').read().split('\n\n')
    )

    @classmethod
    def a_header(cls):
        """Return a random gravestone header."""
        return random.choice(cls.headers)

    @classmethod
    def an_epitaph(cls):
        """Return a random gravestone epitaph."""
        return random.choice(cls.epitaphs)