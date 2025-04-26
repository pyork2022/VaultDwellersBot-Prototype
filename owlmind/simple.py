##
## OwlMind - Platform for Education and Experimentation with Hybrid Intelligent Systems
## simple.py :: provides simple implementations to many of the functionality asn utilities to get the framework running.
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
# Documentation and Getting Started:
#    https://github.com/genilab-fau/owlmind
#
# Disclaimer: 
# Generative AI has been used extensively while developing this package.
# 

import csv
from .agent import Plan
from .bot import BotEngine, BotMessage

class SimpleEngine(BotEngine):
    """
    SimpleEngine provides a very simple Rule-based message processing from a list of predefined plans (Rules).

    Methods:
        load(file_name):
            Loads plans from a CSV file. Each row in the file should contain conditions as columns (excluding 'action') and an 'action' column specifying the associated action.
            See example for the CVS format in the method documentation.

        process(context):
            Processes a BotMessage context, matches it against the loaded plans, and assigns a response based on the best match.
    """
    VERSION = "1.2"

    def __init__(self, id):
        super().__init__(id)
        self.rule_file = None
        self.model_provider = None
        return 

    def load(self, file_name):
        """
        Load plans from a CSV file.

        The CSV file should have a structure where:
            Header defines the FIELDS for matching and a column named 'response'
            Each line contains the RgEx for matching the FIELD and the RESPONSE for that Rule.
        
        Where the FIELDS available include:

        server_name     : Server name (or '#dm' for direct message)
        channel_name    : Channel name (or '#dm' for DM)
        thread_name     : Thread name (empty if no thread)
        author_name     : Author name (username)
        author_fullname : Author full name (global_name)
        message         : Message content

        Example of CSV file:

        message, response
        *hello*, Hi there!
        *hello*, Hello!
        *, I dont know how to respond to this message.

        """
        row_count = 0
        try:
            with open(file_name, mode='r', encoding='utf-8') as file:
                self.rule_file = file_name
                reader = csv.DictReader((row for row in file if row.strip() and not row.strip().startswith('#')), escapechar='\\')
                for row in reader:
                    condition = {"message" : row["message"].strip()}
                    response = row["response"].strip()
                    self += Plan(condition=condition, action=response)
                    row_count += 1
        except FileNotFoundError:
            if self.debug: print(f'SimpleEngine.load(.): ERROR, file {file_name} not found.')

        ## Update announcement
        self.announcement = f'SimpleEngine {self.id} loaded {row_count} Rules from {file_name}.'
        return 

    def process(self, context:BotMessage):
        """
        Simplified deliberation logic.
        """

        if context['message'] == '/help':
            context.response = f'### Version: {BotMessage.VERSION}\n'
            context.response += f'### Help\n'
            context.response += f'* ``/info``: displays basic information\n'
            context.response += f'* ``/reload``: reload rule file'
        
        elif context['message'] == '/info':
            context.response = f'### Version: {BotMessage.VERSION}\n'
            
            if self.model_provider:
                context.response += f'### Model Provider:\n'
                context.response += f'* type: {self.model_provider.type}\n'
                context.response += f'* url: {self.model_provider.base_url}\n'

            context.response += f'### PlanRepo: \n'
            context.response += f'* Number of plans: {len(self.plans)}\n'
            plan_str : str = str(self.plans)
            context.response += "```\n" + plan_str[0:1500] + "\n```"



        elif context['message'] == '/reload':
            context.response = f'### Version: {BotMessage.VERSION}\n'
            self.plans.clear()
            if self.rule_file:
                context.response += f'### Loading: {self.rule_file}\n'
                self.load(file_name=self.rule_file)
            context.response += f'### Reloaded with {len(self.plans)} plans!'

        elif context in self.plans:
            if self.debug: print(f'SimpleEngine: response={context.result}, alternatives={len(context.alternatives)}, score={context.score}')
            if self.is_action(context.result):
                command, prompt = context.result.split('/', maxsplit=1) if '/' in context.result else (context.result, '')
                print('-->', command, prompt, context['message'])
                
                if command == '@prompt' and self.model_provider:
                    prompt = prompt + '\n' + context['message']
                    print('E--> requesting:', prompt)
                    context.response = self.model_provider.request(prompt)
                    
            else: 
                context.response = context.compile(context.result)
        else:
            context.response = "#### DEFAULT: There are no rules setup for this request!"
        return 



