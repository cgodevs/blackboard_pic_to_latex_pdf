import os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

DEFAULT_USER = "cgodevs"
DEFAULT_PROJECT = "project1"
IMAGE_URL = "blackboard_photo_sample.jpg"
TOKEN_PRICE = 0.002

def get_image_date(image_path):
    try:
        image = Image.open(image_path)
        exif = image.getexif()

        # Try EXIF DateTime first
        datetime_fields = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
        for tagid in exif:
            tag_name = TAGS.get(tagid, tagid)
            if tag_name in datetime_fields and exif[tagid]:
                try:
                    return datetime.strptime(exif[tagid], '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    continue

        # If no EXIF datetime, try file modification time
        file_time = os.path.getmtime(image_path)
        return datetime.fromtimestamp(file_time)

    except Exception as e:
        print(f"Error getting image date: {e}. Returning current time as last resort.")
        return datetime.now()

def extract_text_from_image(image_path):
    return "some text", 0  # number of tokens


text, tokens = extract_text_from_image(IMAGE_URL)

payload = {
    "user_id": DEFAULT_USER,
    "project_id": DEFAULT_PROJECT,
    "s3_link": IMAGE_URL,
    "creation_timestamp": get_image_date(IMAGE_URL),
    "text_content": text,
    "tokens_count": tokens,
    "text_extraction_count": tokens * TOKEN_PRICE
}

date = get_image_date(IMAGE_URL)
print(f"Image date: {date}")