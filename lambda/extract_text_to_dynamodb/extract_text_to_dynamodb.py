import openai
import boto3
from datetime import datetime
from urllib.parse import unquote

DEFAULT_USER = "cgodevs"
DEFAULT_PROJECT = "000001"
TOKEN_PRICE = 0.0

DYNAMODB_PAYLOAD = {
    "user_id": DEFAULT_USER,
    "project_id": DEFAULT_PROJECT,
    "s3_link": "",
    "creation_timestamp": "",
    "text_content": "",
    "tokens_count": "",
    "cost": ""
}


def lambda_handler(event, context):
    s3_client = boto3.client('s3')

    for record in event["Records"]:
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]
        DYNAMODB_PAYLOAD["s3_link"] = object_key
        DYNAMODB_PAYLOAD["user_id"] = get_partition_value(object_name=object_key, partition_key="user_id", default_value=DEFAULT_USER)
        DYNAMODB_PAYLOAD["project_id"] = get_partition_value(object_name=object_key, partition_key="project_id", default_value=DEFAULT_PROJECT)
        DYNAMODB_PAYLOAD["creation_timestamp"] = get_obj_creation_time(s3_client, bucket_name, object_key)
        DYNAMODB_PAYLOAD["text_content"], DYNAMODB_PAYLOAD["tokens_count"] = extract_text_from_image(object_key)
        DYNAMODB_PAYLOAD["cost"] = get_text_extraction_cost(DYNAMODB_PAYLOAD["tokens_count"])

        print(DYNAMODB_PAYLOAD)
    return DYNAMODB_PAYLOAD


def get_partition_value(object_name, partition_key, default_value=""):
    for item in object_name.split("/"):
        if partition_key in unquote(item):
            return unquote(item).split("=")[-1]
    return default_value


def get_obj_creation_time(s3_client, bucket_name, object_key):
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=unquote(object_key))
        last_modified = response.get("LastModified","")
        return last_modified.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        raise Exception("Error fetching metadata for object creation time. Quitting.")


def extract_text_from_image(object_key):
    return "", 1  # number of tokens


def get_text_extraction_cost(tokens_count: int):
    return 0.0