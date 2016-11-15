from utils import fit_probability_distribution


class RoutineConfig(object):
    """Configuration parameters related to character daily routines."""
    # Deciding whether to leave home on a simulated timestep
    chance_someone_leaves_home_on_day_off_floor = {
        # The actual chance is a person's extroversion, but these represent
        # the minimum chance. (Keep in mind, they currently will be spending
        # the entire day/night cycle at some particular place in public
        "day": 0.3, "night": 0.15
    }
    chance_someone_leaves_home_on_day_off_cap = {
        # The actual chance is a person's extroversion, but these represent
        # the maximum chance. (Keep in mind, they currently will be spending
        # the entire day/night cycle at some particular place in public
        "day": 0.95, "night": 0.9
    }
    chance_someone_leaves_home_multiplier_due_to_kids = 0.3  # i.e., 0.3 means 30% as likely to leave if you have kids
    # Having decided to leave home, deciding whether to go on errands or visit someone
    chance_someone_goes_on_errand_vs_visits_someone = 0.75  # Thus 25% chance of visiting someone
    # Having decided to go on errands, relative frequencies for deciding what kind of errand
    # to go on (e.g., if 'baked goods' has a frequency of 3 and 'insurance' has a frequency of
    # 1, then the former will be three times more likely to be the impetus for an errand)
    relative_frequencies_of_errands_for_service_types = {
        # Keep in mind: this person will be spending the entire day/night cycle there
        "day": {
            'baked goods': 3,
            'dairy': 3,
            'meat': 3,
            'clothes': 2.5,
            'banking': 2,
            'furniture': 2,
            'haircut': 2,
            'restaurant': 2,
            'park': 2,
            'medicine': 1.5,
            'shoes': 1.5,
            'tools': 1.5,
            'insurance': 1,
            'jewelry': 1,
            'confections': 0.5,
            'bar': 0.25,
            'dentist': 0.25,
            'eyeglasses': 0.15,
            'cemetery': 0.1,
            'tattoo': 0.1,
            'plastic surgery': 0.0,
            'transport': 0.0,  # No taxis or buses in this version
        },
        "night": {
            'restaurant': 5,
            'bar': 5,
            'cemetery': 0.05,
            'park': 0.05,
            'tattoo': 0.01,
            'baked goods': 0,
            'banking': 0,
            'clothes': 0,
            'confections': 0,
            'dairy': 0,
            'dentist': 0,
            'eyeglasses': 0,
            'furniture': 0,
            'haircut': 0,
            'insurance': 0,
            'jewelry': 0,
            'meat': 0,
            'medicine': 0,
            'plastic surgery': 0.0,
            'shoes': 0,
            'tools': 0,
            'transport': 0.0,  # No taxis or buses in this version
        },
    }
    # Fit a probability distribution to the above relative frequencies (do not alter this)
    probabilities_of_errand_for_service_type = {
        "day": fit_probability_distribution(
            relative_frequencies_dictionary=relative_frequencies_of_errands_for_service_types["day"]
        ),
        "night": fit_probability_distribution(
            relative_frequencies_dictionary=relative_frequencies_of_errands_for_service_types["night"]
        )
    }
    # Once a particular type of errand has been selected, these parameters drive reasoning
    # about which associated business to go to
    chance_someone_goes_to_closest_business_of_type = 0.75
    # Having decided to visit someone (rather than go on an errand), relative frequencies for the
    # relation of the person whom they will be visiting
    who_someone_visiting_will_visit_relative_frequencies = {
        'nb': 3.5,  # Neighbor
        'fr': 3.0,  # Friend
        'if': 2.5,  # Immediate family
        'ef': 1.0  # Extended family
    }
    # Do not alter these two
    temp_probabilities = fit_probability_distribution(who_someone_visiting_will_visit_relative_frequencies)
    who_someone_visiting_will_visit_probabilities = tuple([
        ((temp_probabilities[relation][0], temp_probabilities[relation][1]), relation)
        for relation in temp_probabilities
    ])
    # Miscellaneous: locking doors -- each building in a town (objects of Business and DwellingPlace
    # subclasses) will have a 'locked' attribute specifying whether the door of that building is
    # currently locked; this could be used to prevent players from entering locked doors (and indeed
    # is used in Bad News)
    chance_someone_locks_their_door = lambda neuroticism: neuroticism  # Usage: if random.random() > neuro: True
    # Miscellaneous: calling in sick to work, or not working on a given timestep (currently all characters
    # who work will be scheduled to work on all timesteps falling on their scheduled shift -- either 'day' or
    # 'night' -- meaning there is no modeling of characters having weekends off from work)
    chance_someone_calls_in_sick_to_work = 0.03
    chance_someone_leaves_home_on_sick_day = 0.05
    chance_someone_doesnt_have_to_work_some_day = 0.00  # Untested, but could be used to model weekend schedules
    # These mappings are used to track the occasion for a character being at the location that they are at on a
    # given timestep; this data is recorded and may also be used to feed the reasoning of various systems
    business_type_to_occasion_for_visit = {
        'Bar': 'leisure',
        'Hotel': 'leisure',
        'Park': 'leisure',
        'Restaurant': 'leisure',
        'Bank': 'errand',
        'Barbershop': 'errand',
        'BusDepot': 'errand',
        'Cemetery': 'errand',
        'OptometryClinic': 'errand',
        'PlasticSurgeryClinic': 'errand',
        'Supermarket': 'errand',
        'TattooParlor': 'errand',
        'TaxiDepot': 'errand',
        'University': 'errand',
        'ApartmentComplex': 'errand',
        'Bakery': 'errand',
        'BlacksmithShop': 'errand',
        'Brewery': 'leisure',
        'ButcherShop': 'errand',
        'CandyStore': 'leisure',
        'CarpentryCompany': 'errand',
        'CityHall': 'errand',
        'ClothingStore': 'errand',
        'CoalMine': 'errand',
        'ConstructionFirm': 'errand',
        'Dairy': 'errand',
        'DayCare': 'errand',
        'Deli': 'leisure',
        'DentistOffice': 'errand',
        'DepartmentStore': 'leisure',
        'Diner': 'leisure',
        'Distillery': 'leisure',
        'DrugStore': 'errand',
        'Farm': 'errand',
        'FireStation': 'errand',
        'Foundry': 'errand',
        'FurnitureStore': 'errand',
        'GeneralStore': 'errand',
        'GroceryStore': 'errand',
        'HardwareStore': 'errand',
        'Hospital': 'errand',
        'Inn': 'errand',
        'InsuranceCompany': 'errand',
        'JeweleryShop': 'errand',
        'LawFirm': 'errand',
        'PaintingCompany': 'errand',
        'Pharmacy': 'errand',
        'PlumbingCompany': 'errand',
        'PoliceStation': 'errand',
        'Quarry': 'errand',
        'RealtyFirm': 'errand',
        'School': 'errand',
        'ShoemakerShop': 'errand',
        'TailorShop': 'errand',
        'Tavern': 'leisure',
    }
