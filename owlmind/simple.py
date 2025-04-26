##
## OwlMind - Platform for Education and Experimentation with Generative Intelligent Systems
## simple.py :: Simplified AI-first message handler
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
    SimpleEngine: AI-first message processing.

    Bypasses CSV rules and forwards every user message directly to the configured
    AI model. Retains a `/help` command for basic info.
    """
    VERSION = "1.2"

    def __init__(self, id):
        super().__init__(id)
        self.rule_file = None
        self.model_provider = None

    def load(self, file_name):
        """
        Legacy CSV rule loader (no longer used with AI-first mode).
        """
        row_count = 0
        try:
            with open(file_name, mode='r', encoding='utf-8') as file:
                self.rule_file = file_name
                reader = csv.DictReader((r for r in file if r.strip() and not r.strip().startswith('#')), escapechar='\\')
                for row in reader:
                    condition = {"message": row["message"].strip()}
                    response = row["response"].strip()
                    self += Plan(condition=condition, action=response)
                    row_count += 1
        except FileNotFoundError:
            if self.debug:
                print(f"SimpleEngine.load: file not found: {file_name}")
        self.announcement = f"SimpleEngine {self.id} loaded {row_count} rules from {file_name}."

    def process(self, context: BotMessage):
        """
        AI-first processing:
        - `/help`: show version and instructions.
        - else: forward message to AI model provider.
        """
        msg = context['message']

        # Built-in help command
        if msg.startswith('/help'):
            context.response = (
                f"### Version: {BotMessage.VERSION}\n"
                "* Use `/help` to show this message.\n"
                "* Simply chat and I'll forward your text to the AI model."
            )
            return

        # Ensure model is configured
        if not self.model_provider:
            context.response = "Error: no AI model configured."
            return

        # Forward raw user message to AI endpoint
        context.response = self.model_provider.request(msg)
        return