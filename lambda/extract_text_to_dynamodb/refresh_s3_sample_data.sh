# RUN THIS BASH WITH: ./refresh_s3_sample_data.sh
# OPTIONAL: Create partitions according to the intended standards

# DELETE EVERYTHING 🔥
aws s3 rm s3://fx-blackboard-pictures --recursive

# Place all images in folder
aws s3 cp ./image_samples/ s3://fx-blackboard-pictures/user_id=cgodevs/project_id=000001/ --recursive

# Place a single image in bucket
#aws s3 cp ./image_samples/blackboard_photo_sample.jpg s3://fx-blackboard-pictures/user_id=cgodevs/project_id=000001/