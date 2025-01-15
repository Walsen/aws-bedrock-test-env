import boto3
import json


def get_models():
    bedrock = boto3.client(service_name='bedrock', region_name='us-east-1')
    model_list = bedrock.list_foundation_models()
    for x in range(len(model_list.get('modelSummaries'))):
        print(model_list.get('modelSummaries')[x]['modelId'])


def test_amazon_titan():
    """
    Review https://repost.aws/knowledge-center/bedrock-invokemodel-api-error
    """
    bedrock_rt = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
    prompt = "What is Amazon Bedrock?"
    configs = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 4096,
            "stopSequences": [],
            "temperature": 0,
            "topP": 1
        }
    }
    body = json.dumps(configs)
    model_id = 'amazon.titan-tg1-large'
    accept = 'application/json'
    content_type = 'application/json'
    response = bedrock_rt.invoke_model(
        body=body,
        modelId=model_id,
        accept=accept,
        contentType=content_type
    )
    response_body = json.loads(response.get('body').read())
    print(response_body.get('results')[0].get('outputText'))

def main():
    # get_models()
    test_amazon_titan()

if __name__ == "__main__":
    main()