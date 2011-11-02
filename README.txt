This has been under development for a couple of weeks locally with backups rather than proper source control.
And, suprise suprise, this document is already out of date. In particular, the whole notion of "taking time"
doesn't really exist any longer.  Each action is independently limited in how many instances of it
an entity can take during a turn. There are more activities now, and some are missing. And they are called actions.

Update this further when everything stabilizes.  No, really. ;)


TODO: CONSIDER UNLIMITING ACTIVITIES... CAN SPLIT AND MOVE AND DISCOVER ALL ON SAME TURN BUT JUST
 NEED TO HAVE THE ENERGY TO DO SO

universe:
* N types of energy
 * N can vary, >1
 * n1 
  * in most universes, completely pervasive at low levels (see baseline energy distribution discussion below)
  * can be used for any activity
 * n2,n3,..,nX 
 * energy types can be converted... conversion rates are per universe and not uniform
 * n2+ vary in use and distribution per universe
* Universe starting state consists of:
 * available advancements
 * energy distrubtions and uses 
 * initial entity properties:
  * count
  * placement
  * advancements

Entity:
* occupies one physical cell in the universe
* can always gather n1 present in current cell and all neighboring cells when not challenged
* with advancements can gather n2+, from cells further away, and against challenges 
* can store energy up to some threshold per energy type (which can be increased with advancements)
 * energy above threshold at end of turn is lost to friction

Activity:
 Activities require some mix of time and energy. Multiple actions can be taken simultaneously, if the
   time to do them can be made fractional, but some have restrictions on partial completion. Advancements
   can allow different actions to be taken as a unit for lower cost, such as discover/teach or split/teach 
   or move/teach. All entities take actions during a time step simultaneously, but the order resolved is:
   gather, split, transfer, discover, teach, unlearn, move, subsist
    * reasons: 
     * gather first so energy is available on current turn 
     * move near last so energy gathering is known for turn to players at least in terms of physical location of entities 
     * subsist after everything else
     * split near beginning so that split/teach is possible
     * unlearn after teach so pre-emptive unlearning can be used as block
     * discover before teach so that discovery networks can be set up
* subsist
 * n1 required per time unit, per universe
 * does not take any time to perform
 * no advancement can block or change this requirement
 * unable to perform action -> removed from universe
* move 
 * base rate of 1 cell per time unit (changed by advancements)
 * depending on universe, might require some amount of some type of energy, per distance, can be changed by advancements
 * cannot move fractional cells per time unit
 * all moves are resolved one cell at a time, regardless of how long total movement is. if there is already an entity in
   a cell that an entity wants to move into, it will lose that piece of movement (but the last movement is removed
   from the movement chain, so that you don't have a move two forward one to right become move one forward and one 
   to the right. It is simply as if the entity had one fewer movement available.) if multiple entities want to
   move into the same cell, none of them will move and will lose that piece of movement. Thus, if two entites arrive at
   an impass, the one with more movements allocated will get to finish more of their movement. this will have the side
   effect that entities cannot march in a line, because they will not be able to move into a place where another
   entity was, even if that entity will no longer be there.  Energy is expended either way. 
   (maybe eventually have some sort of entity-based property that determines prescedence in movement so that 
   *someone* gets to move?)    
* split (create entity in another cell, split energy between self and new)
 * base cell must be neighbor
 * base energy is split evenly (remainder to splitter), minus per-universe split tax, can be changed by advancements 
 * no advancements are transfered
 * base rate of 1 split per time unit, can change with advancements
 * cannot split fractionally per time unit
 * cannot split into another entity's zone of possible split places (maybe eventually allow this with a breeding mechanic?)
* discover (learn advancements without a teacher)
 * base rate: something like 10 units of energy? (maybe only certain types of energy, per universe?), can be changed by advancements
 * base rate: one time unit per aggregate depth of advancement, can be changed by advancements
 * can discover advancements fractionally, but they do not activate until fully discovered
* teach (copy advancements)
 * base rate: one time unit per aggregate depth of advancement, can be changed by advancements
 * base: target (learner) must be neighbor, can be changed by advancements
 * base: no energy required, can be changed by advancements (e.g. negative ones)
 * required advancements must be taught to target first
 * target does nothing in process and cannot stop from learning
* unlearn
 * base: not available
 * advancements can allow negative learning of advancements in reverse order of order they must be learned
* gather (energy)
 * automatic action
 * no energy cost (defeats purpose ;)
 * no time cost
 * "gather efficency" per energy type
  * [0,1]
  * n0 base: 0.5? (can be changed with advancements)
  * n2+ base: 0 (can be changed with advancements)
  * base distance: neighbors only (can be changed with advancements, per energy type)
 * if two or more entities lay claim to a cell for energy gathering, result is determined thusly:
  * if sum of efficencies <= 1, then everyone gets full amount
  * if sum of efficencies > 1, then each entity's amount is scaled by the the sum.
  * example:
   * A has 0.3 claim, B has 0.4 claim, and C has 0.5 claim
   * If A claims alone, A gets 0.3 of available energy
   * If B claims alone, B gets 0.4 of available energy
   * If A and B claim together, A gets 0.3 and B gets 0.4
   * If A and C claim together, A gets 0.3 and C gets 0.5
   * If A and B and C claim together, A gets 0.3/1.2, B gets 0.4/1.2, and C gets 0.5/1.2
* transfer (energy)
 * no time cost (i.e. entities can form a power line)
 * base: 50%(?) transfer efficency, per energy type (can be changed with advancements) 

Advancements:
 * some advancements require other advancements (creating an acyclic directed advancement graph)
 * aggregate depth: minimum number of advancements required to get an advancement 
 * all advancements alter the rate, cost, efficency, or distance of something.  when they make a new action available, 
   they are simply changing something like cost or efficency from infinite or zero, etc.
 * advancements can be negative, and can be taught aggresively
 * having certain advancements can block the learning of other advancements


********************
Let's determine some simple possible universes
* Hex grid of cells
 * Only n1. distribution: 1/cell/time unit
 * subsistance rate is 5 n1 / time unit
 * splitting tax is 1 n1, rate 1 split / time unit
 * movement is 1 n1
 * storage is 6 n1
 * gather efficency is 1.0 n1
 * transfer efficency is 0 (no transfers)
 * no advancements, so no discover/teach/unlearn
* Quad grid of cells, 4-neighbors are connected, not 8-neighbors.
 * Only n1. distribution: 1/cell/time unit
 * subsistance rate is 3 n1 / time unit
 * movement is 1 n1
 * storage is 4 n1
 * gather efficency is 1.0 n1
 * transfer efficency is 0 (no transfers)
 * no advancements, so no discover/teach/unlearn

