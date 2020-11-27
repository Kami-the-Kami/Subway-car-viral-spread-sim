import numpy    as np


class Station:
    import random

    def __init__(self, index, stationName, passengersPerMin, timeToNextStation, startingPassengerQueue=None):
        self.index = index
        self.passengersPerMin = passengersPerMin
        self.stationName = stationName
        self.timeToNextStation = timeToNextStation
        self.passengerQueue = startingPassengerQueue

        if startingPassengerQueue is None:
            self.passengerQueue = []
        else:
            self.passengerQueue = startingPassengerQueue

        self.MAX_STATION_INDEX = 23

    def __str__(self):
        return "Passengers/min: {} , Name: {}, mins to next station: {}".format(self.passengersPerMin,
                                                                                self.stationName,
                                                                                self.timeToNextStation)

    # Pop passengers waiting at station
    def LoadPassengers(self):
        passengers = self.passengerQueue.copy()
        self.passengerQueue.clear()
        return passengers

    # Add passengers to station
    def QueuePassengers(self, passengers):
        for p in passengers:
            self.passengerQueue.append(p)

    # returns passengersPerMin Passengers
    def GeneratePassengers(self, minIndex):
        self.random.seed(42)

        passIndex = minIndex
        passengers = list()
        numArrivals = np.random.poisson(self.passengersPerMin)
        for i in range(numArrivals):
            indexEntered = self.index
            indexToExit = self.random.randrange(indexEntered + 1, self.MAX_STATION_INDEX + 1)
            stationsUntilExit = indexToExit - indexEntered

            isInfected = False
            rand = self.random.randrange(0, 99)  # 1% infection rate
            if rand == 0:
                isInfected = True
                print("[INF]: ", self.stationName)
            passengers.append(Passenger(passIndex, stationsUntilExit, isInfected))
            passIndex += 1

        self.QueuePassengers(passengers)
        return self.passengersPerMin


class Train:

    def __init__(self, uniqueID, carCount, startingStation: Station, maximumCapacity=20, safeCapacity=4):
        self.identifier = uniqueID
        self.cars = [Car(maximumCapacity, safeCapacity) for i in range(carCount)]
        self.station = startingStation
        self.minsToNextStation = 0

    # Add 1 passenger to a safe zone, returns false if train car is at max capacity
    def AddPassenger(self, passenger):
        bestCar = self.cars[0]
        for car in self.cars:
            if car.occupancy < bestCar.occupancy:
                bestCar = car
        return bestCar.AddPassenger(passenger)

    # make passengers depart if their stop counter is 0
    def ArriveAtStation(self):
        passengersDeparting: Passenger = list()
        for car in self.cars:
            passengersDeparting += car.ArriveAtStation()
        return passengersDeparting

    # tick mins
    def DecrementMinsToNextStation(self):
        self.minsToNextStation -= 1

    # get index of station
    def GetStationIndex(self):
        return self.station.index

    # return time to next station
    def GetMinsToNextStation(self):
        return self.minsToNextStation

    # Set station and update time to next station
    def SetStation(self, station):
        self.minsToNextStation = self.station.timeToNextStation
        self.station = station

    # Update everything
    def Tick(self):
        for car in self.cars:
            car.Tick()


class Car:

    def __init__(self, maximumCapacity, safeCapacity):
        self.maximumCapacity = maximumCapacity
        self.safeCapacity = safeCapacity
        self.spaces = [[None for i in range(int(maximumCapacity / safeCapacity))] for j in range(safeCapacity)]
        self.occupancy = 0

    def __str__(self):
        output = ""
        for i in self.spaces:
            output += str(i) + '\n'
        return output

    # Add 1 passenger to a safe zone, returns false if train car is at max capacity
    def AddPassenger(self, passenger):
        bestSafeZone = self.__GetBestSafeZone()
        if bestSafeZone == -1:
            return False
        else:
            self.__AddPassengerToSafeZone(passenger, bestSafeZone)
            self.occupancy += 1
            return True

    # Add passenger to safe zone at first available index
    def __AddPassengerToSafeZone(self, passenger, index):
        for i in range(0, len(self.spaces[index])):
            if self.spaces[index][i] is None:
                self.spaces[index][i] = passenger
                break

    # Determines safezone with least people
    def __GetBestSafeZone(self):
        bestIndex = -1
        for i in range(0, len(self.spaces)):
            space = self.spaces[i].count(None)
            if space > 0 and bestIndex == -1:
                bestIndex = i
            if space > self.spaces[bestIndex].count(None):
                bestIndex = i
        return bestIndex

    # returns # of empty spots in safe zone
    def __GetSpaceInSafeZone(self, arr):
        return arr.count(None)

    # make passengers depart if their stop counter is 0
    def ArriveAtStation(self):
        passengersDeparting: Passenger = list()
        for i in range(0, len(self.spaces)):
            for j in range(0, len(self.spaces[i])):
                if self.spaces[i][j] is not None:
                    self.spaces[i][j].DecrementStops()
                    if self.spaces[i][j].GetStopsUntilDisembark() == 0:
                        passengersDeparting.append(self.spaces[i][j])
                        self.spaces[i][j] = None
                        self.occupancy -= 1
        return passengersDeparting

    # Do everything needed every minute
    # Incremenets passengers vars
    def Tick(self):
        for i in range(0, len(self.spaces)):
            numberInfected = 0
            for j in range(0, len(self.spaces[i])):
                if self.spaces[i][j] is not None and self.spaces[i][j].GetIsInfected():
                    numberInfected += 1
            for j in range(0, len(self.spaces[i])):
                if self.spaces[i][j] is not None:
                    self.spaces[i][j].IncrementRideTime()
                    if not self.spaces[i][j].GetIsInfected():
                        self.spaces[i][j].AddExposureTime(numberInfected)


class Passenger():
    def __init__(self, index, stopsUntillDisembark, infected):
        self.stopsUntillDisembark = stopsUntillDisembark
        self.infected = infected
        self.rideTime = 0
        self.exposureTime = 0

        self.index = index

    def __str__(self):
        return "index: {}, stops to go: {}, Infected: {}, ride time: {}, exposure time: {}".format(self.index,
                                                                                                   self.stopsUntillDisembark,
                                                                                                   self.infected,
                                                                                                   self.rideTime,
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


def Simulation(trainSchedule, simulationTime):
    trainCounter = 0
    passengerIndex = 0
    departedPassengers = list()
    clock = 0
    subwayLine = GetSubwayLine()
    trainsEnroute = list()

    carMaxCapacity = 258
    carSafeCapacity = 20

    # Run the simulation until there are no more trains scheduled to enter the line
    # and all trains which have entered the line have also exited the line.
    while trainSchedule or trainsEnroute:

        if trainSchedule and clock == trainSchedule[0]:
            trainSchedule.pop(0)
            trainCounter += 1
            trainsEnroute.append(Train(trainCounter, 8, subwayLine[0], carMaxCapacity, carSafeCapacity))
            print("[ADD](", clock, "):", trainCounter, sep=' ')

        # Generate new passengers at every station in line except for the final station
        for stationIndex in range(0, len(subwayLine) - 1):
            passengerIndex += subwayLine[stationIndex].GeneratePassengers(passengerIndex)

        for train in trainsEnroute:

            # Tick trains (updates new values for passengers)
            train.Tick()

            # if train has arrived at next station
            if train.GetMinsToNextStation() <= 0:
                print("[STN](", clock, "):", train.identifier, train.station.stationName, sep=' ')

                # Get passengers off trains who arrived at their stop, add to list for later
                departingPassengers = train.ArriveAtStation()
                for p in departingPassengers:
                    departedPassengers.append(p)

                # get passengers waiting to board train at station
                passengersToLoad = subwayLine[train.GetStationIndex()].LoadPassengers()
                for p in passengersToLoad:
                    if train.AddPassenger(p):  # if passenger was succesfully added
                        passengersToLoad.remove(p)
                    else:  # train is full, exit loop
                        break
                # if train filled before station emptied, add passengers back into station queue
                if len(passengersToLoad) > 0:
                    subwayLine[train.GetStationIndex()].QueuePassengers(passengersToLoad)

                # If we're at the final stop, remove the train
                if train.GetStationIndex() == subwayLine[-1].index:
                    print("[RMV](", clock, "):", train.identifier, sep=' ')
                    trainsEnroute.remove(train)

                # Otherwise Advance train to the next station it will arive at
                else:
                    train.minsToNextStation = train.station.timeToNextStation
                    train.station = subwayLine[train.GetStationIndex() + 1]

            # Train is in transit.
            train.DecrementMinsToNextStation()
        clock += 1

    # Main loop ended, show data gathered.
    infectedPassengers = 0
    exposedPassengers = 0
    safePassengers = 0
    totalRideTime = 0
    totalExposureTime = 0
    for passenger in departedPassengers:
        totalRideTime += passenger.GetRideTime()
        if passenger.GetIsInfected():
            infectedPassengers += 1
        elif passenger.GetExposureTime() > 0:
            exposedPassengers += 1
            totalExposureTime += passenger.GetExposureTime()
        else:
            safePassengers += 1

    print("Passengers (Infected): ", infectedPassengers)
    print("Passengers (Exposed ): ", exposedPassengers)
    print("Passengers (Safe    ): ", safePassengers)
    print("Passengers (Total   ): ", infectedPassengers + exposedPassengers + safePassengers)
    print("")
    print("Transit  Time: ", totalRideTime)
    print("Exposure Time: ", totalExposureTime)
    print("")
    print("Expected exposure time (per passenger)", totalExposureTime / len(departedPassengers))
    print("Expected exposure time (per minute   )", totalExposureTime / totalRideTime)


def GetSubwayLine():
    data = [
        ["Canarsie - Rockaway Pkwy", 3, 4],
        ["E 105 St", 2, 5],
        ["New Lots Av", 3, 4],
        ["Livonia Av", 3, 3],
        ["Sutter Av", 4, 5],
        ["Atlantic Av", 3, 5],
        ["Broadway Jct", 4, 6],
        ["Bushwick Av - Aberdeen St", 6, 4],
        ["Wilson Av", 5, 1],
        ["Halsey St", 6, 3],
        ["Myrtle - Wyckoff Avs", 7, 2],
        ["Dekalb Av", 5, 3],
        ["Jefferson St", 5, 3],
        ["Morgan Av", 6, 4],
        ["Montrose Av", 5, 3],
        ["Grand St", 5, 3],
        ["Graham Av", 5, 1],
        ["Lorimer St", 4, 3],
        ["Bedford Av ", 4, 2],
        ["1 Av", 4, 4],
        ["3 Av", 7, 4],
        ["Union Sq - 14 St", 5, 1],
        ["14 St - 6 Avenue", 2, 2],
        ["14 St - 8 Avenue", 0, 0]
    ]
    stationList = list()
    index = 0
    for s in data:
        stationList.append(Station(index, s[0], s[1], s[2]))
        index += 1
    return stationList


# Generate the L-train manhattan-bound train arrival schedule at Canarsie Station.
# Information from: https://new.mta.info/document/18241
def GetTrainSchedule():
    trainSchedule = []

    # Add late night/early morning prefix
    for (h, m) in trainSchedulePart1:
        trainSchedule.append(h * 60 + m)

    # Add morning every 3/4 minutes times
    beginTime = trainSchedule[-1]
    counter = 0
    for i in range(120):
        counter += 1
        if counter == 3 or counter == 7:
            trainSchedule.append(beginTime + i + 1)
            if counter == 7:
                counter = 0

    # Add late mid-morning times
    for (h, m) in trainSchedulePart2:
        trainSchedule.append(h * 60 + m)

    # Add mid-day every 4/5 minutes times
    beginTime = trainSchedule[-1]
    counter = 0
    for i in range(360):
        counter += 1
        if counter == 4 or counter == 9:
            trainSchedule.append(beginTime + i + 1)
            if counter == 9:
                counter = 0

    # Add afternoon times
    for (h, m) in trainSchedulePart3:
        trainSchedule.append(h * 60 + m)

    # Add morning every 3/4 minutes times
    beginTime = trainSchedule[-1]
    counter = 0
    for i in range(160):
        counter += 1
        if counter == 3 or counter == 7:
            trainSchedule.append(beginTime + i + 1)
            if counter == 7:
                counter = 0

    # Add afternoon times
    for (h, m) in trainSchedulePart4:
        trainSchedule.append(h * 60 + m)

    # Add evening every 4/5 minutes times
    beginTime = trainSchedule[-1]
    counter = 0
    for i in range(130):
        counter += 1
        if counter == 4 or counter == 9:
            trainSchedule.append(beginTime + i + 1)
            if counter == 9:
                counter = 0

    # Add night times
    for (h, m) in trainSchedulePart5:
        trainSchedule.append(h * 60 + m)

    return trainSchedule


trainSchedulePart1 = [(0, 7)
    , (0, 19)
    , (0, 31)
    , (0, 43)
    , (1, 3)
    , (1, 23)
    , (1, 43)
    , (2, 3)
    , (2, 23)
    , (2, 43)
    , (3, 3)
    , (3, 23)
    , (3, 43)
    , (4, 3)
    , (4, 23)
    , (4, 43)
    , (4, 59)
    , (5, 9)
    , (5, 16)
    , (5, 22)
    , (5, 29)
    , (5, 35)
    , (5, 41)
    , (5, 47)
    , (5, 53)
    , (5, 59)
    , (6, 5)
                      ]

trainSchedulePart2 = [(8, 8)
    , (8, 11)
    , (8, 14)
    , (8, 17)
    , (8, 20)
    , (8, 23)
    , (8, 26)
    , (8, 29)
    , (8, 33)
    , (8, 37)
    , (8, 40)
    , (8, 44)
    , (8, 47)
    , (8, 51)
    , (8, 55)
    , (8, 58)
    , (9, 0)
    , (9, 4)
    , (9, 8)
    , (9, 11)
    , (9, 14)
    , (9, 17)
    , (9, 22)
    , (9, 23)
    , (9, 28)
    , (9, 30)
    , (9, 35)
    , (9, 38)
    , (9, 42)
    , (9, 46)
    , (9, 51)
    , (9, 55)
    , (10, 0)
                      ]

trainSchedulePart3 = [(16, 4)
    , (16, 9)
    , (16, 13)
    , (16, 17)
    , (16, 21)
    , (16, 25)
    , (16, 29)
    , (16, 33)
    , (16, 37)
    , (16, 41)
    , (16, 45)
    , (16, 49)
    , (16, 53)
    , (16, 57)
                      ]

trainSchedulePart4 = [(19, 39)
    , (19, 45)
    , (19, 49)
    , (19, 53)
    , (19, 57)
    , (20, 0)
    , (20, 5)
                      ]

trainSchedulePart5 = [(22, 22)
    , (22, 27)
    , (22, 33)
    , (22, 42)
    , (22, 53)
    , (23, 3)
    , (23, 13)
    , (23, 23)
    , (23, 33)
    , (23, 43)
    , (23, 55)
                      ]

Simulation(GetTrainSchedule(), 1440)

