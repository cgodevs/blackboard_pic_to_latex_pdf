FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY join_latex_texts.py ${LAMBDA_TASK_ROOT}

CMD ["join_latex_texts.lambda_handler"]