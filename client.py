import httplib
from universe import Universe
import time
import json

class AbstratRESTClient:
    def __init__(self):
        self.__post_headers = {"Content-type": "application/json", "Accept": "application/json"}

    def PlayerShow(self, command, currentEntity):
        if len(command) == 2:
            for entity in self.universe.entities:
                if entity.Name.lower() == command[1].lower():
                    currentEntity = entity
                    break
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
    PlayerShow.Help = "show [ent] - shows map and info for entity ent or current entity if ent is empty"

    def PlayerDiscover(self, command, currentEntity):
        self.universe.actions.PendingDiscoveries.append((currentEntity, command[1], ((command[2],int(command[3])),)))
        return True
    PlayerDiscover.Help = "discover advancement energyType amount - spend amount of energyType towards advancement. use showadv to list advancements."

    def ShowAdv(self, command, currentEntity):
        for name,info in self.universe.Advancements.items():
            print name,"requires energy:",info[0], "and adv:", info[1]
        return True
    ShowAdv.Help = "showadv - show advancements"
    
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
    PlayerTeach.Help = "teach advancement energyType amount target - spend amount of energyType towards advancement for entity target."
    
    def PlayerMove(self, command, currentEntity):
        self.universe.actions.PendingMoves.append((currentEntity, self.universe.cells[int(command[1])*10+int(command[2])]))
        return True
    PlayerMove.Help = "move y x - move to (x,y)... yes, they are switched, sorry."
    
    def PlayerSplit(self, command, currentEntity):
        self.universe.actions.PendingSplits.append((currentEntity, self.universe.cells[int(command[1])*10+int(command[2])]))
        return True
    PlayerSplit.Help = "split y x - split new entity into (x,y)... yes, they are switched, sorry."
    
    def BudgetShow(self, command, currentEntity):
        print "subsist:", self.universe.subsistEnergyRequirements
        print "move:", self.universe.moveEnergyRequirements
        print "max local energy:", self.CalculateLocalEnergy(currentEntity)
        return True
    BudgetShow.Help = "budget - show notes about the expected energy buget"
    
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

    def GetUniverseFromServer(self):
        conn = httplib.HTTPConnection(self.serverAddress,port=self.port)
        conn.request("GET", "/universeState/"+str(self.t))
        response = conn.getresponse()
        if response.status != 200:
            print response.status
            print response.reason
            print response.read()
            raise "out of sync?"
        jsonString = response.read()
        self.universe = Universe.FromJson(jsonString)

    def PostActionsToServer(self):
        jsonString = self.universe.actions.ToJson()
        conn = httplib.HTTPConnection(self.serverAddress,port=self.port)
        conn.request("POST", "/actions/"+str(self.t)+"/"+self.Team, jsonString, self.__post_headers)
        response = conn.getresponse()
        if response.status != 200:
            print response.status
            print response.reason
            print response.read()
            raise "sadface"

    def PollForNewTime(self, takeWhatever=False):
        while (True):
            conn = httplib.HTTPConnection(self.serverAddress,port=self.port)
            conn.request("GET", "/timestep/latest")
            response = conn.getresponse()
            if response.status != 200:
                print response.status
                print response.reason
                print response.read()
                raise "sadface"
            newT = int(json.loads(response.read())['t'])
            
            if takeWhatever or newT == self.universe.t+1:
                self.t = newT
                return
            elif t < newT:
                raise "t on server is "+str(newT)+" -- we're looking for "+str(t)
            time.sleep(10) # wait ten seconds
            print "...still waiting for other player"

    def GetCommands(self):
        commands = {
            'exit': lambda a,b: False, 
            'd': lambda a,b: True,  # done
            'move': self.PlayerMove, 
            'split': self.PlayerSplit, 
            'show': self.PlayerShow,
            'budget': self.BudgetShow,
#            'debug': self.PlayerDebug,
#            'save': self.PlayerSave,
#            'load': self.PlayerLoad,
            'showadv': self.ShowAdv,
            'discover': self.PlayerDiscover,
            'teach': self.PlayerTeach,
            '?': self.ShowHelp,
        }
        commands['exit'].Help = "exit - quit the game"
        commands['d'].Help = "d - done with this entity"
        return commands

    def ShowHelp(self, command, currentEntity):
        if len(command) == 1:
            print self.GetCommands().keys()
        if len(command) == 2:
            forCommand = command[1].lower()
            if self.GetCommands().has_key(forCommand):
                try:
                    print self.GetCommands()[forCommand].Help
                except:
                    print "no help for", forCommand
        return True
    ShowHelp.Help = "? [command] - show help for command or list commands if command is empty"
    
    def Play(self, serverAddress, port, team):
        self.serverAddress = serverAddress
        self.port = port
        self.PollForNewTime(True)
        self.Team = team
        self.restartLoop = False
        playing = True
        while (playing):
            self.GetUniverseFromServer()
            print "="*10,"time:",self.universe.t,"="*10
            myEntities = [entity for entity in self.universe.entities if entity.Team.lower() == self.Team.lower()]
            if len(myEntities) == 0:
                print "You have no more entities"
                self.PlayerShow(None, None)
                raw_input("press enter to quit...")
                break
            for currentEntity in myEntities:
                command = []
                self.PlayerShow(command, currentEntity)
                while ((len(command) == 0 or not(command[0] in ("d","done"))) and playing):
                    command = raw_input("> ").lower().split(" ")
                    try:
                        playing = self.GetCommands()[command[0]](command, currentEntity)
                    except KeyError:
                        print "unknown command"
                if not(playing): break
            if not(playing):
                if self.restartLoop:
                    self.restartLoop = False
                    playing = True
            else:
                self.PostActionsToServer()
                print "waiting for other players..."
                self.PollForNewTime()    

if __name__=='__main__':
    serverAddress = raw_input("server address? ")
    port = raw_input("port? ")
    team = raw_input("team you are playing? ")
    AbstratRESTClient().Play(serverAddress, port, team)
