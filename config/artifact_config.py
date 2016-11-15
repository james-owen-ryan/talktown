class ArtifactConfig(object):
    """Configuration parameters related to artifacts."""
    # Artifacts represent a system that I've been wanting to develop but haven't had a chance
    # to; currently, the only real example of this is character gravestones, which are
    # procedurally generated to reflect some aspects of their life in the simulation
    occupations_that_may_appear_on_gravestones = [
        'Groundskeeper', 'Nurse', 'Architect', 'Doctor', 'FireChief', 'Firefighter',
        'Barber', 'Lawyer', 'Mortician', 'Optometrist', 'PoliceChief', 'PoliceOfficer',
        'Principal', 'Professor', 'Teacher', 'Baker', 'Barkeeper', 'Blacksmith', 'Brewer',
        'Bricklayer', 'Butcher', 'Carpenter', 'Clothier', 'Cooper', 'Dentist', 'Distiller',
        'Dressmaker', 'Druggist', 'Engineer', 'Farmer', 'Grocer', 'Innkeeper', 'Jeweler',
        'Joiner', 'Milkman', 'Miner', 'Painter', 'Plumber', 'Puddler', 'Quarryman', 'Seamstress',
        'Shoemaker', 'Stonecutter', 'Tailor', 'Turner', 'Woodworker'
    ]
