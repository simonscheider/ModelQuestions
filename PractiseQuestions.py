from QuestionGrammar import QuestionGrammar

grammar = QuestionGrammar()

questions_tryout = [
    'What is the (act if this person now does act such that this person then does eat at this place) for each place for each person if this person now is staying at that place?'

]
grammar.parsetrees(questions_tryout)