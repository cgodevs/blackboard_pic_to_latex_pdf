# RUN THIS BASH WITH: ./refresh_s3_sample_data.sh

aws s3 rm s3://fx-blackboard-pictures --recursive
#aws s3 cp ./blackboard_photo_sample.jpg s3://fx-blackboard-pictures

# OPTIONAL: Create partitions according to the intended standards
 aws s3 cp ./blackboard_photo_sample.jpg s3://fx-blackboard-pictures/user_id=cgodevs/project_id=000002/blackboard_photo_sample.jpg