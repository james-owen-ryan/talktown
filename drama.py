class StoryRecognizer(object):
    """A module that excavates nuggets of dramatic intrigue from the raw emergent material of a simulation instance."""

    def __init__(self, simulation):
        """Initialize a StoryRecognizer object."""
        self.simulation = simulation
        self.unrequited_love_cases = []  # Gets set by self._excavate_unrequited_love_cases()
        self.love_triangles = []  # Gets set by self._excavate_love_triangles()
        self.extramarital_romantic_interests = []  # Gets set by self._excavate_extramarital_romantic_interests()
        self.asymmetric_friendships = []  # Gets set by self._excavate_asymmetric_friendships()
        self.misanthropes = []  # Gets set by self._excavate_misanthropes()
        self.rivalries = []  # Gets set by self._excavate_rivalries()
        self.sibling_rivalries = []  # Gets set by self._excavate_sibling_rivalries()
        self.business_owner_rivalries = []  # Gets set by self._excavate_business_owner_rivalries()
        self.settlers_living_descendants = []
        self.rags_to_riches = []

    def __str__(self):
        """Return string representation."""
        return "A story-recognition module for the town of {town_name}".format(town_name=self.simulation.town.name)

    def excavate(self):
        """Excavate and record nuggets of dramatic intrigue."""
        self.unrequited_love_cases = self._excavate_unrequited_love_cases()
        print "\tFound {n} cases of unrequited love".format(n=len(self.unrequited_love_cases))
        self.love_triangles = self._excavate_love_triangles()
        print "\tFound {n} love triangles".format(n=len(self.love_triangles))
        self.extramarital_romantic_interests = self._excavate_extramarital_romantic_interests()
        print "\tFound {n} cases of extramarital romantic interest".format(n=len(self.extramarital_romantic_interests))
        self.asymmetric_friendships = self._excavate_asymmetric_friendships()
        print "\tFound {n} asymmetric friendships".format(n=len(self.asymmetric_friendships))
        self.misanthropes = self._excavate_misanthropes()
        print "\tFound {n} misanthropes".format(n=len(self.misanthropes))
        self.rivalries = self._excavate_rivalries()
        print "\tFound {n} character rivalries".format(n=len(self.rivalries))
        self.sibling_rivalries = self._excavate_sibling_rivalries()
        print "\tFound {n} sibling rivalries".format(n=len(self.sibling_rivalries))
        self.business_owner_rivalries = self._excavate_business_owner_rivalries()
        print "\tFound {n} business-owner rivalries".format(n=len(self.business_owner_rivalries))
        self.settlers_living_descendants = self._excavate_living_descendants_of_settlers()
        print "\tFound {n} settlers with living descendants".format(n=len(self.settlers_living_descendants))
        self.rags_to_riches = self._excavate_rags_to_riches()
        print "\tFound {n} settlers who went from rags to riches".format(n=len(self.rags_to_riches))
        self.riches_to_rags = self._excavate_riches_to_rags()
        print "\tFound {n} settlers who went from riches to rags".format(n=len(self.riches_to_rags))
    def _excavate_unrequited_love_cases(self):
        """Recognize cases where one character's love for another is not reciprocated."""
        unrequited_love_cases = []
        for first_person in self.simulation.town.residents:
            first_person_love_interests = set(first_person.is_captivated_by)
            for second_person in first_person_love_interests:
                second_person_love_interests = set(second_person.is_captivated_by)
                if first_person not in second_person_love_interests:
                    unrequited_love_cases.append(UnrequitedLove(subjects=(first_person, second_person)))
        return unrequited_love_cases

    def _excavate_love_triangles(self):
        """Recognize character love triangles that have emerged in a simulation instance."""
        love_triangles = []
        for first_person in self.simulation.town.residents:
            first_person_love_interests = set(first_person.is_captivated_by)
            for second_person in first_person_love_interests:
                second_person_love_interests = set(second_person.is_captivated_by)
                if first_person not in second_person_love_interests:
                    for third_person in second_person_love_interests:
                        third_person_love_interests = set(third_person.is_captivated_by)
                        if second_person not in third_person_love_interests:
                            if first_person in third_person_love_interests:
                                subjects = (first_person, second_person, third_person)
                                if not any(lt for lt in love_triangles if set(lt.subjects) == set(subjects)):
                                    love_triangles.append(LoveTriangle(subjects=subjects))
        return love_triangles

    def _excavate_extramarital_romantic_interests(self):
        """Excavate cases where married characters are in love with people they are not married to."""
        extramarital_romantic_interests = []
        for person in self.simulation.town.residents:
            if person.spouse and person.love_interest is not person.spouse:
                subjects = (person, person.love_interest)
                extramarital_romantic_interests.append(ExtramaritalRomanticInterest(subjects=subjects))
        return extramarital_romantic_interests

    def _excavate_asymmetric_friendships(self):
        """Recognizes cases where a character A considers another, B, to be a friend,
        while B considers A to be an enemy.
        """
        asymmetric_friendships = []
        for person in self.simulation.town.residents:
            for friend in person.friends:
                if friend.dislikes(person):
                    asymmetric_friendships.append(AsymmetricFriendship(subjects=(person, friend)))
        return asymmetric_friendships

    def _excavate_misanthropes(self):
        """Recognizes cases of characters who dislike many other characters."""
        misanthropes = []
        threshold_for_misanthropy = self.simulation.config.minimum_number_of_disliked_people_to_be_misanthrope
        for person in self.simulation.town.residents:
            number_of_disliked_people = len([p for p in person.relationships if person.dislikes(p)])
            if number_of_disliked_people >= threshold_for_misanthropy:
                misanthropes.append(Misanthropy(subjects=(person,)))
        return misanthropes

    def _excavate_rivalries(self):
        """Recognize cases where mutual animosity exists between a pair of characters."""
        rivalries = []
        for person in self.simulation.town.residents:
            for other_person in person.relationships:
                if person.dislikes(other_person) and other_person.dislikes(person):
                    subjects = (person, other_person)
                    if not any(r for r in self.rivalries if set(r.subjects) == set(subjects)):
                        rivalries.append(Rivalry(subjects=subjects))
        return rivalries

    def _excavate_sibling_rivalries(self):
        """Recognize cases where mutual animosity exists between a pair of siblings."""
        sibling_rivalries = []
        for person in self.simulation.town.residents:
            for sibling in person.siblings:
                if person.dislikes(sibling) and sibling.dislikes(person):
                    subjects = (person, sibling)
                    if not any(sr for sr in self.sibling_rivalries if set(sr.subjects) == set(subjects)):
                        sibling_rivalries.append(SiblingRivalry(subjects=subjects))
        return sibling_rivalries

    def _excavate_business_owner_rivalries(self):
        """Recognize cases where mutual animosity exists between owners of rival businesses."""
        business_owner_rivalries = []
        for company in self.simulation.town.companies:
            for rival_company in self.simulation.town.businesses_of_type(business_type=company.__class__.__name__):
                if rival_company is not company and rival_company.owner and company.owner:
                    if not company.owner.person.likes(rival_company.owner.person):
                        if not rival_company.owner.person.likes(company.owner.person):
                            subjects = (company.owner.person, rival_company.owner.person)
                            if not any(br for br in self.business_owner_rivalries if set(br.subjects) == set(subjects)):
                                business_owner_rivalries.append(BusinessOwnerRivalry(subjects=subjects))
        return business_owner_rivalries

    def _excavate_living_descendants_of_settlers(self):
        """All living descendants of settlers"""
        all_living_descendants = []
        for settler in self.simulation.town.settlers:
            current_settler_descendants = []
            for descendant in settler.descendants:
                if descendant.alive == True:
                  current_settler_descendants.append(descendant) 
            if len(current_settler_descendants) != 0:
              subjects = (settler, current_settler_descendants)
              all_living_descendants.append(SettlerLivingDescendants(subjects=subjects))
        return all_living_descendants

    def _excavate_rags_to_riches(self):
        all_rags_to_riches = []
        for settler in self.simulation.town.settlers:
            current_settler_occupation_levels = []
            for occupation in settler.occupations:
              current_settler_occupation_levels.append(occupation.level)
            if len(current_settler_occupation_levels) > 1:
              first_job = current_settler_occupation_levels[0]
              last_job = current_settler_occupation_levels[-1]
              if first_job == 1 and last_job == 5:
                subjects = (settler, settler.occupations)
                all_rags_to_riches.append(RagsToRiches(subjects=subjects))
        return all_rags_to_riches

    def _excavate_riches_to_rags(self):
        all_riches_to_rags = []
        for settler in self.simulation.town.settlers:
            current_settler_occupation_levels = []
            for occupation in settler.occupations:
              current_settler_occupation_levels.append(occupation.level)
            if len(current_settler_occupation_levels) > 1:
              first_job = current_settler_occupation_levels[0]
              last_job = current_settler_occupation_levels[-1]
              if (first_job == 5 or first_job == 4) and (last_job == 1 or last_job == 2):
                subjects = (settler, settler.occupations)
                all_riches_to_rags.append(RichesToRags(subjects=subjects))
        return all_riches_to_rags

class UnrequitedLove(object):
    """A case of one character's love not being reciprocated by a second character."""

    def __init__(self, subjects):
        """Initialize a UnrequitedLove object.

        @param subjects: The characters involved in this situation, ordered such that
                         subjects[0]'s love for subject[1] is not being reciprocated.
        """
        self.subjects = subjects
        self.lover, self.nonreciprocator = subjects

    def __str__(self):
        """Return string representation."""
        return "A case of unrequited love: {lover}'s love for {nonreciprocator} is not reciprocated".format(
            lover=self.lover.name,
            nonreciprocator=self.nonreciprocator.name
        )


class ExtramaritalRomanticInterest(object):
    """A case where a married character is in love with someone else."""

    def __init__(self, subjects):
        """Initialize an ExtramaritalRomanticInterest object.

        @param subjects: A tuple comprising the married character who is in love with someone
                         else and that other character (in that order).
        """
        self.subjects = subjects
        self.married_person, self.love_interest = subjects

    def __str__(self):
        """Return string representation."""
        return (
            "A case of extramarital romantic interest: {married_person} is married to {spouse}, but {pron} "
            "is in love with {love_interest}".format(
                married_person=self.married_person.name,
                spouse=self.married_person.spouse.name,
                pron=self.married_person.subject_pronoun,
                love_interest=self.love_interest.name
            )
        )


class LoveTriangle(object):
    """A love triangle constituted across three characters."""

    def __init__(self, subjects):
        """Initialize a LoveTriangle object.

        @param subjects: The characters involved in this love triangle, ordered such
                         that subjects[0] is in love with subjects[1] who is in love
                         with subjects[2]; a tuple.
        """
        self.subjects = subjects
        self.first_person, self.second_person, self.third_person = subjects

    def __str__(self):
        """Return string representation."""
        s = (
            "A love triangle: {first_person} {heart_emoji} {second_person} {heart_emoji} "
            "{third_person} {heart_emoji} {first_person}".format(
                first_person=self.first_person.name,
                second_person=self.second_person.name,
                third_person=self.third_person.name,
                heart_emoji='\xf0\x9f\x92\x96 '
            )
        )
        return s


class AsymmetricFriendship(object):
    """A case of two characters, where A considers B to be a friend but B dislikes A."""

    def __init__(self, subjects):
        """Initialize an AsymmetricFriendship object.

        @param subjects: A tuple containing the two characters, where subjects[0] considers
                         subjects[1] to be a friend, and subjects[1] dislikes subjects[0].
        """
        self.subjects = subjects
        self.friend, self.enemy = subjects

    def __str__(self):
        """Return string representation."""
        return "An asymmetric friendship: {} considers {} a friend, but {} dislikes {}".format(
            self.subjects[0].name, self.subjects[1].name, self.subjects[1].name, self.subjects[0].name
        )


class Misanthropy(object):
    """A case of a character who dislikes many other characters."""

    def __init__(self, subjects):
        """Initialize a Misanthropy object.

        @param subjects: A tuple containing just the misanthrope.
        """
        self.subjects = subjects
        self.misanthrope = subjects[0]

    def __str__(self):
        """Return string representation."""
        return "A case of misanthropy: {misanthrope} dislikes {n} people in this town".format(
            misanthrope=self.subjects[0].name,
            n=len([p for p in self.subjects[0].relationships if self.subjects[0].dislikes(p)])
        )


class Rivalry(object):
    """A case of mutual animosity between characters."""

    def __init__(self, subjects):
        """Initialize a Rivalry object.

        @param subjects: A tuple containing the two siblings.
        """
        self.subjects = subjects

    def __str__(self):
        """Return string representation."""
        return (
            "A case of mutual animosity between characters: {first_sibling} and {second_sibling} do not like each other".format(
                first_sibling=self.subjects[0].name,
                second_sibling=self.subjects[1].name
            )
        )


class SiblingRivalry(object):
    """A case of mutual animosity between characters."""

    def __init__(self, subjects):
        """Initialize a SiblingRivalry object.

        @param subjects: A tuple containing the two siblings.
        """
        self.subjects = subjects

    def __str__(self):
        """Return string representation."""
        return (
            "A case of mutual animosity between siblings: {first_sibling} and {second_sibling} do not like each other".format(
                first_sibling=self.subjects[0].name,
                second_sibling=self.subjects[1].name
            )
        )


class BusinessOwnerRivalry(object):
    """A case of animosity between owners of rival companies."""

    def __init__(self, subjects):
        """Initialize a BusinessOwnerRivalry object.

        @param subjects: The owners of the respective businesses.
        """
        self.subjects = subjects
        self.companies = [subjects[0].occupation.company, subjects[1].occupation.company]
        self.industry = self.companies[0].__class__.__name__

    def __str__(self):
        """Return string representation."""
        return (
            "A case of animosity between business owners: {first_owner}, owner of {first_company}, "
            "is a heated rival of {second_owner}, owner of {second_company}".format(
                first_owner=self.subjects[0].name,
                first_company=self.subjects[0].occupation.company.name,
                second_owner=self.subjects[1].name,
                second_company=self.subjects[1].occupation.company.name
            )
        )

class SettlerLivingDescendants(object):
  """A case of a living descendant of the town's initial settlers"""
  def __init__(self, subjects):
    """Initialize a SettlerLivingDescendants object.
    
    @param subjects: The descendants of a settler and the settler themself
    """
    self.subjects = subjects
    self.settler = subjects[0]
    self.descendants = subjects[1:]
    
    def __str__(self):
      """Return string representation"""
      return (
        "The living descendants of the settler {settler}: "
	"{self.descendants}".format(
          settler = self.settler,
          descendants = self.descendants
        )
     )

class RagsToRiches(object):
  """A case of rags to riches, aka first job level 1, last job level 5"""
  def __init__(self, subjects):
    self.subjects = subjects
    self.settler = subjects[0]
    self.occupations = subjects[1]
  def __str__(self):
    """Return string representation"""
    return (
      "The occupations of the settler {settler}: "
      "{occupations}".format(
        settler = self.settler,
        occupations = self.occupations
      )
   )

class RichesToRags(object):
  """A case of riches to rags, aka first job level 5, last job level 1"""
  def __init__(self, subjects):
    self.subjects = subjects
    self.settler = subjects[0]
    self.occupations = subjects[1] 
  def __str__(self):
    """Return string representation"""
    return (
      "The occupations of the settler {settler}: "
      "{occupations}".format(
        settler = self.settler,
        occupations = self.occupations
      )
    )
