import sys
import pulumi
import pulumi_aws as aws
import json

from pulumi import automation as auto


def set_role():
    assume_role = aws.iam.get_policy_document(statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            principals=[{
                "type": "AWS",
                "identifiers": ["arn:aws:iam::862307432587:root"]
            }],
            actions=["sts:AssumeRole"],  # Correct: using 'actions' instead of 'Action'
            conditions=[{
                "test": "Bool",
                "variable": "aws:MultiFactorAuthPresent",
                "values": ["true"]
            }]
        )
    ])

    allow_bedrock_role = aws.iam.Role("role",
                            name="allow-bedrock-role",
                            assume_role_policy=assume_role.json)

    allow_aws_marketplace_policy_statement = aws.iam.get_policy_document(statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            actions=[
                "aws-marketplace:ViewSubscriptions",
                "aws-marketplace:Unsubscribe",
                "aws-marketplace:Subscribe"
            ],
            resources=["*"]
        )
    ])

    allow_aws_marketplace_policy = aws.iam.Policy("allow-aws-marketplace-policy",
                                              policy=allow_aws_marketplace_policy_statement.json,
                                              opts=pulumi.ResourceOptions(parent=allow_bedrock_role))

    attach_bedrock_full_access_policy = aws.iam.RolePolicyAttachment("allow-full-bedrock-access",
                                                   role=allow_bedrock_role.name,
                                                   policy_arn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess")

    attach_allow_aws_marketplace_policy = aws.iam.RolePolicyAttachment("allow-aws-marketplace-policy-attach",
                                                   role=allow_bedrock_role.name,
                                                   policy_arn=allow_aws_marketplace_policy.arn)


    pulumi.export("role_arn", allow_bedrock_role.arn)


# To destroy our program, we can run python main.py destroy
destroy = False
args = sys.argv[1:]
if len(args) > 0:
    if args[0] == "destroy":
        destroy = True

project_name = "bedrock_iam_role"
# We use a simple stack name here, but recommend using auto.fully_qualified_stack_name for maximum specificity.
stack_name = "dev"
# stack_name = auto.fully_qualified_stack_name("myOrgOrUser", project_name, stack_name)

# create or select a stack matching the specified name and project.
# this will set up a workspace with everything necessary to run our inline program (pulumi_program)
stack = auto.create_or_select_stack(stack_name=stack_name,
                                    project_name=project_name,
                                    program=set_role)

print("successfully initialized stack")

# for inline programs, we must manage plugins ourselves
print("installing plugins...")
stack.workspace.install_plugin("aws", "v4.0.0")
print("plugins installed")

# set stack configuration specifying the AWS region to deploy
print("setting up config")
stack.set_config("aws:region", auto.ConfigValue(value="us-east-1"))
print("config set")

print("refreshing stack...")
stack.refresh(on_output=print)
print("refresh complete")

if destroy:
    print("destroying stack...")
    stack.destroy(on_output=print)
    print("stack destroy complete")
    sys.exit()

print("updating stack...")
up_res = stack.up(on_output=print)
print(f"update summary: \n{json.dumps(up_res.summary.resource_changes, indent=4)}")
print(f"role arn: {up_res.outputs['role_arn'].value}")
