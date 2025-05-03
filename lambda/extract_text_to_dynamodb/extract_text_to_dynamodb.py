import os
import openai
import boto3
from datetime import datetime

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    for record in event["Records"]:
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]

        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
            metadata = response.get("Metadata", {})  # Custom metadata
            content_type = response.get("ContentType", "")  # Standard metadata
            content_length = response.get("ContentLength", 0)

            print(f"Custom Metadata: {metadata}")
            print(f"Content-Type: {content_type}")
            print(f"Content-Length: {content_length}")

        except Exception as e:
            print(f"Error fetching metadata: {e}")

    return {"statusCode": 200, "body": "Success"}



# def get_image_date(image_path):
#     try:
#         image = Image.open(image_path)
#         exif = image.getexif()
#
#         # Try EXIF DateTime first
#         datetime_fields = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
#         for tagid in exif:
#             tag_name = TAGS.get(tagid, tagid)
#             if tag_name in datetime_fields and exif[tagid]:
#                 try:
#                     return datetime.strptime(exif[tagid], '%Y:%m:%d %H:%M:%S')
#                 except ValueError:
#                     continue
#
#         # If no EXIF datetime, try file modification time
#         file_time = os.path.getmtime(image_path)
#         return datetime.fromtimestamp(file_time)
#
#     except Exception as e:
#         print(f"Error getting image date: {e}. Returning current time as last resort.")
#         return datetime.now()

# def extract_text_from_image(image_path):
#     return "some text", 0  # number of tokens


# text, tokens = extract_text_from_image(IMAGE_URL)
#
# payload = {
#     "user_id": DEFAULT_USER,
#     "project_id": DEFAULT_PROJECT,
#     "s3_link": IMAGE_URL,
#     "creation_timestamp": '',#get_image_date(IMAGE_URL),
#     "text_content": text,
#     "tokens_count": tokens,
#     "text_extraction_count": tokens * TOKEN_PRICE
# }

# date = get_image_date(IMAGE_URL)
# print(f"Image date: {date}")