from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

DEFAULT_USER = "cgodevs"
DEFAULT_PROJECT = "000001"

def get_image_metadata_dict(directory="."):
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
                        if date_time:
                            date_time = datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                    metadata_dict[filename] = {"DateTime": date_time}
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                metadata_dict[filename] = {"DateTime": None}
    return metadata_dict


def upload_to_s3(bucket, region_name="us-east-1", directory="."):

    s3 = boto3.client("s3", region_name=region_name)
    metadata = get_image_metadata_dict(directory)

    for filename, meta in metadata.items():
        file_path = os.path.join(directory, filename)
        print(f"Uploading {filename} to S3...")

        try:
            s3_metadata = {
                "image_creation_timestamp": meta.get("DateTime", None),
                "user_id": DEFAULT_USER,
                "project_id": DEFAULT_PROJECT
            }
            s3.upload_file(
                Filename=file_path,
                Bucket=bucket,
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


def delete_all_objects(bucket, region_name="us-east-1"):
    s3 = boto3.client("s3", region_name=region_name)
    try:
        response = s3.list_objects_v2(Bucket=bucket)
        if "Contents" not in response:
            print(f"The bucket '{bucket}' is already empty.")
            return
        objects = response["Contents"]
        for obj in objects:
            object_key = obj["Key"]
            s3.delete_object(Bucket=bucket, Key=object_key)
            print(f"Deleted: {object_key}")
        print(f"All objects deleted from the bucket '{bucket}'.\n")
    except NoCredentialsError:
        print("AWS credentials not found. Please configure them using AWS CLI or environment variables.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Please check your configuration.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    bucket_name = f"fx-blackboard-pictures"
    delete_all_objects(bucket=bucket_name)  # Optional: Comment
    upload_to_s3(bucket=bucket_name, directory=".")

