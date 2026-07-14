# Python script to parse spatio-temporal modeling questions using a grammar of spatio-temporal experiments


from lark import Lark, tree
from rich import print

import pydot
import os

#Grammars:
footer= r'''
        %import common.ESCAPED_STRING -> STRING
        %import common.SIGNED_NUMBER -> NUMBER
        %import common.WS 
        YEAR: /[0-9]{4}/
        DATE: /[a-zA-Z]+ [0-9]{1,2}, [0-9]{4}/
        %ignore WS
'''

identitydomainGrammar = '''
    identityconcept : object | event | time | space | occurrence
    object : place | living | socialobject | functionalobject |  STRING
    person : "inhabitant" | "person" | "passenger" | (stuff)? "consumer" | (stuff)? "producer"
    plant : "tree" | "plant" | animal
    animal : "lifestock" | "species" | "animal" | person
    living : plant
    socialobject :  group | organisation 
    group : "language group" | "group"
    organisation : "institution" | "association" | "community"   
    functionalobject : "solarpanel" | "windmill" | "windfarm" | "road intersection" |  "road" | "sensor" | "tram line" | "metro line" 
    place : "route" | "forest" | "path" | "area" | "place" | "place of worship" | "house" | "building" | "settlement" | "city" | "neighborhood" | "municipality" | "hospital" | "ambulance station" | "address" | ("postcode " NUMBER " area") | "postcode identifier" | "territory" 
    event : "trip" | "period" | "earthquake" | "road accident" | "event" | STRING
    time : "time" 
    tr : "before" | "after" | "during" | "on" | "in"
    space : "space" | "location" |  STRING
    spr : "in" | "within" | "touching" | "overlapping" | "away from" | "west of" | "north of" | "south of"| "east of" | "at" | "between" | "close to" | "around" | STRING    
    compr : "larger than" | "less than" | "equal to" | "changed to" | "below" | "above" | STRING 
    occurrence : process | state | action
    state : "state"
    process : flow | movement    
    flow : "flow"
    movement : "movement" 
    action : "action" 
'''
amountGrammar = identitydomainGrammar + '''
    portion : stuff | amountofobjects
    amount :  stuff | set | "sum of" ("the")? amount
    stuff : ("amount of" | "production of")? ("the")? (material | energy | value |  "exposure" | "weather" | "crop management practice" | "conservation measure" | STRING)
    material : "forest" | "canopy" | "rain" | "soil" | "water" | "green" | "landcover" | "CO2 emissions"| "NO2" | "ethanol" | "soil conditions" | "soil loss" | "wheat yield" | STRING
    value : "money" | "cost" | "tax" | "labour cost" | "health" | STRING
    energy : "temperature" | (STRING? "energy") | "noise" | "heat" | "air pressure"       
    set : ("interval of" linearquantity) | timeinterval | region | amountofobjects | (("amount of" | "set of")? ("(" spexperiment ")" | identityconcept) ("s")?)
    amountofobjects : (("amount of")? object ("s")?) | "population" | "amount of people"
    timeinterval : "interval of" time | "travel time" | "time of the year" | "year" | "month" | "day" | "hour" | "minute" | "second"
    region : "region" | "amount of" space | "area" | "grid cell"      
'''
quantityGrammar = amountGrammar + '''
    linearquantity : (magnitude | proportion | ("averaged" set) ) ("in" unit)?     
    magnitude : numberof | areaof | durationof | measurement | (("magnitude of" | "quantified" | "capacity of" | "size of") ("the")? amount) |  (amount ("magnitude" | "size" ) ("s")?) | "magnitude" 
    measurement : "number" | "temperature" | "duration" | "length" | "distance" | "height" | "housing price" | (STRING? "area")
    numberof : ("number of" | "size of") ("the")? set |  set ("count" | "number")
    areaof : ("area of" | "size of") ("the")? region
    durationof : ("duration of") ("the")? (timeinterval | event)
    proportion :  monolithic | heterolithic
    monolithic : continuousshare | discreteshare
    continuousshare :  ("proportional" | "proportion of" | "fraction of" | "share of") stuff | stuff
    discreteshare :  ("proportional" | "proportion of" | "fraction of" | "share of") set
    heterolithic : density | power | ppobject | ppunit | "speed" | "tempo" | "power"
    density : "density of" ("the")? amount ("per" region)?
    power : energy "per" timeinterval 
    ppobject : magnitude "per" object 
    ppunit : magnitude "per" unit     
'''
predicatorGrammar = quantityGrammar + '''
    predicator : pair | event | occurrence | thing | linearquantity   
    pair : identityconcept "pair" | "pair of" identityconcept
    thing : endurant | time | space | amount 
    endurant : object | portion       
'''
nominatorGrammar = predicatorGrammar + '''
    nominator : objectnominator | eventnominator | amountnominator | temporalnominator | spatialnominator | ("this"|"that") predicator | quantityvalue | STRING
    objectnominator : "this" object | placenominator | "the world’s economy" | STRING
    amountnominator : "all" stuff | optimal set 
    eventnominator : "the latest" event
    placenominator :  "this" place | "the Netherlands" | "Brazil" | "Sudan" | "Amsterdam" | "Utrecht" | "Ij" | "Rotterdam" | "Groningen province" | "Schiphol Airport"
    optimal : ("the")? ("maximal" | "minimal" | "maximum" | "minimum" | "closest" | "smallest" | "largest" | "shortest")  
    temporalnominator :  "this" (time| timeinterval | event) | "Christmas" | contemporaryreference | pastreference | futurereference | YEAR | DATE
    contemporaryreference : ("starting")? ("now" | "currently" | "at present" | "today" | "from now on" | "until now"|"this summer" | "at the end of the African humid period")
    pastreference : ("starting")? ("earlier" | "in the past" | NUMBER "years ago" | "last week" | "yesterday")
    futurereference : ("starting")? ("in the future" | "later"   | "in 2030" | "tomorrow" | "from now on" | "in 20 years"|"this summer")
    spatialnominator :  placenominator | "this" (space | region) |  STRING
    quantityvalue : NUMBER unit | "infinite" unit | STRING  | NUMBER | "halved" | relativechange
    unit : "minutes" | "kilometers" | "meters" | "R/l" | "liters" | "C" | "µg/m³" | "decibel"
    relativechange : ("increased"|"decreased"|"doubled"|"halved"|"reduced") ("by" NUMBER ("percent")?)?    
'''
spatialExperimentGrammar = nominatorGrammar + r'''    
    spexperiment: (measure)+ (control)* (fix)* 
    measure : nominator | predicator            
    control : ("for" | "from" | "to" | "of" | spr) ("each"|"some") (predicator)      
    fix : tr temporalnominator | spr spatialnominator | ("for" | "from" | "to" | "of" | spr) nominator |  nominator |  compr quantityvalue | quantityvalue | ("with" optimal linearquantity) 
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

l_spEx = Lark(spatialExperimentGrammar + footer
        ,parser='earley', start='spexperiment', keep_all_tokens=True)

experiments = [
'proportional amount of (space of all green) for each neighborhood in "Amsterdam"',
'quantified amount of (space of all green) in kilometers for each neighborhood in "Amsterdam"',
'averaged amount of (area of the amount of space of each building) for each neighborhood in "Amsterdam"',
'averaged amount of (height of each building) for each neighborhood in "Amsterdam"',
'averaged amount of (quantified amount of green for each location) for each neighborhood in "Amsterdam"',
'proportional amount of (area of the amount of space of all green north of "Ij") for each neighborhood in "Amsterdam"',
'number of (building of some height larger than 5 meters) for each neighborhood in "Amsterdam"',
'quantified amount of (time to some hospital with minimal quantified amount of time) from each building in "Rotterdam"',
'sum of amount of (energy for each windmill) for this windfarm',
'location for each windmill of this windfarm',
'space of each municipality',
'time before this earthquake',
'amount of trees in "Utrecht"',
'averaged amount of (magnitude of each earthquake) in "Amsterdam"',
'largest (amount of money of each municipality)',
'tomorrow for each day in this year'
]

#parsetrees(l_spEx,experiments)


l_questions = Lark(questionGrammar  + footer
        ,parser='earley', start='question', keep_all_tokens=True, debug=True)
testquestions=[
'What should be the amount of green for each neighborhood in "Amsterdam" now so that the proportional amount of NO2 will be below 20 µg/m³ this summer?',
'What should be the location for each windmill of this windfarm now so that the sum of amount of (energy for each windmill) for this windfarm will be maximal in the future?',
'What would be the sum of the (capacity of the amount of ethanol for each producer) in "Brazil" in 2030 if the proportional amount of (tax for each consumer of all amount of ethanol) in "Brazil" was equal to 1.23 R/l from now on ?',
'What would be the averaged amount of (ethanol for each consumer) for "Brazil" in 2030 if the proportional amount of (tax for each consumer of all amount of ethanol) in "Brazil" was equal to 1.23 R/l from now on?',
'What could have been the density of the amount of lifestock for each location in "Sudan" 10.000 years ago given that the landcover for each location in "Sudan" was equal to "arid land" at the end of the African humid period?',
'What is the proportional amount of (space of all green) for each neighborhood in "Amsterdam" now?',
'What would be the proportional amount of (space of all green) for each neighborhood in "Amsterdam" in the future if the quantified amount of building was such and such now?',
'What should be the proportional amount of (space of all green) for each neighborhood in "Amsterdam" now such that the quantified amount of health for each inhabitant will be such and such in the future?',
]
#parsetrees(l_questions,testquestions)

#These are the questions used in the paper:
questions =[
'What is the shortest (duration of travel time to some ambulance station from each building) in "Rotterdam" at present?',
'What is the temperature for each location in "Utrecht" now given that the temperature for each (location of each sensor) is such and such now?',
'What will be the temperature in "Utrecht" tomorrow given that the temperature in "Utrecht" is 5 C today?',
'What could have been the event in "Utrecht" yesterday causing the proportional amount of water for all soil in "Utrecht" being 0.3 today?',
'What would be the temperature in "Utrecht" in 20 years if the proportional amount of CO2 emissions of the world’s economy were halved today?',
'What should be the amount of green in "Utrecht" today so that the maximal (temperature for each location) in "Utrecht" will be below 30 C this summer?',

'What is the closest ambulance station for each building in "Rotterdam" at present given that the location of each ambulance station is such and such now?',
'What will be the time to each building from the closest ambulance station in "Rotterdam" from now on given that the location of each ambulance station is such and such now?',
'What will be the sum of the amount of rain for each location in "Dortmund" tomorrow given that the air pressure temperature for each location in "Germany" is such and such now?',
'What could have been the event for each road intersection pair in "Rotterdam" last week causing the travel time of this ambulance station to this road accident in "Rotterdam" to be 30 minutes now?',
'What could have been the route for each language group in "the Amazon" starting 15.000 years ago causing the location of each language group to be such and such at present?',
'What would be the travel time to each building from the closest ambulance station in "Rotterdam" in the future if the travel time between this road intersection pair was infinite minutes from now on?',
'What would be the sum of the production of ethanol for each producer in "Brazil" in 2030 if the proportional amount of (tax for each consumer of all the ethanol) in "Brazil" was equal to 1.23 R/l from now on',
'What should be the location of each ambulance stations in "Rotterdam" now such that the travel time to each building from the closest ambulance station will be less than 14 minutes in the future?',
'What should be the location for each windmill of this windfarm now so that the sum of the (amount of energy for each windmill of this windfarm) will be maximal in the future?'
]
#parsetrees(l_questions,questions)







# -------- ThesisCasper ------------


#These are the questions that are used in the survey
survey_questions = [
    {
        "dataset_id": "NO2_Amsterdam_2025",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What is the concentration of NO₂ for each location of some sensor in Amsterdam in 2025?",
        "parser_question": 'What is the quantified amount of NO2 for each (location of each sensor) in "Amsterdam" now?'
    },
    {
        "dataset_id": "NO2_Amsterdam_2025",
        "option_id": "B",
        "is_correct": False,
        "mismatch_type": "measure_control_mismatch",
        "display_question": "What is the location for each NO₂ concentration value in Amsterdam?",
        "parser_question": 'What is the location for each quantified amount of NO2 in "Amsterdam" now?'
    },
    {
        "dataset_id": "NO2_Amsterdam_2025",
        "option_id": "C",
        "is_correct": False,
        "mismatch_type": "temporal_mismatch",
        "display_question": "What will be concentration of NO₂ for each location of some sensor in Amsterdam in 2026?",
        "parser_question": 'What will be the quantified amount of NO2 for each (location of each sensor) in "Amsterdam" in the future given that the quantified amount of NO2 for each (location of each sensor) is such and such now?'
    },
    {
        "dataset_id": "HousingValue_Amsterdam_2024",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What was the amount of space for interval of housing price in Amsterdam in 2024?",
        "parser_question": 'What is the amount of space for each interval of housing price in "Amsterdam" in 2024?'
    },
    {
        "dataset_id": "HousingValue_Amsterdam_2024",
        "option_id": "B",
        "is_correct": False,
        "mismatch_type": "measure_control_mismatch",
        "display_question": "What was the average housing price for each area in Amsterdam in 2024?",
        "parser_question": 'What is the averaged (housing price for each area) in "Amsterdam" in 2024?'
    },
    {
        "dataset_id": "HousingValue_Amsterdam_2024",
        "option_id": "C",
        "is_correct": False,
        "mismatch_type": "measure_mismatch",
        "display_question": "What was the amount of houses occupied by each interval of housing price in Amsterdam in 2024?",
        "parser_question": 'What is the number of buildings for each interval of housing price in "Amsterdam" in 2024?'
    },
    {
        "dataset_id": "Earthquakes_Groningen_2025",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What was the magnitude of each earthquake that occurred in Groningen province in 2025, and where did each event occur?",
        "parser_question": 'What is the magnitude of each earthquake within "Groningen province" in 2025?'
    },
    {
        "dataset_id": "Earthquakes_Groningen_2025",
        "option_id": "B",
        "is_correct": False,
        "mismatch_type": "measure_mismatch",
        "display_question": "What was the number of earthquakes that were observed for each location in Groningen province in 2025?",
        "parser_question": 'What is the number of earthquakes for each location in "Groningen province" in 2025?'
    },
    {
        "dataset_id": "Earthquakes_Groningen_2025",
        "option_id": "C",
        "is_correct": False,
        "mismatch_type": "measure_mismatch",
        "display_question": "What was the duration of the latest earthquake in Groningen province in 2025?",
        "parser_question": 'What is the duration of the latest earthquake in "Groningen province" in 2025?'
    },
    {
        "dataset_id": "MetroLines_Amsterdam",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What is the amount of linear space occupied by each tram line in Amsterdam now?",
        "parser_question": 'What is the length for each tram line in "Amsterdam" now?'
    },
    {
        "dataset_id": "MetroLines_Amsterdam",
        "option_id": "B",
        "is_correct": False,
        "mismatch_type": "measure_control_mismatch",
        "display_question": "What is the amount of metro lines crossing each area in Amsterdam now?",
        "parser_question": 'What is the number of metro lines for each area in "Amsterdam" now?'
    },
    {
        "dataset_id": "MetroLines_Amsterdam",
        "option_id": "C",
        "is_correct": False,
        "mismatch_type": "measure_mismatch",
        "display_question": "What is the number of passengers that use each metro or tram line in Amsterdam right now?",
        "parser_question": 'What is the number of passengers for each tram line in "Amsterdam" now?'
    },
    {
        "dataset_id": "Noise_Amsterdam_2021",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What was the amount of space occupied by each interval of quantified noise in decibel in Amsterdam in 2021?",
        "parser_question": 'What is the amount of space for each interval of quantified noise in decibel in "Amsterdam" in 2021?'
    },
    {
        "dataset_id": "Noise_Amsterdam_2021",
        "option_id": "B",
        "is_correct": False,
        "mismatch_type": "spatial_mismatch",
        "display_question": "What was the amount of space occupied by each interval of quantified noise in decibel around Schiphol Airport in 2021?",
        "parser_question": 'What is the amount of space for each interval of quantified noise in decibel around "Schiphol Airport" in 2021?'
    },
    {
        "dataset_id": "Noise_Amsterdam_2021",
        "option_id": "C",
        "is_correct": False,
        "mismatch_type": "measure_control_mismatch",
        "display_question": "What was the interval of quantified noise in decibel for each neighborhood region in Amsterdam in 2021?",
        "parser_question": 'What is the interval of quantified noise in decibel for each region in "Amsterdam" in 2021?'
    },
    {
        "dataset_id": "Trees_Amsterdam",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What are the location, species and height of each tree in Amsterdam now?",
        "parser_question": 'What is the height for each tree in "Amsterdam" now?'
    },
    {
        "dataset_id": "Trees_Amsterdam",
        "option_id": "B",
        "is_correct": False,
        "mismatch_type": "measure_control_mismatch",
        "display_question": "What is the amount of space covered by the amount of trees for each interval of tree height in Amsterdam now?",
        "parser_question": 'What is the amount of space of each (amount of trees for each interval of height) in "Amsterdam" now?'
    },
    {
        "dataset_id": "Trees_Amsterdam",
        "option_id": "C",
        "is_correct": False,
        "mismatch_type": "measure_mismatch",
        "display_question": "What is the total canopy coverage area for each tree species in Amsterdam now?",
        "parser_question": 'What is the region for each (amount of canopy for each species) in "Amsterdam" now?'
    },
    {
        "dataset_id": "PostcodeAreas_Amsterdam",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What is the postcode identifier for each address in Amsterdam?",
        "parser_question": 'What is the postcode identifier for each address in "Amsterdam" now?'
    },
    {
        "dataset_id": "PostcodeAreas_Amsterdam",
        "option_id": "B",
        "is_correct": False,
        "mismatch_type": "measure_control_mismatch",
        "display_question": "What amount of space is covered by each postcode 4 area in Amsterdam?",
        "parser_question": 'What is the amount of space for each postcode 4 area in "Amsterdam" now?'
    },
    {
        "dataset_id": "PostcodeAreas_Amsterdam",
        "option_id": "C",
        "is_correct": False,
        "mismatch_type": "measure_control_mismatch",
        "display_question": "What is the number of postcode 4 areas per neighborhood in Amsterdam?",
        "parser_question": 'What is the number of postcode 4 areas for each neighborhood in "Amsterdam" now?'
    },
    {
        "dataset_id": "PopulationDensity_Netherlands",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What is the population for each 1 km² grid cell in the Netherlands?",
        "parser_question": 'What is the population for each grid cell in "the Netherlands" now?'
    },
    # {
    #     "dataset_id": "PopulationDensity_Netherlands",
    #     "option_id": "B",
    #     "is_correct": False,
    #     "mismatch_type": "measure_control_mismatch",
    #     "display_question": "What is the amount of space for each interval of population counts in the Netherlands?",
    #     "parser_question": 'What is the amount of space for each (interval of population counts in "the Netherlands" now?'
    # },
    {
        "dataset_id": "PopulationDensity_Netherlands",
        "option_id": "C",
        "is_correct": False,
        "mismatch_type": "measure_control_mismatch",
        "display_question": "What is the average number of inhabitants per municipality in the Netherlands?",
        "parser_question": 'What is the averaged (number of inhabitant for each municipality) in "the Netherlands" now?'
    },
    {
        "dataset_id": "NO2_Projection",
        "option_id": "B",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What will be the change of quantified amount of NO₂ exposure for each location in \"Amsterdam\" tomorrow?",
        "parser_question": 'What will be the quantified amount of NO2 for each location in "Amsterdam" tomorrow given that the quantified amount of NO2 for each location in "Amsterdam" is such and such now?'
    },
    {
        "dataset_id": "NO2_Projection",
        "option_id": "C",
        "is_correct": False,
        "mismatch_type": "prediction_mismatch",
        "display_question": "What would be the change of quantified amount of NO₂ exposure for each location in \"Amsterdam\" in the future if the traffic restriction zone scenario was implemented now?",
        "parser_question": 'What would be the quantified amount of NO2 for each location in "Amsterdam" in the future if the quantified amount of NO2 for each location in "Amsterdam" was such and such now?'
    },
    {
        "dataset_id": "NO2_Projection",
        "option_id": "A",
        "is_correct": False,
        "mismatch_type": "retrodiction_mismatch",
        "display_question": "What could have been the traffic event yesterday causing the change of the quantified amount of NO₂ exposure in \"Amsterdam\" being such and such now?",
        "parser_question": 'What could have been the event yesterday given that the quantified amount of NO2 for each location in "Amsterdam" is such and such now?'
    },
    {
        "dataset_id": "WheatYield_Prediction",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What will be the quantified amount of wheat yield for each location in the study area in the future given that weather and soil conditions are such and such now?",
        "parser_question": 'What will be the quantified amount of wheat yield for each location in "study area" in the future given that the weather for each location in "study area" is such and such now?'
    },
    {
        "dataset_id": "WheatYield_Prediction",
        "option_id": "B",
        "is_correct": False,
        "mismatch_type": "retrojection_mismatch",
        "display_question": "What should be the crop management practice for each location in the study area now now so that wheat yield be maximal in the future?",
        "parser_question": 'What should be the crop management practice for each location in "study area" now so that the quantified amount of wheat yield for each location in "study area" will be maximal in the future?'
    },
    {
        "dataset_id": "WheatYield_Prediction",
        "option_id": "C",
        "is_correct": False,
        "mismatch_type": "retrodiction_mismatch",
        "display_question": "What could have been the event causing wheat yield being such and such now?",
        "parser_question": 'What could have been the event earlier given that the quantified amount of wheat yield is such and such now?'
    },
    {
        "dataset_id": "ConservationMeasures_Retrojection",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What should be the amount of space (or region) occupied by each conservation measure in agricultural land now so that the quantified amount of soil loss and labour cost will be minimal in the future?",
        "parser_question": 'What should be the amount of space for each conservation measure in "agricultural land" now so that the quantified amount of soil loss will be minimal in the future?'
    },
    {
        "dataset_id": "ConservationMeasures_Retrojection",
        "option_id": "B",
        "is_correct": False,
        "mismatch_type": "retrodiction_mismatch",
        "display_question": "What could have been the land management event causing the quantified amount of soil loss and labour cost being such and such now?",
        "parser_question": 'What could have been the event earlier given that the quantified amount of soil loss is such and such now?'
    },
    {
        "dataset_id": "ConservationMeasures_Retrojection",
        "option_id": "C",
        "is_correct": False,
        "mismatch_type": "prediction_mismatch",
        "display_question": "What will be the quantified amount of soil loss and labour cost in the study area in the future?",
        "parser_question": 'What will be the quantified amount of soil loss in "study area" in the future given that the quantified amount of soil loss in "study area" is such and such now?'
    },
        {
        "dataset_id": "RoadAccidents_NL",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What was the number of road accidents for each municipality in the Netherlands in 2024?",
        "parser_question": 'What is the number of road accident for each municipality in "the Netherlands" in 2024?'
    },
    {
        "dataset_id": "GreenSpace_Amsterdam",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What is the amount of green space for each neighborhood in Amsterdam now?",
        "parser_question": 'What is the amount of space for each neighborhood of all green in "Amsterdam" now?'
    },
    {
        "dataset_id": "Temperature_Sensors_NL",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What was the minimum temperature for each sensor location in the Netherlands on April 27, 2024?",
        "parser_question": 'What is the minimal (temperature for each (location of each sensor)) in "the Netherlands" on April 27, 2024?'
    },
    {
        "dataset_id": "Rainfall_Sensors_NL",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What was the rainfall amount for each sensor location in the Netherlands on March 30, 2024?",
        "parser_question": 'What is the quantified amount of rain for each (location of each sensor) in "the Netherlands" on March 30, 2024?'
    },
    {
        "dataset_id": "Hospitals_NL",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What is the location of each hospital in the Netherlands now?",
        "parser_question": 'What is the location for each "Huisartsenspoedpost" in "the Netherlands" now?'
    },
    {
        "dataset_id": "Landcover_NL",
        "option_id": "A",
        "is_correct": True,
        "mismatch_type": None,
        "display_question": "What is the land cover type for each location in the Netherlands now?",
        "parser_question": 'What is the landcover for each location in "the Netherlands" now?'
    },

]


# -------- OUTPUT SECTION ---------

for q in survey_questions:
    if q["is_correct"]:
        print(q["parser_question"])

def print_survey_parse_trees():
    questions_only = [q["parser_question"] for q in survey_questions]
    parsetrees(l_questions, questions_only)

def save_png_parse_trees():
    output_folder = "parseTreesSurvey"
    os.makedirs(output_folder, exist_ok=True)

    for q in survey_questions:
        filename = os.path.join(output_folder, f'{q["dataset_id"]}_{q["option_id"]}.png')
        make_png(filename, l_questions, q["parser_question"])
        print(f"Saved: {filename}")

PRINT_TREES = True
SAVE_PNGS = False

if PRINT_TREES:
    print_survey_parse_trees()

if SAVE_PNGS:
    save_png_parse_trees()




