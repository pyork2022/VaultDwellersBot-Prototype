
<img src="docs/images/owlmind-banner.png" width=800>

### [Understand](../README.md) | [Get Started](../README.md#getting-started) | [Contribute](../CONTRIBUTING.md)


# How-to Configure Dialog Rules in Bot-1?

Bot-1 is our Getting Started with simple Discord Bot connected to a Rule-Based Bot engine.

It works based on a Rule-Based system with simple deliberation process, defined by the [SimpleEngine Class](../owlmind/simple.py)

The code loads a set of Rules (Condition-Actions) from a Common-Separated-Value (CSV) file:

```python
    # Load Simples Bot Engine loading rules from a CSV
    brain = SimpleEngine(id='bot-1')
    brain.load('rules/bot-rules-2.csv')
```

Next, it kick starts the Discord bot whose interaction is governed by those Rules:

```
    # Kick start the Bot Runner process
    bot = DiscordBot(token=TOKEN, brain=brain, debug=True)
    bot.run()
```

# Question-Answer Rules

The CSV file should have a structure where:
* HEADER defines the matching FIELDS and one column named 'response'
* The COLUMN named 'response' provides the Answer string.
* Matching FIELDS match the field_name with a Regular Expression (*-matching)
* Lines starting with '#' are comments and will not be processed

The following FIELDS are available for the RULES:
* server_name     : Discord Server name (or '#dm' for direct message)
* channel_name    : Discord Channel name (or '#dm' for DM)
* thread_name     : Discord Thread name (empty if no thread)
* author_name     : Discord message's Author name (username)
* author_fullname : Discord message's Author full name (global_name)
* message         : Discord Message content

Example of CSV file (first row is the HEADER; then the RULES)

```
message, response
*hello*, Hi there!
*hello*, Hello!
*, I dont know how to respond to this message.
```

Examples:

```
If the Question is 'Hello, how are you?'
There are two possible answers as '*hello*' wll match twice:
    - Hi there! 
    - Hello!

The deliberation will randomly pick one of the possible answers.

Any other question will be responded using the catch-all rule '*'.
```

# Configuring Question-Answer Rules

Examples:

To create a Rule for this Interaction:

```
Q: What is the purpose of requirement analysis?
A: Understanding the purpose helps in defining clear requirements.
```

The RULE could be configured as follows:

```
message, repose
(...)
*purpose*requirement analysis*, Understanding the purpose helps in defining clear requirements.
```

 In this rule:

* the Condition will match any message that contains the words purpose-requirement-analysis.
* the Action (value under the column "response") will be returned as Answer


Hence, if you have mapped three Questions-Answers for your interaction, for instance:

```
Q: What is the purpose of requirement analysis?
A: Understanding the purpose helps in defining clear requirements.
```

```
Q: How can we determine what are useful requirements?
A: By analyzing user needs and stakeholder input.
```

```
Q: Why do we need the Solution Overview document?
A: Solution Overview ensures clarity and traceability.
```

Your rules.csv file could look like, for instance:

```
message, response
*purpose of*requirement analysys*, Understanding the purpose helps in defining clear requirements.
*determine*requirements*, By analyzing user needs and stakeholder input.
*need*solution overview*, Solution Overview ensures clarity and traceability.
```

Next, you have to load the CSV file while starting bot-1.py, by either:

* (Option 1) Place your CSV file in rules/bot-rules-2.csv OR
* (Option 2) Hard-code the position of your CSV file in bot-1.py:

```python

    # Load Simples Bot Engine loading rules from a CSV
    engine = SimpleEngine(id='bot-1')
    engine.load('Enter_Your_CSV_File_Here.csv')

```

Next, start bot-1.py and make sure it is loading YOUR CSV file:

```bash

$ python3 bot-1.py
Bot is running as: DemoBot.
Debug is on!
Bot is connected to SimpleEngine(bot-1).
SimpleEngine bot-1 loaded 66 Rules from rules/bot-rules-2.csv.

```


