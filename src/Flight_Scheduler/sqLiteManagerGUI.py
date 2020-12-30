# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 18:29:26 2014

@author: Anders Quigg
"""
import random
import sqlite3
from datetime import datetime


class sqLiteDB:
    def __init__(self, filePath):
        self.filePath = filePath
        self.desiredAircraft = []
        self.desiredOrigin = []
        self.desiredDest = []
        self.desiredAirline = []
        self.minDuration = -1
        self.maxDuration = -1
        self.timeFromNow = -1
        self.desiredEras = [1, 1, 1, 1, 1, 1, 1]
        # DELETE TEMPORARY TABLES IF THEY EXIST###
        cursor = self.dbOpen(self.filePath)
        cursor.execute("DROP TABLE IF EXISTS tempRouteTable")
        cursor.close()

    def buildAirportQuery(self):
        query = ""
        if len(self.desiredOrigin) > 0 and not self.desiredOrigin[0] == "":
            depString = "("
            for origin in self.desiredOrigin:
                depString += "origin = '" + origin + "' OR "
            depString = depString[:-4]
            query += depString + ") AND "
        if len(self.desiredDest) > 0 and not self.desiredDest[0] == "":
            destString = "("
            for destination in self.desiredDest:
                destString += "destination = '" + destination + "' OR "
            destString = destString[:-4]
            query += destString + ") AND "
        return query

    def buildDurationQuery(self):
        query = ""
        if not self.minDuration == -1:
            query += (
                "duration > "
                + str(self.minDuration)
                + " AND duration < "
                + str(self.maxDuration)
                + " AND "
            )
        return query

    def buildAircraftQuery(self):
        query = ""
        if len(self.desiredAircraft) > 0:
            aircraftString = "("
            for aircraft in self.desiredAircraft:
                aircraftString += "aircraft = '" + aircraft + "' OR "
            aircraftString = aircraftString[:-4]
            query += aircraftString + ") AND "
        return query

    def buildAirlineQuery(self):
        query = ""
        if len(self.desiredAirline) > 0 and not self.desiredAirline[0] == "":
            airlineString = "(flightId IN (SELECT flightId FROM Flight WHERE "
            for airline in self.desiredAirline:
                airlineString += "airline = '" + airline + "' OR "
            airlineString = airlineString[:-4]
            query += airlineString + ")) AND "
        return query

    def buildCurrentTimeQuery(self):
        query = ""
        if not self.timeFromNow == -1:
            if self.timeFromNow < 5:
                self.timeFromNow = 5
            if self.timeFromNow > 120:
                self.timeFromNow = 120
            t = datetime.utcnow()
            day = t.isoweekday()
            hour = t.hour
            minute = t.minute
            time = int(minute + (hour * 60) + ((day - 1) * 24 * 60))
            priorTime = time + self.timeFromNow
            if priorTime > 10080:
                priorTime -= 10080
            if priorTime > time:
                currentString = (
                    "(departureTime > "
                    + str(time)
                    + " AND departureTime < "
                    + str(priorTime)
                )
            else:
                currentString = (
                    "(departureTime > "
                    + str(time)
                    + " OR departuretime < "
                    + str(priorTime)
                )
            query += currentString + ") AND "
        return query

    def buildEraQuery(self):
        query = ""
        if 0 in self.desiredEras:
            query = "("
            for index, value in enumerate(self.desiredEras):
                if value == 1:
                    if index == 0:
                        query += "(year > 1949 and year < 1960) OR "
                    if index == 1:
                        query += "(year > 1959 and year < 1970) OR "
                    if index == 2:
                        query += "(year > 1969 and year < 1980) OR "
                    if index == 3:
                        query += "(year > 1979 and year < 1990) OR "
                    if index == 4:
                        query += "(year > 1989 and year < 2000) OR "
                    if index == 5:
                        query += "(year > 2000 and year < 2007) OR "
                    if index == 6:
                        query += "(year > 2006) OR "
            query = query[:-4]
            query += ") AND "
        return query

    def getAirportDetails(self, airport):
        query = "SELECT * FROM Airport WHERE airportCode = '" + airport + "';"
        cursor = self.dbOpen(self.filePath)
        data = cursor.execute(query).fetchone()
        cursor.close()
        self.con.close()
        return data

    def getAirlineFull(self, airline):
        query = "SELECT airlineFullName FROM Airline WHERE airline = '" + airline + "';"
        cursor = self.dbOpen(self.filePath)
        data = cursor.execute(query).fetchone()[0]
        cursor.close()
        self.con.close()
        return data

    def getAircraftDetails(self, aircraft):
        query = "SELECT * FROM Aircraft WHERE aircraft = '" + aircraft + "';"
        cursor = self.dbOpen(self.filePath)
        data = cursor.execute(query).fetchone()
        cursor.close()
        self.con.close()
        return data

    def getTableDetails(self):
        baseQuery = "SELECT DISTINCT airline,origin,destination,aircraft FROM Flight NATURAL JOIN Leg WHERE "
        baseQuery += self.buildAirlineQuery()
        baseQuery += self.buildAirportQuery()
        baseQuery += self.buildDurationQuery()
        baseQuery += self.buildAircraftQuery()
        baseQuery += self.buildCurrentTimeQuery()
        baseQuery += self.buildEraQuery()
        if baseQuery.endswith("AND "):
            baseQuery = (
                baseQuery[:-5] + " ORDER BY airline,origin,destination,aircraft;"
            )
        else:
            baseQuery = (
                baseQuery[:-7] + " ORDER BY airline,origin,destination,aircraft;"
            )
        cursor = self.dbOpen(self.filePath)
        data = cursor.execute(baseQuery).fetchall()
        cursor.close()
        self.con.close()
        return data

    def getSpecificFlight(self, airline, origin, dest, aircraft):
        baseQuery = (
            "SELECT DISTINCT flightId,legId FROM Flight NATURAL JOIN Leg WHERE origin = '"
            + origin
            + "' AND destination = '"
            + dest
            + "' AND aircraft = '"
            + aircraft
            + "' AND (flightId IN (SELECT flightId FROM Flight WHERE airline = '"
            + airline
            + "')) AND "
        )
        baseQuery += self.buildCurrentTimeQuery()
        baseQuery += self.buildDurationQuery()
        baseQuery += self.buildEraQuery()
        baseQuery = baseQuery[:-5] + " ORDER BY RANDOM() LIMIT 1;"

        cursor = self.dbOpen(self.filePath)
        data = cursor.execute(baseQuery).fetchone()
        if data is None:
            return []
        legID = data[1]
        mainQuery = (
            "SELECT * FROM Flight NATURAL JOIN Leg WHERE flightId = "
            + str(data[0])
            + ";"
        )
        cursor.execute(mainQuery)
        data = cursor.fetchall()
        cursor.close()
        self.con.close()
        if len(data) == 0:
            return []
        return [data, legID]

    def getRandomRoute(self):
        routeQuery = "SELECT DISTINCT origin,destination FROM Leg WHERE "
        subQuery = ""
        # airlineMatch
        if len(self.desiredAirline) > 0 and not self.desiredAirline[0] == "":
            airlineString = "flightId IN (SELECT DISTINCT flightId FROM Flight WHERE "
            for airline in self.desiredAirline:
                airlineString += "airline = '" + airline + "' OR "
            airlineString = airlineString[:-4]
            subQuery += airlineString + ") AND "
        # durationMatch
        if not self.minDuration == -1:
            subQuery += (
                "duration > "
                + str(self.minDuration)
                + " AND duration < "
                + str(self.maxDuration)
                + " AND "
            )
        # aircraftMatch
        if len(self.desiredAircraft) > 0:
            aircraftString = "("
            for aircraft in self.desiredAircraft:
                aircraftString += "aircraft = '" + aircraft + "' OR "
            aircraftString = aircraftString[:-4]
            subQuery += aircraftString + ") AND "
        # origin,destination match
        if len(self.desiredOrigin) > 0 and not self.desiredOrigin[0] == "":
            depString = "("
            for origin in self.desiredOrigin:
                depString += "origin = '" + origin + "' OR "
            depString = depString[:-4]
            subQuery += depString + ") AND "
        if len(self.desiredDest) > 0 and not self.desiredDest[0] == "":
            destString = "("
            for destination in self.desiredDest:
                destString += "destination = '" + destination + "' OR "
            destString = destString[:-4]
            subQuery += destString + ") AND "
        # EraMatch
        # CurrentMatch

        if subQuery.endswith("AND "):
            subQuery = subQuery[:-5] + " ORDER BY RANDOM() LIMIT 1"
        else:
            subQuery = subQuery[:-7] + " ORDER BY RANDOM() LIMIT 1"
        if subQuery == " ORDER BY RANDOM() LIMIT 1":
            routeQuery = routeQuery[:-7]
        routeQuery += subQuery + ";"
        cursor = self.dbOpen(self.filePath)
        route = cursor.execute(routeQuery).fetchone()
        origin = route[0]
        destination = route[1]
        mainQuery = (
            "SELECT DISTINCT flightId FROM Leg WHERE origin = '"
            + origin
            + "' AND destination = '"
            + destination
            + "' AND "
        )

        if len(self.desiredAirline) > 0 and not self.desiredAirline[0] == "":
            airlineString = "flightId IN (SELECT DISTINCT flightId FROM Flight WHERE "
            for airline in self.desiredAirline:
                airlineString += "airline = '" + airline + "' OR "
            airlineString = airlineString[:-4]
            mainQuery += airlineString + ") AND "
        # durationMatch
        if not self.minDuration == -1:
            mainQuery += (
                "duration > "
                + str(self.minDuration)
                + " AND duration < "
                + str(self.maxDuration)
                + " AND "
            )
        # aircraftMatch
        if len(self.desiredAircraft) > 0:
            aircraftString = "("
            for aircraft in self.desiredAircraft:
                aircraftString += "aircraft = '" + aircraft + "' OR "
            aircraftString = aircraftString[:-4]
            mainQuery += aircraftString + ") AND "
        if mainQuery.endswith("AND "):
            mainQuery = mainQuery[:-5] + " ORDER BY RANDOM() LIMIT 1"
        else:
            mainQuery = mainQuery[:-7] + " ORDER BY RANDOM() LIMIT 1"

        mainQuery = (
            "SELECT * FROM Flight NATURAL JOIN Leg WHERE flightId = ("
            + mainQuery
            + ");"
        )
        data = cursor.execute(mainQuery).fetchall()
        cursor.close()
        self.con.close()
        if len(data) == 0:
            return []
        return data

    def getRandomFlight(self):
        baseQuery = "SELECT * FROM Flight NATURAL JOIN Leg WHERE "
        baseQuery += self.buildAirportQuery()
        baseQuery += self.buildDurationQuery()
        baseQuery += self.buildAircraftQuery()
        baseQuery += self.buildAirlineQuery()
        baseQuery += self.buildCurrentTimeQuery()
        baseQuery += self.buildEraQuery()
        if baseQuery.endswith("AND "):
            baseQuery = baseQuery[:-5]
        else:
            baseQuery = baseQuery[:-7]
        baseQuery = (
            "SELECT DISTINCT legID,registration,flightID FROM (" + baseQuery + ");"
        )
        cursor = self.dbOpen(self.filePath)
        cursor.execute(baseQuery)
        data = cursor.fetchall()
        availFlights = []
        for tuple in data:
            listTuple = list(tuple)
            availFlights.append(listTuple)
        # get all regs and pick one
        regSet = set()
        for row in availFlights:
            regSet.add(row[1])
        chosenReg = random.sample(regSet, 1)[0]
        chosenFlights = []
        for row in availFlights:
            if row[1] == chosenReg:
                chosenFlights.append(row)
        chosenFlight = random.choice(chosenFlights)
        baseQuery = (
            "SELECT * FROM Flight NATURAL JOIN Leg WHERE flightID = "
            + str(chosenFlight[2])
            + ";"
        )
        cursor.execute(baseQuery)
        data = cursor.fetchall()
        cursor.close()
        self.con.close()
        if len(data) == 0:
            return []
        return [data, chosenFlight[0]]

    def dbOpen(self, filePath):
        self.con = sqlite3.connect(filePath)
        self.con.text_factory = str
        return self.con.cursor()

    def pullAircraft(self):
        cursor = self.dbOpen(self.filePath)
        data = cursor.execute(
            "SELECT DISTINCT aircraftFamily,aircraft,fullName,aircraftClass FROM Aircraft"
        ).fetchall()
        famDict = {}
        nameDict = {}
        roleDict = {}
        for tuple in data:
            if not tuple[0] in famDict.keys():
                famDict[tuple[0]] = []

            famDict[tuple[0]].append(tuple[1])
            nameDict[tuple[1]] = tuple[2]
            roleDict[tuple[1]] = tuple[3]
        cursor.close()
        self.con.close()
        return (famDict, nameDict, roleDict)

    def dbClose(self):
        # print("Connection closing")
        self.con.close()
