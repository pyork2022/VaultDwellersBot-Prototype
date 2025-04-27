import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('VaultUsers')

def get_or_create_user(uid):
    response = table.get_item(Key={"discordUserID": uid})
    if 'Item' in response:
        return response['Item']
    else:
        user = {
            'discordUserID': uid,
            'XP': 0,
            'Level': 1,
            'SPECIAL': {},
            'History': [],
            'Perks': []
        }
        table.put_item(Item=user)
        return user

def save_user(user):
    table.put_item(Item=user)
