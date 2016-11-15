import random


class DwellingPlace(object):
    """A dwelling place in a town."""

    def __init__(self, lot, owners):
        """Initialize a DwellingPlace object.

        @param lot: A Lot object representing the lot this building is on.
        """
        self.id = owners[0].sim.current_place_id
        owners[0].sim.current_place_id += 1
        self.type = "residence"
        self.town = lot.town
        self.town.dwelling_places.add(self)
        self.lot = lot
        if self.__class__ is House:
            self.house, self.apartment = True, False
            self.address = self.lot.address
        elif self.__class__ is Apartment:
            self.house, self.apartment = False, True
            self.address = ""  # Gets set by Apartment._init_generate_address()
        self.house_number = lot.house_number
        self.block = lot.block
        self.residents = set()
        self.former_residents = set()
        self.transactions = []
        self.move_ins = []
        self.move_outs = []
        self.owners = set()  # Gets set via self._init_ownership()
        self.former_owners = set()
        self._init_ownership(initial_owners=owners)
        self.people_here_now = set()  # People at home on a specific time step (either a resident or visitor)
        self.demolition = None  # Potentially gets set by event.Demolition.__init__()

    def __str__(self):
        """Return string representation."""
        if self.demolition or self.apartment and self.complex.demolition:
            if self.house:
                construction_year = self.construction.year
                demolition_year = self.demolition.year
            else:
                construction_year = self.complex.construction.year
                demolition_year = self.complex.demolition.year
            return "{}, {} ({}-{})".format(self.name, self.address, construction_year, demolition_year)
        else:
            return "{}, {}".format(self.name, self.address)

    @property
    def locked(self):
        """Return True if the door to this dwelling place is currently locked, else false."""
        locked = False
        if not self.owners:
            locked = True
        elif self.town.sim.time_of_day == 'day' and not self.people_here_now:
            # Randomly decide who was the last to leave this home today
            index_in_owners_of_last_to_leave = int(
                round(self.town.sim.random_number_this_timestep * len(self.owners))
            )
            index_in_owners_of_last_to_leave -= 1
            last_to_leave = list(self.owners)[index_in_owners_of_last_to_leave]
            if self.town.sim.random_number_this_timestep > last_to_leave.personality.neuroticism:
                locked = True
        elif self.town.sim.time_of_day == "night":
            most_neurotic_owner = max(self.owners, key=lambda o: o.personality.neuroticism)
            if self.town.sim.random_number_this_timestep > most_neurotic_owner.personality.neuroticism:
                locked = True
        return locked

    @property
    def name(self):
        """Return the name of this residence."""
        if self.owners:
            owner_surnames = set([o.last_name for o in self.owners])
            name = "{} residence".format('-'.join(owner_surnames))
        else:
            name = 'Uninhabited residence'
        return name

    def _init_ownership(self, initial_owners):
        """Set the initial owners of this dwelling place."""
        # I'm doing this klugey thing for now because of circular-dependency issue
        list(initial_owners)[0].purchase_home(purchasers=initial_owners, home=self)
        # HomePurchase(subjects=initial_owners, home=self, realtor=None)

    def get_feature(self, feature_type):
        """Return this person's feature of the given type."""
        if feature_type == "home is apartment":
            return "yes" if self.apartment else "no"
        elif feature_type == "home block":
            return self.block
        elif feature_type == "home address":
            return self.address


class Apartment(DwellingPlace):
    """An individual apartment unit in an apartment building in a town."""

    def __init__(self, apartment_complex, lot, unit_number):
        self.complex = apartment_complex
        self.unit_number = unit_number
        super(Apartment, self).__init__(lot, owners=(apartment_complex.owner.person,))
        self.address = self._init_generate_address()

    def _init_generate_address(self):
        """Generate an address, given the lot building is on."""
        return "{0} (Unit #{1})".format(self.lot.address, self.unit_number)


class House(DwellingPlace):
    """A house in a town.

    @param lot: A Lot object representing the lot this building is on.
    @param construction: A BusinessConstruction object holding data about
                         the construction of this building.
    """

    def __init__(self, lot, construction):
        super(House, self).__init__(lot, owners=construction.subjects)
        self.construction = construction
        self.lot.building = self