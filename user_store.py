import os
import boto3

# initialize DynamoDB resource in your configured region
ddb   = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION'))
table = ddb.Table('VaultUsers')

def get_or_create_user(discord_id: str) -> dict:
    """Fetch or initialize a user record."""
    resp = table.get_item(Key={'discordUserID': discord_id})
    if 'Item' in resp:
        return resp['Item']
    # first‐time user—seed their profile
    item = {
        'discordUserID': discord_id,
        'XP': 0,
        'Level': 1,
        'SPECIAL': {
            'Strength': 0, 'Perception': 0, 'Endurance': 0,
            'Charisma': 0, 'Intelligence': 0, 'Agility': 0, 'Luck': 0
        },
        'Perks': [],
        'History': []
    }
    table.put_item(Item=item)
    return item

def save_user(item: dict):
    """Persist user state back to DynamoDB."""
    table.put_item(Item=item)
