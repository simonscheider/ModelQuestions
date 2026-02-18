from lark import Lark, tree
from rich import print
#import pydot
from lark.tree import Tree
import hashlib
import warnings
try:
    import CustomLarkFunctions
except ImportError:
    warnings.warn('To use the show_image() function you need to install the "PIL" package.')

class QuestionGrammar():
    def __init__(self):
        footer = r'''

                %import common.ESCAPED_STRING -> STRING
                %import common.SIGNED_NUMBER -> NUMBER
                %import common.WS 
                %ignore WS
        '''

        conceptGrammar = '''
            amount : "interval of" magnitude | timeinterval | region | (("amount of")? ("(" experiment ")" | concept) ("s")?) | "sum of" ("the")? amount  
            concept : onec | twoc
            onec : object  | event | stuff | space | time | magnitude | occurrence
            twoc : onec "pair" | "pair of" onec
            time : "time" 
            timeinterval : "interval of" time | "travel time" | "time of the year" | "year" | "month" | "day" | "hour" | "minute" | "second"
            tr : "before" | "after" | "during" | "at" | "in"
            space : "space" | "location" |  STRING
            region : "region" | "amount of" space | "area" 
            spr : "in" | "within" | "touching" | "overlapping" | "not overlapping" | "away from" | "west of" | "north of" | "south of"| "east of" | "at" | "between" | "close to" | STRING    
            compr : "larger than" | "less than" | "equal to" | "changed to" | "below" | "above" | STRING   
            magnitude : (quantified amount | "averaged" amount | "magnitude" | "temperature" | "duration" | "length" | "distance" | "height") ("in" unit)? 
            quantified : intensive | extensive
            intensive :  "proportional" | "proportion of" | "density of" ("the")? | "normalized" | "concentration of"      
            extensive : "quantified" | "number of" | "capacity of" ("the")? | "production of" ("the")? | "duration of"
            object : "object" | "destination"|"goal" | "perceived goals" | person | "book" | "tree"| "lifestock" | "street segment" | "place" | "building" | "city" | "neighborhood" | "municipality" | "hospital" | "inhabitant" | "windmill" | "windfarm" | ("ethanol")? "consumer" | ("ethanol")? "producer" | "ambulance station" | "road intersection" | "language group" | "route" | "sensor"| "the world’s economy"|STRING
            person : "person"
            stuff :  "stuff" |"BMI" | "money" | "rain" | "soil"| "water" | "air pressure" | "noise" | "temperature" | "green" | "landcover" | "health" |  "energy"| "ethanol" | "cost" | "tax" | "CO2 emissions"| "recreational value" | "weighted score" | "NO2" | "PM"| STRING 
            event : "event" | "trip" | "period" | "earthquake" | "road accident" | STRING
            occurrence : process | state | act
            act : "act" | "make" | "measure" | "run" | "stay" | "cycle" | "bike" | "throw" | "bake" | "read" | "go" | "plan" | "eat" | "walk"| "arrive"
            process : "process"| "generate" | "stumble" | "rain"  | "grow" | "burn" | "flow" | "breathe" | "perceive"
            state : "state" | "stay" | "linger" | "rest" | "contain"

        '''
        nominatorGrammar = conceptGrammar + '''
            indicator : "this" | "that" | "some"
            nominator : temporalnominator | spatialnominator | objectnominator | indicator (concept | amount) | optimal amount | value | STRING  
            optimal : ("the")? ("maximal" | "minimal" | "maximum" | "minimum" | "closest" | "smallest" | "largest" | "shortest" | "first" | "last" | "final")  
            temporalnominator :  indicator (time| timeinterval | event) | "Christmas" | contemporaryreference | pastreference | futurereference | STRING    
            personnominator : "I" | "you" | "he" | "she" | STRING | indicator person
            objectnominator : "home" | STRING | indicator object | "Rotterdam" |personnominator 
            contemporaryreference : ("starting")? ("now" | "then" | "currently" | "at present" | "today" | "from now on" | "until now"|"this summer" | "at the end of the African humid period")
            pastreference : ("starting")? ("earlier" | "in the past" | NUMBER "years ago" | "last week" | "yesterday")
            futurereference : ("starting")? ("in the future" | "later"   | "in 2030" | "tomorrow" | "from now on" | "in 20 years"|"this summer")
            spatialnominator :  indicator (space | region) | STRING
            value : NUMBER unit | "infinite" unit | STRING  | NUMBER | "halved" | relativechange
            unit : "minutes" | "kilometers" | "meters" | "R/l" | "liters" | "C" | "µg/m³" | "decibel"
            relativechange : ("increased"|"decreased"|"doubled"|"halved"|"reduced") ("by" NUMBER ("percent")?)?
            nomlist : nomlist nominator | nominator

        '''
        situationGrammar = nominatorGrammar + '''
            situation : (personnominator)? action | (nominator)? happening
            do : "do"("es")?
            kappa : "is" | "are"
            preposition : "at" | "in" | "on" |"to"
            epsilon : "is"
            attribution : nominator epsilon object
            appredicator : (outcome)?  (means)?  (preposition nominator)?    
            outcome : nomlist
            means : "with" nomlist
            performance : ("at")? (temporalnominator)? do |  time (personnominator) do  | person temporalnominator do
            action : performance  act ("ing")? (appredicator)? | actionwithgoal
            generativegoal : "such that" (attribution)
            modificativegoal :  "such that" (situation)
            goal : generativegoal | modificativegoal
            goals: goal ((","|"or") goal)* # test
            generativeaction : performance   (act ("ing")?)? (appredicator)? generativegoal
            modificativeaction : performance   (act ("ing")?)? (appredicator)? modificativegoal 
            actionwithgoal : generativeaction |  modificativeaction
            happening : ("at")? temporalnominator kappa (state|process) ("ing")? (appredicator)?     
        '''

        ExperimentGrammar = situationGrammar + r'''
            
            decexperiment: (measure)+ (control)* (fix)* modificativegoal
            spexperiment: (measure)+ (control)* (fix)*
            experiment: (decexperiment|spexperiment)
            measure : nominator | concept | amount
            control : ("for" | "from" | "to" | "of" | spr) ("each"|"some")? (concept | amount)
            fix : tr temporalnominator | spr spatialnominator | "if" situation | ("for" | "from" | "to" | "of" | spr) nominator | compr value | value | "with" optimal amount
            '''
        questionGrammar = ExperimentGrammar + r'''
            question :  (contemporary | prediction | retrodiction | projection | retrojection) ("?")?    
            factualcondition : experiment ("is"|"are"|"was"|"were"|"to be"|"being") ("such and such"| optimal | fix)  contemporaryreference 
            counterfactualcondition : experiment ("was"|"were") ("such and such"| optimal | fix) contemporaryreference 
            projectedcondition : experiment ("will be"|"being") ("such and such"| optimal | fix) futurereference 
            simplemodel : experiment (contemporaryreference)?
            transformationmodel : experiment contemporaryreference "given that" ("the")?  factualcondition
            contemporary : "What" ("is"|"are") ("the")? (simplemodel|transformationmodel) 
            prediction : "What" "will be" ("the")? experiment futurereference "given that" ("the")?  factualcondition 
            retrodiction : "What" "could have been" ("the")? experiment pastreference ("given that" | "causing") ("the")? factualcondition 
            projection : "What" "would be" ("the")? experiment futurereference ("if"|"when") ("the")? counterfactualcondition 
            retrojection : "What" "should" ("have")? ("be"|"been") ("the")? experiment contemporaryreference ("so"|"such") "that" ("the")? projectedcondition
            '''

        self.l_questions = Lark(questionGrammar + footer
                           , parser='earley', start='question', keep_all_tokens=True)

    def parsetrees(self, questions):
        cnt = 0
        for e in questions:
            cnt += 1
            print(e)
            print(self.l_questions.parse(e).pretty())


    def pydot__tree_to_dot_custom(self,tree, filename, rankdir="LR", **kwargs):
        graph = self.pydot__tree_to_graph_custom(tree, rankdir, **kwargs)
        graph.write(filename)

    def pydot__tree_to_png_custom(self, tree, filename, rankdir = "LR",**kwargs):
        graph = self.pydot__tree_to_graph_custom(tree, rankdir, **kwargs)
        graph.write_png(filename)

    def pydot__tree_to_graph_custom(self,tree, rankdir="LR", **kwargs):
        """Creates a colorful image that represents the tree (data+children, without meta)

        Possible values for `rankdir` are "TB", "LR", "BT", "RL", corresponding to
        directed graphs drawn from top to bottom, from left to right, from bottom to
        top, and from right to left, respectively.

        `kwargs` can be any graph attribute (e. g. `dpi=200`). For a list of
        possible attributes, see https://www.graphviz.org/doc/info/attrs.html.
        """

        import pydot  # type: ignore[import-not-found]
        graph = pydot.Dot(graph_type='digraph', rankdir=rankdir, **kwargs)

        i = [0]

        def new_leaf(leaf):
            node = pydot.Node(i[0], label=repr(leaf))
            i[0] += 1
            graph.add_node(node)
            return node

        def _to_pydot(subtree):
            color = int(hashlib.md5(subtree.data.encode('utf-8')).hexdigest()[:6], 16)

            color |= 0x808080

            subnodes = [_to_pydot(child) if isinstance(child, Tree) else new_leaf(child)
                        for child in subtree.children]
            node = pydot.Node(i[0], style="filled", fillcolor="#%x" % color, label=subtree.data)
            i[0] += 1
            graph.add_node(node)

            for subnode in subnodes:
                graph.add_edge(pydot.Edge(node, subnode))

            return node

        _to_pydot(tree)
        return graph
