from PIL import Image
from PIL.ExifTags import TAGS
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

DEFAULT_USER = "cgodevs"
DEFAULT_PROJECT = "000001"

def get_image_metadata_dict(directory="."):
    """
    Fetch metadata for image files in the given directory and return as a dictionary
    where keys are filenames, and values are dicts containing 'DateTime' metadata.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"Error: {directory} is not a valid directory.")

    metadata_dict = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and (filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff'))):
            try:
                with Image.open(file_path) as img:
                    exif_data = img._getexif()
                    date_time = None
                    if exif_data:
                        exif_dict = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_data.items()}
                        date_time = exif_dict.get('DateTime', None)
                    metadata_dict[filename] = {"DateTime": date_time}
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                metadata_dict[filename] = {"DateTime": None}
    return metadata_dict


def upload_to_s3(bucket_name, region_name="us-east-1", directory="."):

    s3 = boto3.client("s3", region_name=region_name)
    metadata = get_image_metadata_dict(directory)

    for filename, meta in metadata.items():
        file_path = os.path.join(directory, filename)
        print(f"Uploading {filename} to S3...")

        try:
            s3_metadata = {
                "image_creation_timestamp": meta.get("DateTime", "None"),
                "user_id": DEFAULT_USER,
                "project_id": DEFAULT_PROJECT
            }
            s3.upload_file(
                Filename=file_path,
                Bucket=bucket_name,
                Key=f"user_id={DEFAULT_USER}/project_id={DEFAULT_PROJECT}/{filename}",
                ExtraArgs={
                    "Metadata": s3_metadata
                },
            )
            print(f"Successfully uploaded {filename} with metadata: {s3_metadata}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except NoCredentialsError:
            print("AWS credentials not found. Please configure them using AWS CLI or environment variables.")
        except PartialCredentialsError:
            print("Incomplete AWS credentials. Please check your configuration.")
        except Exception as e:
            print(f"Failed to upload {filename}: {e}")


if __name__ == "__main__":
    bucket_name = f"fx-blackboard-pictures"
    upload_to_s3(bucket_name=bucket_name, directory=".")

