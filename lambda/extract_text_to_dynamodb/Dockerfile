FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY extract_text_to_dynamodb.py ${LAMBDA_TASK_ROOT}

CMD ["extract_text_to_dynamodb.lambda_handler"]