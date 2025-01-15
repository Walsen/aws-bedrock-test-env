import boto3

bedrock = boto3.client(service_name='bedrock', region_name='us-east-1')
model_list = bedrock.list_foundation_models()
for x in range(len(model_list.get('modelSummaries'))):
    print(model_list.get('modelSummaries')[x]['modelId'])
