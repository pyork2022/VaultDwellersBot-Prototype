##
## OwlMind - Platform for Education and Experimentation with Hybrid Intelligent Systems
## context.py :: Context Representation, Contextualized Record, and Contextualized Store.
## 
## These components implement Context-Aware Reasoning and Rule Base Inference
## at the core of Agent-based systems.
##
#  
# Copyright (c) 2024, The Generative Intelligence Lab @ FAU
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# Documentation:
#    https://github.com/genilab-fau/owlmind
#
# Disclaimer: 
# Generative AI has been used extensively while developing this package.
# 

import re
import random
from collections.abc import Iterable

class Context(dict):
    """
    Context represents a group of facts (key-value) organized in a dict of context-tree.
    
    Functionality:
    - Context key retrieval, including Context-Tree logic (parent-, sub-context)
    - Context matching, as Context-test in Context-target
    - Context-based Sentence compilation, as context << 'string $var_id
    - Tagging through 'namespace' for labelling by ContextRepo
    
    Example:
    c = Context({'code':'3333', 'name': 'FK'})
    c['other'] = 'new value'
    c += {'example': ['e1','e2']}
    print(c['code'])

    test = Context({'code':'*'})
    if test in c:
        print(test.subs)
    """

    VERSION = "1.3"

    _ = '_'
    MAX_CLAUSE = 100.0
    CASE_SENSITIVE = False
    DEBUG = True

    def __init__(self, facts=None, namespace=None, parent=None):
        """
        Constructor
        """
        self.namespace = namespace
        self.parent = parent
        if facts:
            self.__iadd__(facts=facts)
        return

    def __hash__(self):
        """
        Return specific hash value
        """
        return hash(tuple(sorted(self.items())))

    def __setitem__(self, key, fact):
        """
        Set specific fact to Context or Sub-Context.
        Instantiate a sub-context when needed.
        
        Functionality
        Context['key-1'] = 'value-1'
        Context['key-2/subkey-1'] = 'value-1_1'
        Context-Sub['../key-1'] = 'new-value-1'

        Example:
        c = Context()
        c['key-1'] = 'value-1'
        c['subc-1/subk-1'] = 'value-1_1' #-> it will create a sub-context and add the fact
        c1['../key-1'] = 'new-value-1'
        print(c)
        print(c1)
        """
        if '/' not in key:
            dict.__setitem__(self, key, fact)
            if isinstance(fact, Context):
                setattr(fact, 'parent', self)
                #dict.__setitem__(fact, '..', self)
        else:
            part, remaining = key.split('/', maxsplit=1)
            value1 = super().get(part, None)
            if not value1:
                value1 = Context()
                self.__setitem__(part, value1)
            value1[remaining] = fact
        return
    

    def __getitem__(self, key:str):
        """
        Retrieve fact based on key.

        Functionality:
        c['key'] #-> look for key at this context level
        c['subc-1/key] #-> look for key on sub-context 
        c['../key'] #-> look for key on parent
        c['*/key'] #-> look for key at this context level or any parent

        Example:
        c = Context(facts={'key-1':'value-1'})
        c1 = Context(facts={'skey-1':'value-1_1'})
        c += {'subc-1' : c1}
        print(c['key-1'])
        print(c['subc-1/skey-1'])
        print(c1['../key-1'])
        print(c1['*/key-1'])
        """

        if key is None:
            return None
        elif key == '.':
            return self
        elif key == '..':
            return self.parent
        elif '/' not in key:
            return super().get(key, None)
        else:
            part, remaining = key.split('/', maxsplit=1)
            value1 = self[part]
            if isinstance(value1, Context) or isinstance(value1, dict):
                return value1[remaining]
        return
    
    def __iadd__(self, facts):
        """
        Add new facts (key-value dict) to Context.
        If fact is a Context, link sub-Context under this Context
        
        Functionality:
        Context += {'key-1' : 'value-1', ..., 'key-n' : 'value-n'}
        Context += {'key-a' : Context}

        Example:
        c = Context()
        c1 = Context({'subkey-1_1':'value-1_1'})
        c2 = Context({'key-2_1':'value-2_2'})

        c += {'key-1':'value-f1'}
        c += {'subkey-1' : c1} #-> add as sub-context
        c += c2 #-> merge facts into c
        """
        if isinstance(facts, Context) or isinstance(facts, dict):
            for k in facts.keys():
                self.__setitem__(k, facts[k])
        elif Context.DEBUG: 
            print(f'ERROR: Context.__iadd__: fact is missing or invalid type, {type(facts)}')
        return self


    ##
    ## LOGIC FOR CONTEXT MATCHING 
    ###
    @staticmethod
    def _match_str(test:str, target:str):
        """ Inner Logic for matching strings in Context-match """
        score = 0

        if not Context.CASE_SENSITIVE:
            test = test.lower()
            target = target.lower()

        if test == target:  #-> String matching
            score += 1.0
        elif test == Context._ or test == '*':
            score += 0.25
        elif '*' in test:
            non_wildcard_count = len([char for char in test if char != '*'])
            if re.fullmatch(test.replace('*', '.*'), target):
                score += 0.5 + (0.49 * (non_wildcard_count / len(target)))
        elif test.startswith('r/'): 
            pattern = test[2:-1] if test.endswith('/') else test[2:] 
            try:
                if re.fullmatch(pattern, str(target)): 
                    score += 0.75
            except re.error:
                if Context.DEBUG: print(f'WARNING: Context.__contains__, regex expecting: {pattern}')
                pass 
        return score

        
    def __contains__(self, test) -> bool:
        """
        Dual functionality!
        If test is STRING, this is a test for 'does this context contains a KEY'
        If test is Context, this is a test for 'does Context-Test fits in Context-target (this one)'
        """
        if isinstance(test, str):
            return dict.__contains__(self, test)
        elif isinstance(test, Context):
            return self.match(test)
        else:
            if Context.DEBUG: print(f'WARNING: Context.__contains__, invalid type: {type(test)}')
        return False

    def match(self, test) -> bool:
        """
        Context-matching logic.
        This is the key logic behind Context-matching and ContextRepos used for the Rule-based deliberation.

        Functionality:
        Test-Context in Target-Context

        Example:
        c = Context({'code':2345})
        t = Context({'code':'*'})
        print(c.match(t), t.subs, t.score) #-> is True
        """

        # CUT-SHORT conditions
        if not test or not isinstance(test, Context):
            if Context.DEBUG: print(f'WARNING: Context.__contains__, test must be Context: {type(test)}')
            return False

        # PROCESSING
        test.subs = {}
        test.key = ''
        test.score = 0

        for key in test.keys():
            if key == '..':
                continue

            score = 0
            testing = test[key]
            target = self[key] if dict.__contains__(self, key) else None

            ##  @TODO must be able to match values of different types (https://github.com/GenILab-FAU/owlmind/issues/6)
            ##

            if not target:
                pass

            elif isinstance(testing, Context) and isinstance(target, Context):
                target.__contains__(testing)
                score = testing.score

            elif isinstance(testing, str) and isinstance(target, str):
                score = Context._match_str(testing, target)

            # If there was a Context-key-value match, accumulate; otherwise break with fail!
            if score:
                test.subs[key] = target
                test.score += Context.MAX_CLAUSE + score
            else:
                test.score = 0
                test.subs = None
                break
        
        return bool(test.score)
        
    def find(self, key):
        """ 
        Look for a key on this level and parents.
        If found, return `value` associated to that `key`
        
        Functionality:
        Context.find(KEY)
    
        Example:
        sc = Context()
        sc['code'] = '4455'
        c = Context(parent=sc)
        print(c.find('code'))
        """
        if key in self:
            return self[key]
        elif self.parent:
            return self.parent.find(key)
        return None

    def compile(self, sentence):
        """ 
        Compile a sentence (str) or sequence of sentences.
        Compilation means to replace $var_id or ${var_id} with values in Context, when these values are also Strings.
        If the target value is not an String, replace with a pointer.
        
        Functionality:
        Context.compile(SENTENCE)

        Example: 
        c = Context()
        c['code'] = '4455'
        c['api/code'] = '2345'
        print(c.compile('The code is ${api/code}'))
        """
        result = ''
        if isinstance(sentence, (list, tuple, set)):
            # Recursively process each element of the sequence
            result = type(sentence)(self.compile(element) for element in sentence)
        elif isinstance(sentence, str):
            # Regex for matching $varid and ${varid}, where varid can include special characters
            pattern = r"\$(\w+)|\$\{([\w/]+)\}"

            def substitute(match):
                var_name = match.group(1) or match.group(2)  # Match either $varid or ${varid}
                value = self.find(var_name)
                value = match.group(0) if value is None else value 
                return str(value) if isinstance(value, str) else f"<pointer to {value}>"

            result = re.sub(pattern, substitute, sentence)
        return result

###
### CONTEXTUALIZED ELEMENT
### 

class ContextRecord():
    """
    Contextualized Records to be used with ContextRepo.
    They represent goal({condition})->{action} structures, which can be used e.g. in Rule Base Stores.
    """
    def __init__(self, condition, action, goal:str = None):
        self.namespace : str = goal if goal else Context._
        self.context : Context = condition if isinstance(condition,Context) else Context(condition)
        self.action : list = action
        return 

    def __hash__(self):
        result = ''
        for field in [self.namespace, self.context, self.action]:
            #result = hash( (result, tuple(field) if field and isinstance(field, Iterable) else '_' ))
            result = hash((result, field.__hash__)) 
        return result
 
    def __repr__(self):
        return f'{self.__class__.__name__}({self.context}, {self.action})'
    

###
### CONTEXTUALIZED REPO
###

class ContextRepo():
    """
    Store of Contextualized Records.
    
    @EXAMPLE
    How to use this class:

    cr = ContextRepo()
    cr += ContextRecord(condition={'code':'*'}, action=('@print','$code'))
    cr += ContextRecord(condition={'name':'*'}, action=('@print','$name'))

    s = Context({'code':'3333', 'name': 'FK'})
    if s in cr:
        print(s.result)

    """
    def __init__(self, valid_class=ContextRecord):
        self.valid_class = valid_class
        self._length = 0
        self._repo = dict()
        return 
   
    def __len__(self):
        return self._length
    
    def __iadd__(self, obj):
        """
        Adds an object to the repository.
        """

        # CUT-SHORT conditions
        if not obj:
            return self
        elif not isinstance(obj, self.valid_class):
            raise ValueError(f'ContextRepo.__iadd__: invalid type for {self.__class__.__name__}, type {type(obj)}')
        
        # Processing
        namespace = getattr(obj, 'namespace', Context._) or Context._
        obj_hash = hash(obj)
        
        if namespace not in self._repo:
            self._repo[namespace] = dict()

        if obj_hash not in self._repo[namespace]:
            self._repo[namespace][obj_hash] = obj
            self._length+=1
        else:
            if Context.DEBUG: print(f'ContextRepo.__iadd__: obj already in the store {self.__class__.__name__}, {self._repo[namespace][obj_hash]}')
        return self
    
    def __getitem__(self, namespace):
        """ 
        Retrieve Contextualized Records stored under a namespace 
        """
        return self._repo[namespace].values() if namespace in self._repo else None 

    def __contains__(self, test:Context):
        """
        Matches a Context-test against selected ContextRecords in ContextRepo.
        Context-test.namespace will narrow the search space for given 'namespace'.
        """

        # CUT-SHORT conditions
        if test is None:
            return None
        elif not (isinstance(test, Context) or isinstance(test, str)):
            raise ValueError(f"ContextRepo.__contains__: expected Context or str, got {type(test)}")

        # PROCESSING
        matching_plans = []
        namespace = test.namespace or Context._

        # @NOTE:
        # This logic needs to be improved; we should be storing already sorted by 'potential match score' and 
        # going through highest-score(s) only, not the whole list!
        #
        # Check every record inside _repo[namespace]
        if namespace in self._repo:
            for record in self._repo[namespace].values():
                ## @NOTE
                # Does record.context (test) matches the target?
                # If so, record.context was loaded with:
                #       record.context.score : matching score
                if record.context in test:
                    test.result = record.context.compile(sentence=record.action)
                    test.score = record.context.score
                    matching_plans.append( (test.result, test.score) )

        # Initialize and load results
        test.score = 0
        test.matching = test.alternatives = test.result = None
        
        if len(matching_plans):
            matching_plans.sort(key=lambda x: x[1], reverse=True)  
            test.score = matching_plans[0][1] 
            test.matching = matching_plans
            test.alternatives = [plan[0] for plan in matching_plans if plan[1] == test.score] # alternatives with highest-score
            test.result = random.choice(test.alternatives) # pick one alternative

        return bool(test.result)

    def __repr__(self):
        """ Return string representation """
        output = []
        for namespace, PlanRules in self._repo.items():
            output.append(f"{namespace}:")
            for PlanRule in PlanRules.values():
                output.append(f"    {PlanRule}")
        return f"{self.__class__.__name__}(\n{chr(10).join(output)}\n)"


    def clear(self):
        """ Remove all items from the repository """
        self._length = 0
        self._repo.clear()
        return 

###
### DEBUG CODE
### TO BE REMOVED
###

if __name__ == "__main__":
    
    def test_setitem(c):
        c['key-1'] = 'value-1'
        c['subc-1/subk-1'] = 'value-1_1' #-> it will create a sub-context and add the fact
        c['subc-1/subk-2/subsubk-1'] = 'value-1_1_1'
        c['subc-1/subk-1'] = 'value-1_1' #-> it will create a sub-context and add the fact
        c1 = c['subc-1']
        print(c1)
        print(c1['subk-2/subsubk-1'])
        return
        
    def test_iadd(c):
        c1 = Context({'subkey-1':'value-1_1'})
        c2 = Context({'key-2':'value-2_2'})

        c += {'key-1':'value-f1'}
        c += {'subc-1' : c1} #-> add as sub-context
        print(c['subc-1/subkey-1'])
        c2 += c #-> merge facts into c
        print(c2)
        print(c2['subc-1/subkey-1'])
        return
    
    def test_getitem(c):
        c1 = Context(facts={'skey-1':'value-1_1'})
        c += {'key-1' : 'value-1'}
        c += {'subc-1' : c1}
        print(c['key-1'])
        print(c['subc-1'])
        print(c['subc-1/skey-1'])
        print(c1['../key-1'])
        print(c1['..'])
        return 
    
    def test_contains(c):
        c = Context({'code':'23456'})
        c['subc-1/subk1'] = '246'
        #t = Context({'code':'23456'})
        #print(t in c, t.subs, t.score) 
        #t = Context({'code':'*'})
        #print(t in c, t.subs, t.score)
        #t = Context({'code':'2*'})
        #print(t in c, t.subs, t.score) 
        #t = Context({'code':'*456'})
        #print(t in c, t.subs, t.score)
        #t = Context({'code':'2*45*'})
        #print(t in c, t.subs, t.score) 
        t = Context({'subc-1/subk1':'*46'})
        print(t in c, t.subs, t.key, t.score) 
        return
    
    def test_find(c):
        sc = Context()
        sc['code'] = '4455'
        c = Context(parent=sc)
        c['code'] = '3345'
        print(c.find('code'))
        print(c['../code'])
        return 
    
    def test_compile(c):
        sc = Context()
        sc['name'] = 'FK'

        c = Context(parent=sc)
        c['api/code'] = '2345'
        c['code'] = '4567'
        print(c.compile('The code for $name is ${api/code}'))
        return
    
    def test_contextrepo(c):
        beliefs = Context()
        beliefs['name'] = 'FK'
        beliefs['code'] = '3232'

        cb = ContextRepo()
        cb += ContextRecord(condition={'message' : 'hello*'}, action='Hello, my name is $name')
        cb += ContextRecord(condition={'message' : '*code*'}, action='The code is $code')
        cb += ContextRecord(condition={'message' : 'Tell*code*'}, action='I am telling you: the code is $code')
        cb += ContextRecord(condition={'message' : 'hi*there'}, action='Hi. My name is $name')
        
        test = Context({'message':'Tell me the code'})
        test.parent = beliefs

        print(test in cb, test.compile(test.result))
        return
    

    c = Context()
    #test_setitem(c)
    #test_iadd(c)
    #test_getitem(c)
    #test_contains(c)
    #test_find(c)
    #test_compile(c)
    test_contextrepo(c)



