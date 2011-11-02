import copy
import json

class Entity:
    def __init__(self, team, name, universe):
        self.Team = team
        self.Name = name
        self.Universe = universe
        self.GatherEfficencies = universe.GetDefaultGatherEfficencies()
        self.EnergyStores = dict()
        for energyType in universe.energyTypes:
            self.EnergyStores[energyType] = 0
        self.PendingMoves = []
        self.PendingSplits = []
        self.PendingDiscoveries = []
        self.PendingTeachings = []
        self.PendingLeachings = []
        self.PresentInCell = None # this is a duplication of data, but probably nice for avoiding scanning the whole universe
        self.MovementRate = universe.GetDefaultMovementRate()
        self.ChildCount = 0
        self.TeachingMultiplier = universe.GetDefaultTeachingMultiplier()
        self.LeachingTargetRate = universe.GetDefaultLeachingTargetRate()
        self.LeachingPowers = universe.GetDefaultLeachingPowers()
        self.LeachingDefenses = universe.GetDefaultLeachingDefenses()
        self.LeachingEfficencies = universe.GetDefaultLeachingEfficencies()
        self.Advancements = dict()
    def __repr__(self):
        s = "==== Entity: " + self.Name + "(" + self.Team +") ====\n"
        s+= " Location: "+self.PresentInCell.Name+"\n"
        s+= " Energy Stores: "+str(self.EnergyStores)+"\n"
        s+= " Advancements: "+str(self.Advancements)+"\n"
        s+= " Movement Rate: "+str(self.MovementRate)+"\n"
        s+= " Teaching Multiplier: "+str(self.TeachingMultiplier)+"\n"
        s+= " Leaching Target Rate: "+str(self.LeachingTargetRate)+"\n"
        s+= " Leaching Powers: "+str(self.LeachingPowers)+"\n"
        s+= " Leaching Defenses: "+str(self.LeachingDefenses)+"\n"
        s+= " Leaching Efficencies: "+str(self.LeachingEfficencies)+"\n"
        return s
    def ToJson(self):
        return json.dumps({
            'team': self.Team,
            'name': self.Name,
            'gatherEfficencies': self.GatherEfficencies,
            'energyStores': self.EnergyStores,
            'presentInCell': self.PresentInCell.Name,
            'childCount': self.ChildCount,
            'movementRate': self.MovementRate,
            'advancements': self.Advancements,
            'teachingMultiplier': self.TeachingMultiplier,
            'leachingTargetRate': self.LeachingTargetRate,
            'leachingPowers': self.LeachingPowers,
            'leachingDefenses': self.LeachingDefenses,
            'leachingEfficencies': self.LeachingEfficencies})
    @staticmethod
    def FromJson(jsonString, universe, cellDict):
        d = json.loads(jsonString)
        entity = Entity(d['team'], d['name'], universe)
        entity.GatherEfficencies = d['gatherEfficencies']
        entity.EnergyStores = d['energyStores']
        entity.PresentInCell = cellDict[d['presentInCell']]
        entity.PresentInCell.EntityPresent = entity
        entity.ChildCount = d['childCount']
        entity.MovementRate = d['movementRate']
        entity.Advancements = d['advancements']
        entity.TeachingMultiplier = d['teachingMultiplier']
        entity.LeachingTargetRate = d['leachingTargetRate']
        entity.LeachingPowers = d['leachingPowers']
        entity.LeachingDefenses = d['leachingDefenses']
        entity.LeachingEfficencies = d['leachingEfficencies']
        return entity
    def InitMoves(self):
        self.__moveChancesRemaining = self.MovementRate
    def OpenMove(self):
        if len(self.PendingMoves) != 0 and self.__moveChancesRemaining != 0:
            self.PendingMoves[0].EntitiesArriving.append(self)
            return True
        else: return False
    def CloseMove(self):
        if (self.__moveChancesRemaining > 0): self.__moveChancesRemaining -= 1
        if len(self.PendingMoves) > 0 and self.PendingMoves[0] == self.PresentInCell:
            self.PendingMoves.pop(0)
    def OpenGather(self):
        for cell in [self.PresentInCell] + self.PresentInCell.Neighbors:
            for energyType in self.Universe.energyTypes:
                cell.GathererEfficencies[energyType] += self.GatherEfficencies[energyType]
    def ResolveGather(self):
        if self.Universe.DEBUG_ENERGY: print "Entity", self.Name, "gathering:"
        for cell in [self.PresentInCell] + self.PresentInCell.Neighbors:
            for energyType in self.Universe.energyTypes:
                amount = cell.Gather(energyType, self.GatherEfficencies[energyType])                 
                self.EnergyStores[energyType] += amount
                if self.Universe.DEBUG_ENERGY: print "...", amount, "of", energyType, "from", cell.Name
    def OpenSplit(self):
        # mark split territory
        for cell in [self.PresentInCell] + self.PresentInCell.Neighbors:
            cell.InSplitZoneFor.append(self)
    def ResolveSplit(self):
        self.PendingSplits = [cell for cell in self.PendingSplits if len(cell.InSplitZoneFor) == 1]
        for cell in self.PendingSplits:
            self.ChildCount += 1
            cell.EntityPresent = Entity(self.Team, self.Name + ":" + str(self.ChildCount), self.Universe)
            cell.EntityPresent.PresentInCell = cell
            self.Universe.entities.append(cell.EntityPresent)
        for energyType in self.Universe.energyTypes:
            totalCount = (len(self.PendingSplits) + 1)
            perDaughter = int(self.EnergyStores[energyType] / totalCount)
            remaining = self.EnergyStores[energyType] - totalCount*perDaughter
            self.EnergyStores[energyType] = perDaughter + remaining
            for cell in self.PendingSplits:
                cell.EntityPresent.EnergyStores[energyType] = perDaughter
        self.PendingSplits = []
    def Subsist(self):
        if self.Universe.DEBUG_SUBSIST: print self.Name,"Subsisting, neeed:",self.Universe.subsistEnergyRequirements," have:",self.EnergyStores
        survived = self.TrySubtractEnergy(self.Universe.subsistEnergyRequirements)
        if self.Universe.DEBUG_SUBSIST: print "...",self.Name," subsisted?",survived
        return survived
    def TrySubtractEnergy(self, energyRequirements):
        success = True
        tempEnergyStores = copy.deepcopy(self.EnergyStores)
        for (energyType, energyAmount) in energyRequirements:
            if not(energyType in tempEnergyStores):
                if self.Universe.DEBUG_ENERGY: print "no energy at all:", self.Name, energyType
                success = False
                break
            tempEnergyStores[energyType] -= energyAmount
            if tempEnergyStores[energyType] < 0:
                success = False
                if self.Universe.DEBUG_ENERGY: print "insufficent:", self.Name, energyType, energyAmount
                break
            elif self.Universe.DEBUG_ENERGY:
                print self.Name,energyType,">=0:", tempEnergyStores[energyType]
        if success:
            self.EnergyStores = tempEnergyStores
            return True
        else:
            return False
    def Discover(self):
        for (name, energyToExpend) in self.PendingDiscoveries:
            if self.Universe.DEBUG_DISCOVER: print self.Name, "trying to discover", name, energyToExpend
            if self.TrySubtractEnergy(energyToExpend):
                if self.Universe.DEBUG_DISCOVER: print "...energy expended"
                if not(name in self.Advancements.keys()):
                    self.Advancements[name] = (AddEnergyToDict(dict(), energyToExpend), False)
                else:
                    self.Advancements[name] = (AddEnergyToDict(self.Advancements[name][0], energyToExpend), self.Advancements[name][1])
                self.__Learn(name)
        self.PendingDiscoveries = []
    def Teach(self):
        for (name, energyToExpend, targetEntity) in self.PendingTeachings:
            if self.Universe.DEBUG_TEACH: print self.Name, "trying to teach", name, energyToExpend,'(*',self.TeachingMultiplier,")", "to", targetEntity.Name
            if not(self.Advancements.has_key(name)) or not(self.Advancements[name][1]): continue
            if self.TrySubtractEnergy(energyToExpend):
                if self.Universe.DEBUG_TEACH: print "...energy expended"
                if not(name in targetEntity.Advancements.keys()):
                    targetEntity.Advancements[name] = (AddEnergyToDict(dict(), energyToExpend, self.TeachingMultiplier), False)
                else:
                    targetEntity.Advancements[name] = (AddEnergyToDict(targetEntity.Advancements[name][0], energyToExpend, self.TeachingMultiplier), targetEntity.Advancements[name][1])
                targetEntity.__Learn(name)
        self.PendingTeachings = []
    def __Learn(self, name):
        if self.Advancements[name][1]: return # already applied!
        energySoFar = self.Advancements[name][0]
        (energyRequirements, prereqs, resultFunc) = self.Universe.Advancements[name]
        fail = False
        for (energyType,amount) in energyRequirements:    
            if not(energyType in energySoFar) or energySoFar[energyType] < amount:
                if self.Universe.DEBUG_LEARN: print "failed",energyType,amount
                fail = True
                break
        if fail: return
        if prereqs != None:
            for prereq in prereqs:
                if not(prereq in self.Advancements.keys()) or not(self.Advancements[prereq][1]):
                    if self.Universe.DEBUG_LEARN: print "failed",prereq
                    fail = True
                    break
            if fail: return   
        else:
            if self.Universe.DEBUG_LEARN: print "no prereqs for:", name
        self.Advancements[name] = (energySoFar, True)
        resultFunc(self)

    def Leach(self):
        print self.LeachingTargetRate
        for targetEntity in self.PendingLeachings[:self.LeachingTargetRate]:
            if self.Universe.DEBUG_LEACH: print self.Name, "trying to leach from", targetEntity.Name
            if self.PresentInCell.IsNStepsAwayFrom(targetEntity.PresentInCell, 1): continue # TODO: add leaching distance
            amountsToLeach = [(etype, max(0, self.LeachingPowers[etype] - targetEntity.LeachingDefenses[etype])) for etype in self.LeachingPowers.keys()]
            actuallyRemoved = targetEntity.__SubtractAsMuchAsAvailable(amountsToLeach)
            AddEnergyToDict(self.EnergyStores, actuallyRemoved, multiplierDict=self.LeachingEfficencies)
        self.PendingLeachings = []

    def __SubtractAsMuchAsAvailable(self, amounts):
        actualAmounts = []
        for (etype, amount) in amounts:
            available = self.EnergyStores[etype]
            if amount <= available:
                self.EnergyStores[etype] -= amount
                actualAmounts.append((etype,amount))
            else:
                self.EnergyStores[etype] = 0
                actualAmounts.append((etype,available))
        return actualAmounts

# ============ helper functions ============
def AddEnergyToDict(d, e, multiplier=1.0,multiplierDict=None):
    d = copy.deepcopy(d)
    for (energyType,amount) in e:
        factor = multiplier
        if multiplierDict:
            factor *= multiplierDict[energyType]
        if not(energyType in d.keys()):
            d[energyType] = amount*factor
        else:
            d[energyType] += amount*factor
    return d
