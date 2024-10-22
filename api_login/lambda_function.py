import json
import boto3
from boto3.dynamodb.conditions import Key
import logging

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Students')  # Assuming we have a Users table for authentication

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    method = event.get('httpMethod', '')  # Get HTTP method (POST, PUT)
    resource = event.get('resource', '')  # Get resource path (e.g., /users, /users/{userId})

    # Set headers for CORS
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",  # Allow all origins
        "Access-Control-Allow-Methods": "GET, POST, PUT",  # Allow specific methods
        "Access-Control-Allow-Headers": "Content-Type"  # Allow specific headers
    }

    if method == 'POST' and resource == '/users/login':
        # Handling POST request: User login
        body = json.loads(event['body'])
        email = body.get('email')
        password = body.get('password')
        
        # Authenticate user
        response = authenticate_user(email, password)
        response['headers'] = headers
        return response

    elif method == 'PUT' and resource == '/users/profile/{userId}':
        # Handling PUT request: Update user profile
        body = json.loads(event['body'])
        student_id = event['pathParameters']['userId']
        name = body.get('name')
        
        response = update_user_profile(student_id, name)
        response['headers'] = headers
        return response

    else:
        return {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps("Method Not Allowed")
        }

def authenticate_user(email, password):
    try:
        # Query DynamoDB by email to authenticate user
        response = table.query(
            IndexName='email-index',  # Assuming an index for querying by email
            KeyConditionExpression=Key('email').eq(email)
        )
        
        if response['Items']:
            user = response['Items'][0]
            if user['password'] == password:
                return {
                    "statusCode": 200,
                    "body": json.dumps({"status": "success", "user": user})
                }
            else:
                return {
                    "statusCode": 401,
                    "body": json.dumps({"status": "fail", "message": "Incorrect password"})
                }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"status": "fail", "message": "User not found"})
            }
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": f"Error: {str(e)}"})
        }

def update_user_profile(student_id, name):
    try:
        # Update DynamoDB with new user information
        response = table.update_item(
            Key={
                'studentId': student_id
            },
            UpdateExpression="SET #name = :name",
            ExpressionAttributeNames={
                '#name': 'name'
            },
            ExpressionAttributeValues={
                ':name': name
            },
            ReturnValues="UPDATED_NEW"
        )
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "message": "Profile updated successfully",
                "updatedAttributes": response['Attributes']  # Newly updated fields
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": f"Error: {str(e)}"
            })
        }


