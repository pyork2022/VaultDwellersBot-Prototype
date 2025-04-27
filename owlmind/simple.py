import csv
from .agent import Plan
from .bot import BotEngine, BotMessage

class SimpleEngine(BotEngine):
    """
    SimpleEngine provides a very simple Rule-based message processing from
    a list of predefined plans (Rules), and delegates to an LLM via model_provider.
    """

    VERSION = "1.2"

    def __init__(self, id, model_provider=None):
        super().__init__(id)
        self.rule_file = None
        self.model_provider = model_provider
        if self.model_provider is None:
            raise ValueError(
                "SimpleEngine needs a model_provider (pass it into constructor)"
            )
        return 

    def load(self, file_name):
        """
        Load plans from a CSV file.
        """
        row_count = 0
        try:
            with open(file_name, mode='r', encoding='utf-8') as file:
                self.rule_file = file_name
                reader = csv.DictReader(
                    (r for r in file if r.strip() and not r.strip().startswith('#')),
                    escapechar='\\'
                )
                for row in reader:
                    condition = {"message": row["message"].strip()}
                    response  = row["response"].strip()
                    self += Plan(condition=condition, action=response)
                    row_count += 1
        except FileNotFoundError:
            if self.debug:
                print(f'SimpleEngine.load(): ERROR, file {file_name} not found.')

        self.announcement = f'SimpleEngine {self.id} loaded {row_count} Rules from {file_name}.'
        return 

    def process(self, context: BotMessage):
        """
        Simplified deliberation logic.
        """
        msg = context['message']

        if msg == '/help':
            context.response = (
                f'### Version: {BotMessage.VERSION}\n'
                '### Help\n'
                '* `/info`: basic info\n'
                '* `/reload`: reload rules\n'
            )

        elif msg == '/info':
            context.response = f'### Version: {BotMessage.VERSION}\n'
            if self.model_provider:
                context.response += (
                    '### Model Provider:\n'
                    f'* type: {self.model_provider.type}\n'
                    f'* url: {self.model_provider.base_url}\n'
                )
            context.response += (
                '### PlanRepo:\n'
                f'* Number of plans: {len(self.plans)}\n'
                '```' + str(self.plans)[:1500] + '\n```'
            )

        elif msg == '/reload':
            context.response = f'### Version: {BotMessage.VERSION}\n'
            self.plans.clear()
            if self.rule_file:
                context.response += f'### Loading: {self.rule_file}\n'
                self.load(self.rule_file)
            context.response += f'### Reloaded with {len(self.plans)} plans!'

        elif context in self.plans:
            if self.debug:
                print(
                    f'SimpleEngine: response={context.result}, '
                    f'alternatives={len(context.alternatives)}, score={context.score}'
                )
            if self.is_action(context.result):
                command, prompt = (
                    context.result.split('/', 1)
                    if '/' in context.result else
                    (context.result, '')
                )
                if command == '@prompt':
                    full = prompt + '\n' + msg
                    context.response = self.model_provider.request(full)
            else:
                context.response = context.compile(context.result)

        else:
            context.response = "#### DEFAULT: There are no rules setup for this request!"
        return
