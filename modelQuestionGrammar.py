# Python script to parse spatio-temporal modeling questions using a grammar of spatio-temporal experiments


from lark import Lark, tree
from rich import print
#import pydot

#Grammars:
footer= r'''

        %import common.ESCAPED_STRING -> STRING
        %import common.SIGNED_NUMBER -> NUMBER
        %import common.WS 
        %ignore WS
'''

conceptGrammar = '''
    amount : "interval of" magnitude | timeinterval | region | (("amount of")? ("(" spexperiment ")" | concept) ("s")?) | "sum of" ("the")? amount  
    concept : onec | twoc
    onec : object  | event | stuff | space | time | magnitude
    twoc : onec "pair" | "pair of" onec
    time : "time" 
    timeinterval : "interval of" time | "travel time" | "time of the year" | "year" | "month" | "day" | "hour" | "minute" | "second"
    tr : "before" | "after" | "during" | "at" | "in"
    space : "space" | "location" |  STRING
    region : "region" | "amount of" space | "area" 
    spr : "in" | "within" | "touching" | "overlapping" | "away from" | "west of" | "north of" | "south of"| "east of" | "at" | "between" | "close to" | STRING    
    compr : "larger than" | "less than" | "equal to" | "changed to" | "below" | "above" | STRING   
    magnitude : (quantified amount | "averaged" amount | "magnitude" | "temperature" | "duration" | "length" | "distance" | "height") ("in" unit)? 
    quantified : intensive | extensive
    intensive :  "proportional" | "proportion of" | "density of" ("the")? | "normalized"       
    extensive : "quantified" | "number of" | "capacity of" ("the")? | "production of" ("the")? | "duration of"
    object : person | "tree"| "lifestock" | "place" | "building" | "city" | "neighborhood" | "municipality" | "hospital" | "inhabitant" | "windmill" | "windfarm" | ("ethanol")? "consumer" | ("ethanol")? "producer" | "ambulance station" | "road intersection" | "language group" | "route" | "sensor"| "the world’s economy"|STRING
    person : "person"
    stuff :  "money" | "rain" | "soil"| "water" | "air pressure" | "noise" | "temperature" | "green" | "landcover" | "health" |  "energy"| "ethanol" | "cost" | "tax" | "CO2 emissions"| "NO2" | STRING
    event : "trip" | "period" | "earthquake" | "road accident" | "event" | STRING
    occurrence : process | state | act
    act : "make" | "measure" | "run" | "stay" | "cycle" | "throw" | "bake"
    process : "generate" | "stumble" | "rain"  | "grow" | "burn" | "flow" | "breathe" | "perceive"
    state : "stay" | "linger" | "rest" | "contain"
    
'''
nominatorGrammar = conceptGrammar + '''
    indicator : "this" | "that" | "some"
    nominator : temporalnominator | spatialnominator | objectnominator | indicator (concept | amount) | optimal amount | value | STRING  
    optimal : ("the")? ("maximal" | "minimal" | "maximum" | "minimum" | "closest" | "smallest" | "largest" | "shortest" | "first" | "last" | "final")  
    temporalnominator :  indicator (time| timeinterval | event) | "Christmas" | contemporaryreference | pastreference | futurereference | STRING    
    personnominator : "I" | "you" | "he" | "she" | STRING | indicator person
    objectnominator : "home" | STRING | indicator object | personnominator
    contemporaryreference : ("starting")? ("now" | "then" | "currently" | "at present" | "today" | "from now on" | "until now"|"this summer" | "at the end of the African humid period")
    pastreference : ("starting")? ("earlier" | "in the past" | NUMBER "years ago" | "last week" | "yesterday")
    futurereference : ("starting")? ("in the future" | "later"   | "in 2030" | "tomorrow" | "from now on" | "in 20 years"|"this summer")
    spatialnominator :  indicator (space | region) | STRING
    value : NUMBER unit | "infinite" unit | STRING  | NUMBER | "halved" | relativechange
    unit : "minutes" | "kilometers" | "meters" | "R/l" | "liters" | "C" | "µg/m³" | "decibel"
    relativechange : ("increased"|"decreased"|"doubled"|"halved"|"reduced") ("by" NUMBER ("percent")?)?
    nomlist : nomlist nominator | nominator
    
'''
situationGrammar = nominatorGrammar +'''
    situation : (personnominator)? action | (nominator)? happening 
    do : "do"("es")?
    kappa : "is" | "are"
    preposition : "at" | "in" | "on" |"to"
    epsilon : "is"
    attribution : nominator epsilon object
    appredicator : (outcome)?  (means)?  (preposition nominator)?    
    outcome : nomlist
    means : "with" nomlist
    performance : ("at")? (temporalnominator)? do |  time (personnominator) do 
    action : performance  act ("ing")? (appredicator)? | actionwithgoal
    generativegoal : "such that" (attribution)
    modificativegoal :  "such that" (situation)
    goal : generativegoal | modificativegoal
    generativeaction : performance   (act ("ing")?)? (appredicator)? generativegoal
    modificativeaction : performance   (act ("ing")?)? (appredicator)? modificativegoal 
    actionwithgoal : generativeaction |  modificativeaction
    happening : ("at")? temporalnominator kappa (state|process) ("ing")? (appredicator)? | time (nominator) kappa (state|process) ("ing")?    
'''
spatialExperimentGrammar = situationGrammar + r'''    
    spexperiment: processexperiment | (measure)+ (control)* (fix)* 
    measure : nominator | concept | amount            
    control : temporalcontrol | ("for" | "from" | "to" | "of" | spr) ("each"|"some")? (concept | amount | situation)
    temporalcontrol : ("for" | "from" | "to" | "of" | spr) ("each"|"some")? time       
    fix : tr temporalnominator | spr spatialnominator | "if" situation | ("for" | "from" | "to" | "of" | spr) nominator | compr value | value | "with" optimal amount     
    processexperiment : (measure)+ temporalcontrol (fix)*
'''
questionGrammar =  spatialExperimentGrammar + r'''
    question :  (contemporary | prediction | retrodiction | projection | retrojection) ("?")?    
    factualcondition : spexperiment ("is"|"are"|"was"|"were"|"to be"|"being") ("such and such"| optimal | fix)  contemporaryreference 
    counterfactualcondition : spexperiment ("was"|"were") ("such and such"| optimal | fix) contemporaryreference 
    projectedcondition : spexperiment ("will be"|"being") ("such and such"| optimal | fix) futurereference 
    simplemodel : spexperiment (contemporaryreference)?
    transformationmodel : spexperiment contemporaryreference "given that" ("the")?  factualcondition
    contemporary : "What" ("is"|"are") ("the")? (simplemodel|transformationmodel) 
    prediction : "What" "will be" ("the")? spexperiment futurereference "given that" ("the")?  factualcondition 
    retrodiction : "What" "could have been" ("the")? spexperiment pastreference ("given that" | "causing") ("the")? factualcondition 
    projection : "What" "would be" ("the")? spexperiment futurereference ("if"|"when") ("the")? counterfactualcondition 
    retrojection : "What" "should" ("have")? ("be"|"been") ("the")? spexperiment contemporaryreference ("so"|"such") "that" ("the")? projectedcondition
    '''


def make_png(filename,parser, sentence):
        tree.pydot__tree_to_png(parser.parse(sentence), filename)


def make_dot(filename,parser, sentence):
        tree.pydot__tree_to_dot(parser.parse(sentence), filename)

def get_variable_name(variable):
    for name in globals():
        if id(globals()[name]) == id(variable):
            return name
    for name in locals():
        if id(locals()[name]) == id(variable):
            return name
    return None
def parsetrees(parser, questions):
        cnt = 0
        for e in questions:
                cnt += 1
                print(e)
                print(parser.parse(e).pretty())
                #print(parser.parse(e))
                #make_png("ModelQuestions/parseTrees/"+str(get_variable_name(questions))+str(cnt) + ".png", parser, e)
                #make_dot("ModelQuestions/parseTrees/"+str(get_variable_name(questions)) + str(cnt) + ".gv", parser, e)

l_sit = Lark(spatialExperimentGrammar + footer
        ,parser='earley', start='situation', keep_all_tokens=True)
situations = ['he now does run',
                'time she is growing'
              ]

parsetrees(l_sit ,situations)

l_spEx = Lark(spatialExperimentGrammar + footer
        ,parser='earley', start='spexperiment', keep_all_tokens=True)

experiments = [
'proportional amount of (space of green) for each neighborhood in "Amsterdam"',
'quantified amount of (space of green) in kilometers for each neighborhood in "Amsterdam"',
'averaged amount of (space of building) for each neighborhood in "Amsterdam"',
'averaged amount of (quantified amount of height of building) for each neighborhood in "Amsterdam"',
'averaged amount of (quantified amount of green for each location) for each neighborhood in "Amsterdam"',
'proportional amount of (space of green north of "Ij") for each neighborhood in "Amsterdam"',
'number of (building of height larger than 5 meters) for each neighborhood in "Amsterdam"',
'quantified amount of (time to hospital with minimal quantified amount of time) from each building in "Rotterdam"',
'sum of amount of (energy for each windmill) for windfarm',
'location for each windmill of this windfarm',
'space of each municipality',
'time before this earthquake',
'amount of trees in "Utrecht"',
'averaged amount of (magnitude of earthquake) in "Amsterdam"',
'largest amount of money of each municipality',
'tomorrow for each day in this year',
'amount of time if he now does run home',
'(location for each time) if he now does run home',
'amount of trees if he then is perceiveing'
]

parsetrees(l_spEx,experiments)


l_questions = Lark(questionGrammar  + footer
        ,parser='earley', start='question', keep_all_tokens=True)
testquestions=[
'What should be the amount of green for each neighborhood in "Amsterdam" now so that the proportional amount of NO2 will be below 20 µg/m³ this summer?',
'What should be the location for each windmill of windfarm now so that the sum of amount of (energy for each windmill) for this windfarm will be maximal in the future?',
'What would be the sum of the amount of (capacity of the amount of ethanol for each producer) for "Brazil" in 2030 if the proportional amount of (tax of amount of ethanol for each consumer) of "Brazil" was equal to 1.23 R/l from now on ?',
'What would be the averaged amount of (ethanol for each consumer) for "Brazil" in 2030 if the proportional amount of (tax of amount of ethanol for each consumer) of "Brazil" was equal to 1.23 R/l from now on?',
'What could have been the density of amount of lifestock for each location in "Sudan" 10.000 years ago given that the landcover for each location in "Sudan" was equal to "arid land" at the end of the African humid period?',
'What is the proportional amount of space of green for each neighborhood in "Amsterdam" now?',
'What would be the proportional amount of space of green for each neighborhood in "Amsterdam" in the future if the quantified amount of building was such and such now?',
'What should be the proportional amount of space of green for each neighborhood in "Amsterdam" now such that the quantified amount of health for each inhabitant will be such and such in the future?',
]

#These are the questions used in the paper:
questions =[
'What is the shortest (time to ambulance station from each building) in "Rotterdam" at present?',
'What is the temperature for each location in "Utrecht" now given that the temperature for each (location of sensor) is such and such now?',
'What will be the temperature in "Utrecht" tomorrow given that the temperature in "Utrecht" is 5 C today?',
'What could have been the event in "Utrecht" yesterday causing the proportional amount of water for soil in "Utrecht" being 0.3 today?',
'What would be the temperature in "Utrecht" in 20 years if the proportional amount of CO2 emissions of the world’s economy were halved today?',
'What should be the amount of green in "Utrecht" today so that the maximal temperature for each location in "Utrecht" will be below 30 C this summer?',

'What is the closest ambulance station for each building in "Rotterdam" at present given that the location of each ambulance station is such and such now?',
'What will be the time to each building from the closest ambulance station in "Rotterdam" from now on given that the location of each ambulance station is such and such now?',
'What will be the sum of the amount of rain for each location in "Dortmund" tomorrow given that the air pressure temperature for each location in "Germany" is such and such now?',
'What could have been the event for each road intersection pair in "Rotterdam" last week causing the travel time of this ambulance station to this road accident in "Rotterdam" to be 30 minutes now?',
'What could have been the route for each language group in "the Amazon" starting 15.000 years ago causing the location of each language group to be such and such at present?',
'What would be the travel time to each building from the closest ambulance station in "Rotterdam" in the future if the travel time between this road intersection pair was infinite minutes from now on?',
'What would be the sum of the production of ethanol for each producer in "Brazil" in 2030 if the proportional amount of (tax for ethanol) for each consumer in "Brazil" was equal to 1.23 R/l from now on',
'What should be the location of ambulance stations in "Rotterdam" now such that the travel time to each building from the closest ambulance station will be less than 14 minutes in the future?',
'What should be the location for each windmill of this windfarm now so that the sum of the (amount of energy for each windmill of this windfarm) will be maximal in the future?'
]
#parsetrees(l_questions,questions)

questions_caspar=[
'What is the averaged (quantified amount of NO2 for each (location of some sensor)) for each year in "Amsterdam" now?',
'What is the amount of space for each (interval of quantified noise in decibel) in "Amsterdam" now?',
'What is the location magnitude interval of time duration of each earthquake in "Amsterdam" until now?',
'What is the location height of each tree in "Amsterdam" now?',
'What is the amount of space for each (interval of quantified amount of cost) for each year after "2002" in "Amsterdam" now?'
]

#parsetrees(l_questions,questions_caspar)

questions_roelof=[
    #Process questions
'What is the final (location for each time) if he then does run home?',
'What is the amount of trees for each time he does run home?',
'What is the amount of trees for each trip?',
'What is the duration of (interval of time if he now does cycle home)?',
'What is the duration of time he does cycle home?',
'What is the duration of (amount of time if he does run home)?'
]
parsetrees(l_questions,questions_roelof)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

