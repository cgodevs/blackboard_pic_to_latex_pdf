import os
import re
import boto3
from google import genai
from datetime import datetime
from urllib.parse import unquote
from botocore.exceptions import ClientError

assert os.getenv("API_KEY") != "", "API_KEY is not set"
DEFAULT_USER = "cgodevs"
DEFAULT_PROJECT = "000001"
LLM_MODEL = os.getenv("LLM_MODEL") or "gemini-2.0-flash"
TOKEN_PRICE = 0.0
TEXT_EXTRACTION_PROMPT = "Extract text from the image into latex."


DYNAMODB_PAYLOAD = {
    "user_id": DEFAULT_USER,
    "project_id": DEFAULT_PROJECT,
    "s3_link": "",
    "object_creation_timestamp": "",
    "record_creation_timestamp": "",
    "text_content": "",
    "tokens_count": "",
    "cost": ""
}


def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    dynamodb_client = boto3.client('dynamodb')

    for record in event["Records"]:
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]

        response = get_object_metadata(s3_client, bucket_name, object_key)
        metadata = response.get("Metadata", {})

        DYNAMODB_PAYLOAD["object_creation_timestamp"]   = response.get("LastModified", "").strftime("%Y-%m-%d %H:%M:%S")
        DYNAMODB_PAYLOAD["image_creation_timestamp"]    = metadata["image_creation_timestamp"]
        DYNAMODB_PAYLOAD["record_creation_timestamp"]   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        DYNAMODB_PAYLOAD["user_id"]                     = metadata["user_id"] if "user_id" in metadata else DEFAULT_USER
        DYNAMODB_PAYLOAD["project_id"]                  = metadata["project_id"] if "project_id" in metadata else DEFAULT_PROJECT
        DYNAMODB_PAYLOAD["s3_link"]                     = f"{bucket_name}/{unquote(object_key)}"
        DYNAMODB_PAYLOAD["cost"]                        = get_text_extraction_cost(DYNAMODB_PAYLOAD["tokens_count"])
        (DYNAMODB_PAYLOAD["text_content"],
         DYNAMODB_PAYLOAD["tokens_count"])              = extract_text_from_image(local_image_path=save_local_image_from_s3(bucket_name, object_key))

        dynamodb_client.put_item(
            TableName='FxBlackboardPicturesData',
            Item=map_payload_to_data_types(DYNAMODB_PAYLOAD)
        )
        print(DYNAMODB_PAYLOAD)
        print("Successfully inserted record into DynamoDB")
    return DYNAMODB_PAYLOAD


def get_object_metadata(s3_client, bucket_name, object_key):
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=unquote(object_key))
        return response
    except s3_client.exceptions.NoSuchKey:
        print(f"Error: Object with key '{object_key}' not found in bucket '{bucket_name}'.")
    except s3_client.exceptions.NoSuchBucket:
        print(f"Error: Bucket '{bucket_name}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


def save_local_image_from_s3(bucket_name, object_key):
    s3_client = boto3.client('s3')
    try:
        object_key = unquote(object_key)  # Decode key in case it has special characters
        local_path = f"/tmp/{os.path.basename(object_key)}"  # Save in /tmp directory
        # Download the image from S3 to a local temporary file
        s3_client.download_file(bucket_name, object_key, local_path)
        return local_path
    except ClientError as e:
        print(f"Error fetching the image from S3: {e}")
        raise Exception("Could not download image.")


def extract_text_from_image(local_image_path):
    extracted_text, total_tokens = "", 0
    try:
        client = genai.Client(api_key=os.getenv("API_KEY"))
        my_file = client.files.upload(file=local_image_path)
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=[my_file, TEXT_EXTRACTION_PROMPT]
        )
        total_tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0
        pattern = r"```latex(.*?)```"
        matches = re.findall(pattern, response.text, flags=re.S)
        if matches:
            for match in matches:
                extracted_text += match.strip() + "\n"
        else:
            print("No content matched the expected pattern.")
    except Exception as e:
        print(f"Error while processing image with GenAI: {e}")
        raise Exception("GenAI processing failed.")
    finally:
        return extracted_text, total_tokens


def get_text_extraction_cost(tokens_count: int):
    return 0.0


def map_payload_to_data_types(payload):
    numeric_keys = ["tokens_count", "cost"]
    dynamodb_payload = {}
    for key, value in payload.items():
        if key in numeric_keys:
            dynamodb_payload[key] = {"N": str(value)}
        else:
            dynamodb_payload[key] = {"S": str(value)}
    return dynamodb_payload
