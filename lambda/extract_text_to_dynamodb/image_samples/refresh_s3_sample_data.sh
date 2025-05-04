#!/bin/bash

# RUN THIS BASH WITH: ./refresh_s3_sample_data.sh
# OPTIONAL: Create partitions according to the intended standards

# DELETE EVERYTHING 🔥
aws s3 rm s3://fx-blackboard-pictures --recursive

# Place all images in folder
#aws s3 cp ./ s3://fx-blackboard-pictures/user_id=cgodevs/project_id=000001/ --recursive

# Place a single image in bucket
#aws s3 cp ./blackboard_photo_sample.jpg s3://fx-blackboard-pictures/user_id=cgodevs/project_id=000001/ --metadata '{"user_id": "cgodevs", "project_id": "000001", "image_creation_timestamp": "2024-04-30 09:18:00"}'
