import heapq
from occupation import *
from person import PersonExNihilo
from residence import *

# Objects of a business class represents both the company itself and the building
# at which it is headquartered. All business subclasses inherit generic attributes
# and methods from the superclass Business, and each define their own methods as
# appropriate.


class Business(object):
    """A business in a town (representing both the notion of a company and its physical building)."""

    def __init__(self, owner):
        """Initialize a Business object.

        @param owner: The owner of this business.
        """
        self.id = owner.sim.current_place_id
        owner.sim.current_place_id += 1
        config = owner.sim.config
        self.type = "business"
        # 'Demise' specifies a year at which point it is highly likely this business will close
        # down (due to being anachronistic at that point, e.g., a dairy past 1930)
        self.demise = config.business_types_advent_demise_and_minimum_population[self.__class__][1]
        # 'Services' is a tuple specifying the services offered by this business, given its type
        self.services = config.services_provided_by_business_of_type[self.__class__]
        self.town = owner.sim.town
        self.town.companies.add(self)
        self.founded = self.town.sim.year
        if self.town.vacant_lots or self.__class__ in config.companies_that_get_established_on_tracts:
            self.lot = self._init_choose_vacant_lot()
            demolition_preceding_construction_of_this_business = None
        else:
            # Acquire a lot currently occupied by a home, demolish the home,
            # and then construct this company's building on that lot
            acquired_lot = self._init_acquire_currently_occupied_lot()
            if self.town.businesses_of_type('ConstructionFirm'):
                demolition_company = random.choice(self.town.businesses_of_type('ConstructionFirm'))
            else:
                demolition_company = None
            demolition_preceding_construction_of_this_business = Demolition(
                building=acquired_lot.building, demolition_company=demolition_company
            )
            self.lot = acquired_lot
        self.lot.building = self
        # First, hire employees -- this is done first because the first-ever business, a
        # construction firm started by the town founder, will need to hire the town's
        # first architect before it can construct its own building
        self.employees = set()
        self.former_employees = set()
        self.former_owners = []
        if self.__class__ in config.public_company_types:  # Hospital, police station, fire station, etc.
            self.owner = None
            self.founder = None
        else:
            self.owner = self._init_set_and_get_owner_occupation(owner=owner)
            self.founder = self.owner
        self._init_hire_initial_employees()
        # Also set the vacancies this company will initially have that may get filled
        # up gradually by people seeking employment (most often, this will be kids who
        # grow up and are ready to work and people who were recently laid off)
        self.supplemental_vacancies = {
            'day': list(config.initial_job_vacancies[self.__class__]['supplemental day']),
            'night': list(config.initial_job_vacancies[self.__class__]['supplemental night'])
        }
        if self.__class__ not in config.companies_that_get_established_on_tracts:
            # Try to find an architect -- if you can't, you'll have to build it yourself
            architect = owner.contract_person_of_certain_occupation(occupation_in_question=Architect)
            architect = None if not architect else architect.occupation
            self.construction = BusinessConstruction(subject=owner, business=self, architect=architect)
            # If a demolition of an earlier building preceded the construction of this business,
            # attribute our new BusinessConstruction object as the .reason attribute for that
            # Demolition attribute
            if demolition_preceding_construction_of_this_business:
                demolition_preceding_construction_of_this_business.reason = self.construction
        # Set address
        self.address = self.lot.address
        self.house_number = self.lot.house_number
        self.street_address_is_on = self.lot.street_address_is_on
        self.block = self.lot.block
        # Choose a name for this business
        self.name = None
        while not self.name or any(c for c in self.town.companies if c is not self and c.name == self.name):
            self._init_get_named()
        # Set miscellaneous attributes
        self.people_here_now = set()
        self.demolition = None  # Potentially gets set by event.Demolition.__init__()
        self.out_of_business = False  # Potentially gets changed by go_out_of_business()
        self.closure = None  # BusinessClosure object itself
        self.closed = None  # Year closed

    def _init_set_and_get_owner_occupation(self, owner):
        """Set the owner of this new company's occupation to Owner."""
        # The order really matters here -- see hire() below
        occupation_class_for_owner_of_this_type_of_business = (
            self.town.sim.config.owner_occupations_for_each_business_type[self.__class__]
        )
        new_position = occupation_class_for_owner_of_this_type_of_business(
            person=owner, company=self, shift="day"
        )
        hiring = Hiring(
            subject=owner, company=self, occupation=occupation_class_for_owner_of_this_type_of_business
        )
        if owner.occupation:
            owner.occupation.terminate(reason=hiring)
        owner.occupation = new_position
        # Lastly, if the person was hired from outside the town, have them move to it
        if owner.town is not self.town:
            owner.move_into_the_town(hiring_that_instigated_move=hiring)
        return owner.occupation

    def _init_get_named(self):
        """Get named by the owner of this building (the client for which it was constructed)."""
        config = self.town.sim.config
        class_to_company_name_component = {
            ApartmentComplex: 'Apartments',
            Bank: 'Bank',
            Barbershop: 'Barbershop',
            BusDepot: 'Bus Depot',
            CityHall: 'City Hall',
            ConstructionFirm: 'Construction',
            DayCare: 'Day Care',
            OptometryClinic: 'Optometry',
            FireStation: 'Fire Dept.',
            Hospital: 'Hospital',
            Hotel: 'Hotel',
            LawFirm: 'Law Offices of',
            PlasticSurgeryClinic: 'Cosmetic Surgery Clinic',
            PoliceStation: 'Police Dept.',
            RealtyFirm: 'Realty',
            Restaurant: 'Restaurant',
            School: 'K-12 School',
            Supermarket: 'Grocers',
            TattooParlor: 'Tattoo',
            TaxiDepot: 'Taxi',
            University: 'University',
            Cemetery: 'Cemetery',
            Park: 'Park',
            Bakery: 'Baking Co.',
            BlacksmithShop: 'Blacksmith Shop',
            Brewery: 'Brewery',
            ButcherShop: 'Butcher Shop',
            CandyStore: 'Candy Store',
            CarpentryCompany: 'Carpentry',
            ClothingStore: 'Clothing Co.',
            CoalMine: 'Coal Mine',
            Dairy: 'Dairy',
            Deli: 'Delicatessen',
            DentistOffice: 'Dentistry',
            DepartmentStore: 'Department Store',
            Diner: 'Diner',
            Distillery: 'Distillery',
            DrugStore: 'Drug Store',
            Farm: 'family farm',
            Foundry: 'Foundry',
            FurnitureStore: 'Furniture Co.',
            GeneralStore: 'General Store',
            GroceryStore: 'Groceries',
            HardwareStore: 'Hardware Co.',
            Inn: 'Inn',
            InsuranceCompany: 'Insurance Co.',
            JeweleryShop: 'Jewelry',
            PaintingCompany: 'Painting',
            Pharmacy: 'Pharmacy',
            PlumbingCompany: 'Plumbing Co.',
            Quarry: 'Rock Quarry',
            ShoemakerShop: 'Shoes',
            TailorShop: 'Tailoring',
            Tavern: 'Tavern',
        }
        classes_that_get_special_names = (
            CityHall, FireStation, Hospital, PoliceStation, School, Cemetery, LawFirm, Bar,
            Restaurant, University, Park, Farm
        )
        if self.__class__ not in classes_that_get_special_names:
            if random.random() < config.chance_company_gets_named_after_owner:
                prefix = self.owner.person.last_name
            else:
                prefix = self.street_address_is_on.name
            name = "{0} {1}".format(prefix, class_to_company_name_component[self.__class__])
        elif self.__class__ in (CityHall, FireStation, Hospital, PoliceStation, School, Cemetery):
            name = "{0} {1}".format(self.town.name, class_to_company_name_component[self.__class__])
        elif self.__class__ is Farm:
            name = "{}'s farm".format(self.owner.person.name)
            if any(c for c in self.town.companies if c.name == name):
                name = "{}'s farm".format(self.owner.person.full_name)
        elif self.__class__ is LawFirm:
            associates = [e for e in self.employees if e.__class__ is Lawyer]
            suffix = "{0} & {1}".format(
                ', '.join(a.person.last_name for a in associates[:-1]), associates[-1].person.last_name
            )
            name = "{0} {1}".format(class_to_company_name_component[LawFirm], suffix)
        elif self.__class__ is Bar:
            name = Names.a_bar_name()
            # if self.town.sim.year > 1968:
            #     # Choose a name from the corpus of bar names
            #     name = Names.a_bar_name()
            # else:
            #     name = self.owner.person.last_name + "'s"
        elif self.__class__ is Restaurant:
            name = Names.a_restaurant_name()
            # if self.town.sim.year > 1968:
            #     # Choose a name from the corpus of restaurant names
            #     name = Names.a_restaurant_name()
            # else:
            #     name = self.owner.person.last_name + "'s"
        elif self.__class__ is University:
            name = "{} College".format(self.town.name)
        elif self.__class__ is Park:
            if self.lot.former_buildings:
                business_here_previously = list(self.lot.former_buildings)[-1]
                owner = business_here_previously.owner.person
                if business_here_previously.__class__ is Farm:
                    x = random.random()
                    if x < 0.25:
                        name = '{} {} Park'.format(
                            owner.first_name, owner.last_name
                        )
                    elif x < 0.5:
                        name = '{} Farm Park'.format(
                            owner.last_name
                        )

                    elif x < 0.75:
                        name = '{} Park'.format(
                            owner.last_name
                        )
                    elif x < 0.8:
                        name = 'Old Farm Park'
                    elif x < 0.9:
                        name = '{} {} Memorial Park'.format(
                            owner.first_name, owner.last_name
                        )
                    elif x < 0.97:
                        name = '{} Memorial Park'.format(
                            owner.last_name
                        )
                    else:
                        name = '{} Park'.format(self.town.name)
                elif business_here_previously.__class__ is Quarry:
                    x = random.random()
                    if x < 0.25:
                        name = '{} {} Park'.format(
                            owner.first_name, owner.last_name
                        )
                    elif x < 0.5:
                        name = '{} Park'.format(
                            business_here_previously.name
                        )

                    elif x < 0.75:
                        name = '{} Park'.format(
                            owner.last_name
                        )
                    elif x < 0.8:
                        name = 'Old Quarry Park'
                    elif x < 0.9:
                        name = '{} {} Memorial Park'.format(
                            owner.first_name, owner.last_name
                        )
                    elif x < 0.97:
                        name = 'Quarry Park'.format(
                            owner.last_name
                        )
                    else:
                        name = '{} Park'.format(self.town.name)
                elif business_here_previously.__class__ is CoalMine:
                    x = random.random()
                    if x < 0.25:
                        name = '{} {} Park'.format(
                            owner.first_name, owner.last_name
                        )
                    elif x < 0.5:
                        name = '{} Park'.format(
                            business_here_previously.name
                        )

                    elif x < 0.75:
                        name = '{} Park'.format(
                            owner.last_name
                        )
                    elif x < 0.8:
                        name = 'Old Mine Park'
                    elif x < 0.9:
                        name = '{} {} Memorial Park'.format(
                            owner.first_name, owner.last_name
                        )
                    elif x < 0.97:
                        name = 'Coal Mine Park'.format(
                            owner.last_name
                        )
                    elif x < 0.99:
                        name = 'Coal Park'.format(
                            owner.last_name
                        )
                    else:
                        name = '{} Park'.format(self.town.name)
        else:
            raise Exception("A company of class {} was unable to be named.".format(self.__class__.__name__))
        self.name = name

    def __str__(self):
        """Return string representation."""
        if not self.out_of_business:
            return "{}, {} (founded {})".format(self.name, self.address, self.founded)
        else:
            return "{}, {} ({}-{})".format(self.name, self.address, self.founded, self.closed)

    def _init_hire_initial_employees(self):
        """Fill all the positions that are vacant at the time of this company forming."""
        # Hire employees for the day shift
        for vacant_position in self.town.sim.config.initial_job_vacancies[self.__class__]['day']:
            self.hire(occupation_of_need=vacant_position, shift="day")
        # Hire employees for the night shift
        for vacant_position in self.town.sim.config.initial_job_vacancies[self.__class__]['night']:
            self.hire(occupation_of_need=vacant_position, shift="night")

    def _init_acquire_currently_occupied_lot(self):
        """If there are no vacant lots in town, acquire a lot and demolish the home currently on it."""
        lot_scores = self._rate_all_occupied_lots()
        if len(lot_scores) >= 3:
            # Pick from top three
            top_three_choices = heapq.nlargest(3, lot_scores, key=lot_scores.get)
            if random.random() < 0.6:
                choice = top_three_choices[0]
            elif random.random() < 0.9:
                choice = top_three_choices[1]
            else:
                choice = top_three_choices[2]
        elif lot_scores:
            choice = max(lot_scores)
        else:
            raise Exception("A company attempted to secure an *occupied* lot in town but somehow could not.")
        return choice

    def _rate_all_occupied_lots(self):
        """Rate all lots currently occupied by homes for their desirability as business locations."""
        lots_with_homes_on_them = (
            l for l in self.town.lots if l.building and l.building.type == 'residence'
        )
        scores = {}
        for lot in lots_with_homes_on_them:
            scores[lot] = self._rate_potential_lot(lot=lot)
        return scores

    def _init_choose_vacant_lot(self):
        """Choose a vacant lot on which to build the company building.

        Currently, a company scores all the vacant lots in town and then selects
        one of the top three. TODO: Probabilistically select from all lots using
        the scores to derive likelihoods of selecting each.
        """
        if self.__class__ in self.town.sim.config.companies_that_get_established_on_tracts:
            vacant_lots_or_tracts = self.town.vacant_tracts
        else:
            vacant_lots_or_tracts = self.town.vacant_lots
        assert vacant_lots_or_tracts, (
            "{} is attempting to found a {}, but there's no vacant lots/tracts in {}".format(
                self.owner.person.name, self.__class__.__name__, self.town.name
            )
        )
        lot_scores = self._rate_all_vacant_lots()
        if len(lot_scores) >= 3:
            # Pick from top three
            top_three_choices = heapq.nlargest(3, lot_scores, key=lot_scores.get)
            if random.random() < 0.6:
                choice = top_three_choices[0]
            elif random.random() < 0.9:
                choice = top_three_choices[1]
            else:
                choice = top_three_choices[2]
        elif lot_scores:
            choice = max(lot_scores)
        else:
            raise Exception("A company attempted to secure a lot in town when in fact none are vacant.")
        return choice

    def _rate_all_vacant_lots(self):
        """Rate all vacant lots for the desirability of their locations.
        """
        if self.__class__ in self.town.sim.config.companies_that_get_established_on_tracts:
            vacant_lots_or_tracts = self.town.vacant_tracts
        else:
            vacant_lots_or_tracts = self.town.vacant_lots
        scores = {}
        for lot in vacant_lots_or_tracts:
            scores[lot] = self._rate_potential_lot(lot=lot)
        return scores

    def _rate_potential_lot(self, lot):
        """Rate a vacant lot for the desirability of its location.

        By this method, a company appraises a vacant lot in the town for how much they
        would like to build there, given considerations to its proximity to downtown,
        proximity to other businesses of the same type, and to the number of people living
        near the lot.
        """
        score = 0
        # As (now) the only criterion, rate lots according to their distance
        # from downtown; this causes a downtown commercial area to naturally emerge
        score -= self.town.dist_from_downtown(lot)
        return score

    @property
    def locked(self):
        """Return True if the entrance to this building is currently locked, else false."""
        locked = False
        # Apartment complexes are always locked
        if self.__class__ is ApartmentComplex:
            locked = True
        # Public institutions, like parks and cemeteries and city hall, are also always locked at night
        if (self.town.sim.time_of_day == "night" and
                self.__class__ in self.town.sim.config.public_places_closed_at_night):
            locked = True
        # Other businesses are locked only when no one is working, or
        # at night when only a janitor is working
        else:
            if not self.working_right_now:
                locked = True
            elif not any(e for e in self.working_right_now if e[0] != 'janitor'):
                locked = True
        return locked

    @property
    def residents(self):
        """Return the employees that work here.

         This is meant to facilitate a Lot reasoning over its population and the population
         of its local area. This reasoning is needed so that developers can decide where to
         build businesses. For all businesses but ApartmentComplex, this just returns the
         employees that work at this building (which makes sense in the case of, e.g., building
         a restaurant nearby where people work); for ApartmentComplex, this is overridden
         to return the employees that work there and also the people that live there.
         """
        return set([employee.person for employee in self.employees])

    @property
    def working_right_now(self):
        people_working = [p for p in self.people_here_now if p.routine.working]
        return [(p.occupation.vocation, p) for p in people_working]

    @property
    def day_shift(self):
        """Return all employees who work the day shift here."""
        day_shift = set([employee for employee in self.employees if employee.shift == "day"])
        return day_shift

    @property
    def night_shift(self):
        """Return all employees who work the night shift here."""
        night_shift = set([employee for employee in self.employees if employee.shift == "night"])
        return night_shift

    @property
    def sign(self):
        """Return a string representing this business's sign."""
        if self.__class__ in self.town.sim.config.public_company_types:
            return self.name
        elif self.town.sim.year - self.founded > 8:
            return '{}, since {}'.format(self.name, self.founded)
        else:
            return self.name

    def _find_candidate(self, occupation_of_need):
        """Find the best available candidate to fill the given occupation of need."""
        # If you have someone working here who is an apprentice, hire them outright
        if (self.town.sim.config.job_levels[occupation_of_need] > self.town.sim.config.job_levels[Apprentice] and
                any(e for e in self.employees if e.__class__ == Apprentice and e.years_experience > 0)):
            selected_candidate = next(
                e for e in self.employees if e.__class__ == Apprentice and e.years_experience > 0
            ).person
        else:
            job_candidates_in_town = self._assemble_job_candidates(occupation_of_need=occupation_of_need)
            if job_candidates_in_town:
                candidate_scores = self._rate_all_job_candidates(candidates=job_candidates_in_town)
                selected_candidate = self._select_candidate(candidate_scores=candidate_scores)
            else:
                selected_candidate = self._find_candidate_from_outside_the_town(occupation_of_need=occupation_of_need)
        return selected_candidate

    def hire(self, occupation_of_need, shift, to_replace=None,
             fills_supplemental_job_vacancy=False, selected_candidate=None, hired_as_a_favor=False):
        """Hire the given selected candidate."""
        # If no candidate has yet been selected, scour the job market to find one
        if not selected_candidate:
            selected_candidate = self._find_candidate(occupation_of_need=occupation_of_need)
        # Instantiate the new occupation -- this means that the subject may
        # momentarily have two occupations simultaneously
        new_position = occupation_of_need(person=selected_candidate, company=self, shift=shift)
        # If this person is being hired to replace a now-former employee, attribute
        # this new position as the successor to the former one
        if to_replace:
            to_replace.succeeded_by = new_position
            new_position.preceded_by = to_replace
            # If this person is being hired to replace the owner, they are now the owner --
            # TODO not all businesses should transfer ownership using the standard hiring process
            if to_replace is self.owner:
                self.owner = new_position
        # Now instantiate a Hiring object to hold data about the hiring
        hiring = Hiring(subject=selected_candidate, company=self, occupation=new_position)
        # Now terminate the person's former occupation, if any (which may cause
        # a hiring chain and this person's former position goes vacant and is filled,
        # and so forth); this has to happen after the new occupation is instantiated, or
        # else they may be hired to fill their own vacated position, which will cause problems
        # [Actually, this currently wouldn't happen, because lateral job movement is not
        # possible given how companies assemble job candidates, but it still makes more sense
        # to have this person put in their new position *before* the chain sets off, because it
        # better represents what really is a domino-effect situation)
        if selected_candidate.occupation:
            selected_candidate.occupation.terminate(reason=hiring)
        # Now you can set the employee's occupation to the new occupation (had you done it
        # prior, either here or elsewhere, it would have terminated the occupation that this
        # person was just hired for, triggering endless recursion as the company tries to
        # fill this vacancy in a Sisyphean nightmare)
        selected_candidate.occupation = new_position
        # If this is a law firm and the new hire is a lawyer, change the name
        # of this firm to include the new lawyer's name
        if self.__class__ == "LawFirm" and new_position == Lawyer:
            self._init_get_named()
        # If this position filled one of this company's "supplemental" job vacancies (see
        # config.py), then remove an instance of this position from that list
        if fills_supplemental_job_vacancy:
            self.supplemental_vacancies[shift].remove(occupation_of_need)
            # This position doesn't have to be refilled immediately if terminated, so
            # attribute to it that it is supplemental
            selected_candidate.occupation.supplemental = True
        # Being hired as a favor means this business created an additional position
        # beyond all their supplemental positions (because those were all filled)
        # specifically to facilitate the hiring of this person (who will have been
        # a family member of this company's owner); because of this, when this position
        # terminates we don't want to add it back to the supplemental vacancies of this
        # company, because they really don't need to refill the position ever and if they
        # do, it yields rampant population growth due to there being way too many jobs
        # in town
        selected_candidate.occupation.hired_as_favor = hired_as_a_favor
        # Lastly, if the person was hired from outside the town, have them move to it
        if selected_candidate.town is not self.town:
            selected_candidate.move_into_the_town(hiring_that_instigated_move=hiring)

    @staticmethod
    def _select_candidate(candidate_scores):
        """Select a person to serve in a certain occupational capacity."""
        if len(candidate_scores) >= 3:
            # Pick from top three
            top_three_choices = heapq.nlargest(3, candidate_scores, key=candidate_scores.get)
            if random.random() < 0.6:
                chosen_candidate = top_three_choices[0]
            elif random.random() < 0.9:
                chosen_candidate = top_three_choices[1]
            else:
                chosen_candidate = top_three_choices[2]
        else:
            chosen_candidate = max(candidate_scores)
        return chosen_candidate

    def _find_candidate_from_outside_the_town(self, occupation_of_need):
        """Generate a PersonExNihilo to move into the town for this job."""
        candidate = PersonExNihilo(
            sim=self.town.sim, job_opportunity_impetus=occupation_of_need, spouse_already_generated=None
        )
        return candidate

    def _rate_all_job_candidates(self, candidates):
        """Rate all job candidates."""
        scores = {}
        for candidate in candidates:
            scores[candidate] = self.rate_job_candidate(person=candidate)
        return scores

    def rate_job_candidate(self, person):
        """Rate a job candidate, given an open position and owner biases."""
        config = self.town.sim.config
        decision_maker = self.owner.person if self.owner else self.town.mayor
        score = 0.0
        if person in self.employees:
            score += config.preference_to_hire_from_within_company
        if person in decision_maker.immediate_family:
            score += config.preference_to_hire_immediate_family
        elif person in decision_maker.extended_family:
            score += config.preference_to_hire_extended_family
        if person.immediate_family & self.employees:
            score += config.preference_to_hire_immediate_family_of_an_employee
        elif person.extended_family & self.employees:
            score += config.preference_to_hire_extended_family_of_an_employee
        if person in decision_maker.friends:
            score += config.preference_to_hire_friend
        elif person in decision_maker.acquaintances:
            score += config.preference_to_hire_acquaintance
        if person in decision_maker.enemies:
            score += config.dispreference_to_hire_enemy
        if person.occupation:
            score *= person.occupation.level
        else:
            score *= config.unemployment_occupation_level
        return score

    def _assemble_job_candidates(self, occupation_of_need):
        """Assemble a group of job candidates for an open position."""
        candidates = set()
        # Consider people that already work in this town -- this will subsume
        # reasoning over people that could be promoted from within this company
        for company in self.town.companies:
            for position in company.employees:
                person_is_qualified = self.check_if_person_is_qualified_for_the_position(
                    candidate=position.person, occupation_of_need=occupation_of_need
                )
                if person_is_qualified:
                    candidates.add(position.person)
        # Consider unemployed (mostly young) people if they are qualified
        for person in self.town.unemployed:
            person_is_qualified = self.check_if_person_is_qualified_for_the_position(
                candidate=person, occupation_of_need=occupation_of_need
            )
            if person_is_qualified:
                candidates.add(person)
        return candidates

    def check_if_person_is_qualified_for_the_position(self, candidate, occupation_of_need):
        """Check if the job candidate is qualified for the position you are hiring for."""
        config = self.town.sim.config
        qualified = False
        level_of_this_position = config.job_levels[occupation_of_need]
        # Make sure they are not already at a job of higher prestige; people that
        # used to work higher-level jobs may stoop back to lower levels if they are
        # now out of work
        if candidate.occupation:
            candidate_job_level = candidate.occupation.level
        elif candidate.occupations:
            candidate_job_level = max(candidate.occupations, key=lambda o: o.level).level
        else:
            candidate_job_level = 0
        if not (candidate.occupation and candidate_job_level >= level_of_this_position):
            # Make sure they have a college degree if one is required to have this occupation
            if occupation_of_need in self.town.sim.config.occupations_requiring_college_degree:
                if candidate.college_graduate:
                    qualified = True
            else:
                qualified = True
        # Make sure the candidate meets the essential preconditions for this position;
        # note: most of these preconditions are meant to maintain basic historically accuracy
        if not config.employable_as_a[occupation_of_need](applicant=candidate):
            qualified = False
        # Lastly, make sure they have been at their old job for at least a year,
        # if they had one
        if candidate.occupation and candidate.occupation.years_experience < 1:
            qualified = False
        return qualified

    def get_feature(self, feature_type):
        """Return this person's feature of the given type."""
        if feature_type == "business block":
            return str(self.block)
        elif feature_type == "business address":
            return self.address

    def go_out_of_business(self, reason):
        """Cease operation of this business."""
        BusinessClosure(business=self, reason=reason)


class ApartmentComplex(Business):
    """An apartment complex."""

    def __init__(self, owner):
        """Initialize an ApartmentComplex object.

        @param owner: The owner of this business.
        """
        # Have to do this to allow .residents to be able to return a value before
        # this object has its units attributed -- this is because new employees
        # hired to work here may actually move in during the larger init() call
        self.units = []
        super(ApartmentComplex, self).__init__(owner)
        self.units = self._init_apartment_units()

    def _init_apartment_units(self):
        """Instantiate objects for the individual units in this apartment complex."""
        config = self.town.sim.config
        n_units_to_build = random.randint(
            config.number_of_apartment_units_in_new_complex_min,
            config.number_of_apartment_units_in_new_complex_max
        )
        if n_units_to_build % 2 != 0:
            # Make it a nice even number
            n_units_to_build -= 1
        apartment_units = []
        for i in xrange(n_units_to_build):
            unit_number = i + 1
            apartment_units.append(
                Apartment(apartment_complex=self, lot=self.lot, unit_number=unit_number)
            )
        return apartment_units

    @property
    def residents(self):
        """Return the residents that live here."""
        residents = set()
        for unit in self.units:
            residents |= unit.residents
        return residents

    def expand(self):
        """Add two extra units in this complex.

        The impetus for this method being called is to accommodate a new person in town seeking housing.
        Since apartment complexes in this simulation always have an even number of units, we add two extra
        ones to maintain that property.
        """
        currently_highest_unit_number = max(self.units, key=lambda u: u.unit_number).unit_number
        next_unit_number = currently_highest_unit_number + 1
        self.units.append(
            Apartment(apartment_complex=self, lot=self.lot, unit_number=next_unit_number)
        )
        self.units.append(
            Apartment(apartment_complex=self, lot=self.lot, unit_number=next_unit_number+1)
        )


class Bakery(Business):
    """A bakery."""

    def __init__(self, owner):
        """Initialize a Bakery object.

        @param owner: The owner of this business.
        """
        super(Bakery, self).__init__(owner)


class Bank(Business):
    """A bank."""

    def __init__(self, owner):
        """Initialize a Bank object.

        @param owner: The owner of this business.
        """
        super(Bank, self).__init__(owner)


class Bar(Business):
    """A bar."""

    def __init__(self, owner):
        """Initialize a Restaurant object.

        @param owner: The owner of this business.
        """
        super(Bar, self).__init__(owner)


class Barbershop(Business):
    """A barbershop."""

    def __init__(self, owner):
        """Initialize a Barbershop object.

        @param owner: The owner of this business.
        """
        super(Barbershop, self).__init__(owner)


class BlacksmithShop(Business):
    """A blacksmith business."""

    def __init__(self, owner):
        """Initialize a BlacksmithShop object.

        @param owner: The owner of this business.
        """
        super(BlacksmithShop, self).__init__(owner)


class Brewery(Business):
    """A brewery."""

    def __init__(self, owner):
        """Initialize a Brewery object.

        @param owner: The owner of this business.
        """
        super(Brewery, self).__init__(owner)


class BusDepot(Business):
    """A bus depot."""

    def __init__(self, owner):
        """Initialize a BusDepot object.

        @param owner: The owner of this business.
        """
        super(BusDepot, self).__init__(owner)


class ButcherShop(Business):
    """A butcher business."""

    def __init__(self, owner):
        """Initialize a ButcherShop object.

        @param owner: The owner of this business.
        """
        super(ButcherShop, self).__init__(owner)


class CandyStore(Business):
    """A candy store."""

    def __init__(self, owner):
        """Initialize a CandyStore object.

        @param owner: The owner of this business.
        """
        super(CandyStore, self).__init__(owner)


class CarpentryCompany(Business):
    """A carpentry company."""

    def __init__(self, owner):
        """Initialize a CarpentryCompany object.

        @param owner: The owner of this business.
        """
        super(CarpentryCompany, self).__init__(owner)


class Cemetery(Business):
    """A cemetery on a tract in a town."""

    def __init__(self, owner):
        """Initialize a Cemetery object."""
        super(Cemetery, self).__init__(owner)
        self.town.cemetery = self
        self.plots = {}

    def inter_person(self, person):
        """Inter a new person by assigning them a plot in the graveyard."""
        if not self.plots:
            new_plot_number = 1
        else:
            new_plot_number = max(self.plots) + 1
        self.plots[new_plot_number] = person
        return new_plot_number


class CityHall(Business):
    """The city hall."""

    def __init__(self, owner):
        """Initialize a CityHall object.

        @param owner: The owner of this business.
        """
        super(CityHall, self).__init__(owner)
        self.town.city_hall = self


class ClothingStore(Business):
    """A store that sells clothing only; i.e., not a department store."""

    def __init__(self, owner):
        """Initialize a ClothingStore object.

        @param owner: The owner of this business.
        """
        super(ClothingStore, self).__init__(owner)


class CoalMine(Business):
    """A coal mine."""

    def __init__(self, owner):
        """Initialize a ClothingStore object.

        @param owner: The owner of this business.
        """
        super(CoalMine, self).__init__(owner)


class ConstructionFirm(Business):
    """A construction firm."""

    def __init__(self, owner):
        """Initialize an ConstructionFirm object.

        @param owner: The owner of this business.
        """
        super(ConstructionFirm, self).__init__(owner)

    @property
    def house_constructions(self):
        """Return all house constructions."""
        house_constructions = set()
        for employee in self.employees | self.former_employees:
            if hasattr(employee, 'house_constructions'):
                house_constructions |= employee.house_constructions
        return house_constructions

    @property
    def building_constructions(self):
        """Return all building constructions."""
        building_constructions = set()
        for employee in self.employees | self.former_employees:
            if hasattr(employee, 'building_constructions'):
                building_constructions |= employee.building_constructions
        return building_constructions


class Dairy(Business):
    """A store where milk is sold and from which milk is distributed."""

    def __init__(self, owner):
        """Initialize a Dairy object.

        @param owner: The owner of this business.
        """
        super(Dairy, self).__init__(owner)


class DayCare(Business):
    """A day care center for young children."""

    def __init__(self, owner):
        """Initialize a DayCare object.

        @param owner: The owner of this business.
        """
        super(DayCare, self).__init__(owner)


class Deli(Business):
    """A delicatessen."""

    def __init__(self, owner):
        """Initialize a Deli object.

        @param owner: The owner of this business.
        """
        super(Deli, self).__init__(owner)


class DentistOffice(Business):
    """A dentist office."""

    def __init__(self, owner):
        """Initialize a DentistOffice object.

        @param owner: The owner of this business.
        """
        super(DentistOffice, self).__init__(owner)


class DepartmentStore(Business):
    """A department store."""

    def __init__(self, owner):
        """Initialize a DepartmentStore object.

        @param owner: The owner of this business.
        """
        super(DepartmentStore, self).__init__(owner)


class Diner(Business):
    """A diner."""

    def __init__(self, owner):
        """Initialize a Diner object.

        @param owner: The owner of this business.
        """
        super(Diner, self).__init__(owner)


class Distillery(Business):
    """A whiskey distillery."""

    def __init__(self, owner):
        """Initialize a Distillery object.

        @param owner: The owner of this business.
        """
        super(Distillery, self).__init__(owner)


class DrugStore(Business):
    """A drug store."""

    def __init__(self, owner):
        """Initialize a DrugStore object.

        @param owner: The owner of this business.
        """
        super(DrugStore, self).__init__(owner)


class Farm(Business):
    """A farm on a tract in a town."""

    def __init__(self, owner):
        """Initialize a Farm object.

        @param owner: The owner of this business.
        """
        super(Farm, self).__init__(owner)


class FireStation(Business):
    """A fire station."""

    def __init__(self, owner):
        """Initialize an FireStation object.

        @param owner: The owner of this business.
        """
        super(FireStation, self).__init__(owner)
        self.town.fire_station = self


class Foundry(Business):
    """A metal foundry."""

    def __init__(self, owner):
        """Initialize a Foundry object.

        @param owner: The owner of this business.
        """
        super(Foundry, self).__init__(owner)


class FurnitureStore(Business):
    """A furniture store."""

    def __init__(self, owner):
        """Initialize a FurnitureStore object.

        @param owner: The owner of this business.
        """
        super(FurnitureStore, self).__init__(owner)


class GeneralStore(Business):
    """A general store."""

    def __init__(self, owner):
        """Initialize a GeneralStore object.

        @param owner: The owner of this business.
        """
        super(GeneralStore, self).__init__(owner)


class GroceryStore(Business):
    """A grocery store."""

    def __init__(self, owner):
        """Initialize a GroceryStore object.

        @param owner: The owner of this business.
        """
        super(GroceryStore, self).__init__(owner)


class HardwareStore(Business):
    """A hardware store."""

    def __init__(self, owner):
        """Initialize a HardwareStore object.

        @param owner: The owner of this business.
        """
        super(HardwareStore, self).__init__(owner)


class Hospital(Business):
    """A hospital."""

    def __init__(self, owner):
        """Initialize an Hospital object.

        @param owner: The owner of this business.
        """
        super(Hospital, self).__init__(owner)
        self.town.hospital = self

    @property
    def baby_deliveries(self):
        """Return all baby deliveries."""
        baby_deliveries = set()
        for employee in self.employees | self.former_employees:
            if hasattr(employee, 'baby_deliveries'):
                baby_deliveries |= employee.baby_deliveries
        return baby_deliveries


class Hotel(Business):
    """A hotel."""

    def __init__(self, owner):
        """Initialize a Hotel object.

        @param owner: The owner of this business.
        """
        super(Hotel, self).__init__(owner)


class Inn(Business):
    """An inn."""

    def __init__(self, owner):
        """Initialize an Inn object.

        @param owner: The owner of this business.
        """
        super(Inn, self).__init__(owner)


class InsuranceCompany(Business):
    """An insurance company."""

    def __init__(self, owner):
        """Initialize an InsuranceCompany object.

        @param owner: The owner of this business.
        """
        super(InsuranceCompany, self).__init__(owner)


class JeweleryShop(Business):
    """A jewelry company."""

    def __init__(self, owner):
        """Initialize a JeweleryShop object.

        @param owner: The owner of this business.
        """
        super(JeweleryShop, self).__init__(owner)


class LawFirm(Business):
    """A law firm."""

    def __init__(self, owner):
        """Initialize a LawFirm object.

        @param owner: The owner of this business.
        """
        super(LawFirm, self).__init__(owner)

    def rename_due_to_lawyer_change(self):
        """Rename this company due to the hiring of a new lawyer."""
        partners = [e for e in self.employees if e.__class__ is Lawyer]
        if len(partners) > 1:
            partners_str = "{} & {}".format(
                ', '.join(a.person.last_name for a in partners[:-1]),
                partners[-1].person.last_name
            )
            self.name = "Law Offices of {}".format(partners_str)
        elif partners:
            # If there's only one lawyer at this firm now, have its
            # name be 'Law Offices of [first name] [last name]'
            self.name = "Law Offices of {} {}".format(
                partners[0].person.first_name, partners[0].person.last_name
            )
        else:
            # The only lawyer working here retired or departed the town -- the
            # business will shut down shortly and this will be its final name
            pass

    @property
    def filed_divorces(self):
        """Return all divorces filed through this law firm."""
        filed_divorces = set()
        for employee in self.employees | self.former_employees:
            if hasattr(employee, 'filed_divorces'):
                filed_divorces |= employee.filed_divorces
        return filed_divorces

    @property
    def filed_name_changes(self):
        """Return all name changes filed through this law firm."""
        filed_name_changes = set()
        for employee in self.employees | self.former_employees:
            filed_name_changes |= employee.filed_name_changes
        return filed_name_changes


class OptometryClinic(Business):
    """An optometry clinic."""

    def __init__(self, owner):
        """Initialize an OptometryClinic object.

        @param owner: The owner of this business.
        """
        super(OptometryClinic, self).__init__(owner)


class PaintingCompany(Business):
    """A painting company."""

    def __init__(self, owner):
        """Initialize a PaintingCompany object."""
        super(PaintingCompany, self).__init__(owner)


class Park(Business):
    """A park on a tract in a town."""

    def __init__(self, owner):
        """Initialize a Park object."""
        super(Park, self).__init__(owner)


class Pharmacy(Business):
    """A pharmacy."""

    def __init__(self, owner):
        """Initialize a Pharmacy object."""
        super(Pharmacy, self).__init__(owner)


class PlasticSurgeryClinic(Business):
    """A plastic-surgery clinic."""

    def __init__(self, owner):
        """Initialize a PlasticSurgeryClinic object.

        @param owner: The owner of this business.
        """
        super(PlasticSurgeryClinic, self).__init__(owner)


class PlumbingCompany(Business):
    """A plumbing company."""

    def __init__(self, owner):
        """Initialize a PlumbingCompany object.

        @param owner: The owner of this business.
        """
        super(PlumbingCompany, self).__init__(owner)


class PoliceStation(Business):
    """A police station."""

    def __init__(self, owner):
        """Initialize a PoliceStation object.

        @param owner: The owner of this business.
        """
        super(PoliceStation, self).__init__(owner)
        self.town.police_station = self


class Quarry(Business):
    """A rock quarry."""

    def __init__(self, owner):
        """Initialize a Quarry object.

        @param owner: The owner of this business.
        """
        super(Quarry, self).__init__(owner)


class RealtyFirm(Business):
    """A realty firm."""

    def __init__(self, owner):
        """Initialize an RealtyFirm object.

        @param owner: The owner of this business.
        """
        super(RealtyFirm, self).__init__(owner)

    @property
    def home_sales(self):
        """Return all home sales."""
        home_sales = set()
        for employee in self.employees | self.former_employees:
            if hasattr(employee, 'home_sales'):
                home_sales |= employee.home_sales
        return home_sales


class Restaurant(Business):
    """A restaurant."""

    def __init__(self, owner):
        """Initialize a Restaurant object.

        @param owner: The owner of this business.
        """
        super(Restaurant, self).__init__(owner)


class School(Business):
    """The local K-12 school."""

    def __init__(self, owner):
        """Initialize a School object.

        @param owner: The owner of this business.
        """
        super(School, self).__init__(owner)
        self.town.school = self


class ShoemakerShop(Business):
    """A shoemaker's company."""

    def __init__(self, owner):
        """Initialize an ShoemakerShop object.

        @param owner: The owner of this business.
        """
        super(ShoemakerShop, self).__init__(owner)


class Supermarket(Business):
    """A supermarket on a lot in a town."""

    def __init__(self, owner):
        """Initialize an Supermarket object.

        @param owner: The owner of this business.
        """
        super(Supermarket, self).__init__(owner)


class TailorShop(Business):
    """A tailor."""

    def __init__(self, owner):
        """Initialize a TailorShop object.

        @param owner: The owner of this business.
        """
        super(TailorShop, self).__init__(owner)


class TattooParlor(Business):
    """A tattoo parlor."""

    def __init__(self, owner):
        """Initialize a TattooParlor object.

        @param owner: The owner of this business.
        """
        super(TattooParlor, self).__init__(owner)


class Tavern(Business):
    """A place where alcohol is served in the 19th century, maintained by a barkeeper."""

    def __init__(self, owner):
        """Initialize a Tavern object.

        @param owner: The owner of this business.
        """
        super(Tavern, self).__init__(owner)


class TaxiDepot(Business):
    """A taxi depot."""

    def __init__(self, owner):
        """Initialize a TaxiDepot object.

        @param owner: The owner of this business.
        """
        super(TaxiDepot, self).__init__(owner)


class University(Business):
    """The local university."""

    def __init__(self, owner):
        """Initialize a University object.

        @param owner: The owner of this business.
        """
        super(University, self).__init__(owner)
        self.town.university = self