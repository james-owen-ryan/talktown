import random
from corpora import GravestoneDetails


class Artifact(object):
    """A base class that all artifact subclasses inherit from."""

    def __init__(self):
        """Initialize an Artifact object."""
        self.provenance = []
        self.origin = None
        self.destruction = None


class Gravestone(Artifact):
    """A gravestone for a deceased character."""

    def __init__(self, subject):
        """Initialize a Gravestone object."""
        super(Gravestone, self).__init__()
        self.subject = subject
        if self.subject.extended_family:
            self.header = GravestoneDetails.a_header() + '\n'
            self.family_inscription = self._generate_family_inscription()
            self.epitaph = GravestoneDetails.an_epitaph() + '\n'
        else:
            self.header = random.choice(['Here lies buried', 'Rest in peace']) + '\n'
            self.family_inscription = ''
            self.epitaph = ''
        if (self.subject.occupations and
                self.subject.occupations[-1].__class__.__name__ in
                self.subject.sim.config.occupations_that_may_appear_on_gravestones):
            self.occupation_inscription = '{vocation_str}\n'.format(
                vocation_str=self.subject.occupations[-1].vocation.title()
            )
        else:
            self.occupation_inscription = ''

    def _generate_family_inscription(self):
        """Generate a short inscription indicating this person's family roles, e.g., 'A loving husband'."""
        pertinent_relations = []
        if self.subject.spouse or self.subject.widowed:
            pertinent_relations.append('Husband' if self.subject.male else 'Wife')
        if self.subject.kids:
            pertinent_relations.append('Father' if self.subject.male else 'Mother')
        if self.subject.grandchildren:
            pertinent_relations.append('Grandfather' if self.subject.male else 'Grandmother')
        if not pertinent_relations:
            if self.subject.parents:
                pertinent_relations.append('Son' if self.subject.male else 'Daughter')
            if self.subject.siblings:
                pertinent_relations.append('Brother' if self.subject.male else 'Sister')
        if pertinent_relations:
            if len(pertinent_relations) == 2:
                return 'Loving {relations_str}\n'.format(
                    relations_str=' and '.join(pertinent_relations)
                )
            else:
                return 'Loving {relations_str}\n'.format(
                    relations_str=', '.join(pertinent_relations)
                )
        else:
            return None

    def _get_age_adjective(self):
        """Return an adjective indicating the age of this gravestone."""
        age_of_this_gravestone = self.subject.sim.year-self.subject.death_year
        if age_of_this_gravestone > 200:
            age_description = 'very weathered'
        elif age_of_this_gravestone > 100:
            age_description = 'weathered'
        elif age_of_this_gravestone > 50:
            age_description = 'worn'
        elif age_of_this_gravestone > 5:
            age_description = 'fairly new'
        else:
            age_description = 'pristine'
        return age_description

    def __str__(self):
        """Return a string representation."""
        return "Gravestone of {subject.name}".format(subject=self.subject)

    @property
    def description(self):
        """A description of this gravestone."""
        age_adj = self._get_age_adjective()
        description = (
            "\nA {age_adj} gravestone that reads:\n\n"
            "{self.header}"
            "\n{subject.full_name}\n"
            "{subject.birth_year}-{subject.death_year}\n\n"
            "{self.occupation_inscription}"
            "{self.family_inscription}"
            "{self.epitaph}\n"
        ).format(
            age_adj=age_adj,
            self=self,
            subject=self.subject
        )
        return description
