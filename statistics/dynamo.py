import boto3


client = boto3.client('dynamodb', endpoint_url='http://localhost:8000')


def create_tables():
    create_comments_table()


def create_comments_table():
    table = client.create_table(
        TableName='Comments6',
        KeySchema=[
            {
                'AttributeName': 'comment_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'count',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'comment_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'count',
                'AttributeType': 'N'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table


def put_new_comment(comment_id, comment, count, users):
    response = client.put_item(
        TableName='Comments6',
        Item={
            'comment_id': {
                'S': "{}".format(comment_id),
            },
            'count': {
                'N': "{}".format(count),
            },
            'comment': {
                'S': "{}".format(comment),
            },
        }
    )
    return response
