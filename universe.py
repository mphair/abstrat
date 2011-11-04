import copy
import json
from cell import Cell
from entity import Entity
from config import Config
from actions import Actions

class Universe:
    DEBUG_MOVE = False
    DEBUG_SUBSIST = False
    DEBUG_ENERGY = False
    DEBUG_DISCOVER = False
    DEBUG_LEARN = False
    DEBUG_TEACH = False
    DEBUG_LEACH = False

    def LoadFromConfig(self):
        # none of these vary during the game:
        self.energyTypes = self.config.GetEnergyTypes()
        self.cells = self.config.GetInitialCells()
        self.subsistEnergyRequirements = self.config.GetSubsistEnergyRequirements()
        self.moveEnergyRequirements = self.config.GetMoveEnergyRequirements()
        self.__DefaultGatherEfficencies = self.config.GetDefaultGatherEfficencies()
        self.__DefaultMovementRate = self.config.GetDefaultMovementRate()
        self.__DefaultTeachingMultiplier = self.config.GetDefaultTeachingMultiplier()
        self.__DefaultLeachingTargetRate = self.config.GetDefaultLeachingTargetRate()
        self.__DefaultLeachingPowers = self.config.GetDefaultLeachingPowers()
        self.__DefaultLeachingDefenses = self.config.GetDefaultLeachingDefenses()
        self.__DefaultLeachingEfficencies = self.config.GetDefaultLeachingEfficencies()
        self.Advancements = self.config.GetAdvancements()
        self.actions = Actions(self)

    def LoadNew(self, configFileName):
        f = open(configFileName)
        jsonString = f.read()
        f.close()
        self.config = Config.FromJson(jsonString, self)
        self.LoadFromConfig()
        # the following vary during the game:
        self.entities = self.config.GetInitialEntities(self.cells)
        self.t = 1
        self.__initTeams()

    def ToJson(self):
        return json.dumps({
            'config': self.config.ToJson(),
            'entities': [entity.ToJson() for entity in self.entities],
            't': self.t})
    @staticmethod
    def FromJson(jsonString):
        universe = Universe()
        universe.ReinitFromJson(jsonString)
        return universe

    def __initTeams(self):
        self.__teams = set()
        for entity in self.entities:
            self.__teams.add(entity.Team.lower())
        self.__teamsAccountedFor = set()

    def ReinitFromJson(self, jsonString):
        d = json.loads(jsonString)
        self.config = Config.FromJson(d['config'], self)
        self.LoadFromConfig()

        cellDict = dict()
        for cell in self.cells:
            cellDict[cell.Name] = cell
        self.entities = [Entity.FromJson(jsonString, self, cellDict) for jsonString in d['entities']]

        self.t = d['t']
        self.__initTeams()
        
    def GetDefaultGatherEfficencies(self):
        return copy.deepcopy(self.__DefaultGatherEfficencies)

    def GetDefaultMovementRate(self):
        return copy.deepcopy(self.__DefaultMovementRate)

    def GetDefaultTeachingMultiplier(self):
        return self.__DefaultTeachingMultiplier

    def GetDefaultLeachingTargetRate(self):
        return self.__DefaultLeachingTargetRate
    def GetDefaultLeachingPowers(self):
        return copy.deepcopy(self.__DefaultLeachingPowers)
    def GetDefaultLeachingDefenses(self):
        return copy.deepcopy(self.__DefaultLeachingDefenses)
    def GetDefaultLeachingEfficencies(self):
        return copy.deepcopy(self.__DefaultLeachingEfficencies)

    def DoTimeStep(self):
        self.actions.DoGather()
        #transfer
        self.actions.DoSplit()
        self.actions.DoDiscover()
        self.actions.DoTeach()
        #unlearn
        self.actions.DoLeach()
        self.actions.DoMove()
        self.actions.DoSubsist()
        self.actions = Actions(self)
        self.__teamsAccountedFor = set()
        self.t+=1
        
    def ActTryTimestep(self, actions, team):
        self.actions.extend(actions)
        self.__AccountFor(team)
        if self.__AllAccountedFor():
            self.DoTimeStep()
            return True
        return False
        
    def __AccountFor(self, team):
        if team not in self.__teams:
            raise "Team " + str(team) + " unknown."
        self.__teamsAccountedFor.add(team)

    def AccountedFor(self, team):
        return (team in self.__teamsAccountedFor)
    def __AllAccountedFor(self):
        return all([self.AccountedFor(team) for team in self.__teams])
        
    def RunTests(self):
        self.LoadNew("basic.config")
        self.DoTimeStep()
        print self.entities
        print "now move"
        self.actions.PendingMoves.append((self.entities[0],self.entities[0].PresentInCell.Neighbors[2]))
        self.actions.PendingMoves.append((self.entities[1],self.entities[1].PresentInCell.Neighbors[0]))
        self.DoTimeStep()
        print self.entities
        print "now just sit"
        self.DoTimeStep()
        print self.entities
        print "now split"
        self.actions.PendingSplits.append((self.entities[0],self.entities[0].PresentInCell.Neighbors[2]))
        self.actions.PendingSplits.append((self.entities[1],self.entities[1].PresentInCell.Neighbors[0]))
        self.DoTimeStep()
        print self.entities
        print "now A:1 and B:1 move too much and die"
        self.entities[2].MovementRate = 4 # hack to allow too much movement
        self.entities[3].MovementRate = 4 # hack to allow too much movement
        next = [self.entities[2].PresentInCell.Neighbors[0], self.entities[3].PresentInCell.Neighbors[0]]
        for x in range(4):
            for n in range(2):
                print "->", next[n].Name
                self.actions.PendingMoves.append((self.entities[n+2],next[n]))
                next[n] = next[n].Neighbors[0]
        self.DoTimeStep()
        print self.entities
#        self.DEBUG_DISCOVER = True
#        self.DEBUG_LEARN = True
#        self.DEBUG_ENERGY = True
        print "try to discover ahead of schedule"
        self.actions.PendingDiscoveries.append((self.entities[0],u"movement+2",((u"n1",2),)))
        self.DoTimeStep()
        print self.entities
        print "now discover prereq"
        self.actions.PendingDiscoveries.append((self.entities[0],u"movement+1",((u"n1",2),)))
        self.DoTimeStep()
        print self.entities
        print "now discover again"
        self.actions.PendingDiscoveries.append((self.entities[0],u"movement+2",((u"n1",0),)))
        self.DoTimeStep()
        print self.entities
        print "teach"
        self.actions.PendingTeachings.append((self.entities[0],u'movement+1',((u'n1',1),),self.entities[1]))
        self.DoTimeStep()
        print self.entities

if __name__ == "__main__":
    Universe().RunTests()
