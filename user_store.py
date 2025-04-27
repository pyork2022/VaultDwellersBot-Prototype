import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('VaultUsers')

# LEVEL_THRESHOLDS: The XP thresholds required for each level.
LEVEL_THRESHOLDS = {
     1:     0,
     2:   100,
     3:   300,
     4:   600,
     5:  1000,
     6:  1500,
     7:  2100,
     8:  2800,
     9:  3600,
    10:  4500,
    11:  5500,
    12:  6600,
    13:  7800,
    14:  9100,
    15: 10500,
    16: 12000,
    17: 13600,
    18: 15300,
    19: 17100,
    20: 19000
}

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

def award_xp(user: dict, base_xp: int = 1):
    """
    Grants XP = base_xp + (Intelligence // 3), updates Level, returns:
    (xp_awarded, old_level, new_level)
    """
    intel = user.get("SPECIAL", {}).get("Intelligence", 0)
    bonus = intel // 3
    total = base_xp + bonus

    user["XP"] = user.get("XP", 0) + total

    old = user.get("Level", 1)
    new = old
    for lvl, req in sorted(LEVEL_THRESHOLDS.items()):
        if user["XP"] >= req:
            new = lvl

    user["Level"] = new
    return total, old, new
