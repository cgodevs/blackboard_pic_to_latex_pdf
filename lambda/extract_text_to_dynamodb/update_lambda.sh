# RUN THIS BASH WITH: ./update_lambda.sh

# Define variables
IMAGE_NAME=image_extract_text_from_image_to_dynamodb_lambda
LAMBDA_NAME=ExtractTextFromImageToDynamoDB
ACCOUNT_ID=339713058242

# Update ECR Image 
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker build -t $IMAGE_NAME .
docker tag $IMAGE_NAME:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/$IMAGE_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/$IMAGE_NAME:latest

# Update the image version for Lambda
aws lambda update-function-code --function-name $LAMBDA_NAME --image-uri $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/$IMAGE_NAME:latest
