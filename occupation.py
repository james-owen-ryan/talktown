import string
from life_event import *


class Occupation(object):
    """An occupation at a business in a town."""

    def __init__(self, person, company, shift):
        """Initialize an Occupation object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        @param shift: Whether this position is for the day or night shift.
        """
        self.person = person
        self.company = company
        self.shift = shift
        self.company.employees.add(self)
        self.start_date = person.sim.year
        self.hiring = None  # event.Hiring object holding data about the hiring; gets set by that object's __init__()
        self.end_date = None  # Changed by self.terminate
        self.terminus = None  # Changed by self.terminate
        self.preceded_by = None  # Employee that preceded this one in its occupation -- gets set by Business.hire()
        self.succeeded_by = None  # Employee that succeeded this one in its occupation -- gets set by Business.hire()
        self.supplemental = False  # Whether this position must be immediately refilled if terminated -- Business.hire()
        self.hired_as_favor = False  # Whether this position must ever be refilled if terminated -- Business.hire()
        self.vocation = self._init_generate_vocation_string()
        # Note: self.person.occupation gets set by Business.hire(), because there's
        # a really tricky pipeline that has to be maintained
        person.occupations.append(self)
        self.level = person.sim.config.job_levels[self.__class__]
        # Update the .coworkers attribute of this person and their new coworkers
        person.coworkers = set()  # Wash out their former coworkers, if any
        person.coworkers = {employee.person for employee in self.company.employees} - {person}
        for coworker in person.coworkers:
            coworker.coworkers.add(person)
        # Update relevant salience values for this person and their new coworkers
        salience_change_for_new_coworker = (
            self.person.sim.config.salience_increment_from_relationship_change['coworker']
        )
        for coworker in person.coworkers:
            person.update_salience_of(entity=coworker, change=salience_change_for_new_coworker)
            coworker.update_salience_of(entity=person, change=salience_change_for_new_coworker)
        # Update the salience value for this person held by everyone else in the town to
        # reflect their new job level
        boost_in_salience_for_this_job_level = self.person.sim.config.salience_job_level_boost(
            job_level=self.level
        )
        for resident in company.town.residents:
            resident.update_salience_of(entity=self.person, change=boost_in_salience_for_this_job_level)
        # Update all relationships this person has to reflect the new job-level difference
        # between this person and the respective other person
        for other_person in self.person.relationships:
            self.person.relationships[other_person].update_spark_and_charge_increments_for_job_level_difference()

    def __str__(self):
        """Return string representation."""
        if not self.terminus:
            return "{} at {} since {}".format(
                self.__class__.__name__, self.company.name, self.start_date
            )
        else:
            return "{} at {} {}-{}".format(
                self.__class__.__name__, self.company.name, self.start_date, self.end_date
            )

    def _init_generate_vocation_string(self):
        """Generate a properly formatted vocation string for this occupation."""
        class_name = self.__class__.__name__
        try:
            camel_case_char = next(letter for letter in class_name[1:] if letter in string.uppercase)
            index_of_camel_case_char = class_name.index(camel_case_char)
            if index_of_camel_case_char == 0:
                index_of_camel_case_char = class_name[1:].index(camel_case_char) + 1
            return "{} {}".format(
                class_name[:index_of_camel_case_char].lower(),
                class_name[index_of_camel_case_char:].lower()
            )
        except StopIteration:
            return class_name.lower()

    @property
    def years_experience(self):
        """Return years this person has had this occupation."""
        return self.person.sim.year - self.start_date

    @property
    def has_a_boss(self):
        """Return whether the person with this occupation has a boss."""
        return True if self.company.owner is not self else False

    def terminate(self, reason):
        """Terminate this occupation, due to another hiring, retirement, or death or departure."""
        self.end_date = self.person.sim.year
        self.terminus = reason
        self.company.employees.remove(self)
        self.company.former_employees.add(self)
        if self is self.company.owner:
            self.company.former_owners.append(self)
        # If this isn't an in-house promotion, update a bunch of attributes
        in_house_promotion = (isinstance(reason, Hiring) and reason.promotion)
        if not in_house_promotion:
            # Update the .coworkers attribute of the person's now former coworkers
            for employee in self.company.employees:
                employee.person.coworkers.remove(self.person)
            # Update the .former_coworkers attribute of everyone involved to reflect this change
            for employee in self.company.employees:
                self.person.former_coworkers.add(employee.person)
                employee.person.former_coworkers.add(self.person)
            # Update all relevant salience values for everyone involved
            config = self.person.sim.config
            change_in_salience_for_former_coworker = (
                config.salience_increment_from_relationship_change["former coworker"] -
                config.salience_increment_from_relationship_change["coworker"]
            )
            for employee in self.company.employees:
                employee.person.update_salience_of(
                    entity=self.person, change=change_in_salience_for_former_coworker
                )
                self.person.update_salience_of(
                    entity=employee.person, change=change_in_salience_for_former_coworker
                )
        # This position is now vacant, so now have the company that this person worked
        # for fill that now vacant position (which may cause a hiring chain) unless
        # this position is supplemental (i.e., not vital to this businesses' basic
        # operation), in which case we add it back into the business's listing of
        # supplemental positions that may be filled at some point that someone really
        # needs work; if this person was hired as a favor by a family member who owned
        # the associated company, we don't even do that much, since that company doesn't
        # ever need to refill that position (i.e., the position was more supplemental than
        # even supplemental positions and was created solely for the purpose of helping out
        # a family member seeking work)
        if not self.company.out_of_business:
            position_that_is_now_vacant = self.__class__
            if not self.supplemental:
                self.company.hire(
                    occupation_of_need=position_that_is_now_vacant, shift=self.shift, to_replace=self
                )
            elif not self.hired_as_favor:
                self.company.supplemental_vacancies[self.shift].append(position_that_is_now_vacant)
        # If the person hasn't already been hired to a new position, set their occupation
        # attribute to None
        if self.person.occupation is self:
            self.person.occupation = None
        # If this person is retiring, set their .coworkers to the empty set
        if reason.__class__.__name__ == "Retirement":
            self.person.coworkers = set()
        else:
            # If they're not retiring, decrement their salience to everyone else
            # commensurate to the job level of this position
            change_in_salience_for_this_job_level = self.person.sim.config.salience_job_level_boost(
                job_level=self.level
            )
            for resident in self.company.town.residents:
                # Note the minus sign here
                resident.update_salience_of(
                    entity=self.person, change=-change_in_salience_for_this_job_level
                )
        # Finally, if this was a Lawyer position, have the law firm rename itself to
        # no longer include this person's name
        if self.__class__ is Lawyer:
            self.company.rename_due_to_lawyer_change()


class Cashier(Occupation):
    """A cashier at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Cashier object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Cashier, self).__init__(person=person, company=company, shift=shift)


class Janitor(Occupation):
    """A janitor at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Janitor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Janitor, self).__init__(person=person, company=company, shift=shift)


class Manager(Occupation):
    """A manager at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Manager object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Manager, self).__init__(person=person, company=company, shift=shift)


class Secretary(Occupation):
    """A secretary at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Secretary object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Secretary, self).__init__(person=person, company=company, shift=shift)


class Proprietor(Occupation):
    """A proprietor of a business."""

    def __init__(self, person, company, shift):
        """Initialize a Proprietor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Proprietor, self).__init__(person=person, company=company, shift=shift)


class Owner(Occupation):
    """An owner of a business."""

    def __init__(self, person, company, shift):
        """Initialize an Owner object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Owner, self).__init__(person=person, company=company, shift=shift)


class Bottler(Occupation):
    """A bottler at a brewery, dairy, or distillery."""

    def __init__(self, person, company, shift):
        """Initialize a Bottler object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Bottler, self).__init__(person=person, company=company, shift=shift)


class Groundskeeper(Occupation):
    """A mortician at a cemetery or park."""

    def __init__(self, person, company, shift):
        """Initialize a Mortician object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Groundskeeper, self).__init__(person=person, company=company, shift=shift)


class Nurse(Occupation):
    """A nurse at a hospital, optometry clinic, plastic-surgery clinic, or school."""

    def __init__(self, person, company, shift):
        """Initialize a Nurse object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Nurse, self).__init__(person=person, company=company, shift=shift)


class Apprentice(Occupation):
    """An apprentice at a blacksmith shop."""

    def __init__(self, person, company, shift):
        """Initialize an Apprentice object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Apprentice, self).__init__(person=person, company=company, shift=shift)


class Architect(Occupation):
    """An architect at a construction firm."""

    def __init__(self, person, company, shift):
        """Initialize an Architect object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Architect, self).__init__(person=person, company=company, shift=shift)
        # Work accomplishments
        self.building_constructions = set()
        self.house_constructions = set()


class BankTeller(Occupation):
    """A bank teller at a bank."""

    def __init__(self, person, company, shift):
        """Initialize a BankTeller object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(BankTeller, self).__init__(person=person, company=company, shift=shift)


class Bartender(Occupation):
    """A bartender at a bar."""

    def __init__(self, person, company, shift):
        """Initialize a Bartender object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Bartender, self).__init__(person=person, company=company, shift=shift)


class BusDriver(Occupation):
    """A bus driver at a bus depot."""

    def __init__(self, person, company, shift):
        """Initialize a BusDriver object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(BusDriver, self).__init__(person=person, company=company, shift=shift)


class Concierge(Occupation):
    """A concierge at a hotel."""

    def __init__(self, person, company, shift):
        """Initialize a Concierge object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Concierge, self).__init__(person=person, company=company, shift=shift)


class Builder(Occupation):
    """A builder at a construction firm."""

    def __init__(self, person, company, shift):
        """Initialize a Builder object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Builder, self).__init__(person=person, company=company, shift=shift)


class DaycareProvider(Occupation):
    """A person who works at a day care."""

    def __init__(self, person, company, shift):
        """Initialize a DaycareProvider object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(DaycareProvider, self).__init__(person=person, company=company, shift=shift)


class Doctor(Occupation):
    """A doctor at a hospital."""

    def __init__(self, person, company, shift):
        """Initialize a Doctor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Doctor, self).__init__(person=person, company=company, shift=shift)
        # Work accomplishments
        self.baby_deliveries = set()

    def deliver_baby(self, mother):
        """Instantiate a new Birth object."""
        Birth(mother=mother, doctor=self)


class FireChief(Occupation):
    """A fire chief at a fire station."""

    def __init__(self, person, company, shift):
        """Initialize a FireChief object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(FireChief, self).__init__(person=person, company=company, shift=shift)


class Firefighter(Occupation):
    """A firefighter at a fire station."""

    def __init__(self, person, company, shift):
        """Initialize a Firefighter object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Firefighter, self).__init__(person=person, company=company, shift=shift)


class Barber(Occupation):
    """A barber at a barbershop."""

    def __init__(self, person, company, shift):
        """Initialize a Barber object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Barber, self).__init__(person=person, company=company, shift=shift)


class HotelMaid(Occupation):
    """A hotel maid at a hotel."""

    def __init__(self, person, company, shift):
        """Initialize a HotelMaid object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(HotelMaid, self).__init__(person=person, company=company, shift=shift)


class Lawyer(Occupation):
    """A lawyer at a law firm."""

    def __init__(self, person, company, shift):
        """Initialize a Lawyer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Lawyer, self).__init__(person=person, company=company, shift=shift)
        # Work accomplishments
        self.filed_divorces = set()
        self.filed_name_changes = set()
        # Have the law firm rename itself to include your name
        self.company.rename_due_to_lawyer_change()

    def file_divorce(self, clients):
        """File a name change on behalf of person."""
        Divorce(subjects=clients, lawyer=self)

    def file_name_change(self, person, new_last_name, reason):
        """File a name change on behalf of person."""
        NameChange(subject=person, new_last_name=new_last_name, reason=reason, lawyer=self)


class Mayor(Occupation):
    """A mayor at the city hall."""

    def __init__(self, person, company, shift):
        """Initialize a Mayor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Mayor, self).__init__(person=person, company=company, shift=shift)


class Mortician(Occupation):
    """A mortician at a cemetery."""

    def __init__(self, person, company, shift):
        """Initialize a Mortician object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Mortician, self).__init__(person=person, company=company, shift=shift)
        # Work accomplishments
        self.body_interments = set()

    def inter_body(self, deceased, cause_of_death):
        """Inter a body in a cemetery."""
        Death(subject=deceased, mortician=self, cause_of_death=cause_of_death)


class Optometrist(Occupation):
    """An optometrist at an optometry clinic."""

    def __init__(self, person, company, shift):
        """Initialize an Optometrist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Optometrist, self).__init__(person=person, company=company, shift=shift)


class PlasticSurgeon(Occupation):
    """A plastic surgeon at a plastic-surgery clinic."""

    def __init__(self, person, company, shift):
        """Initialize a PlasticSurgeon object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(PlasticSurgeon, self).__init__(person=person, company=company, shift=shift)


class PoliceChief(Occupation):
    """A police chief at a police station."""

    def __init__(self, person, company, shift):
        """Initialize a PoliceChief object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(PoliceChief, self).__init__(person=person, company=company, shift=shift)


class PoliceOfficer(Occupation):
    """A police officer at a police station."""

    def __init__(self, person, company, shift):
        """Initialize a PoliceOfficer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(PoliceOfficer, self).__init__(person=person, company=company, shift=shift)


class Principal(Occupation):
    """A principal at a school."""

    def __init__(self, person, company, shift):
        """Initialize a Principal object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Principal, self).__init__(person=person, company=company, shift=shift)


class Realtor(Occupation):
    """A realtor at a realty firm."""

    def __init__(self, person, company, shift):
        """Initialize an Realtor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Realtor, self).__init__(person=person, company=company, shift=shift)
        # Work accomplishments
        self.home_sales = set()


class Professor(Occupation):
    """A professor at the university."""

    def __init__(self, person, company, shift):
        """Initialize a Professor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Professor, self).__init__(person=person, company=company, shift=shift)


class TattooArtist(Occupation):
    """A tattoo artist at a tattoo parlor."""

    def __init__(self, person, company, shift):
        """Initialize a TattooArtist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(TattooArtist, self).__init__(person=person, company=company, shift=shift)


class TaxiDriver(Occupation):
    """A taxi driver at a taxi depot."""

    def __init__(self, person, company, shift):
        """Initialize a TaxiDriver object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(TaxiDriver, self).__init__(person=person, company=company, shift=shift)


class Teacher(Occupation):
    """A teacher at the K-12 school."""

    def __init__(self, person, company, shift):
        """Initialize a Teacher object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Teacher, self).__init__(person=person, company=company, shift=shift)


class Waiter(Occupation):
    """A waiter at a restaurant."""

    def __init__(self, person, company, shift):
        """Initialize a Waiter object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Waiter, self).__init__(person=person, company=company, shift=shift)


class Baker(Occupation):
    """A baker at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Baker object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Baker, self).__init__(person=person, company=company, shift=shift)


class Barkeeper(Occupation):
    """A barkeeper at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Barkeeper object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Barkeeper, self).__init__(person=person, company=company, shift=shift)


class Blacksmith(Occupation):
    """A blacksmith at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Blacksmith object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Blacksmith, self).__init__(person=person, company=company, shift=shift)


class Brewer(Occupation):
    """A brewer at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Brewer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Brewer, self).__init__(person=person, company=company, shift=shift)


class Bricklayer(Occupation):
    """A bricklayer at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Bricklayer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Bricklayer, self).__init__(person=person, company=company, shift=shift)


class Busboy(Occupation):
    """A busboy at a restaurant."""

    def __init__(self, person, company, shift):
        """Initialize a Busboy object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Busboy, self).__init__(person=person, company=company, shift=shift)


class Butcher(Occupation):
    """A butcher at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Butcher object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Butcher, self).__init__(person=person, company=company, shift=shift)


class Carpenter(Occupation):
    """A carpenter at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Carpenter object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Carpenter, self).__init__(person=person, company=company, shift=shift)


class Clothier(Occupation):
    """A clothier at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Clothier object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Clothier, self).__init__(person=person, company=company, shift=shift)


class Cook(Occupation):
    """A cook at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Cook object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Cook, self).__init__(person=person, company=company, shift=shift)


class Cooper(Occupation):
    """A cooper at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Cooper object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Cooper, self).__init__(person=person, company=company, shift=shift)


class Dentist(Occupation):
    """A dishwasher at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Dentist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Dentist, self).__init__(person=person, company=company, shift=shift)


class Dishwasher(Occupation):
    """A dishwasher at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Dishwasher object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Dishwasher, self).__init__(person=person, company=company, shift=shift)


class Distiller(Occupation):
    """A distiller at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Distiller object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Distiller, self).__init__(person=person, company=company, shift=shift)


class Dressmaker(Occupation):
    """A dressmaker at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Dressmaker object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Dressmaker, self).__init__(person=person, company=company, shift=shift)


class Druggist(Occupation):
    """A druggist at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Druggist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Druggist, self).__init__(person=person, company=company, shift=shift)


class Engineer(Occupation):
    """An engineer at a coal mine or quarry."""

    def __init__(self, person, company, shift):
        """Initialize a Engineer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Engineer, self).__init__(person=person, company=company, shift=shift)


class Farmer(Occupation):
    """A farmer at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Farmer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Farmer, self).__init__(person=person, company=company, shift=shift)


class Farmhand(Occupation):
    """A farmhand at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Farmhand object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Farmhand, self).__init__(person=person, company=company, shift=shift)


class Grocer(Occupation):
    """A grocer at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Grocer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Grocer, self).__init__(person=person, company=company, shift=shift)


class Innkeeper(Occupation):
    """A innkeeper at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Innkeeper object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Innkeeper, self).__init__(person=person, company=company, shift=shift)


class InsuranceAgent(Occupation):
    """A insuranceagent at a business."""

    def __init__(self, person, company, shift):
        """Initialize a InsuranceAgent object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(InsuranceAgent, self).__init__(person=person, company=company, shift=shift)


class Jeweler(Occupation):
    """A jeweler at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Jeweler object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Jeweler, self).__init__(person=person, company=company, shift=shift)


class Joiner(Occupation):
    """A joiner at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Joiner object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Joiner, self).__init__(person=person, company=company, shift=shift)


class Laborer(Occupation):
    """A laborer at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Laborer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Laborer, self).__init__(person=person, company=company, shift=shift)


class Landlord(Occupation):
    """A landlord at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Landlord object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Landlord, self).__init__(person=person, company=company, shift=shift)


class Milkman(Occupation):
    """A milkman at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Milkman object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Milkman, self).__init__(person=person, company=company, shift=shift)


class Miner(Occupation):
    """A miner at a coal mine."""

    def __init__(self, person, company, shift):
        """Initialize a Miner object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Miner, self).__init__(person=person, company=company, shift=shift)


class Molder(Occupation):
    """A molder at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Molder object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Molder, self).__init__(person=person, company=company, shift=shift)


class Painter(Occupation):
    """A painter at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Painter object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Painter, self).__init__(person=person, company=company, shift=shift)


class Pharmacist(Occupation):
    """A pharmacist at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Pharmacist object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Pharmacist, self).__init__(person=person, company=company, shift=shift)


class Plasterer(Occupation):
    """A plasterer at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Plasterer object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Plasterer, self).__init__(person=person, company=company, shift=shift)


class Plumber(Occupation):
    """A plumber at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Plumber object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Plumber, self).__init__(person=person, company=company, shift=shift)


class Puddler(Occupation):
    """A puddler at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Puddler object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Puddler, self).__init__(person=person, company=company, shift=shift)


class Quarryman(Occupation):
    """A quarryman at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Quarryman object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Quarryman, self).__init__(person=person, company=company, shift=shift)


class Seamstress(Occupation):
    """A seamstress at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Seamstress object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Seamstress, self).__init__(person=person, company=company, shift=shift)


class Shoemaker(Occupation):
    """A shoemaker at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Shoemaker object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Shoemaker, self).__init__(person=person, company=company, shift=shift)


class Stocker(Occupation):
    """A stocker at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Stocker object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Stocker, self).__init__(person=person, company=company, shift=shift)


class Stonecutter(Occupation):
    """A stonecutter at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Stonecutter object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Stonecutter, self).__init__(person=person, company=company, shift=shift)


class Tailor(Occupation):
    """A tailor at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Tailor object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Tailor, self).__init__(person=person, company=company, shift=shift)


class Turner(Occupation):
    """A turner at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Turner object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Turner, self).__init__(person=person, company=company, shift=shift)


class Whitewasher(Occupation):
    """A whitewasher at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Whitewasher object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Whitewasher, self).__init__(person=person, company=company, shift=shift)


class Woodworker(Occupation):
    """A woodworker at a business."""

    def __init__(self, person, company, shift):
        """Initialize a Woodworker object.

        @param person: The Person object for the person whose occupation this is.
        @param company: The Company object for the company that person works for in this capacity.
        """
        super(Woodworker, self).__init__(person=person, company=company, shift=shift)