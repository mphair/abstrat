from cell import Cell
from entity import Entity
import json
import copy

class Config:
    @staticmethod
    def FromJson(jsonString, universe):
        c = Config(universe)
        c.InitFromJson(jsonString)
        return c
    def InitFromJson(self, jsonString):
        d = json.loads(jsonString)
        self.Name = d['name']
        self.__defaultGatherEfficencies = d['defaultGatherEfficencies']
        self.__defaultMovementRate = d['defaultMovementRate']
        self.__energyTypes = d['energyTypes']
        self.__subsistEnergyRequirements = d['subsistEnergyRequirements']
        self.__moveEnergyRequirements = d['moveEnergyRequirements']
        self.__energyDistributions = d['energyDistributions']
        self.__cellLayoutPlan = d['cellLayoutPlan']
        self.__initialEntityPlan = d['initialEntityPlan']
        self.__advancementsPlan = d['advancementsPlan']
        self.__defaultTeachingMultiplier = d['defaultTeachingMultiplier']
        self.__defaultLeachingTargetRate = d['defaultLeachingTargetRate']
        self.__defaultLeachingPowers = d['defaultLeachingPowers']
        self.__defaultLeachingDefenses = d['defaultLeachingDefenses']
        self.__defaultLeachingEfficencies = d['defaultLeachingEfficencies']
    def __init__(self, universe):
        self.Universe = universe
    def ToJson(self):
        return json.dumps({
            'name': self.Name,
            'defaultGatherEfficencies': self.__defaultGatherEfficencies,
            'defaultMovementRate': self.__defaultMovementRate,
            'energyTypes': self.__energyTypes,
            'subsistEnergyRequirements': self.__subsistEnergyRequirements,
            'moveEnergyRequirements': self.__moveEnergyRequirements,
            'energyDistributions': self.__energyDistributions,
            'cellLayoutPlan': self.__cellLayoutPlan,
            'initialEntityPlan': self.__initialEntityPlan,
            'advancementsPlan': self.__advancementsPlan,
            'defaultTeachingMultiplier': self.__defaultTeachingMultiplier,
            'defaultLeachingTargetRate': self.__defaultLeachingTargetRate,
            'defaultLeachingPowers': self.__defaultLeachingPowers,
            'defaultLeachingDefenses': self.__defaultLeachingDefenses,
            'defaultLeachingEfficencies': self.__defaultLeachingEfficencies,
            })
    def GetDefaultGatherEfficencies(self):
        return copy.deepcopy(self.__defaultGatherEfficencies)
    def GetDefaultMovementRate(self):
        return self.__defaultMovementRate
    def GetEnergyTypes(self):
        return copy.deepcopy(self.__energyTypes)
    def GetSubsistEnergyRequirements(self):
        return copy.deepcopy(self.__subsistEnergyRequirements)
    def GetMoveEnergyRequirements(self):
        return copy.deepcopy(self.__moveEnergyRequirements)
    def GetEnergyFunctions(self): # eventually this should be much more interesting? Maybe families of functions available? definitely need based on location.
        energyFunctions = dict()
        for (energyType, amount) in self.__energyDistributions.items():
            energyFunctions[energyType] = lambda t: amount 
        return energyFunctions
    def GetInitialCells(self):
        funcName, funcArgs = self.__cellLayoutPlan
        return CellLayoutFunctions[funcName](funcArgs, self.GetEnergyFunctions(), self.Universe)
    def GetInitialEntities(self, cells):
        entities = []
        for team,namesAndIndicies in self.__initialEntityPlan:
            for cell,name in [(cells[index],name) for name,index in namesAndIndicies]:
                newEntity = Entity(team, name, self.Universe)
                newEntity.PresentInCell = cell
                cell.EntityPresent = newEntity
                entities.append(newEntity)
        return entities
    def GetAdvancements(self):
        advancements = dict()
        for name,adv in self.__advancementsPlan.items():
            energyRequirements, prereqs, funcName, funcArgs = adv
            advancements[name] = (energyRequirements, prereqs, lambda x: AdvancementFunctions[funcName](x, funcArgs))
        return advancements
    def GetDefaultTeachingMultiplier(self):
        return self.__defaultTeachingMultiplier

    def GetDefaultLeachingTargetRate(self):
        return self.__defaultLeachingTargetRate
    def GetDefaultLeachingPowers(self):
        return copy.deepcopy(self.__defaultLeachingPowers)
    def GetDefaultLeachingDefenses(self):
        return copy.deepcopy(self.__defaultLeachingDefenses)
    def GetDefaultLeachingEfficencies(self):
        return copy.deepcopy(self.__defaultLeachingEfficencies)

############################## Cell Layout Functions ##############################
CellLayoutFunctions = dict()
def Square(args, energyFunctions, universe):
    sideLen = args[0]
    cells = [None]*(sideLen*sideLen)
    for x in range(sideLen):
        for y in range(sideLen):
            index = x*sideLen+y
            name = str(x)+','+str(y)
            thisCell = Cell(name, energyFunctions, universe)
            cells[index] = thisCell
            if (x > 0):
                up = cells[(x-1)*sideLen+y]
                thisCell.Neighbors.append(up)
                up.Neighbors.append(thisCell)
            if (y > 0):
                left = cells[x*sideLen+y-1]
                thisCell.Neighbors.append(left)
                left.Neighbors.append(thisCell)
    return cells
CellLayoutFunctions[u"Square"] = Square

############################## Advancement Functions ##############################
AdvancementFunctions = dict()
def MovementPlus(entity, args):
    entity.MovementRate += args[0]
AdvancementFunctions[u"MovementPlus"] = MovementPlus
def GatherEfficencyPlus(entity, args):
    entity.GatherEfficencies[args[0]] += args[1]
AdvancementFunctions[u"GatherEfficencyPlus"] = GatherEfficencyPlus
def TeachingMultiplierPlus(entity, args):
    entity.TeachingMultiplier += args[0]
AdvancementFunctions[u"TeachingMultiplierPlus"] = TeachingMultiplierPlus
##def SplitRatePlus(entity, args):
##    entity.SplitRate += args[0]
##AdvancementFunctions[u"SplitRatePlus"] = SplitRatePlus #TODO: Implement split rate limitations
##def TeachRatePlus(entity, args):
##    entity.TeachRate += args[0]
##AdvancementFunctions[u"TeachRatePlus"] = TeachRatePlus #TODO: Implement teach rate limitations
def LeachingTargetRatePlus(entity, args):
    entity.LeachingTargetRate += args[0]
AdvancementFunctions[u"LeachingTargetRatePlus"] = LeachingTargetRatePlus
def LeachingPowerPlus(entity, args):
    entity.LeachingPowers[args[0]] += args[1]
AdvancementFunctions[u"LeachingPowerPlus"] = LeachingPowerPlus
def LeachingDefensePlus(entity, args):
    entity.LeachingDefenses[args[0]] += args[1]
AdvancementFunctions[u"LeachingDefensePlus"] = LeachingDefensePlus
def LeachingEfficencyPlus(entity, args):
    entity.LeachingEfficencies[args[0]] += args[1]
AdvancementFunctions[u"LeachingEfficencyPlus"] = LeachingEfficencyPlus

#################### HELPERS ##################
def valueOrDefault(d, key, default):
    if d.has_key(key): return d[key]
    else: return default

def ValidateSchema(filename):
    f_in = open(filename)
    jsonString = f_in.read()
    f_in.close()
    import universe
    jsonString = Config.FromJson(jsonString, universe.Universe()).ToJson()

def LearnNewSchema(filename):
    f_in = open(filename)
    jsonString = f_in.read()
    f_in.close()
    del f_in
    f_backup = open(filename+".bak", 'w')
    f_backup.write(jsonString)
    f_backup.close()
    del f_backup
    import universe
    jsonString = Config.FromJson(jsonString, universe.Universe()).ToJson()
    f_out = open(filename, 'w')
    f_out.write(jsonString)
    f_out.close()
    del f_out
