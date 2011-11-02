from entity import Entity
import json

def NameOrNone(s):
    if s:
        return s.Name
    else:
        return None

class Cell:
    def __init__(self, name, energyFunctions, universe):
        self.Universe = universe
        self.EnergyFunctions = energyFunctions
        self.Name = name
        self.EntityPresent = None
        self.Neighbors = []
        self.EntitiesArriving = []
        self.GathererEfficencies = dict()
        self.InSplitZoneFor = []
    def __repr__(self):
        s = "==== Cell: " + self.Name + " ====\n"
        if (self.EntityPresent): s+= " Entity Present: "+self.EntityPresent.Name+"\n"
        s+= " Neighbors: "+str([n.Name for n in self.Neighbors])+"\n"
        return s
    def ToDict(self):
        return {'name': self.Name, 'entityPresent': NameOrNone(self.EntityPresent), 'neighbors': [cell.Name for cell in self.Neighbors]}
    def ToJson(self):
        return json.dumps(self.ToDict())
##    @staticmethod
##    def FromJson(jsonString, energyFunctions, universe):
##        d = json.loads(jsonString)
##        cell = Cell(d['name'], energyFunctions, universe)
##        cell.EntityPresent = d['entityPresent']
##        cell.Neighbors = d['neighbors']
##        return cell
##    def Reconstitute(self, entityDict, cellDict):
##        if self.EntityPresent: self.EntityPresent = entityDict[self.EntityPresent]
##        self.Neighbors = [cellDict[name] for name in self.Neighbors]
    def FailBadMoves(self):
        if self.EntityPresent != None or len(self.EntitiesArriving) != 1:
            self.EntitiesArriving = []
    def ExecuteGoodMoves(self):
        if len(self.EntitiesArriving) == 0:
            return

        mover = self.EntitiesArriving[0]
        if not(mover.TrySubtractEnergy(self.Universe.moveEnergyRequirements)): # if successful, pays the energy cost
            return # move failure, not enough energy
        
        if len(self.EntitiesArriving) == 1:
            self.EntityPresent = mover
            mover.PresentInCell.EntityPresent = None
            mover.PresentInCell = self
            self.EntitiesArriving = []
        else:    
            raise "Logic failure... Should be none or 1"
    def PrepareGather(self):
        self.GathererEfficencies = dict()
        for energyType in self.Universe.energyTypes:
            self.GathererEfficencies[energyType] = 0
    def Gather(self, energyType, efficiency):
        totalEfficency = self.GathererEfficencies[energyType]
        if totalEfficency > 1.0:
            fraction = efficiency / totalEfficency
        else:
            fraction = efficiency
        return int(self.EnergyFunctions[energyType](self.Universe.t) * fraction)
    

    def IsNStepsAwayFrom(self, cell, n):
        toCheck = [(self,0)]
        while len(toCheck) > 0:
            (cellToCheck,dist) = toCheck.pop(0)
            if cellToCheck == cell:
                return True
            if dist < n:
                toCheck.extend([(cell,dist+1) for cell in self.Neighbors])
        return False
