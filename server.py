import BaseHTTPServer
from universe import Universe
import json
from actions import Actions

universe = Universe()
universe.LoadNew('basic.config')

universeStates = {1: universe.ToJson()}

class AbstratRESTHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def respondJson(self, o=None, s=''):
        self.send_response(200)
        self.send_header("Content Type", "application/json")
        self.end_headers()
        if s == '':
            content = json.dumps(o)
        else:
            content = s
        self.wfile.write(content)
    def respondHtml(self, filename):
        self.respondContent(filename, "text/html")
    def respondJavascript(self, filename):
        self.respondContent(filename, "application/javascript")
    def respondContent(self, filename, contenttype):
        self.send_response(200)
        self.send_header("Content Type", contenttype)
        self.end_headers()
        f = open(filename)
        content = f.read()
        f.close()
        del f
        self.wfile.write(content)

    def do_GET(self):
        print "get request"
        pathParts = self.path.split("/")
        print pathParts
        if pathParts[1].lower() == 'timestep':
            if pathParts[2].lower() == 'latest':
                self.respondJson(o={'t':universe.t})
            else:
                self.send_error(404, "available timestep commands: latest")
        elif pathParts[1].lower() == 'cells':
            if pathParts[2].lower() == 'all':
                self.respondJson(o={'cells':[cell.ToDict() for cell in universe.cells]})
            else:
                self.send_error(404, "available cell commands: all")
        elif pathParts[1].lower() == 'universestate':
            timestep = int(pathParts[2])
            if universeStates.has_key(timestep):
                self.respondJson(s=universeStates[timestep])
            else:
                self.send_error(404, "timestep not available:"+str(timestep))
        elif pathParts[1].lower() == 'entities':
            responded = False
            for entity in universe.entities:
                if entity.Name.lower() == pathParts[2].lower():
                    self.respondJson(s=entity.ToJson())
                    responded = True
                    break
            if not(responded):
                print "not responded"
                self.send_error(404, "entity "+pathParts[2]+" not found")
        elif pathParts[1].lower() == "html":
            if pathParts[2].lower() == "celllayout.html":
                self.respondHtml("cellLayout.html")
            else:
                self.send_error(404, "unknown file:"+pathParts[2])
##for offline use
##        elif pathParts[1].lower() == "d3.js":
##            self.respondJavascript("d3.js")
        else:
            self.send_error(404)
            
    def do_POST(self):
        pathParts = self.path.split("/")
        print pathParts
        if pathParts[1].lower() == 'actions':
            timestep = int(pathParts[2])
            if timestep != universe.t:
                self.send_error(404, "incorrect timestep")
            else:
                team = pathParts[3].lower()
                if universe.AccountedFor(team):
                    self.send_error(404, "team already acted this timestep")
                else:
                    length = int(self.headers.getheader('content-length'))
                    actionJson = self.rfile.read(length)
                    actions = Actions.FromJson(actionJson, universe)
                    if universe.ActTryTimestep(actions, team):
                        universeStates[universe.t] = universe.ToJson()                
                    self.respondJson(o={'actionsSet':timestep})
        else:
            self.send_error(404)

if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080
    server = BaseHTTPServer.HTTPServer((HOST, PORT), AbstratRESTHandler)
    print "hosting at", HOST, ":", PORT
    server.serve_forever()
