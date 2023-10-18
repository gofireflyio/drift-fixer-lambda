FROM amazon/aws-lambda-python:3.8
COPY requirements.txt .
#just to trigger rebuild docker image layer of pip3 install
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
RUN mkdir ${LAMBDA_TASK_ROOT}/drift_fixer_lambda
COPY  utils.py ${LAMBDA_TASK_ROOT}
COPY  drift_fixer_lambda/consumer.py drift_fixer_lambda/models.py drift_fixer_lambda/__init__.py  ${LAMBDA_TASK_ROOT}/drift_fixer_lambda/
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "drift_fixer_lambda/consumer.lambda_handler" ]