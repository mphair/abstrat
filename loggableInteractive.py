from universe import Universe

class LoggableInteractive:
    def PlayerShow(self, command, currentEntity):
        for x in range(10):
            for y in range(10):
                cell = self.universe.cells[x*10+y]
                if cell.EntityPresent:
                    if cell.EntityPresent == currentEntity:
                        print "#",
                    else:
                        print cell.EntityPresent.Name[0],
                else:
                    print ".",
            print "" # to get next line
        print "="*10
        print currentEntity
        return True

    def PlayerDiscover(self, command, currentEntity):
        self.universe.actions.PendingDiscoveries.append((currentEntity, command[1], ((command[2],int(command[3])),)))
        return True
    def PlayerTeach(self, command, currentEntity):
        # this really needs to move into Universe
        target = None
        for entity in self.universe.entities:
            if command[4] == entity.Name.lower():
                target = entity
                break
        if target == None:
            print 'unknown entity'
        else:
            self.universe.actions.PendingTeachings.append((currentEntity, command[1], ((command[2],int(command[3])),), target))
        return True
    def PlayerMove(self, command, currentEntity):
        self.universe.actions.PendingMoves.append((currentEntity, self.universe.cells[int(command[1])*10+int(command[2])]))
        return True
    def PlayerSplit(self, command, currentEntity):
        self.universe.actions.PendingSplits.append((currentEntity, self.universe.cells[int(command[1])*10+int(command[2])]))
        return True
    def AdvancementsShow(self, command, currentEntity):
        print self.universe.Advancements
        return True
    def BudgetShow(self, command, currentEntity):
        print "subsist:", self.universe.subsistEnergyRequirements
        print "move:", self.universe.moveEnergyRequirements
        print "local energy:", self.CalculateLocalEnergy(currentEntity)
        return True
    def PlayerDebug(self, command, currentEntity):
        if command[1] == 'e':
            self.universe.DEBUG_ENERGY = not(self.universe.DEBUG_ENERGY)
            print self.universe.DEBUG_ENERGY
        return True
    def PlayerSave(self, command, currentEntity):
        filename = command[1]
        jsonString = self.universe.ToJson()
        f = open(filename, 'w')
        f.write(jsonString)
        f.close()
        return True
    def PlayerLoad(self, command, currentEntity):
        filename = command[1]
        f = open(filename, "r")
        jsonString = f.read()
        f.close()
        self.universe.ReinitFromJson(jsonString)
        self.restartLoop = True
        return False

    def CalculateLocalEnergy(self, currentEntity):
        return [(energyType,sum([cell.EnergyFunctions[energyType](None) for cell in [currentEntity.PresentInCell]+currentEntity.PresentInCell.Neighbors])) for energyType in self.universe.energyTypes]
            
    def VisualLoop(self):
        self.universe = Universe()
        self.universe.LoadNew("basic.config")
        self.restartLoop = False
        playing = True
        while (playing):
            for currentEntity in self.universe.entities:
                command = []
                self.PlayerShow(command, currentEntity)
                while ((len(command) == 0 or not(command[0] in ("d","done"))) and playing):
                    command = raw_input("> ").lower().split(" ")
    ##                    '?': ShowHelp, _
    ##                    'help': ShowHelp, _
                    try:
                        playing = {
                            'quit': lambda a,b: False, 
                            'exit': lambda a,b: False, 
                            'q': lambda a,b: False, 
                            'd': lambda a,b: True,  # done
                            'done': lambda a,b: True,          
                            'move': self.PlayerMove, 
                            'split': self.PlayerSplit, 
                            'show': self.PlayerShow,
                            'budget': self.BudgetShow,
                            'debug': self.PlayerDebug,
                            'save': self.PlayerSave,
                            'load': self.PlayerLoad,
                            'ashow': self.AdvancementsShow,
                            'discover': self.PlayerDiscover,
                            'teach': self.PlayerTeach,
                        }[command[0]](command, currentEntity)
                    except KeyError:
                        print "unknown command"
                if not(playing): break
            if not(playing):
                if self.restartLoop:
                    self.restartLoop = False
                    playing = True
            else:
                self.universe.DoTimeStep()
                print "="*10,"time:",self.universe.t,"="*10

if __name__=='__main__':
    LoggableInteractive().VisualLoop()
