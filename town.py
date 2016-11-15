import random
from business import *
from residence import *
from occupation import *
import pyqtree
from random import gauss,randrange
from corpora import Names
from config import Config
import heapq


class Town(object):
    """A procedurally generated American small town on a 9x9 grid of city blocks.

    Most of the code for this class was written by Adam Summerville.
    """

    def __init__(self, sim):
        """Initialize a Town object."""
        self.sim = sim
        self.founded = sim.year
        self.settlers = set()  # Will get added to during Simulation.establish_setting()
        self.residents = set()
        self.departed = set()  # People who left the town (i.e., left the simulation)
        self.deceased = set()  # People who died in in the town
        self.companies = set()
        self.former_companies = set()
        self.lots = set()
        self.tracts = set()
        self.dwelling_places = set()  # Both houses and apartment units (not complexes)
        self.streets = set()
        self.parcels = set()
        self.blocks = set()
        self.generate_lots(sim.config)
        for lot in self.lots | self.tracts:
            lot.set_neighboring_lots_for_town_generation()
            lot.init_generate_address()
        # Survey all town lots to instantiate conventional city blocks
        for lot in self.lots | self.tracts:
            number, street = lot.parcel_address_is_on.number, lot.parcel_address_is_on.street
            try:
                city_block = next(b for b in self.blocks if b.number == number and b.street is street)
                city_block.lots.append(lot)
                lot.block = city_block
            except StopIteration:
                city_block = Block(number=number, street=street)
                self.blocks.add(city_block)
                city_block.lots.append(lot)
                lot.block = city_block
        for block in self.blocks:
            block.lots.sort(key=lambda lot: lot.house_number)
        # Fill in any missing blocks, which I think gets caused by tracts being so large
        # in some cases; these blocks will not have any lots on them, so they'll never
        # have buildings on them, but it makes town navigation more natural during simplay
        for street in self.streets:
            street.blocks.sort(key=lambda block: block.number)
            current_block_number = min(street.blocks, key=lambda block: block.number).number
            largest_block_number = max(street.blocks, key=lambda block: block.number).number
            while current_block_number != largest_block_number:
                current_block_number += 100
                if not any(b for b in street.blocks if b.number == current_block_number):
                    self.blocks.add(Block(number=current_block_number, street=street))
            # Sort one last time to facilitate easy navigation during simplay
            street.blocks.sort(key=lambda block: block.number)
        self.paths = {}
        self.generatePaths()
        # Determine coordinates for each lot in the town, which are critical for
        # graphically displaying the town
        self._determine_lot_coordinates()
        # Determine the lot central to the highest density of lots in the town and
        # make this lot downtown
        self.downtown = None
        highest_density = -1
        for lot in self.lots:
            density = self.tertiary_density(lot)
            if density > highest_density:
                highest_density = density
                self.downtown = lot
        self.name = None  # Gets set by Simulation.establish_setting() so that it may be named after an early settler
        # Finally, reset the neighboring lots to all lots to be the other
        # lots on the same city block
        for lot in self.lots:
            lot.init_set_neighbors_lots_as_other_lots_on_same_city_block()
        # These get set when these businesses get established (by their __init__() magic methods)
        self.cemetery = None
        self.city_hall = None
        self.fire_station = None
        self.hospital = None
        self.police_station = None
        self.school = None
        self.university = None

    def __str__(self):
        """Return the town's name and population."""
        return "{} (pop. {})".format(self.name, self.population)
        
    def get_parcels(self):
        output_parcels = {}
        for parcel in self.parcels:
            neighbors = []
            for neighbor in parcel.neighbors:
                neighbors.append(neighbor.id)
            lots = []
            for lot in parcel.lots:
                lots.append(lot.id)
            output_parcels[parcel.id] = {
                "street": parcel.street.id,
                "number": parcel.number,
                "coords": parcel.coords,
                "lots": lots,
                "neighbors": neighbors
            }
        return output_parcels
        
    def get_lots(self):
        output_lots = {}
        for lot in self.lots | self.tracts:
            building_id = -1
            if lot.building is not None:
                building_id = lot.building.id
            parcel_ids = []
            for parcel in lot.parcels:
                parcel_ids.append(parcel.id)
            output_lots[lot.id] = {
                "index_of_street_address_will_be_on": lot.index_of_street_address_will_be_on,
                "building": building_id,
                "blocks": parcel_ids,
                "house_numbers": lot.house_numbers,
                "positionsInBlock": lot.positions_in_city_blocks,
                "sidesOfStreet": lot.sides_of_street
            }
        return output_lots

    def getHouses(self):
        output = {}
        for house in self.houses:
            people_here_now = set([p.id for p in house.people_here_now])
            output[house.id] = {"address":house.address,"lot":house.lot.id, "people_here_now":people_here_now}
        return output

    def getApartments(self):
        output = {}
        for apartment in self.apartment_complexes:
            people_here_now = set([p.id for p in apartment.people_here_now])
            for unit in apartment.units:
                people_here_now |= set([q.id for q in unit.people_here_now])
            output[apartment.id] = {"address":apartment.name,"lot":apartment.lot.id, "people_here_now":people_here_now}
        return output

    def getBusinesses(self):
        output = {}
        for business in self.other_businesses:
            people_here_now = set([p.id for p in business.people_here_now])
            output[business.id] = {"address":business.name,"lot":business.lot.id, "people_here_now":people_here_now}
        return output

    def get_streets(self):
        output = {}
        for street in self.streets:
            output[street.id] = {
                "number": street.number,
                "name": street.name,
                "startingBlock": street.starting_parcel,
                "endingBlock": street.ending_parcel,
                "direction": street.direction
            }
        return output

    def dist_from_downtown(self,lot):
        
        return self.distance_between(lot,self.downtown)

    def generatePaths(self):
        for start in self.parcels:
            for goal in self.parcels:
                if (start == goal):
                     self.paths[(start,goal)] = 0
                else :
                    if ((start,goal) not in self.paths):
                        came_from, cost_so_far = Town.a_star_search(start, goal)
                        current  = goal
                        count = 0
                        while (current != start):
                            current = came_from[current]
                            count += 1
                        self.paths[(start,goal)] =count
                        self.paths[(goal,start)] =count
                        
    def distance_between(self, lot1, lot2):
        min_dist = float("inf")
        for parcel in lot1.parcels:
            for other_parcel in lot2.parcels:
                if self.paths[(parcel, other_parcel)] < min_dist:
                    min_dist = self.paths[(parcel, other_parcel)]
        return min_dist

    def nearest_business_of_type(self, lot, business_type):
        """Return the Manhattan distance between this lot and the nearest company of the given type.

        @param business_type: The Class representing the type of company in question.
        """
        businesses_of_this_type = self.businesses_of_type(business_type)
        if businesses_of_this_type:
            return min(businesses_of_this_type, key=lambda b: self.distance_between(lot, b.lot))
        else:
            return None
        
    def dist_to_nearest_business_of_type(self, lot, business_type, exclusion):
        """Return the Manhattan distance between this lot and the nearest company of the given type.

        @param business_type: The Class representing the type of company in question.
        @param exclusion: A company who is being excluded from this determination because they
                          are the ones making the call to this method, as they try to decide where
                          to put their lot.
        """
        distances = [
            self.distance_between(lot, company.lot) for company in self.companies if isinstance(company, business_type)
            and company is not exclusion
        ]
        if distances:
            return max(99, min(distances))  # Elsewhere, a max of 99 is relied on
        else:
            return None

    @staticmethod
    def secondary_population(lot):
        """Return the total population of this lot and its neighbors."""
        secondary_population = 0
        for neighbor in {lot} | lot.neighboring_lots:
            secondary_population += neighbor.population
        return secondary_population

    @staticmethod
    def tertiary_population(lot):
        lots_already_considered = set()
        tertiary_population = 0
        for neighbor in {lot} | lot.neighboring_lots:
            if neighbor not in lots_already_considered:
                lots_already_considered.add(neighbor)
                tertiary_population += neighbor.population
                for neighbor_to_that_lot in neighbor.neighboring_lots:
                    if neighbor_to_that_lot not in lots_already_considered:
                        lots_already_considered.add(neighbor_to_that_lot)
                        tertiary_population += neighbor.population
        return tertiary_population

    @staticmethod
    def tertiary_density(lot):
        lots_already_considered = set()
        tertiary_density = 0
        for neighbor in {lot} | lot.neighboring_lots:
            if neighbor not in lots_already_considered:
                lots_already_considered.add(neighbor)
                tertiary_density += 1
                for neighbor_to_that_lot in neighbor.neighboring_lots:
                    if neighbor_to_that_lot not in lots_already_considered:
                        lots_already_considered.add(neighbor_to_that_lot)
                        tertiary_density += 1
        return tertiary_density
        
    def generate_lots(self, config):
        loci = 3
        samples = 32
        size = 16
        lociLocations = []
        for ii in range(loci):
            lociLocations.append([gauss(size/2.0,size/6.0), gauss(size/2.0,size/6.0)])
        tree = pyqtree.Index(bbox=[0,0,size,size])
        for ii in range(samples):
            center = lociLocations[randrange(len(lociLocations))]
            point = [clamp(gauss(center[0],size/6.0),0,size-1),clamp(gauss(center[1],size/6.0),0,size-1)]
            point.append(point[0]+1)
            point.append(point[1]+1)
            tree.insert(point,point)
            
        nsstreets = {}
        ewstreets = {}
        parcels = []
        lots = []
        tracts =[]
            
        nsEnd = []
        ewEnd = []
        streets = []
        
        def traverseTree(node):
            if (len(node.children)==0 and node.width != 1):
                w =int( node.center[0]-node.width*0.5)
                e =int( node.center[0]+node.width*0.5)
                n =int( node.center[1]-node.width*0.5)
                s =int( node.center[1]+node.width*0.5)
                parcels.append((w,n,node.width))

                nsstreets[ (w,n)] = (w,s)
                nsstreets[ (e,n)] = (e,s)
                ewstreets[ (w,n)] = (e,n)
                ewstreets[ (w,s)] = (e,s)
                
            for child in node.children:
                traverseTree(child)
        traverseTree(tree)        
        
        for ii in range(0,size+2,2):
            for jj in range(0,size+2,2):
                street = (ii,jj)
                if street in nsstreets:
                    start = street
                    end = nsstreets[start]
                    while end in nsstreets:
                        end = nsstreets[end]
                    if (end not in nsEnd):
                        nsEnd.append(end)             
                        streets.append(['ns',start, end])
                if street in ewstreets:
                    start = street
                    end = ewstreets[start]
                    while end in ewstreets:
                        end = ewstreets[end]
                    if (end not in ewEnd):
                        ewEnd.append(end)             
                        streets.append(['ew',start, end])         
        
        nsStreets = {}
        ewStreets = {}
        connections = {}
        for street in streets:            
            number = int(street[1][0]/2 if street[0] == "ns" else street[1][1]/2)+1
            direction = ""
            starting_parcel = 0
            ending_parcel = 0
            if (street[0] == "ns"):
                direction = ("N" if number < size/4 else "S")
                starting_parcel =  street[1][1]
                ending_parcel =  street[2][1]

            if (street[0] == "ew"):
                direction =( "E" if number < size/4 else "W")
                starting_parcel =  street[1][0]
                ending_parcel =  street[2][0]
            
            starting_parcel = int(starting_parcel/2)+1
            ending_parcel = int(ending_parcel/2)+1
            reifiedStreet = (Street(self, number, direction, starting_parcel, ending_parcel))
            self.streets.add(reifiedStreet)
            for ii in range(starting_parcel, ending_parcel+1):
                if (street[0] == "ns"):
                    nsStreets[(number,ii)] = reifiedStreet
                else:
                    ewStreets[(ii,number)] = reifiedStreet
            for ii in range(starting_parcel,ending_parcel):
                coord = None
                next = None
                if (street[0] == "ns"):
                    coord = (number,ii)
                    next = (number,ii+1)
                else:
                    coord = (ii,number)
                    next = (ii+1,number)
                if (not coord in connections):
                    connections[coord] = set()
                connections[coord].add(next)
                if (not next in connections):
                    connections[next] = set()
                connections[next].add(coord)
                

        def insertInto(dict,key,value):
            if (not key in dict):
                dict[key] = []
            dict[key].append(value)
            
        def insertOnce(dict,key,value):
            if (not key in dict):
                dict[key] = value
                
        lots = {}
        Parcels = {}
        Numberings = {}
        n_buildings_per_parcel = 2

        corners = set()
        for parcel in parcels:
            ew = int(parcel[0]/2)+1
            ns = int(parcel[1]/2)+1
            size_of_parcel = int(parcel[2]/2)
            tract = None
            if (size_of_parcel > 1):
                tract = Tract(self, size=size_of_parcel)
                self.tracts.add(tract)
            for ii in range(0,size_of_parcel+1):
                
                insertOnce(Parcels,(ew,ns+ii,'NS'),Parcel( nsStreets[(ew,ns)], (ii+ns)*100,(ew,ns+ii)))
                insertOnce(Numberings,(ew,ns+ii,'E'),Parcel.determine_house_numbering( (ii+ns)*100,'E', config))
                insertOnce(Parcels,(ew+ii,ns,'EW'),Parcel( ewStreets[(ew,ns)], (ii+ew)*100,(ew+ii,ns)))
                insertOnce(Numberings,(ew+ii,ns,'N'),Parcel.determine_house_numbering( (ii+ew)*100,'N', config))
                insertOnce(Parcels,(ew+size_of_parcel,ns+ii,'NS'),Parcel( nsStreets[(ew+size_of_parcel,ns)], (ii+ns)*100,(ew+size_of_parcel,ns+ii)))
                insertOnce(Numberings,(ew+size_of_parcel,ns+ii,'W'),Parcel.determine_house_numbering( (ii+ns)*100,'W', config))
                insertOnce(Parcels,(ew+ii,ns+size_of_parcel,'EW'),Parcel( ewStreets[(ew,ns+size_of_parcel)], (ii+ew)*100,(ew+ii,ns+size_of_parcel)))
                insertOnce(Numberings,(ew+ii,ns+size_of_parcel,'S'),Parcel.determine_house_numbering( (ii+ew)*100,'S', config))
                if (tract != None):
                    tract.add_parcel(Parcels[(ew,ns+ii,'NS')],Numberings[(ew,ns+ii,'E')][n_buildings_per_parcel],'E',0)
                    tract.add_parcel( Parcels[(ew+ii,ns,'EW')],Numberings[(ew+ii,ns,'N')][n_buildings_per_parcel] ,'N',0)
                    if (ew+size_of_parcel <= size/2):
                        tract.add_parcel(Parcels[(ew+size_of_parcel,ns+ii,'NS')],Numberings[(ew+size_of_parcel,ns+ii,'W')][n_buildings_per_parcel],'W',0)
                    
                    if (ns+size_of_parcel <= size/2):
                        tract.add_parcel( Parcels[(ew+ii,ns+size_of_parcel,'EW')],Numberings[(ew+ii,ns+size_of_parcel,'S')][n_buildings_per_parcel],'S',0)
             
            neCorner = Lot(self)
            insertInto(lots,(ew,ns,'N'),(0,neCorner))
            insertInto(lots,(ew,ns,'E'),(0,neCorner))
            self.lots.add(neCorner)
            corners.add((ew,ns,'EW',ew,ns,'NS'))
            
            nwCorner = Lot(self)
            if (ew+size_of_parcel <= size/2):
                insertInto(lots,(ew+size_of_parcel-1,ns,'N'),(n_buildings_per_parcel-1,nwCorner))
            insertInto(lots,(ew+size_of_parcel,ns,'W'),(0,nwCorner))
            corners.add((ew+size_of_parcel-1,ns,'EW',ew+size_of_parcel,ns,'NS'))
            self.lots.add(nwCorner)
            
            seCorner = Lot(self)
            insertInto(lots,(ew,ns+size_of_parcel,'S'),(0,seCorner))
            if (ns+size_of_parcel <= size/2):
                insertInto(lots,(ew,ns+size_of_parcel-1,'E'),(n_buildings_per_parcel-1,seCorner))
            self.lots.add(seCorner)
            corners.add((ew,ns+size_of_parcel,'EW',ew,ns+size_of_parcel-1,'NS'))
            
            swCorner = Lot(self)
            insertInto(lots,(ew+size_of_parcel-1,ns+size_of_parcel,'S'),(n_buildings_per_parcel-1,swCorner))
            insertInto(lots,(ew+size_of_parcel,ns+size_of_parcel-1,'W'),(n_buildings_per_parcel-1,swCorner))
            corners.add((ew+size_of_parcel-1,ns+size_of_parcel,'EW',ew+size_of_parcel,ns+size_of_parcel-1,'NS'))
            self.lots.add(swCorner)
            
            for ii in range(1,size_of_parcel*n_buildings_per_parcel-1):
                parcel_n = int(ii/2)
                lot = Lot(self)
                self.lots.add(lot)      
                insertInto(lots,(ew,ns+parcel_n,'E'),(ii %n_buildings_per_parcel,lot))
                lot = Lot(self)
                self.lots.add(lot)      
                insertInto(lots,(ew+parcel_n,ns,'N'),(ii %n_buildings_per_parcel,lot))
                lot = Lot(self)
                self.lots.add(lot)      
                insertInto(lots,(ew+size_of_parcel,ns+parcel_n,'W'),(ii %n_buildings_per_parcel,lot))
                lot = Lot(self)
                self.lots.add(lot)      
                insertInto(lots,(ew+parcel_n,ns+size_of_parcel,'S'),(ii %n_buildings_per_parcel,lot))
        for parcel in lots:
            dir = 'NS' if parcel[2] == 'W' or parcel[2] == 'E' else 'EW'
            parcel_object = Parcels[(parcel[0],parcel[1],dir)]
            lotList = lots[parcel]
            
            for lot in lotList:
                lot[1].add_parcel(parcel_object,Numberings[parcel][lot[0]],parcel[2],lot[0])
                parcel_object.lots.append(lot[1])
                
        for conn in connections: 
            for neighbor in connections[conn]:
                dx = neighbor[0] - conn[0]
                dy = neighbor[1] - conn[1]
                if dx != 0:
                    if (conn[0],conn[1],'EW') in Parcels and (neighbor[0],neighbor[1],'EW') in Parcels:
                        Parcels[(conn[0],conn[1],'EW')].add_neighbor(Parcels[(neighbor[0],neighbor[1],'EW')])
                if dy != 0:
                    if (conn[0],conn[1],'NS') in Parcels and (neighbor[0],neighbor[1],'NS') in Parcels:
                        Parcels[(conn[0],conn[1],'NS')].add_neighbor(Parcels[(neighbor[0],neighbor[1],'NS')])
        for corner in corners:
            Parcels[(corner[0],corner[1],corner[2])].add_neighbor(Parcels[(corner[3],corner[4],corner[5])])
            Parcels[(corner[3],corner[4],corner[5])].add_neighbor(Parcels[(corner[0],corner[1],corner[2])])
            
        for parcel in Parcels:
            self.parcels.add(Parcels[parcel])
        # Currently being set to town founder by CityHall.__init__(); this is never updated or used
        # later on, though
        self.mayor = None

    def _determine_lot_coordinates(self):
        """Determine coordinates for each lot in this town.

        Coordinates are of the form (number_of_east_west_street, number_of_north_south_street),
        but with the coordinate corresponding to the street that the lot's address is *not* on
        being set to either that street's number plus 0.25 or plus 0.75, depending on the lot's
        position on the city block (which can be inferred from its address).
        """
        for lot in self.lots | self.tracts:
            # Determine base x- and y-coordinates, which can be inferred from the
            # number of the street that the lot's address is on and the lot's house
            # number itself
            if lot.street_address_is_on.direction in ('E', 'W'):
                x_coordinate = int(lot.house_number/100.0)
                y_coordinate = lot.street_address_is_on.number
            else:
                x_coordinate = lot.street_address_is_on.number
                y_coordinate = int(lot.house_number/100.0)
            # Figure out this lot's position in its city block
            index_of_street_lot_address_is_on = lot.streets.index(lot.street_address_is_on)
            position_in_city_block = lot.positions_in_city_blocks[index_of_street_lot_address_is_on]
            # Convert this to an increase (on the axis matching the direction of the street
            # that this lot's address is on) of either 0.25 or 0.75; we do this so that lots
            # are spaced evenly
            if lot.street_address_is_on.direction in ('E', 'W'):
                x_coordinate = int(x_coordinate)+0.25 if position_in_city_block == 0 else int(x_coordinate)+0.75
            elif lot.street_address_is_on.direction in ('N', 'S'):
                y_coordinate = int(y_coordinate)+0.25 if position_in_city_block == 0 else int(y_coordinate)+0.75
            # Figure out what side of the street this lot is on
            index_of_street_lot_address_is_on = lot.streets.index(lot.street_address_is_on)
            lot_side_of_street_on_the_street_its_address_is_on = lot.sides_of_street[index_of_street_lot_address_is_on]
            # Update coordinates accordingly
            if lot_side_of_street_on_the_street_its_address_is_on == 'N':
                y_coordinate += 0.25
            elif lot_side_of_street_on_the_street_its_address_is_on == 'S':
                y_coordinate -= 0.25
            elif lot_side_of_street_on_the_street_its_address_is_on == 'E':
                x_coordinate += 0.25
            elif lot_side_of_street_on_the_street_its_address_is_on == 'W':
                x_coordinate -= 0.25
            # Attribute these coordinates to the lot
            lot.coordinates = (x_coordinate, y_coordinate)

    @property
    def pop(self):
        """Return the number of residents living in the town."""
        return len(self.residents)

    @property
    def population(self):
        """Return the number of residents living in the town."""
        return len(self.residents)

    @property
    def buildings(self):
        """Return all businesses and houses (not apartment units) in this town."""
        houses = {d for d in self.dwelling_places if d.__class__ is House}
        return houses | self.companies

    @property
    def vacant_lots(self):
        """Return all vacant lots in the town."""
        vacant_lots = [lot for lot in self.lots if not lot.building]
        return vacant_lots

    @property
    def vacant_tracts(self):
        """Return all vacant tracts in the town."""
        vacant_tracts = [tract for tract in self.tracts if not tract.building]
        return vacant_tracts

    @property
    def vacant_homes(self):
        """Return all vacant homes in the town."""
        vacant_homes = [home for home in self.dwelling_places if not home.residents]
        return vacant_homes

    @property
    def all_time_residents(self):
        """Return everyone who has at one time lived in the town."""
        return self.residents | self.deceased | self.departed

    @property
    def unemployed(self):
        """Return unemployed (mostly young) people, excluding retirees."""
        unemployed_people = set()
        for resident in self.residents:
            if not resident.occupation and not resident.retired:
                if resident.in_the_workforce:
                    unemployed_people.add(resident)
        return unemployed_people

    def workers_of_trade(self, occupation):
        """Return all population in the town who practice to given occupation.

        @param occupation: The class pertaining to the occupation in question.
        """
        return [resident for resident in self.residents if isinstance(resident.occupation, occupation)]

    def businesses_of_type(self, business_type):
        """Return all business in this town of the given type.

        @param business_type: A string of the Class name representing the type of business in question.
        """
        businesses_of_this_type = [
            company for company in self.companies if company.__class__.__name__ == business_type
        ]
        return businesses_of_this_type

    @staticmethod
    def heuristic(a, b):
        (x1, y1) = a.coords
        (x2, y2) = b.coords
        return abs(x1 - x2) + abs(y1 - y2)

    @staticmethod
    def a_star_search(start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        
        while not frontier.empty():
            current = frontier.get()
            
            if current == goal:
                break
            
            for next in current.neighbors:
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + Town.heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current
        
        return came_from, cost_so_far


class Street(object):
    """A street in a town."""

    counter = 0

    def __init__(self, town, number, direction, starting_parcel, ending_parcel):
        """Initialize a Street object."""
        self.id = Street.counter
        Street.counter += 1
        self.town = town
        self.number = number
        self.direction = direction  # Direction relative to the center of the town
        self.name = self.generate_name(number, direction)
        self.starting_parcel = starting_parcel
        self.ending_parcel = ending_parcel
        self.blocks = []  # Gets appended to by Block.__init__()

    def generate_name(self, number, direction):
        """Generate a street name."""
        config = self.town.sim.config
        number_to_ordinal = {
            1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th',
            6: '6th', 7: '7th', 8: '8th', 9: '9th'
        }
        if direction == 'E' or direction == 'W':
            street_type = 'Street'
            if random.random() < config.chance_street_gets_numbered_name:
                name = number_to_ordinal[number]
            else:
                if random.random() < 0.5:
                    name = Names.any_surname()
                else:
                    name = Names.a_place_name()
        else:
            street_type = 'Avenue'
            if random.random() < config.chance_avenue_gets_numbered_name:
                name = number_to_ordinal[number]
            else:
                if random.random() < 0.5:
                    name = Names.any_surname()
                else:
                    name = Names.a_place_name()
        # name = "{0} {1} {2}".format(name, street_type, direction)
        name = "{0} {1}".format(name, street_type)
        return name

    def __str__(self):
        """Return string representation."""
        return self.name


class Parcel(object):
    """A collection of between zero and four contiguous lots in a town."""

    counter = 0

    def __init__(self, street, number, coords):
        """Initialize a Parcel object."""
        self.id = Parcel.counter
        Parcel.counter += 1
        self.street = street
        self.number = number
        self.lots = []
        self.neighbors = []
        self.coords = coords

    @staticmethod
    def determine_house_numbering(block_number, side_of_street, config):
        """Devise an appropriate house numbering scheme given the number of buildings on the block."""
        n_buildings = 3
        house_numbers = []
        house_number_increment = int(100.0 / n_buildings)
        even_or_odd = 0 if side_of_street == "E" or side_of_street == "N" else 1
        for i in xrange(n_buildings):
            base_house_number = (i * house_number_increment) - 1
            house_number = base_house_number + int(random.random() * house_number_increment)
            if house_number % 2 == (1-even_or_odd):
                house_number += 1
            if house_number < 1+even_or_odd:
                house_number = 1+even_or_odd
            elif house_number > 98+even_or_odd:
                house_number = 98+even_or_odd
            house_number += block_number
            house_numbers.append(house_number)
        return house_numbers

    def add_neighbor(self, other):
        self.neighbors.append(other)


class Block(object):
    """A city block in the conventional sense, e.g., the 400 block of Hennepin Ave."""

    def __init__(self, number, street):
        """Initialize a block object."""
        self.number = number
        self.street = street
        self.street.blocks.append(self)
        self.lots = []
        self.type = 'block'
        # Helper attributes for rendering a town
        if self.street.direction in ('N', 'S'):
            self.starting_coordinates = (self.street.number, self.number/100)
            self.ending_coordinates = (self.starting_coordinates[0], self.starting_coordinates[1]+1)
        else:
            self.starting_coordinates = (self.number/100, self.street.number)
            self.ending_coordinates = (self.starting_coordinates[0]+1, self.starting_coordinates[1])

    def __str__(self):
        """Return string representation."""
        return "{} block of {}".format(self.number, str(self.street))

    @property
    def direction(self):
        return 'n-s' if self.street.direction.lower() in ('n', 's') else 'e-w'

    @property
    def buildings(self):
        """Return all the buildings on this block."""
        return [lot.building for lot in self.lots if lot.building]


class Lot(object):
    """A lot on a city block (and multiple parcels) in a town, upon which buildings and houses get erected."""

    counter = 0

    def __init__(self, town):
        """Initialize a Lot object."""
        self.id = Lot.counter
        Lot.counter += 1
        self.lot = True if self.__class__ is Lot else False
        self.tract = True if self.__class__ is Tract else False
        self.town = town
        self.streets = []
        self.parcels = []
        self.block = None
        self.sides_of_street = []
        self.house_numbers = []  # In the event a business is erected here, it inherits this
        self.building = None
        # Positions in city blocks correspond to streets this lot is on and elements of this list
        # will be either 0 or 1, indicating whether this is the leftmost/topmost lot on its side
        # of the street of its city block or else rightmost/bottommost
        self.positions_in_city_blocks = []
        # This one gets set by Town.set_neighboring_lots_for_town_generation() after all lots have
        # been generated
        self.neighboring_lots = set()
        # This gets set by Town._determine_lot_coordinates()
        self.coordinates = None
        # These get set by init_generate_address(), which gets called by Town
        self.house_number = None
        self.address = None
        self.street_address_is_on = None
        self.parcel_address_is_on = None
        self.index_of_street_address_will_be_on = None
        self.former_buildings = []

    def __str__(self):
        """Return string representation."""
        if self.__class__ is Lot:
            if self.building:
                return 'A lot at {} on which {} has been erected'.format(
                    self.address, self.building.name
                )
            else:
                return 'A vacant lot at {}'.format(self.address)
        else:  # Tract
            if self.building:
                return 'A tract of land at {} that is the site of {}'.format(
                    self.address, self.building.name
                )
            else:
                return 'A vacant tract of land at {}'.format(self.address)

    @property
    def population(self):
        """Return the number of people living/working on the lot."""
        if self.building:
            population = len(self.building.residents)
        else:
            population = 0
        return population

    def add_parcel(self, parcel, number, side_of_street, position_in_parcel):
        self.streets.append(parcel.street)
        self.parcels.append(parcel)
        self.sides_of_street.append(side_of_street)
        self.house_numbers.append(number)
        self.positions_in_city_blocks.append(position_in_parcel)

    def set_neighboring_lots_for_town_generation(self):
        neighboring_lots = set()
        for parcel in self.parcels:
            for lot in parcel.lots:
                if lot is not self:
                    neighboring_lots.add(lot)
        self.neighboring_lots = neighboring_lots

    def init_generate_address(self):
        """Generate an address, given the lot building is on."""
        self.index_of_street_address_will_be_on = random.randint(0, len(self.streets)-1)
        house_number = self.house_numbers[self.index_of_street_address_will_be_on]
        self.house_number = int(house_number)
        street = self.streets[self.index_of_street_address_will_be_on]
        self.address = "{} {}".format(house_number, street.name)
        self.street_address_is_on = street
        self.parcel_address_is_on = self.parcels[self.index_of_street_address_will_be_on]

    def init_set_neighbors_lots_as_other_lots_on_same_city_block(self):
        """Set the neighbors to this lot as all the other lots on the same city block.

        This makes for more intuitive simplay, since we're delimiting the player's
        simplay to city blocks, so it would seem right that people reason about
        other people in that same locality when asked about their neighbors.
        """
        self.neighboring_lots = set(self.block.lots)


class Tract(Lot):
    """A tract of land on multiple parcels in a town, upon which businesses requiring
    extensive land (e.g., parks and cemeteries) are established.
    """

    def __init__(self, town, size):
        """Initialize a Tract object."""
        self.size = size
        super(Tract, self).__init__(town)


class PriorityQueue:
    """A helper class used when generating a town layout."""

    def __init__(self):
        """Initialize a PriorityQueue object."""
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]


def clamp(val, minimum, maximum):
    return max(minimum, min(val, maximum))