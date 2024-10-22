import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import logging

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Students')

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    method = event.get('httpMethod', '')  # Safely get the httpMethod

    # Set headers with CORS enabled
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",  # Allow all origins
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",  # Allow specific methods
        "Access-Control-Allow-Headers": "Content-Type"  # Allow specific headers
    }

    if method == 'GET':
        # Handling GET request: Fetch student by studentId
        if 'queryStringParameters' in event and 'studentId' in event['queryStringParameters']:
            student_id = event['queryStringParameters']['studentId']
            response = get_student(student_id)
        else:
            response = {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps("Missing studentId in query parameters")
            }
    elif method == 'POST':
        # Handling POST request: Add new student
        body = json.loads(event['body'])
        response = add_student(body)
    elif method == 'PUT':
        # Handling PUT request: Update student
        body = json.loads(event['body'])
        response = update_student(body)
    elif method == 'DELETE':
        # Handling DELETE request: Delete student
        body = json.loads(event['body'])
        if 'studentId' in body:
            student_id = body['studentId']
            response = delete_student(student_id)
        else:
            response = {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps("Missing studentId in request body")
            }
    else:
        response = {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps("Method Not Allowed")
        }

    # Ensure headers are present in the response
    response['headers'] = headers

    return response

# Function to handle GET request
def get_student(student_id):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    try:
        response = table.get_item(
            Key={
                'studentId': student_id
            }
        )
        if 'Item' in response:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(response['Item'], default=decimal_default)
            }
        else:
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps(f"Student with ID {student_id} not found.")
            }
    except Exception as e:
        logger.error(f"Error retrieving student: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps(f"Error retrieving student: {str(e)}")
        }

# Function to handle POST request (add new student)
def add_student(student_info):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    try:
        table.put_item(Item=student_info)
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(f"Student {student_info['studentId']} added successfully.")
        }
    except Exception as e:
        logger.error(f"Error adding student: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps(f"Error adding student: {str(e)}")
        }

# Function to handle PUT request (update student)
def update_student(student_info):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    try:
        # Update student information based on studentId
        table.put_item(Item=student_info)  # DynamoDB put_item overwrites existing item with same key
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(f"Student {student_info['studentId']} updated successfully.")
        }
    except Exception as e:
        logger.error(f"Error updating student: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps(f"Error updating student: {str(e)}")
        }

# Function to handle DELETE request
def delete_student(student_id):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    try:
        table.delete_item(
            Key={
                'studentId': student_id
            }
        )
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(f"Student with ID {student_id} deleted successfully.")
        }
    except Exception as e:
        logger.error(f"Error deleting student: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps(f"Error deleting student: {str(e)}")
        }

# Helper function to handle Decimal objects in JSON
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj) if obj % 1 else int(obj)
    raise TypeError
