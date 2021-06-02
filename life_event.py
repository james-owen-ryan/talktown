import random
from name import Name
from person import Person
from corpora import Names
from residence import House
from artifact import Gravestone


# TODO HOW TO GIVE RETCONNED EVENTS PROPERLY ORDERED EVENT NUMBERS?

class Event(object):
    """A superclass that all event subclasses inherit from."""

    def __init__(self, sim):
        """Initialize an Event object."""
        self.year = sim.year
        if self.year < sim.config.year_worldgen_begins:  # This event is being retconned; generate a random day
            self.month, self.day, self.ordinal_date = sim.get_random_day_of_year(year=self.year)
            self.date = sim.get_date(ordinal_date=self.ordinal_date)
        else:
            self.month = sim.month
            self.day = sim.day
            self.ordinal_date = sim.ordinal_date
            self.date = sim.date
        # Also request and attribute an event number, so that we can later
        # determine the precise ordering of events that happen on the same timestep
        self.event_number = sim.assign_event_number(new_event=self)


class Adoption(Event):
    """An adoption of a child by a person(s) who is/are not their biological parent.

    Adoptions have not been fully implemented yet.
    """

    def __init__(self, subject, adoptive_parents):
        """Initialize an Adoption object.

        @param subject: The adoptee.
        @param adoptive_parents: The adoptive parent(s).
        """
        super(Adoption, self).__init__(sim=subject.sim)
        self.town = adoptive_parents[0].town  # May be None if parents not in the town yet
        self.subject = subject
        self.subject.adoption = self  # Could there be multiple, actually?
        self.adoptive_parents = adoptive_parents
        for adoptive_parent in adoptive_parents:
            adoptive_parent.adoptions.append(self)

    def __str__(self):
        """Return string representation."""
        return "Adoption of {0} by {1} in {2}".format(
            self.subject.name, ' and '.join(ap.name for ap in self.adoptive_parents), self.year
        )


class Birth(Event):
    """A birth of a person."""

    def __init__(self, mother, doctor):
        """Initialize a Birth object."""
        super(Birth, self).__init__(sim=mother.sim)
        self.town = mother.town
        self.biological_mother = mother
        self.mother = mother
        self.biological_father = mother.impregnated_by
        self.father = self.mother.spouse if self.mother.spouse and self.mother.spouse.male else self.biological_father
        self.subject = Person(sim=mother.sim, birth=self)
        if self.father and self.father is not self.biological_father:
            self.adoption = Adoption(subject=self.subject, adoptive_parents=(self.father,))
        if self.biological_father is self.mother.spouse:
            self.mother.marriage.children_produced.add(self.subject)
        self.doctor = doctor
        # Update the sim's listing of all people's birthdays
        try:
            mother.sim.birthdays[(self.month, self.day)].add(self.subject)
        except KeyError:
            mother.sim.birthdays[(self.month, self.day)] = {self.subject}
        self._name_baby()
        self._update_mother_attributes()
        if self.mother.town:
            self._take_baby_home()
        if self.mother.occupation:
            self._have_mother_potentially_exit_workforce()
        if self.doctor:  # There won't be a doctor if the birth happened outside the town
            self.hospital = doctor.company
            self.nurses = {
                position for position in self.hospital.employees if
                position.__class__.__name__ == 'Nurse'
            }
            self.doctor.baby_deliveries.add(self)
        else:
            self.hospital = None
            self.nurses = set()

    def __str__(self):
        """Return string representation."""
        return "Birth of {} {} {} in {}".format(
            self.subject.first_name, self.subject.middle_name,
            self.subject.maiden_name, self.year
        )

    def _update_mother_attributes(self):
        """Update attributes of the mother that are affected by this birth."""
        self.mother.conception_date = None
        self.mother.due_date = None
        self.mother.impregnated_by = None
        self.mother.pregnant = False

    def _name_baby(self):
        """Name the baby.

        TODO: Support a child inheriting a person's middle name as their own
        first or middle name.
        """
        config = self.subject.sim.config
        baby = self.subject
        if (
            random.random() < config.chance_son_inherits_fathers_exact_name and
            baby.male and
            not(any(bro for bro in baby.brothers if bro.first_name == self.father.first_name))
        ):
            # Name the son after his father
            baby.first_name = self.father.first_name
            baby.middle_name = self.father.middle_name
            baby.suffix = self._get_suffix()
            baby.named_for = (self.father, self.father)
        else:
            if baby.male:
                potential_namegivers = self._get_potential_male_namegivers()
            else:
                potential_namegivers = self._get_potential_female_namegivers()
            # Make sure person doesn't end up with a sibling's name or their mother's name
            off_limits_names = {
                p.first_name for p in {baby.mother} | baby.siblings
            }
            potential_first_name, first_name_namegiver = (
                self._decide_first_name(potential_namegivers=potential_namegivers)
            )
            while potential_first_name in off_limits_names:
                potential_first_name, first_name_namegiver = (
                    self._decide_first_name(potential_namegivers=[])
                )
            baby.first_name = potential_first_name
            potential_middle_name, middle_name_namegiver = (
                self._decide_middle_name(potential_namegivers=potential_namegivers)
            )
            while potential_middle_name == baby.first_name:
                potential_middle_name, middle_name_namegiver = (
                    self._decide_middle_name(potential_namegivers=[])
                )
            baby.middle_name = potential_middle_name
            baby.suffix = ''
            baby.named_for = (first_name_namegiver, middle_name_namegiver)
        baby.last_name = self._decide_last_name()
        baby.maiden_name = baby.last_name

    def _decide_last_name(self):
        """Return what will be the baby's last name."""
        if self.mother.marriage:
            if self.mother.marriage.will_hyphenate_child_surnames:
                last_name = self._get_hyphenated_last_name()
            else:
                last_name = self.father.last_name
        else:
            last_name = self.mother.last_name
        return last_name

    def _get_hyphenated_last_name(self):
        """Get a hyphenated last name for the child, if the parents have decided to attribute one."""
        hyphenated_last_name = "{0}-{1}".format(
            self.father.last_name, self.mother.last_name
        )
        # Check if this child will be the progenitor of this hyphenated surname, i.e.,
        # whether an older sibling has already been given it
        if any(k for k in self.mother.marriage.children_produced if k.maiden_name == hyphenated_last_name):
            older_sibling_with_hyphenated_surname = next(
                k for k in self.mother.marriage.children_produced if k.maiden_name == hyphenated_last_name
            )
            hyphenated_surname_object = older_sibling_with_hyphenated_surname.maiden_name
        else:
            # Instantiate a new Name object with this child as the progenitor
            hyphenated_surname_object = Name(
                hyphenated_last_name, progenitor=self.subject, conceived_by=self.subject.parents,
                derived_from=(self.mother.last_name, self.father.last_name,)
            )
        return hyphenated_surname_object

    def _decide_first_name(self, potential_namegivers):
        """Return what will be the baby's first name."""
        config = self.subject.sim.config
        if potential_namegivers and random.random() < config.chance_child_inherits_first_name:
            first_name_namegiver = random.choice(potential_namegivers)
            first_name = first_name_namegiver.first_name
        else:
            first_name_namegiver = None
            if self.subject.male:
                first_name_rep = Names.a_masculine_name(year=self.year)
            else:
                first_name_rep = Names.a_feminine_name(year=self.year)
            first_name = Name(
                value=first_name_rep, progenitor=self.subject, conceived_by=self.subject.parents, derived_from=()
            )
        return first_name, first_name_namegiver

    def _decide_middle_name(self, potential_namegivers):
        """Return what will be the baby's first name."""
        config = self.subject.sim.config
        if potential_namegivers and random.random() < config.chance_child_inherits_middle_name:
            middle_name_namegiver = random.choice(potential_namegivers)
            middle_name = middle_name_namegiver.first_name
        else:
            middle_name_namegiver = None
            if self.subject.male:
                middle_name_rep = Names.a_masculine_name(year=self.year)
            else:
                middle_name_rep = Names.a_feminine_name(year=self.year)
            middle_name = Name(
                value=middle_name_rep, progenitor=self.subject, conceived_by=self.subject.parents, derived_from=()
            )
        return middle_name, middle_name_namegiver

    def _get_potential_male_namegivers(self):
        """Return a set of men on the father's side of the family whom the child may be named for."""
        config = self.subject.sim.config
        namegivers = []
        for parent in self.subject.parents:
            # Add the child's legal father
            if parent.male:
                namegivers += [parent] * config.frequency_of_naming_after_father
            # Add the child's (legal) great/grandfathers
            if parent.father:
                namegivers += [parent.father] * config.frequency_of_naming_after_grandfather
                if parent.father.father:
                    namegivers += [parent.father.father] * config.frequency_of_naming_after_greatgrandfather
                if parent.mother.father:
                    namegivers += [parent.mother.father] * config.frequency_of_naming_after_greatgrandfather
            # Add a random sampling child's uncles and great uncles
            namegivers += random.sample(parent.brothers, random.randint(0, len(parent.brothers)))
            namegivers += random.sample(parent.uncles, random.randint(0, len(parent.uncles)))
        return namegivers

    def _get_potential_female_namegivers(self):
        """Return a set of women on the father's side of the family whom the child may be named for."""
        config = self.subject.sim.config
        namegivers = []
        for parent in self.subject.parents:
            # Add the child's mother
            if parent.female:
                namegivers += [parent] * config.frequency_of_naming_after_mother
            # Add the child's (legal) great/grandmothers
            if parent.mother:
                namegivers += [parent.mother] * config.frequency_of_naming_after_grandmother
                if parent.father.mother:
                    namegivers += [parent.father.mother] * config.frequency_of_naming_after_greatgrandmother
                if parent.mother.mother:
                    namegivers += [parent.mother.mother] * config.frequency_of_naming_after_greatgrandmother
            # Add a random sampling child's aunts and great aunts
            namegivers += random.sample(parent.sisters, random.randint(0, len(parent.sisters)))
            namegivers += random.sample(parent.aunts, random.randint(0, len(parent.aunts)))
        return namegivers

    def _get_suffix(self):
        """Return a suffix if the person shares their parent's full name, else an empty string."""
        son, father = self.subject, self.subject.father
        increment_suffix = {
            '': 'II', 'II': 'III', 'III': 'IV', 'IV': 'V', 'V': 'VI',
            'VI': 'VII', 'VII': 'VIII', 'VIII': 'IX', 'IX': 'X'
        }
        suffix = increment_suffix[father.suffix]
        return suffix

    def _take_baby_home(self):
        """Take the baby home to the mother's house."""
        self.subject.move(new_home=self.mother.home, reason=self)

    def _have_mother_potentially_exit_workforce(self):
        """Have the mother potentially quit her job."""
        if not self.town.businesses_of_type('DayCare'):
            # If there's no day care in town, have the mother quit her
            # job; TODO, model other solutions here, like the child staying
            # with a retired family member in town, etc.
            self.mother.occupation.terminate(reason=self)
        else:
            if random.random() < self.mother.sim.config.chance_mother_of_young_children_stays_home(year=self.year):
                self.mother.occupation.terminate(reason=self)


class BusinessConstruction(Event):
    """Construction of the building where a business is headquartered.

    This must be preceded by the business being founded -- the business makes the
    call to instantiate one of these objects -- where in a HouseConstruction the
    direction is opposite: a HouseConstruction object makes the call to instantiate
    a House object.
    """

    def __init__(self, subject, business, architect, demolition_that_preceded_this=None):
        """Initialize a BusinessConstruction object."""
        super(BusinessConstruction, self).__init__(sim=subject.sim)
        self.subject = subject
        self.architect = architect
        self.business = business
        if self.architect:
            self.construction_firm = architect.company
            self.builders = set([
                position.person for position in self.construction_firm.employees if
                position.__class__.__name__ == 'Builder'
            ])
            self.architect.building_constructions.add(self)
        else:
            # Build it yourself
            self.construction_firm = None
            self.builders = {p for p in subject.nuclear_family if p.in_the_workforce}
        self.subject.building_commissions.add(self)
        self.demolition_that_preceded_this = demolition_that_preceded_this
        if demolition_that_preceded_this:
            demolition_that_preceded_this.reason = self

    def __str__(self):
        """Return string representation."""
        return "Construction of {} at {} in {}".format(
            self.business.name, self.business.address, self.year
        )


class BusinessClosure(Event):
    """The closure of a business."""

    def __init__(self, business, reason=None):
        """Initialize a Demolition object."""
        super(BusinessClosure, self).__init__(sim=business.town.sim)
        self.town = business.town
        self.business = business
        self.reason = reason  # Potentially this will point to a object for the owner's Retirement
        business.closure = self
        # The company's out_of_business attribute must be set before anyone is laid off,
        # else the company will try to replace that person
        business.out_of_business = True
        business.closed = self.year
        for employee in list(business.employees):
            LayOff(subject=employee.person, company=business, occupation=employee)
        self.town.companies.remove(business)
        self.town.former_companies.add(business)
        # Demolish the building -- TODO reify buildings separately from companies
        if self.town.businesses_of_type('ConstructionFirm'):
            demolition_company = random.choice(self.town.businesses_of_type('ConstructionFirm'))
        else:
            demolition_company = None
        Demolition(building=business, demolition_company=demolition_company, reason=self)

    def __str__(self):
        """Return string representation."""
        return "Closure of {} in {}".format(
            self.business.name, self.year
        )


class Death(Event):
    """A death of a person in the town."""

    def __init__(self, subject, mortician, cause_of_death):
        """Initialize a Death object."""
        super(Death, self).__init__(sim=subject.sim)
        self.town = subject.town
        self.subject = subject
        self.subject.death_year = self.year
        self.subject.death = self
        self.widow = None  # Will get set by _update_attributes_of_deceased_and_spouse() if person was married
        self.cause = cause_of_death
        self.mortician = mortician
        self.cemetery = self.subject.town.cemetery
        self.next_of_kin = subject.next_of_kin
        subject.town.residents.remove(subject)
        subject.town.deceased.add(subject)
        self._update_attributes_of_deceased_and_spouse()  # Must come before self.subject.go_to()
        self._vacate_job_position_of_the_deceased()
        if mortician:
            # Death shouldn't be possible outside the town, but I'm doing
            # this to be consistent with other event classes
            self.cemetery_plot = self._inter_the_body()
            mortician.body_interments.add(self)
        else:
            self.cemetery_plot = None
        # If this person has kids at home and no spouse to take care of them,
        # have those kids depart the town (presumably to live with relatives
        # elsewhere) -- TODO have the kids be adopted by a relative in town,
        # but watch out, because kids at home may be old maids still living with
        # their parents
        if subject.kids_at_home and not subject.spouse:
            for kid in subject.kids_at_home:
                kid.depart_town()
        # Update attributes of this person's home
        subject.home.residents.remove(subject)
        subject.home.former_residents.add(subject)
        if subject in subject.home.owners:
            subject.home.owners.remove(subject)
            if subject.home.residents and not subject.home.owners:
                self._transfer_ownership_of_home_owned_by_the_deceased()
        subject.go_to(destination=self.town.cemetery)
        subject.gravestone = Gravestone(subject=subject)

    def __str__(self):
        """Return string representation."""
        return "Death of {0} in {1}".format(
            self.subject.name, self.year
        )

    def _update_attributes_of_deceased_and_spouse(self):
        config = self.subject.sim.config
        self.subject.alive = False
        if self.subject.marriage:
            self.widow = widow = self.subject.spouse
            widow.marriage.terminus = self
            widow.marriage = None
            widow.spouse = None
            widow.significant_other = None
            widow.widowed = True
            widow.grieving = True
            widow.chance_of_remarrying = config.function_to_derive_chance_spouse_changes_name_back(
                years_married=self.subject.marriage.duration
            )

    def _vacate_job_position_of_the_deceased(self):
        """Vacate the deceased's job position, if any."""
        if self.subject.occupation:
            self.subject.occupation.terminate(reason=self)

    def _transfer_ownership_of_home_owned_by_the_deceased(self):
        """Transfer ownership of the deceased's home to another one of its residents."""
        self.subject.home.former_owners.add(self.subject)
        if any(r for r in self.subject.home.residents if r.in_the_workforce):
            heir = next(r for r in self.subject.home.residents if r.in_the_workforce)
            self.subject.home.owners = {heir}

    def _inter_the_body(self):
        """Inter the body at the local cemetery."""
        return self.cemetery.inter_person(person=self.subject)


class Demolition(Event):
    """The demolition of a house or other building."""

    def __init__(self, building, demolition_company, reason=None):
        """Initialize a Demolition object."""
        super(Demolition, self).__init__(sim=building.town.sim)
        self.town = building.town
        self.building = building
        self.demolition_company = demolition_company  # ConstructionFirm handling the demolition
        self.reason = reason  # May also get set by HouseConstruction or BusinessConstruction object __init__()
        building.demolition = self
        building.lot.building = None
        building.lot.former_buildings.append(building)
        # If this is a dwelling place, have its now-displaced residents find new housing
        if building.__class__.__name__ is 'House':
            self.town.dwelling_places.remove(building)
            self.town.former_dwelling_places.add(building)
            if building.residents:
                self._have_the_now_displaced_residents_move(house_or_apartment_unit=building)
        if building.__class__.__name__ is 'ApartmentComplex':
            for unit in building.units:
                self.town.dwelling_places.remove(unit)
                self.town.former_dwelling_places.add(unit)
                if unit.residents:
                    self._have_the_now_displaced_residents_move(house_or_apartment_unit=unit)

    def _have_the_now_displaced_residents_move(self, house_or_apartment_unit):
        """Handle the full pipeline from them finding a place to moving into it."""
        an_owner = list(house_or_apartment_unit.owners)[0]
        home_they_will_move_into = an_owner.secure_home()
        if home_they_will_move_into:
            for resident in list(house_or_apartment_unit.residents):
                resident.move(new_home=home_they_will_move_into, reason=self)
        else:
            an_owner.depart_town(
                forced_nuclear_family=house_or_apartment_unit.residents
            )

    def __str__(self):
        """Return string representation."""
        if self.reason:
            return "Demolition of {} on behalf of {} in {}".format(
                self.building.name, self.reason.business, self.year
            )
        else:
            return "Demolition of {} in {}".format(
                self.building.name, self.year
            )


class Departure(Event):
    """A departure by which someone leaves the town (i.e., leaves the simulation)."""

    def __init__(self, subject):
        """Initialize a Departure object."""
        super(Departure, self).__init__(sim=subject.sim)
        self.subject = subject
        subject.town.residents.remove(subject)
        subject.town.departed.add(subject)
        subject.departure = self
        self._vacate_job_position_of_the_departed()
        self.subject.go_to(destination=None)
        self.subject.home.residents.remove(self.subject)
        self.subject.home.former_residents.add(self.subject)
        # Update .neighbor attributes for subject and for their now former neighbors
        self._update_neighbor_attributes()

    def _update_neighbor_attributes(self):
        """Update the neighbor attributes of the people moving and their new and former neighbors"""
        # Prepare the salience increment at play here, because attribute accessing
        # is expensive
        config = self.subject.sim.config
        salience_change_for_former_neighbor = (
            config.salience_increment_from_relationship_change['former neighbor'] -
            config.salience_increment_from_relationship_change['neighbor']
        )
        # Remove the departed from all their old neighbor's .neighbors attribute...
        subject = self.subject
        for old_neighbor in subject.neighbors:
            old_neighbor.neighbors.remove(subject)
            old_neighbor.former_neighbors.add(subject)
            subject.former_neighbors.add(old_neighbor)
            # ...and update the relevant salience values (because people still living in the
            # town may discuss this person)
            old_neighbor.update_salience_of(
                entity=subject, change=salience_change_for_former_neighbor
            )
            subject.update_salience_of(
                entity=old_neighbor, change=salience_change_for_former_neighbor
            )
        # Set the departed's .neighbors attribute to the empty set
        self.subject.neighbors = set()

    def __str__(self):
        """Return string representation."""
        return "Departure of {0} in {1}".format(
            self.subject.name, self.year
        )

    def _vacate_job_position_of_the_departed(self):
        """Vacate the departed's job position, if any."""
        if self.subject.occupation:
            self.subject.occupation.terminate(reason=self)


class Divorce(Event):
    """A divorce between two people in the town."""

    def __init__(self, subjects, lawyer):
        """Initialize a divorce object."""
        super(Divorce, self).__init__(sim=subjects[0].sim)
        self.town = subjects[0].town
        self.subjects = subjects
        self.lawyer = lawyer
        self.marriage = subjects[0].marriage
        self.marriage.terminus = self
        self._update_divorcee_attributes()
        self._have_divorcees_split_up_money()
        self._have_a_spouse_and_possibly_kids_change_name_back()
        if lawyer:
            self.law_firm = lawyer.company
            self.lawyer.filed_divorces.add(self)
        if self.town:
            # Divorce isn't currently possible outside a town, but still
            # doing this to be consistent with other event classes
            self._decide_and_enact_new_living_arrangements()
        else:
            self.law_firm = None

    def __str__(self):
        """Return string representation."""
        return "Divorce of {0} and {1} in {2}".format(
            self.subjects[0].name, self.subjects[1].name, self.year
        )

    def _update_divorcee_attributes(self):
        """Update divorcee attributes that pertain to marriage concerns."""
        spouse1, spouse2 = self.subjects
        config = spouse1.sim.config
        spouse1.marriage = None
        spouse2.marriage = None
        spouse1.spouse = None
        spouse2.spouse = None
        spouse1.significant_other = None
        spouse2.significant_other = None
        spouse1.divorces.append(self)
        spouse2.divorces.append(self)
        spouse1.immediate_family.remove(spouse2)
        spouse2.immediate_family.remove(spouse1)
        # Revert each back to their own extended families
        spouse1.extended_family = (
            spouse1.greatgrandparents | spouse1.immediate_family | spouse1.uncles | spouse1.aunts |
            spouse1.cousins | spouse1.nieces | spouse1.nephews
        )
        spouse2.extended_family = (
            spouse2.greatgrandparents | spouse2.immediate_family | spouse2.uncles | spouse2.aunts |
            spouse2.cousins | spouse2.nieces | spouse2.nephews
        )
        self._have_divorcees_fall_out_of_love(divorcees=self.subjects, config=config)
        # Update salience values
        salience_change = (
            spouse1.sim.config.salience_increment_from_relationship_change['significant other'] +
            spouse1.sim.config.salience_increment_from_relationship_change['immediate family']
        )
        spouse1.update_salience_of(entity=spouse2, change=-salience_change)  # Notice the minus sign
        spouse2.update_salience_of(entity=spouse1, change=-salience_change)

    @staticmethod
    def _have_divorcees_fall_out_of_love(divorcees, config):
        """Make the divorcees (probably) lose each other as their strongest love interests."""
        spouse1, spouse2 = divorcees
        if random.random() < config.chance_a_divorcee_falls_out_of_love:
            spouse1.relationships[spouse2].raw_spark = (
                config.new_raw_spark_value_for_divorcee_who_has_fallen_out_of_love
            )
            spouse1.relationships[spouse2].spark = config.function_to_normalize_raw_spark(
                n_simulated_timesteps=spouse1.sim.n_simulated_timesteps,
                raw_spark=spouse1.relationships[spouse2].raw_spark
            )
            if spouse2 is spouse1.love_interest:
                new_love_interest = max(spouse1.relationships, key=lambda r: spouse1.relationships[r].spark)
                if spouse1.relationships[new_love_interest] > 0:
                    spouse1.love_interest = new_love_interest
                    spouse1.spark_of_love_interest = spouse1.relationships[new_love_interest].spark
        if random.random() < config.chance_a_divorcee_falls_out_of_love:
            spouse2.relationships[spouse1].raw_spark = (
                config.new_raw_spark_value_for_divorcee_who_has_fallen_out_of_love
            )
            spouse2.relationships[spouse1].spark = config.function_to_normalize_raw_spark(
                n_simulated_timesteps=spouse2.sim.n_simulated_timesteps,
                raw_spark=spouse2.relationships[spouse1].raw_spark
            )
            if spouse1 is spouse2.love_interest:
                new_love_interest = max(spouse2.relationships, key=lambda r: spouse2.relationships[r].spark)
                if spouse2.relationships[new_love_interest] > 0:
                    spouse2.love_interest = new_love_interest
                    spouse2.spark_of_love_interest = spouse2.relationships[new_love_interest].spark

    def _have_divorcees_split_up_money(self):
        """Have the divorcees split their money up (50/50)."""
        money_to_split_up = self.marriage.money
        amount_given_to_each = money_to_split_up / 2
        self.subjects[0].money = amount_given_to_each
        self.subjects[1].money = amount_given_to_each

    def _have_a_spouse_and_possibly_kids_change_name_back(self):
        """Have a spouse and kids potentially change their names back."""
        config = self.subjects[0].sim.config
        chance_of_a_name_reversion = config.function_to_derive_chance_spouse_changes_name_back(
            years_married=self.marriage.duration
        )
        if random.random() < chance_of_a_name_reversion:
            for name_change in self.marriage.name_changes:
                name_change.subject.change_name(
                    new_last_name=name_change.old_last_name, reason=self
                )

    def _decide_and_enact_new_living_arrangements(self):
        """Handle the full pipeline from discussion to one spouse (and possibly kids) moving out."""
        spouse_who_will_move_out = self._decide_who_will_move_out()
        kids_who_will_move_out_also = self._decide_which_kids_will_move_out(
            spouse_moving=spouse_who_will_move_out
        )
        family_members_who_will_move = {spouse_who_will_move_out} | kids_who_will_move_out_also
        home_spouse_will_move_to = self._decide_where_spouse_moving_out_will_live(
            spouse_who_will_move=spouse_who_will_move_out
        )
        self._move_spouse_and_possibly_kids_out(
            home_spouse_will_move_to=home_spouse_will_move_to, family_members_who_will_move=family_members_who_will_move
        )

    def _decide_who_will_move_out(self):
        """Decide which of the divorcees will move out."""
        spouse1, spouse2 = self.subjects
        config = spouse1.sim.config
        if spouse1.male:
            if random.random() < config.chance_a_male_divorcee_is_one_who_moves_out:
                spouse_who_will_move_out = spouse1
            else:
                spouse_who_will_move_out = spouse2
        elif spouse2.male:
            if random.random() < config.chance_a_male_divorcee_is_one_who_moves_out:
                spouse_who_will_move_out = spouse2
            else:
                spouse_who_will_move_out = spouse2
        else:
            spouse_who_will_move_out = spouse1
        return spouse_who_will_move_out

    def _decide_which_kids_will_move_out(self, spouse_moving):
        """Decide which kids will also be moving out, if any.

        This currently only has stepkids to the spouse who is staying move out
        along with the spouse who is moving out (who in this case would be their only
        biological parent in the marriage).
        """
        spouse_staying = next(s for s in self.subjects if s is not spouse_moving)
        # In case of a blended family, have kids go with their own parent (these
        # will be empty sets otherwise)
        living_with_spouse_moving = spouse_moving.kids_at_home - spouse_staying.kids_at_home
        # Have any kids they had together stay in the home with that spouse
        return living_with_spouse_moving

    @staticmethod
    def _decide_where_spouse_moving_out_will_live(spouse_who_will_move):
        """Decide where the spouse who is moving out will live.

        This may require that they find a vacant lot to build a home on.
        """
        home_spouse_will_move_into = spouse_who_will_move.secure_home()
        return home_spouse_will_move_into

    def _move_spouse_and_possibly_kids_out(self, home_spouse_will_move_to, family_members_who_will_move):
        """Move the two newlyweds (and any kids) in together.

        Note: The spouse/kids will depart the town (and thus the simulation) if they are
        unable to secure housing.
        """
        if home_spouse_will_move_to:
            for family_member in family_members_who_will_move:
                family_member.move(new_home=home_spouse_will_move_to, reason=self)
        else:
            for family_member in family_members_who_will_move:
                family_member.depart_town()


class Hiring(Event):
    """A hiring of a person by a company to serve in a specific occupational role.

    TODO: Add in data about who they beat out for the job.
    """

    def __init__(self, subject, company, occupation):
        """Initialize a Hiring object."""
        super(Hiring, self).__init__(sim=subject.sim)
        self.subject = subject
        self.company = company
        self.old_occupation = subject.occupation
        self.occupation = occupation
        # Determine whether this was a promotion
        if self.old_occupation and self.old_occupation.company is self.company:
            self.promotion = True
        else:
            self.promotion = False
        self.occupation.hiring = self

    def __str__(self):
        """Return string representation."""
        return "Hiring of {} as {} at {} in {}".format(
            self.subject.name, self.occupation.__class__.__name__, self.company.name, self.year
        )


class HomePurchase(Event):
    """A purchase of a home by a person or couple, with the help of a realtor."""

    def __init__(self, subjects, home, realtor):
        """Initialize a HomePurchase object."""
        super(HomePurchase, self).__init__(sim=subjects[0].sim)
        self.town = subjects[0].town
        self.subjects = subjects
        for subject in subjects:
            subject.home_purchases.append(self)
        self.home = home
        self.home.transactions.append(self)
        self.realtor = realtor
        self._transfer_ownership()
        if realtor:
            self.realty_firm = realtor.company
            self.realtor.home_sales.add(self)
        else:  # No realtor when setting initial owners as people who built the home
            self.realty_firm = None

    def __str__(self):
        """Return string representation."""
        return "Purchase of {0} at {1} by {2} in {3}".format(
            "apartment" if self.home.apartment else "house", self.home.address,
            " and ".join(s.name for s in self.subjects), self.year
        )

    def _transfer_ownership(self):
        """Transfer ownership of this house to its new owners."""
        self.home.former_owners |= self.home.owners
        self.home.owners = set(self.subjects)


class HouseConstruction(Event):
    """Construction of a house."""

    def __init__(self, subjects, architect, lot, demolition_that_preceded_this=None):
        """Initialize a HouseConstruction object."""
        super(HouseConstruction, self).__init__(sim=subjects[0].sim)
        self.subjects = subjects
        self.architect = architect
        self.house = House(lot=lot, construction=self)
        if self.architect:
            self.construction_firm = architect.company
            self.builders = set([
                position.person for position in self.construction_firm.employees if
                position.__class__.__name__ == 'Builder'
            ])
            self.architect.building_constructions.add(self)
        else:
            self.construction_firm = None
            self.builders = set()
        for subject in self.subjects:
            subject.building_commissions.add(self)
        self.demolition_that_preceded_this = demolition_that_preceded_this
        if demolition_that_preceded_this:
            demolition_that_preceded_this.reason = self

    def __str__(self):
        """Return string representation."""
        subjects_str = ', '.join(s.name for s in self.subjects)
        if self.construction_firm:
            return "Construction of house at {} by {} for {} in {}".format(
                self.house.address, self.construction_firm, subjects_str, self.year
            )
        else:
            return "Construction of house at {} for {} in {}".format(
                self.house.address, subjects_str, self.year
            )


class LayOff(Event):
    """A laying off of a person by a company that is going out of business."""

    def __init__(self, subject, company, occupation):
        """Initialize a LayOff object."""
        super(LayOff, self).__init__(sim=subject.sim)
        self.subject = subject
        subject.lay_offs.append(self)
        self.company = company
        self.reason = company.closure
        self.occupation = occupation
        self.occupation.terminate(reason=self)

    def __str__(self):
        """Return string representation."""
        return "Laying off of {} as {} at {} in {}".format(
            self.subject.name, self.occupation.__class__.__name__, self.occupation.company.name, self.year
        )


class Marriage(Event):
    """A marriage between two people in the town."""

    def __init__(self, subjects):
        """Initialize a Marriage object."""
        super(Marriage, self).__init__(sim=subjects[0].sim)
        self.town = subjects[0].town
        self.subjects = subjects
        self.names_at_time_of_marriage = (self.subjects[0].name, self.subjects[1].name)
        self.name_changes = []  # Gets set by NameChange object, as appropriate
        self.terminus = None  # May point to a Divorce or Death object, as determined by self.terminate()
        self.money = None  # Gets set by self._have_newlyweds_pool_money_together()
        self.children_produced = set()  # Gets set by Birth objects, as appropriate
        self._update_newlywed_attributes()
        self._have_newlyweds_pool_money_together()
        self._have_one_spouse_and_possibly_stepchildren_take_the_others_name()
        self.will_hyphenate_child_surnames = self._decide_whether_children_will_get_hyphenated_names()
        if self.town:
            self._decide_and_enact_new_living_arrangements()
            # If they're not in the town yet (marriage between two PersonsExNihilo during
            # world generation), living arrangements will be made once they move into it

    def __str__(self):
        """Return string representation."""
        return "Marriage between {} and {} in {}".format(
            self.names_at_time_of_marriage[0], self.names_at_time_of_marriage[1], self.year
        )

    @property
    def duration(self):
        """Return the duration of this marriage."""
        if self.terminus:
            duration = self.terminus.year - self.year
        else:
            duration = self.subjects[0].sim.year-self.year
        return duration

    def _update_newlywed_attributes(self):
        """Update newlywed attributes that pertain to marriage concerns."""
        spouse1, spouse2 = self.subjects
        spouse1.marriage = self
        spouse2.marriage = self
        spouse1.marriages.append(self)
        spouse2.marriages.append(self)
        spouse1.spouse = spouse2
        spouse2.spouse = spouse1
        spouse1.significant_other = spouse2
        spouse2.significant_other = spouse1
        spouse1.immediate_family.add(spouse2)
        spouse2.immediate_family.add(spouse1)
        spouse1.extended_family |= spouse2.extended_family  # TODO THIS IS NOT TOTALLY ACCURATE
        spouse2.extended_family |= spouse1.extended_family
        self._cease_grieving_of_former_spouses(newlyweds=self.subjects)
        # Update salience values
        salience_change = (
            spouse1.sim.config.salience_increment_from_relationship_change['significant other'] +
            spouse1.sim.config.salience_increment_from_relationship_change['immediate family']
        )
        spouse1.update_salience_of(entity=spouse2, change=salience_change)
        spouse2.update_salience_of(entity=spouse1, change=salience_change)

    @staticmethod
    def _cease_grieving_of_former_spouses(newlyweds):
        """Make the newlyweds stop grieving former spouses, if applicable."""
        if any(newlywed for newlywed in newlyweds if newlywed.grieving):
            for newlywed in newlyweds:
                newlywed.grieving = False

    def _have_newlyweds_pool_money_together(self):
        """Have the newlyweds combine their money holdings into a single account."""
        self.money = self.subjects[0].money + self.subjects[1].money
        self.subjects[0].money = 0
        self.subjects[1].money = 0

    def _have_one_spouse_and_possibly_stepchildren_take_the_others_name(self):
        """Have one spouse (potentially) take the other's name.

        TODO: Have this be affected by the newlyweds' personalities."""
        config = self.subjects[0].sim.config
        if any(newlywed for newlywed in self.subjects if newlywed.female):
            spouse_who_may_take_name = next(newlywed for newlywed in self.subjects if newlywed.female)
        else:
            spouse_who_may_take_name = self.subjects[0]
        other_spouse = next(newlywed for newlywed in self.subjects if newlywed is not spouse_who_may_take_name)
        if spouse_who_may_take_name.last_name is not other_spouse.last_name:
            if random.random() < config.chance_one_newlywed_takes_others_name:
                spouse_who_may_take_name.change_name(new_last_name=other_spouse.last_name, reason=self)
        if random.random() < config.chance_stepchildren_take_stepparent_name:
            for stepchild in spouse_who_may_take_name.kids:
                if stepchild.age <= config.age_after_which_stepchildren_will_not_take_stepparent_name:
                    stepchild.change_name(new_last_name=other_spouse.last_name, reason=self)

    def _decide_whether_children_will_get_hyphenated_names(self):
        """Decide whether any children resulting from this marriage will get hyphenated names.

        TODO: Have this be affected by newlywed personalities.
        """
        if self.subjects[0].last_name != self.subjects[1].last_name:  # First, make sure they have different surnames
            config = self.subjects[0].sim.config
            if any(s for s in self.subjects if s.last_name.hyphenated):
                choice = False
            elif random.random() < config.chance_newlyweds_decide_children_will_get_hyphenated_surname:
                choice = True
            else:
                choice = False
        else:
            choice = False
        return choice

    def _decide_and_enact_new_living_arrangements(self):
        """Handle the full pipeline from finding a place to moving into it."""
        home_they_will_move_into = self._decide_where_newlyweds_will_live()
        # This method may spark a departure if they are not able to secure housing in town
        self._move_spouses_and_any_kids_in_together(home_they_will_move_into=home_they_will_move_into)

    def _decide_where_newlyweds_will_live(self):
        """Decide where the newlyweds will live.

        This may require that they find a vacant lot to build a home on.
        """
        # If one of the newlyweds has their own place, have them move in there
        if any(s for s in self.subjects if s in s.home.owners):
            home_they_will_move_into = next(s for s in self.subjects if s in s.home.owners).home
        else:
            # If they both live at home, have them find a vacant home to move into
            # or a vacant lot to build on (it doesn't matter which person the method is
            # called for -- both will take part in the decision making)
            home_they_will_move_into = self.subjects[0].secure_home()
        return home_they_will_move_into

    def _move_spouses_and_any_kids_in_together(self, home_they_will_move_into):
        """Move the two newlyweds (and any kids) in together.

        Note: The family will depart the town (and thus the simulation) if they are
        unable to secure housing.
        """
        spouse1, spouse2 = self.subjects
        family_members_that_will_move = set()
        if home_they_will_move_into is not spouse1.home:
            # Have (non-adult) children of spouse1, if any, also move too
            family_members_that_will_move.add(spouse1)
            for kid in spouse1.kids:
                if kid.present and kid.home is spouse1.home:
                    family_members_that_will_move.add(kid)
        if home_they_will_move_into is not spouse2.home:
            family_members_that_will_move.add(spouse2)
            # Have (non-adult) children of spouse2, if any, also move too
            for kid in spouse2.kids:
                if kid.present and not kid.marriage and kid.home is spouse2.home:
                    family_members_that_will_move.add(kid)
        if home_they_will_move_into:
            # Make sure both spouses are among the home's listed owners
            for spouse in self.subjects:
                home_they_will_move_into.owners.add(spouse)
            # Move the whole family in
            for family_member in family_members_that_will_move:
                family_member.move(new_home=home_they_will_move_into, reason=self)
        else:
            # This will spark a Departure for each person in family_members_that_will_move
            self.subjects[0].depart_town(
                forced_nuclear_family=family_members_that_will_move
            )


class Move(Event):
    """A move from one home into another, or from no home to a home."""

    def __init__(self, subjects, new_home, reason):
        """Initialize a Move object."""
        super(Move, self).__init__(sim=subjects[0].sim)
        self.subjects = subjects
        self.old_home = self.subjects[0].home  # May be None if newborn or person moved from outside the town
        self.new_home = new_home
        if self.old_home:
            self.old_home.move_outs.append(self)
        self.new_home.move_ins.append(self)
        self.reason = reason  # Will (likely) point to an Occupation object, or else a Marriage or Divorce object
        # Actually move the person(s)
        for person in self.subjects:
            # Move out of old home, if any
            if person.home:
                person.home.residents.remove(person)
                person.home.former_residents.add(person)
            # Move into new home
            person.home = new_home
            new_home.residents.add(person)
            person.moves.append(self)
            # Add yourself to town residents, if you moved from outside the town
            person.town = person.sim.town
            person.sim.town.residents.add(person)
            # Go to your new home
            person.go_to(destination=new_home, occasion='home')
        # Update .neighbor attributes for subjects, as well as their new and now former neighbors
        self._update_mover_and_neighbor_attributes()

    def _update_mover_and_neighbor_attributes(self):
        """Update the neighbor attributes of the people moving and their new and former neighbors"""
        # Collect relevant salience increments (because attribute accessing is expensive)
        config = self.subjects[0].sim.config
        salience_change_for_former_neighbor = (
            config.salience_increment_from_relationship_change['former neighbor'] -
            config.salience_increment_from_relationship_change['neighbor']
        )
        salience_change_for_new_neighbor = (
            config.salience_increment_from_relationship_change['neighbor']
        )
        movers = set(self.subjects)
        # Collect all now former neighbors
        old_neighbors = set()
        for mover in movers:
            old_neighbors |= mover.neighbors
        # Update the old neighbors' .neighbors and .former_neighbors attributes (no need
        # to update the movers' .neighbors attributes in this loop as those will be totally
        # overwritten below)
        for mover in movers:
            for this_movers_old_neighbor in mover.neighbors:
                this_movers_old_neighbor.neighbors.remove(mover)
                this_movers_old_neighbor.former_neighbors.add(mover)
                mover.former_neighbors.add(this_movers_old_neighbor)
                # Also update salience values
                this_movers_old_neighbor.update_salience_of(
                    entity=mover, change=salience_change_for_former_neighbor
                )
                mover.update_salience_of(
                    entity=this_movers_old_neighbor, change=salience_change_for_former_neighbor
                )
        # Update the movers' .neighbors attributes by...
        new_neighbors = set()
        # ...surveying all people living on neighboring lots
        for lot in self.new_home.lot.neighboring_lots:
            if lot.building:
                new_neighbors |= lot.building.residents
        # ...surveying other people in the apartment complex, if new_home is an apartment unit;
        # note that we have to check whether the apartment even has units left, because this
        # method may be called for someone moving into the ApartmentComplex before it has even
        # been fully instantiated (i.e., someone hired to start working there moves into it before
        # its init() call has finished)
        if self.new_home.apartment:
            neighbors_in_the_same_complex = self.new_home.complex.residents - movers
            new_neighbors |= neighbors_in_the_same_complex
        # Make sure none of the residents you will be moving in with were included (e.g.,
        # in the case of a baby being brought home)
        new_neighbors -= self.new_home.residents
        # Update the .neighbors attribute of all new neighbors, as well as salience values
        for mover in movers:
            mover.neighbors = set(new_neighbors)
            for new_neighbor in new_neighbors:
                mover.update_salience_of(entity=new_neighbor, change=salience_change_for_new_neighbor)
                new_neighbor.neighbors.add(mover)
                new_neighbor.update_salience_of(entity=mover, change=salience_change_for_new_neighbor)

    def __str__(self):
        """Return string representation."""
        return "Move to {0} at {1} by {2} in {3}".format(
            "apartment" if self.new_home.apartment else "house", self.new_home.address,
            ", ".join(s.name for s in self.subjects), self.year
        )


class NameChange(Event):
    """A (legal) name change someone makes."""

    def __init__(self, subject, new_last_name, reason, lawyer):
        """Initialize a NameChange object."""
        super(NameChange, self).__init__(sim=subject.sim)
        self.town = subject.town
        self.subject = subject
        self.old_last_name = subject.last_name
        self.new_last_name = new_last_name
        self.old_name = subject.name
        self.lawyer = lawyer
        # Actually change the name
        subject.last_name = new_last_name
        self.new_name = subject.name
        self.reason = reason  # Likely will point to a Marriage or Divorce object
        if isinstance(reason, Marriage):
            reason.name_changes.append(self)
        subject.name_changes.append(self)
        if lawyer:
            self.law_firm = lawyer.company
            self.lawyer.filed_name_changes.add(self)
        else:
            self.law_firm = None

    def __str__(self):
        """Return string representation."""
        return "Name change by which {} became known as {} in {}".format(
            self.old_name, self.new_name, self.year
        )


class Retirement(Event):
    """A retirement by which a person ceases some occupation."""

    def __init__(self, subject):
        """Initialize a Retirement object."""
        super(Retirement, self).__init__(sim=subject.sim)
        self.subject = subject
        self.subject.retired = True
        self.subject.retirement = self
        self.occupation = self.subject.occupation
        self.company = self.subject.occupation.company
        self.occupation.terminus = self
        self.subject.occupation.terminate(reason=self)

    def __str__(self):
        """Return string representation."""
        return "Retirement of {} as {} at {} in {}".format(
            self.subject.name, self.occupation.__class__.__name__, self.occupation.company.name, self.year
        )
