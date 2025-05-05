import os
import re
import boto3
from google import genai
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

assert os.getenv("API_KEY") != "", "API_KEY is not set"

TOKEN_PRICE = 0.0
TABLE_NAME = "FxBlackboardPicturesData"
LLM_MODEL = os.getenv("LLM_MODEL") or "gemini-2.0-flash"
LATEX_UNION_PROMPT = ("Join all latex texts into a single latex text. "
                      "You must try to identify order and sense among the complete set of latex texts."
                      "You may exclude whatever marks or repetitions there may be, trying to create a concise final "
                      "text out of the whole set of latex texts, according to the context of the subject and your own knowledge about it."
                      "Even though you must not add to the original content, you must try to fill possibly identifiable gaps within the text to make it complete.")


def lambda_handler(event, context):
    items = retrieve_dynamodb_records(project_id=event["project_id"], user_id=event["user_id"])
    ordered_items = sorted(
        items,
        key=lambda x: int(datetime.strptime(x["image_creation_timestamp"], "%Y-%m-%d %H:%M:%S").timestamp())
    )
    latex_texts = "\n\n".join([f"Latex text {i}: {ordered_items[i]["text_content"]}" for i in range(len(ordered_items))])
    final_text = latex_texts
    print(final_text)
    # final_text = unite_text_into_final_latex(latex_texts)
    # dynamodb_client.put_item(
    #     TableName='FxBlackboardPicturesData',
    #     Item=map_payload_to_data_types(DYNAMODB_PAYLOAD)
    # )
    return {"status": "success", "final_text": final_text}


def retrieve_dynamodb_records(project_id, user_id):
    dynamodb_resource = boto3.resource('dynamodb')
    table = dynamodb_resource.Table(TABLE_NAME)
    items = []
    try:
        response = table.query(
            KeyConditionExpression=Key("project_id").eq(project_id),
            FilterExpression=Attr("user_id").eq(user_id)
        )
        items = response.get('Items', [])
    except Exception as e:
        print(f"Error querying DynamoDB table: {e}")
    return items


def unite_text_into_final_latex(local_image_path):
    extracted_text, total_tokens = "", 0
    try:
        client = genai.Client(api_key=os.getenv("API_KEY"))
        my_file = client.files.upload(file=local_image_path)
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=[my_file, LATEX_UNION_PROMPT]
        )
        total_tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0
        pattern = r"```latex(.*?)```"
        matches = re.findall(pattern, response.text, flags=re.S)
        if matches:
            for match in matches:
                extracted_text += match.strip() + "\n"
        else:
            print("No latex was provided by the final text aggregation.")
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
