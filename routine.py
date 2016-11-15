import random


# TODO -- visiting methods don't take into account
# whether the person they will visit is even home;
# once we implement a telephone system, have them
# call first, or have people invite people over too;
# if someone does have someone over, whether they were
# invited or not, the occasion should actually be
# 'leisure', not 'home'


class Routine(object):
    """A person's daily routine."""

    def __init__(self, person):
        """Initialize a Routine object."""
        self.person = person
        self.working = False  # Whether or not the person is working on an exact timestep
        self.occasion = None  # A person's purpose for being where they are on a timestep

    def __str__(self):
        """Return string representation."""
        return "Daily routine of {}".format(self.person.name)

    def enact(self):
        """Enact this person's daily routine for a particular timestep."""
        new_location, occasion = self.decide_where_to_go()
        self.occasion = occasion
        self.working = True if occasion == 'work' else False
        self.person.go_to(destination=new_location, occasion=occasion)

    def decide_where_to_go(self):
        """Return the location at which this person will spend the next timestep, as well as the
        occasion for them doing so.
        """
        config = self.person.sim.config
        # If they're a kid, potentially send them to school or daycare -- TODO NO DAYCARE IF PARENT HOME
        if not self.person.adult:
            if self.person.sim.time_of_day == "day":
                location, occasion = self._go_to_school_or_daycare(), 'school'
                if location is self.person.home:  # They are very young child and living in a town/time without daycare
                    occasion = 'home'
            else:
                location, occasion = self.person.home, 'home'  # Kids stay home at night
        # If they have a job...
        elif self.person.occupation and self.person.occupation.shift == self.person.sim.time_of_day:
            if random.random() < config.chance_someone_doesnt_have_to_work_some_day:
                if random.random() < config.chance_someone_leaves_home_on_day_off[self.person.sim.time_of_day]:
                    location, occasion = self._go_in_public()
                else:
                    location, occasion = self.person.home, 'home'
            elif random.random() < config.chance_someone_calls_in_sick_to_work:
                if random.random() < config.chance_someone_leaves_home_on_sick_day:
                    location, occasion = self._go_in_public()
                else:
                    location, occasion = self.person.home, 'home'
            else:
                # We specifically note that they are working, because they could be going into
                # their place of work on an off-day (e.g., restaurant)
                location, occasion = self.person.occupation.company, 'work'
        # If they don't have a job...
        else:
            chance_of_leaving_home = (
                (self.person.personality.extroversion + self.person.personality.openness_to_experience) / 2.0
            )
            if self.person.kids_at_home:
                chance_of_leaving_home *= config.chance_someone_leaves_home_multiplier_due_to_kids
            floor = config.chance_someone_leaves_home_on_day_off_floor[self.person.sim.time_of_day]
            cap = config.chance_someone_leaves_home_on_day_off_cap[self.person.sim.time_of_day]
            if chance_of_leaving_home < floor:
                chance_of_leaving_home = floor
            elif chance_of_leaving_home > cap:
                chance_of_leaving_home = cap
            if random.random() < chance_of_leaving_home:
                location, occasion = self._go_in_public()
            else:
                location, occasion = self.person.home, 'home'
        return location, occasion

    def _go_to_school_or_daycare(self):
        """Return the school or day care that this child attends."""
        person_is_school_age = self.person.age > self.person.sim.config.age_children_start_going_to_school
        if person_is_school_age and self.person.town.school:
            school_or_day_care = self.person.town.school
        elif not person_is_school_age and self.person.town.businesses_of_type('DayCare'):
            school_or_day_care = self.person.town.businesses_of_type('DayCare')[0]
        else:
            school_or_day_care = self.person.home  # They stay home
        return school_or_day_care

    def _go_in_public(self):
        """Return the location in public that this person will go to."""
        config = self.person.sim.config
        if random.random() < config.chance_someone_goes_on_errand_vs_visits_someone:
            location, occasion = self._go_on_errand_or_out_for_leisure()
        else:
            person_they_will_visit = self._visit_someone()
            if person_they_will_visit:
                location, occasion = person_they_will_visit.home, 'leisure'
            else:
                location, occasion = self.person.home, 'home'
        # In case something went wrong, e.g., there's no business of a type
        # in this town currently, just have them stay at home
        if not location:
            location, occasion = self.person.home, 'home'
        return location, occasion

    def _go_on_errand_or_out_for_leisure(self):
        """Return the location associated with some errand this person will go on."""
        config = self.person.sim.config
        # TODO -- if someone goes on one of these errands, have them actually get
        # served by that business, e.g., have them actually get a haircut
        # TODO -- have people become loyal to certain businesses (or maybe not because such small town?)
        # Determine the type of service this errand will be for
        x = random.random()
        service_type_probs = config.probabilities_of_errand_for_service_type[self.person.sim.time_of_day]
        service_type_of_errand = next(
            # See config.py to understand what's going on here
            e for e in service_type_probs if service_type_probs[e][0] <= x <= service_type_probs[e][1]
        )
        businesses_in_town_providing_that_service = [
            b for b in self.person.town.companies if service_type_of_errand in b.services
        ]
        if businesses_in_town_providing_that_service:
            if random.random() < config.chance_someone_goes_to_closest_business_of_type:
                # Choose between the one closest to your house and the one closest to your work
                closest_to_home = min(
                    businesses_in_town_providing_that_service,
                    key=lambda business: self.person.town.distance_between(self.person.home.lot, business.lot)
                )
                if self.person.occupation:
                    closest_to_work = min(
                        businesses_in_town_providing_that_service,
                        key=lambda business: self.person.town.distance_between(
                            self.person.occupation.company.lot, business.lot
                        )
                    )
                    one_i_will_go_to = closest_to_home if random.random() < 0.5 else closest_to_work
                else:
                    one_i_will_go_to = closest_to_home
            else:
                one_i_will_go_to = random.choice(businesses_in_town_providing_that_service)
        else:
            one_i_will_go_to = None
        # Determine whether the occasion is an errand or just leisure -- in the case of location
        # being None, which happens if there is no business of that type in town currently,
        # simply set occasion to None, since _go_in_public() will end up having the
        # person staying home anyway (and will change occasion to 'home')
        if one_i_will_go_to:
            occasion = config.business_type_to_occasion_for_visit[one_i_will_go_to.__class__.__name__]
        else:
            occasion = None
        return one_i_will_go_to, occasion

    def _visit_someone(self):
        """Return the residence of the person who this person will go visit."""
        config = self.person.sim.config
        x = random.random()
        relationship_to_person_who_person_who_will_be_visited = next(
            r for r in config.who_someone_visiting_will_visit_probabilities if r[0][0] <= x <= r[0][1]
        )[1]
        if (relationship_to_person_who_person_who_will_be_visited == 'nb' and
                self.person.neighbors):
            person_they_will_visit = self._visit_a_neighbor()
        elif (relationship_to_person_who_person_who_will_be_visited == "fr" and
                any(f for f in self.person.friends if f.present and f.home is not self.person.home)):
            person_they_will_visit = self._visit_a_friend()
        elif (relationship_to_person_who_person_who_will_be_visited == "if" and
                any(f for f in self.person.immediate_family if f.present and f.home is not self.person.home)):
            person_they_will_visit = self._visit_an_immediate_family_member()
        elif (relationship_to_person_who_person_who_will_be_visited == "ef" and
                any(f for f in self.person.extended_family if f.present and f.home is not self.person.home)):
            person_they_will_visit = self._visit_an_extended_family_member()
        else:
            # Just stay home lol
            person_they_will_visit = None
        return person_they_will_visit

    def _visit_a_neighbor(self):
        """Return the neighbor that this person will visit.

        TODO: Flesh this out.
        """
        neighbor_they_will_visit = random.choice(list(self.person.neighbors))
        return neighbor_they_will_visit

    def _visit_a_friend(self):
        """Return the friend that this person will visit.

        TODO: Flesh this out.
        """
        friends_person_doesnt_live_with = [
            f for f in self.person.friends if f.present and f.home is not self.person.home
        ]
        if random.random() > 0.5:
            # Visit best friend (who doesn't live with them)
            friend_they_will_visit = max(
                friends_person_doesnt_live_with, key=lambda friend: self.person.relationships[friend].charge
            )
        else:
            friend_they_will_visit = random.choice(friends_person_doesnt_live_with)
        return friend_they_will_visit

    def _visit_an_immediate_family_member(self):
        """Return the immediate family member that this person will visit.

        TODO: Flesh this out.
        """
        immediate_family_person_doesnt_live_with = [
            f for f in self.person.immediate_family if f.present and f.home is not self.person.home
        ]
        immediate_family_they_will_visit = random.choice(immediate_family_person_doesnt_live_with)
        return immediate_family_they_will_visit

    def _visit_an_extended_family_member(self):
        """Return the extended family member that this person will visit.

        TODO: Flesh this out.
        """
        extended_family_person_doesnt_live_with = [
            f for f in self.person.extended_family if f.present and f.home is not self.person.home
        ]
        extended_family_they_will_visit = random.choice(extended_family_person_doesnt_live_with)
        return extended_family_they_will_visit