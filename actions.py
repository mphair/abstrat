import json

# TODO:
#  * move dict creation from FromJson to universe
#  * add some sort of hash and game-timestamp for verification purpose

class Actions:
    def __init__(self, universe):
        self.universe = universe
        self.PendingMoves = []
        self.PendingSplits = []
        self.PendingDiscoveries = []
        self.PendingTeachings = []
        self.PendingLeachings = []
    def extend(self, actions):
        self.PendingMoves.extend(actions.PendingMoves)
        self.PendingSplits.extend(actions.PendingSplits)
        self.PendingDiscoveries.extend(actions.PendingDiscoveries)
        self.PendingTeachings.extend(actions.PendingTeachings)
        self.PendingLeachings.extend(actions.PendingLeachings)

    def ToJson(self):
        return json.dumps({
            'pendingDiscoveries': [(entity.Name, advName, energyExpend) for (entity, advName, energyExpend) in self.PendingDiscoveries],
            'pendingTeachings': [(entity.Name, advName, energyExpend, target.Name) for (entity, advName, energyExpend, target) in self.PendingTeachings],
            'pendingLeachings': [(entity.Name, target.Name) for (entity,target) in self.PendingLeachings],
            'pendingMoves': [(entity.Name, cell.Name) for (entity,cell) in self.PendingMoves],
            'pendingSplits': [(entity.Name, cell.Name) for (entity,cell) in self.PendingSplits]})
    @staticmethod
    def FromJson(jsonString, universe):
        actions = Actions(universe)
        d = json.loads(jsonString)

        # these name -> cell or entity maps should
        #  be maintained by the universe as cells
        #  and entities are created and destroyed.
        #  It should be the only thing that creates
        #  or destroys them so that this is possible.
        cellDict = dict()
        for cell in universe.cells:
            cellDict[cell.Name] = cell
        entityDict = dict()
        for entity in universe.entities:
            entityDict[entity.Name] = entity

        actions.PendingDiscoveries = [(entityDict[ename], advName, energyExpend) for (ename, advName, energyExpend) in d['pendingDiscoveries']]
        actions.PendingTeachings = [(entityDict[ename], advName, energyExpend, entityDict[targetName]) for (ename, advName, energyExpend, targetName) in d['pendingTeachings']]
        actions.PendingLeachings = [(entityDict[ename], entityDict[tname]) for (ename, tname) in d['pendingLeachings']]
        actions.PendingMoves = [(entityDict[ename], cellDict[cname]) for (ename, cname) in d['pendingMoves']]
        actions.PendingSplits = [(entityDict[ename], cellDict[cname]) for (ename,cname) in d['pendingSplits']]

        return actions

    def DoDiscover(self):
        for (entity, advName, energyToExpend) in self.PendingDiscoveries:
            if self.universe.DEBUG_DISCOVER: print "DoDiscover:", entity.Name, advName, energyToExpend
            entity.PendingDiscoveries.append((advName, energyToExpend))
        # don't do these (stuff above, below) at the same time, might be more than one entry for an entity in the list above    
        for entity in self.universe.entities:
            entity.Discover()

    def DoTeach(self):
        for (entity, advName, energyToExpend, target) in self.PendingTeachings:
            if self.universe.DEBUG_TEACH: print "DoTeach:", entity.Name, advName, energyToExpend, target.Name
            entity.PendingTeachings.append((advName, energyToExpend, target))
        # don't do these (stuff above, below) at the same time, might be more than one entry for an entity in the list above    
        for entity in self.universe.entities:
            entity.Teach()
        
    def DoMove(self):
        for (entity, cell) in self.PendingMoves:
            entity.PendingMoves.append(cell)
        # don't do these (stuff above, below) at the same time, might be more than one entry for an entity in the list above    
        for entity in self.universe.entities:
            entity.InitMoves()

        while (True):
            if (self.universe.DEBUG_MOVE): print "moving..."
            anyAttempts = any([entity.OpenMove() for entity in self.universe.entities])
            if not(anyAttempts): break
            for cell in self.universe.cells:
                cell.FailBadMoves()
            for cell in self.universe.cells:
                cell.ExecuteGoodMoves()
            for entity in self.universe.entities:
                entity.CloseMove()

    def DoGather(self):
        for cell in self.universe.cells:
            cell.PrepareGather()
        for entity in self.universe.entities:
            entity.OpenGather()
        for entity in self.universe.entities:
            entity.ResolveGather()

    def DoSplit(self):
        for (entity, cell) in self.PendingSplits:
            entity.PendingSplits.append(cell)
        for entity in self.universe.entities:
            entity.OpenSplit()
        for entity in self.universe.entities:
            entity.ResolveSplit()
        for cell in self.universe.cells:
            cell.InSplitZoneFor = []

    def DoSubsist(self):
        results = [(entity, entity.Subsist()) for entity in self.universe.entities]
        if (self.universe.DEBUG_SUBSIST): print results
        for (entity, survived) in results:
            if not(survived):
                self.universe.entities.remove(entity)
                entity.PresentInCell.EntityPresent = None
                del entity

    def DoLeach(self):
        for (entity, target) in self.PendingLeachings:
            entity.PendingLeaches.append(target)
            if self.universe.DEBUG_LEACH: print "DoLeach:", entity.Name, target.Name
            entity.PendingLeachings.append(target)
        # don't do these (stuff above, below) at the same time, might be more than one entry for an entity in the list above    
        for entity in self.universe.entities:
            entity.Leach()
