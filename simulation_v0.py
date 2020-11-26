class Station:
    import random

    def __init__(self, index, stationName, passengersPerMin, timeToNextStation, startingPassengerQueue=list()):
        self.index = index
        self.passengersPerMin = passengersPerMin
        self.stationName = stationName
        self.timeToNextStation = timeToNextStation
        self.passengerQueue = startingPassengerQueue

        self.MAX_STATION_INDEX = 23

    def __str__(self):
        return "Passengers/min: {} , Name: {}, mins to next station: {}".format(self.passengersPerMin,
                                                                                self.stationName,
                                                                                self.timeToNextStation)

    #Pop passengers waiting at station
    def LoadPassengers(self):
        passengers = self.passengerQueue.copy()
        self.passengerQueue.clear()
        return passengers

    #Add passengers to station
    def QueuePassengers(self, passengers):
        for p in passengers:
            self.passengerQueue.append(p)

    #returns passengersPerMin Passengers
    def GeneratePassengers(self, minIndex):
        self.random.seed(42)


        passIndex = minIndex
        passengers = list()
        for i in range(self.passengersPerMin):
            indexEntered = self.index
            indexToExit = self.random.randrange(indexEntered+1, self.MAX_STATION_INDEX + 1)
            stationsUntilExit = indexToExit - indexEntered

            #TODO: proper random function if passenger is infected
            isInfected = False
            rand = self.random.randrange(0,101)
            if rand <= 10:
                isInfected = True
            passengers.append(Passenger(passIndex, stationsUntilExit, isInfected))
            passIndex += 1

        self.QueuePassengers(passengers)
        return self.passengersPerMin

class Car:
    #defaults to 20 max capacity and 4 safe capacity for testing
    def __init__(self, startingStation : Station,  maximumCapacity=20, safeCapacity=4):
        self.maximumCapacity = maximumCapacity
        self.safeCapacity = safeCapacity
        self.spaces = [[None for i in range(int(maximumCapacity/safeCapacity))] for j in range(safeCapacity)]
        self.station = startingStation
        self.minsToNextStation = 0

    def __str__(self):
        output = ""
        for i in self.spaces:
            output += str(i) + '\n'
        return output

    #Add 1 passenger to a safe zone, returns false if train car is at max capacity
    def AddPassenger(self, passenger):
        bestSafeZone = self.__GetBestSafeZone()
        if bestSafeZone == -1:
            return False
        else:
            self.__AddPassengerToSafeZone(passenger, bestSafeZone)
            return True

    #Add passenger to safe zone at first available index
    def __AddPassengerToSafeZone(self, passenger, index):
        for i in range(0, len(self.spaces[index])):
            if self.spaces[index][i] is None:
                self.spaces[index][i] = passenger
                break

    #Determines safezone with least people
    def __GetBestSafeZone(self):
        bestIndex = -1
        for i in range(0, len(self.spaces)):
            space = self.spaces[i].count(None)
            if space > 0 and bestIndex == -1:
                bestIndex = i
            if space > self.spaces[bestIndex].count(None):
                bestIndex = i
        return bestIndex

    #returns # of empty spots in safe zone
    def __GetSpaceInSafeZone(self, arr):
        return arr.count(None)

    #return time to next station
    def GetMinsToNextStation(self):
        return self.minsToNextStation

    #Set station and update time to next station
    def SetStation(self, station):
        self.station = station
        self.minsToNextStation = station.timeToNextStation

    #tick mins
    def DecrementMinsToNextStation(self):
        self.minsToNextStation -= 1

    #get index of station
    def GetStationIndex(self):
        return self.station.index

    #make passengers depart if their stop counter is 0
    def ArriveAtStation(self):
        passengersDeparting : Passenger = list()
        for i in range(0,len(self.spaces)):
            for j in range(0, len(self.spaces[i])):
                if self.spaces[i][j] is not None:
                    self.spaces[i][j].DecrementStops()
                    if self.spaces[i][j].GetStopsUntilDisembark() == 0:
                        passengersDeparting.append(self.spaces[i][j])
                        self.spaces[i][j] = None
        return passengersDeparting

    #Do everything needed every minute
    #Incremenets passengers vars
    def Tick(self):
        for i in range(0, len(self.spaces)):
            numberInfected = 0
            for j in range(0, len(self.spaces[i])):
                if self.spaces[i][j] is not None:
                    if self.spaces[i][j].GetIsInfected():
                        numberInfected += 1
            for j in range(0, len(self.spaces[i])):
                if self.spaces[i][j] is not None:
                    self.spaces[i][j].AddExposureTime(numberInfected)
                    self.spaces[i][j].IncrementRideTime()

class Passenger():
    def __init__(self,index, stopsUntillDisembark, infected):
        self.stopsUntillDisembark = stopsUntillDisembark
        self.infected = infected
        self.rideTime = 0
        self.exposureTime = 0

        self.index = index

    def __str__(self):
        return "index: {}, stops to go: {}, Infected: {}, ride time: {}, exposure time: {}".format(self.index,
                                                                                        self.stopsUntillDisembark,
                                                                                        self.infected, self.rideTime,
                                                                                        self.exposureTime)

    def DecrementStops(self):
        self.stopsUntillDisembark -= 1

    def GetExposureTime(self):
        return self.exposureTime

    def GetIsInfected(self):
        return self.infected

    def GetStopsUntilDisembark(self):
        return self.stopsUntillDisembark

    def GetRideTime(self):
        return self.rideTime

    def AddExposureTime(self, num):
        self.exposureTime += num

    def IncrementRideTime(self):
        self.rideTime += 1


def Simulation():

    passengerIndex = 0
    departedPassengers = list()
    clock = 0
    subwayLine = GetSubwayLine()
    trainsEnroute = list()

    carMaxCapacity = 258
    carSafeCapacity = 20
    

    #how many minutes to run the simulation for
    while clock < 100:
        # Launch new train todo: change it so it doesnt happen every minute
        trainsEnroute.append(Car(subwayLine[0], carMaxCapacity, carSafeCapacity))

        #Generate new passengers at every station in line except for the final station
        for stationIndex in range(0, len(subwayLine)-1):
            passengerIndex += subwayLine[stationIndex].GeneratePassengers(passengerIndex)

        for train in trainsEnroute:

            # Tick trains (updates new values for passengers)
            train.Tick()

            #if train has arrived at next station
            if train.GetMinsToNextStation() == 0:
                train.station = subwayLine[train.GetStationIndex()]

                #Get passengers off trains who arrived at their stop, add to list for later
                departingPassengers = train.ArriveAtStation()
                for p in departingPassengers:
                    departedPassengers.append(p)

                #get passengers waiting to board train at station
                passengersToLoad = subwayLine[train.GetStationIndex()].LoadPassengers()
                for p in passengersToLoad:
                    if train.AddPassenger(p): #if passenger was succesfully added
                        passengersToLoad.remove(p)
                    else: #train is full, exit loop
                        break
                #if train filled before station emptied, add passengers back into station queue
                if len(passengersToLoad) > 0:
                    subwayLine[train.GetStationIndex()].QueuePassengers(passengersToLoad)

                #If we're at the final stop, remove the train
                if train.GetStationIndex() == len(subwayLine):
                    trainsEnroute.remove(train)
            #Train is in transit.
            else:
                train.DecrementMinsToNextStation()
        clock += 1

    #Main loop ended, show data gathered.
    for passenger in departedPassengers:
        infected = "not infected"
        if passenger.GetIsInfected():
            infected = "infected"
        print("Passenger {} rode for {} mins, was exposed for {} mins, started off {}".format(passenger.index,
                                                                                              passenger.GetRideTime(),
                                                                                              passenger.exposureTime,
                                                                                              infected))



def GetSubwayLine():
    data = [
            ["Canarsie - Rockaway Pkwy",3,4],
            ["E 105 St",2,5],
            ["New Lots Av",3,4],
            ["Livonia Av",1,3],
            ["Sutter Av",2,5],
            ["Atlantic Av",1,5],
            ["Broadway Jct",2,6],
            ["Bushwick Av - Aberdeen St",3,4],
            ["Wilson Av",3,1],
            ["Halsey St",2,3],
            ["Myrtle - Wyckoff Avs",3,2],
            ["Dekalb Av",1,3],
            ["Jefferson St",4,3],
            ["Morgan Av",3,4],
            ["Montrose Av",2,3],
            ["Grand St",1,3],
            ["Graham Av",3,1],
            ["Lorimer St",2,3],
            ["Bedford Av ",3,2],
            ["1 Av",1,4],
            ["3 Av",6,4],
            ["Union Sq - 14 St",2,1],
            ["14 St - 6 Avenue",1,2],
            ["14 St - 8 Avenue",0,0]
           ]
    stationList = list()
    index = 0
    for s in data:
        stationList.append(Station(index,s[0],s[1],s[2]))
        index += 1
    return stationList


Simulation()
