import json
import time
from simulation import Simulation


# Generate a town!
sim = Simulation()  # Objects of the class Simulation are Talk of the Town simulations
# Simulate from the date specified as the start of town generation to the date specified
# as its terminus; both of these dates can be set in config/basic_config.py
try:
    sim.establish_setting()  # This is the worldgen procedure
    town = sim.town
except KeyboardInterrupt:  # Enter "ctrl+C" (a keyboard interrupt) to end worldgen early
    # In the case of keyboard interrupt, we need to tie up a few loose ends
    sim.advance_time()
    for person in list(sim.town.residents):
        person.routine.enact()
# Export JSON data
filename = "town-{time}.json".format(time=int(time.time()))
with open(filename, 'w') as outfile:
    # Missing: whereabouts, life events (maybe add event with id?), full data about past occupations,
    # story sifting nuggets
    data = {
        "characters": [],
        "places": [],
        "lots": [],
    }
    for character in sorted(sim.town.all_time_residents, key=lambda c: c.id):
        character_data = {
            "id": character.id,
            "firstName": character.first_name,
            "middleName": character.middle_name,
            "lastName": character.last_name,
            "maidenName": character.maiden_name,
            "suffix": character.suffix,
            "fullName": character.full_name,
            "firstNameNamesake": (
                character.named_for[0].id if character.named_for and character.named_for[0] else None
            ),
            "middleNameNamesake": (
                character.named_for[1].id if character.named_for and character.named_for[1] else None
            ),
            "openness": character.personality.openness_to_experience,
            "conscientiousness": character.personality.conscientiousness,
            "extroversion": character.personality.extroversion,
            "agreeableness": character.personality.agreeableness,
            "neuroticism": character.personality.neuroticism,
            "bornHere": bool(character.birth),
            "birthYear": character.birth_year,
            "birthdate": character.birth.date if character.birth else None,
            "birthDoctor": (
                character.birth.doctor.person.id if character.birth and character.birth.doctor else None
            ),
            "birthNurses": [nurse.person.id for nurse in character.birth.nurses] if character.birth else [],
            "birthHospital": character.birth.hospital.id if character.birth and character.birth.hospital else None,
            "age": character.age,
            "alive": character.alive,
            "deathYear": character.death_year,
            "deathDate": character.death.date if character.death else None,
            "causeOfDeath": character.death.cause if character.death else None,
            "nextOfKin": character.death.next_of_kin.id if character.death else None,
            "deathMortician": (
                character.death.mortician.person.id if character.death and character.death.mortician else None
            ),
            "burialPlace": character.death.cemetery.id if character.death and character.death.cemetery else None,
            "gender": "male" if character.male else "female",
            "infertile": character.infertile,
            "attracted_to_men": character.attracted_to_men,
            "attracted_to_women": character.attracted_to_women,
            "eyeVerticalSettedness": character.face.eyes.vertical_settedness,
            "eyeHorizontalSettedness": character.face.eyes.horizontal_settedness,
            "eyeColor": character.face.eyes.color,
            "eyeShape": character.face.eyes.shape,
            "eyeSize": character.face.eyes.size,
            "skinColor": character.face.skin.color,
            "earAngle": character.face.ears.angle,
            "earSize": character.face.ears.size,
            "mouthSize": character.face.mouth.size,
            "headSize": character.face.head.size,
            "headShape": character.face.head.shape,
            "eyebrowColor": character.face.eyebrows.color,
            "eyebrowSize": character.face.eyebrows.size,
            "facialHairStyle": character.face.facial_hair.style,
            "hairColor": character.face.hair.color,
            "hairLength": character.face.hair.length,
            "noseSize": character.face.nose.size,
            "noseShape": character.face.nose.shape,
            "tattoo": character.face.distinctive_features.tattoo,
            "sunglasses": character.face.distinctive_features.sunglasses,
            "freckles": character.face.distinctive_features.freckles,
            "birthmark": character.face.distinctive_features.birthmark,
            "scar": character.face.distinctive_features.scar,
            "glasses": character.face.distinctive_features.glasses,
            "mother": character.mother.id if character.mother else None,
            "father": character.father.id if character.father else None,
            "ancestors": [ancestor.id for ancestor in character.ancestors],
            "descendants": [descendant.id for descendant in character.descendants],
            "immediate_family": [family_member.id for family_member in character.immediate_family],
            "extended_family": [family_member.id for family_member in character.extended_family],
            "grandparents": [grandparent.id for grandparent in character.grandparents],
            "greatgrandparents": [greatgrandparent.id for greatgrandparent in character.greatgrandparents],
            "aunts": [aunt.id for aunt in character.aunts],
            "uncles": [uncle.id for uncle in character.uncles],
            "siblings": [sibling.id for sibling in character.siblings],
            "full_siblings": [full_sibling.id for full_sibling in character.full_siblings],
            "half_siblings": [half_sibling.id for half_sibling in character.half_siblings],
            "brothers": [brother.id for brother in character.brothers],
            "full_brothers": [full_brother.id for full_brother in character.full_brothers],
            "half_brothers": [half_brother.id for half_brother in character.half_brothers],
            "sisters": [sister.id for sister in character.sisters],
            "full_sisters": [full_sister.id for full_sister in character.full_sisters],
            "half_sisters": [half_sister.id for half_sister in character.half_sisters],
            "cousins": [cousin.id for cousin in character.cousins],
            "kids": [kid.id for kid in character.kids],
            "sons": [son.id for son in character.sons],
            "daughters": [daughter.id for daughter in character.daughters],
            "nephews": [nephew.id for nephew in character.nephews],
            "nieces": [niece.id for niece in character.nieces],
            "grandchildren": [grandchild.id for grandchild in character.grandchildren],
            "grandsons": [grandson.id for grandson in character.grandsons],
            "granddaughters": [granddaughter.id for granddaughter in character.granddaughters],
            "greatgrandchildren": [greatgrandchild.id for greatgrandchild in character.greatgrandchildren],
            "greatgrandsons": [greatgrandson.id for greatgrandson in character.greatgrandsons],
            "greatgranddaughters": [greatgranddaughter.id for greatgranddaughter in character.greatgranddaughters],
            "spouse": character.spouse.id if character.spouse else None,
            "widowed": character.widowed,
            "chargeValues": (
                {subject.id: character.relationships[subject].charge for subject in character.relationships}
            ),
            "sparkValues": {subject.id: character.relationships[subject].spark for subject in character.relationships},
            "compatibilities": (
                {
                    subject.id: int(round(character.relationships[subject].compatibility * 100))
                    for subject in character.relationships
                }
            ),
            "saliences": {
                subject.id: int(round(character.salience_of_other_people[subject] if subject is not character else 999))
                for subject in character.salience_of_other_people
            },
            "whereTheyMet": (
                {subject.id: character.relationships[subject].where_they_met.id for subject in character.relationships}
            ),
            "whenTheyMet": (
                {subject.id: character.relationships[subject].when_they_met for subject in character.relationships}
            ),
            "whereTheyLastMet": {
                subject.id: character.relationships[subject].where_they_last_met.id for subject in character.relationships
            },
            "whenTheyLastMet": {
                subject.id: character.relationships[subject].when_they_last_met for subject in character.relationships
            },
            "totalInteractions": {
                subject.id: character.relationships[subject].total_interactions for subject in character.relationships
            },
            "mostSalientRelationship": {
                subject.id: character.relation_to_me(person=subject) for subject in character.town.all_time_residents
            },
            "friends": [friend.id for friend in character.friends],
            "enemies": [enemy.id for enemy in character.enemies],
            "acquaintances": [acquaintance.id for acquaintance in character.acquaintances],
            "neighbors": [neighbor.id for neighbor in character.neighbors],
            "formerNeighbors": [former_neighbor.id for former_neighbor in character.former_neighbors],
            "coworkers": [coworker.id for coworker in character.coworkers],
            "formerCoworkers": [former_coworkers.id for former_coworkers in character.former_coworkers],
            "bestFriend": character.best_friend.id if character.best_friend else None,
            "worstEnemy": character.worst_enemy.id if character.worst_enemy else None,
            "strongestLoveInterest": character.love_interest.id if character.love_interest else None,
            "significantOther": character.significant_other.id if character.significant_other else None,
            "sexualPartners": [partner.id for partner in character.sexual_partners],
            "pregnant": character.pregnant,
            "impregnated_by": character.impregnated_by.id if character.impregnated_by else None,
            "occupationVocation": character.occupation.vocation if character.occupation else None,
            "occupationStartDate": character.occupation.start_date if character.occupation else None,
            "occupationEndDate": character.occupation.end_date if character.occupation else None,
            "occupationShift": character.occupation.shift if character.occupation else None,
            "occupationCompany": character.occupation.company.id if character.occupation else None,
            "occupationJobLevel": character.occupation.level if character.occupation else None,
            "occupationHiredAsFavor": character.occupation.hired_as_favor if character.occupation else None,
            "occupationPositionPrecededBy": (
                character.occupation.preceded_by.person.id
                if character.occupation and character.occupation.preceded_by
                else None
            ),
            "occupationPositionSucceededBy": (
                character.occupation.succeeded_by.person.id
                if character.occupation and character.occupation.succeeded_by
                else None
            ),
            "allOccupations": [(job.vocation, job.company.id) for job in character.occupations],
            "retired": character.retired,
            "collegeGraduate": character.college_graduate,
            "grieving": character.grieving,  # After spouse dies
            "currentLocation": character.location.id if character.location else None,
            "currentlyWorking": character.routine.working,
            "currentLocationOccasion": character.routine.occasion,
            "lifeEvents": [str(life_event) for life_event in character.life_events],
        }
        data["characters"].append(character_data)  # Character with id i will be in data["characters"][i]
    all_places = (
        sim.town.companies | sim.town.former_companies | sim.town.dwelling_places | sim.town.former_dwelling_places
    )
    for place in sorted(all_places, key=lambda p: p.id):
        if place.type == "business":
            business = place
            business_data = {
                "id": business.id,
                "name": business.name,
                "business": True,
                "residence": False,
                "type": business.__class__.__name__,
                "founder": business.founder.person.id if business.founder else None,
                "founded": business.founded,
                "owner": business.owner.person.id if business.owner else None,
                "outOfBusiness": business.out_of_business,
                "demolished": bool(business.demolition),
                "demolishedYear": business.demolition.year if business.demolition else None,
                "demolitionCompany": (
                    business.demolition.demolition_company.id
                    if business.demolition and business.demolition.demolition_company
                    else None
                ),
                "houseNumber": business.house_number,
                "lot": business.lot.id,
                "former_owners": [former_owner.person.id for former_owner in business.former_owners],
                "closureYear": business.closure.year if business.closure else None,
                "peopleHereNow": [character.id for character in business.people_here_now],
                "constructionYear": business.construction.year if business.construction else None,
                "constructionFirm": (
                    business.construction.construction_firm.id
                    if business.construction and business.construction.construction_firm
                    else None
                ),
                "architect": (
                    business.construction.architect.person.id
                    if business.construction and business.construction.architect
                    else None
                ),
                "builders": [builder.id for builder in business.construction.builders] if business.construction else [],
                "buildingDemolishedToConstructThis": (
                    business.construction.demolition_that_preceded_this.building.id
                    if business.construction and business.construction.demolition_that_preceded_this
                    else None
                ),
                "address": business.address,
                "services": business.services,
                "street": business.street_address_is_on.name,
                "employees": [employee.person.id for employee in business.employees],
                "formerEmployees": [employee.person.id for employee in business.former_employees],
            }
            data["places"].append(business_data)
        else:
            residence = place
            residence_data = {
                "id": residence.id,
                "name": residence.name,
                "residence": True,
                "business": False,
                "isApartment": residence.apartment,
                "peopleHereNow": [character.id for character in residence.people_here_now],
                "formerResidents": [resident.id for resident in residence.former_residents],
                "demolished": bool(residence.demolition),
                "demolishedYear": residence.demolition.year if residence.demolition else None,
                "demolitionCompany": (
                    residence.demolition.demolition_company.id
                    if residence.demolition and residence.demolition.demolition_company
                    else None
                ),
                "houseNumber": residence.house_number,
                "owners": [owner.id for owner in residence.owners],
                "constructionYear": residence.construction.year if residence.construction else None,
                "constructionFirm": (
                    residence.construction.construction_firm.id
                    if residence.construction and residence.construction.construction_firm
                    else None
                ),
                "architect": (
                    residence.construction.architect.person.id
                    if residence.construction and residence.construction.architect
                    else None
                ),
                "builders": [builder.id for builder in residence.construction.builders] if residence.construction else [],
                "buildingDemolishedToConstructThis": (
                    business.construction.demolition_that_preceded_this.building.id
                    if business.construction and business.construction.demolition_that_preceded_this
                    else None
                ),
                "lot": residence.lot.id,
                "address": residence.address,
                "residents": [resident.id for resident in residence.residents],
                "formerOwners": [resident.id for resident in residence.former_owners],
                "unitNumber": residence.unit_number if residence.apartment else None,
                "apartmentComplex": residence.complex.id if residence.apartment else None,
            }
            data["places"].append(residence_data)
    for lot in sorted(sim.town.lots | sim.town.tracts, key=lambda l: l.id):
        lot_data = {
            "id": lot.id,
            "building": lot.building.id if lot.building else None,
            "formerBuildings": [building.id for building in lot.former_buildings],
            "streetAddressIsOn": lot.street_address_is_on.name,
            "houseNumber": lot.house_number,
            "neighboringLots": [neighboring_lot.id for neighboring_lot in lot.neighboring_lots],
            "adjoiningStreets": [street.name for street in lot.streets],
            "coordinates": lot.coordinates,
            "sidesOfStreet": lot.sides_of_street,
            "isTract": lot.tract,
            "address": lot.address,
        }
        data["lots"].append(lot_data)
    # Sort data
    data["places"].sort(key=lambda p: p["id"])
    data["lots"].sort(key=lambda l: l["id"])
    # Validate data
    for i, character_data in enumerate(data["characters"]):
        assert character_data["id"] == i, "Mismatched character ID and index: ID is {id} and index is {i}".format(
            id=character_data["id"],
            i=i
        )
    for i, place_data in enumerate(data["places"]):
        assert place_data["id"] == i, "Mismatched place ID and index: ID is {id} and index is {i}".format(
            id=place_data["id"],
            i=i
        )
    for i, lot_data in enumerate(data["lots"]):
        assert lot_data["id"] == i, "Mismatched lot ID and index: ID is {id} and index is {i}".format(
            id=residence_data["id"],
            i=i
        )
    # Write to file
    json_string = json.dumps(data)
    outfile.write(json_string)
