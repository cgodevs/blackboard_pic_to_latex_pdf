# RUN THIS BASH WITH: ./update_lambda.sh

# Define variables
IMAGE_NAME=image_extract_text_from_image_to_dynamodb_lambda
LAMBDA_NAME=ExtractTextFromImageToDynamoDB

# Update ECR Image 
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 339713058242.dkr.ecr.us-east-1.amazonaws.com
docker build -t $IMAGE_NAME .
docker tag $IMAGE_NAME:latest 339713058242.dkr.ecr.us-east-1.amazonaws.com/$IMAGE_NAME:latest
docker push 339713058242.dkr.ecr.us-east-1.amazonaws.com/$IMAGE_NAME:latest

# Update the image version for Lambda
aws lambda update-function-code --function-name $LAMBDA_NAME --image-uri 339713058242.dkr.ecr.us-east-1.amazonaws.com/$IMAGE_NAME:latest
