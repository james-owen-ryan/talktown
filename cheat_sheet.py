# To simulate ahead in time, simply use the 'Simulation.simulate()' method, which 
# takes the number of timesteps as its argument. There's two timesteps for each 
# day, so Simulation.simulate(730) will simulate one year, and so forth.

# To retrieve a person (i.e., the Python object in memory that represents them) by
# their name, use the command Simulation.find_person(string_of_their_full_name), e.g.,
# Simulation.find('James Ryan').

# Besides that, here's some new functions that may be useful.


def list_attributes(entity):
	"""Print out a list of attributes that an entity has.

	This will specifically print out a list of attributes that the object passed for
	the 'entity' argument has. You can then see what values are held in these attributes by
	using simple dot-notation commands. For instance, if a person has the attribute 'neighbors',
	you can see what's held in that attribute by using a command like 'print entity.neighbors'.

	The listing of attributes won't give an exhuastive account of the kinds of data that are
	stored for most entities, since some attributes will hold objects that themselves have
	attributes. For example, 'person.face' will hold a Face object, which itself will have 
	attributes holding objects pertaining to components of the face. Generally, though, the 
	listing	produced by this function should give you a good idea of some of the kinds of data 
	that are stored (some of which may be narratively potent).

	Additionally, any attributes that are computed dynamically (by using Python @property
	decorators) won't show up. Here's a current list of those kinds of attributes for Person
	objects:
		age_and_gender_description
		basic_appearance_description
		boss
		dead
		description
		first_home
		full_name
		full_name_without_suffix
		honorific
		is_captivated_by
		kids_at_home
		life_events
		name
		nametag
		next_of_kin
		nuclear_family
		object_pronoun
		possessive_pronoun
		present
		queer
		reflexive_pronoun
		requited_love_interest
		subject_pronoun
		year_i_moved_here
		years_i_lived_here
	"""
	for attribute in sorted(vars(entity).keys()):  # Prints them out in alphabetical order
		print attribute


def outline_physical_description(person):
	"""Outline a person's physical description."""
	print person.description


def outline_personality(person):
	"""Outline a person's physical description."""
	str = "\nFive-factor personality model of {}:\n\n".format(person.name)
	str += "\tOpenness: {}{}\n".format(
		person.personality.component_str('o'),
		'' if not person.personality.o.inherited_from else 
		' (takes after {})'.format(person.personality.o.inherited_from.name)
	)
	str += "\tConscientiousness: {}{}\n".format(
		person.personality.component_str('c'),
		'' if not person.personality.c.inherited_from else 
		' (takes after {})'.format(person.personality.c.inherited_from.name)
	)
	str += "\tExtroversion: {}{}\n".format(
		person.personality.component_str('e'),
		'' if not person.personality.e.inherited_from else 
		' (takes after {})'.format(person.personality.e.inherited_from.name)
	)
	str += "\tAgreeableness: {}{}\n".format(
		person.personality.component_str('a'),
		'' if not person.personality.a.inherited_from else 
		' (takes after {})'.format(person.personality.a.inherited_from.name)
	)
	str += "\tNeuroticism: {}{}\n".format(
		person.personality.component_str('n'),
		'' if not person.personality.n.inherited_from else 
		' (takes after {})'.format(person.personality.n.inherited_from.name)
	)
	print str


def outline_love_life(person):
	"""Outline a person's love life, including their strongest love interest and anyone else they are
	very interested in romantically.
	"""
	spouse = person.spouse
	other_love_interests = sorted(person.is_captivated_by, key=lambda li: person.relationships[li].spark, reverse=True)
	if spouse in other_love_interests:
		other_love_interests.remove(spouse)
	str = "\nRomantic life of {}:\n\n".format(person.name)
	if person.spouse:
		str += "\tSpouse: {name} ({person_spark_for_them} {heart_emoji} {their_spark_for_person})\n".format(
			name=spouse.name,
			person_spark_for_them=person.relationships[person.spouse].spark,
			heart_emoji='\xe2\x9d\xa4',
			their_spark_for_person=person.spouse.relationships[person].spark
		)
	else:
		str += "\tSpouse: none\n"
	if other_love_interests:
		str += "\tOther love interests: {}\n".format(
			', '.join('{name} ({person_spark_for_them} {heart_emoji} {their_spark_for_person})'.format(
				name=other_love_interest.name,
				person_spark_for_them=person.relationships[other_love_interest].spark,
				heart_emoji='\xe2\x9d\xa4',
				their_spark_for_person=other_love_interest.relationships[person].spark
			) for other_love_interest in other_love_interests)
		)
	else:
		str += "\tOther love interests: none\n"
	print str


def outline_family(person):
	"""Outline a person's family members."""
	str = "\nFamily of {}:\n".format(person.name)
	str += "\tSpouse: {}\n".format(person.spouse.name if person.spouse else 'none')
	str += "\tChildren: {}\n".format(', '.join(x.name for x in person.kids) if person.kids else 'none')
	str += "\tGrandchildren: {}\n".format(', '.join(x.name for x in person.grandchildren) if person.grandchildren else 'none')
	str += "\tGrandchildren: {}\n".format(', '.join(x.name for x in person.greatgrandchildren) if person.greatgrandchildren else 'none')
	str += "\tParents: {}\n".format(', '.join(x.name for x in person.parents) if person.parents else 'none')
	str += "\tBrothers: {}\n".format(', '.join(x.name for x in person.brothers) if person.brothers else 'none')
	str += "\tSisters: {}\n".format(', '.join(x.name for x in person.sisters) if person.sisters else 'none')
	str += "\tGrandparents: {}\n".format(', '.join(x.name for x in person.grandparents) if person.grandparents else 'none')
	str += "\tGreatgrandparents: {}\n".format(', '.join(x.name for x in person.greatgrandparents) if person.greatgrandparents else 'none')
	str += "\tAunts: {}\n".format(', '.join(x.name for x in person.aunts) if person.aunts else 'none')
	str += "\tUncles: {}\n".format(', '.join(x.name for x in person.uncles) if person.uncles else 'none')
	str += "\tNieces: {}\n".format(', '.join(x.name for x in person.nieces) if person.nieces else 'none')
	str += "\tNephews: {}\n".format(', '.join(x.name for x in person.nephews) if person.nephews else 'none')
	str += "\tCousins: {}\n".format(', '.join(x.name for x in person.cousins) if person.cousins else 'none')
	print str


def list_ancestors(person):
	"""List all of a person's ancestors."""
	for ancestor in person.ancestors:
			print ancestor


def list_work_history(person):
	"""List out a person's occupational history."""
	for o in person.occupations:
			print o

