import aws_cdk as core
import aws_cdk.assertions as assertions
import pytest

from monitord_aws.monitord_aws_stack import MonitordAwsStack

ENV = core.Environment(account='123456789012', region='eu-north-1')


@pytest.fixture(scope='module')
def template():
    app = core.App(context={'aws:cdk:bundling-stacks': []})
    stack = MonitordAwsStack(app, 'monitord-aws', env=ENV)
    return assertions.Template.from_stack(stack)


def test_lambda_right_handler(template):
    template.has_resource_properties(
        'AWS::Lambda::Function',
        {
            'Handler': 'api.handler',
            'Runtime': 'python3.12',
        },
    )


def test_lambda_memory_256(template):
    template.has_resource_properties('AWS::Lambda::Function', {'MemorySize': 256})


def test_lambda_timeout_30_sec(template):
    template.has_resource_properties('AWS::Lambda::Function', {'Timeout': 30})


def test_dynamodb_table_count(template):
    template.resource_count_is('AWS::DynamoDB::Table', 7)


def test_ec2_type_t3_micro(template):
    template.has_resource_properties('AWS::EC2::Instance', {'InstanceType': 't3.micro'})


def test_ec2_role_has_ssm_policy(template):
    template.has_resource_properties(
        'AWS::IAM::Role',
        {
            'ManagedPolicyArns': assertions.Match.array_with(
                [
                    {
                        'Fn::Join': [
                            '',
                            [
                                'arn:',
                                {'Ref': 'AWS::Partition'},
                                ':iam::aws:policy/AmazonSSMManagedInstanceCore',
                            ],
                        ]
                    }
                ]
            )
        },
    )


def test_ec2_role_has_read_access_to_dynamodb(template):
    template.has_resource_properties(
        'AWS::IAM::Policy',
        {
            'PolicyDocument': {
                'Statement': assertions.Match.array_with(
                    [
                        assertions.Match.object_like(
                            {
                                'Action': assertions.Match.array_with(
                                    [
                                        'dynamodb:BatchGetItem',
                                        'dynamodb:Query',
                                    ]
                                ),
                                'Effect': 'Allow',
                            }
                        )
                    ]
                )
            },
            'Roles': assertions.Match.array_with(
                [{'Ref': assertions.Match.string_like_regexp('DaemonRole.*')}]
            ),
        },
    )


def test_ec2_role_has_write_access_to_dynamodb(template):
    template.has_resource_properties(
        'AWS::IAM::Policy',
        {
            'PolicyDocument': {
                'Statement': assertions.Match.array_with(
                    [
                        assertions.Match.object_like(
                            {
                                'Action': assertions.Match.array_with(
                                    [
                                        'dynamodb:BatchWriteItem',
                                        'dynamodb:PutItem',
                                    ]
                                ),
                                'Effect': 'Allow',
                            }
                        )
                    ]
                )
            },
            'Roles': assertions.Match.array_with(
                [{'Ref': assertions.Match.string_like_regexp('DaemonRole.*')}]
            ),
        },
    )


def test_has_api_url_output(template):
    template.has_output('ApiUrl', {})


def test_has_dashboard_url_output(template):
    template.has_output('DashboardUrl', {})
