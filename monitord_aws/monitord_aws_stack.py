from aws_cdk import (
    BundlingOptions,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
)
from aws_cdk import (
    aws_apigatewayv2 as apigw,
)
from aws_cdk import (
    aws_apigatewayv2_integrations as integrations,
)
from aws_cdk import (
    aws_cloudfront as cloudfront,
)
from aws_cdk import (
    aws_cloudfront_origins as origins,
)
from aws_cdk import (
    aws_dynamodb as dynamodb,
)
from aws_cdk import (
    aws_ec2 as ec2,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from aws_cdk import (
    aws_s3 as s3,
)
from aws_cdk import (
    aws_s3_deployment as s3deploy,
)
from constructs import Construct


class MonitordAwsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        fn = lambda_.Function(
            self,
            'MonitordApi',
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler='api.handler',
            code=lambda_.Code.from_asset(
                'lambda',
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        'bash',
                        '-c',
                        'pip install -r requirements.txt -t /asset-output'
                        ' && cp -au . /asset-output',
                    ],
                ),
            ),
            timeout=Duration.seconds(30),
            memory_size=256,
        )

        cpu_table = dynamodb.Table(
            self,
            'CpuTable',
            table_name='cpu_metrics',
            partition_key=dynamodb.Attribute(
                name='metric', type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='timestamp', type=dynamodb.AttributeType.NUMBER
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        cpu_table.grant_read_data(fn)

        ram_table = dynamodb.Table(
            self,
            'RamTable',
            table_name='ram_metrics',
            partition_key=dynamodb.Attribute(
                name='metric', type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='timestamp', type=dynamodb.AttributeType.NUMBER
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        ram_table.grant_read_data(fn)

        disk_table = dynamodb.Table(
            self,
            'DiskTable',
            table_name='disk_metrics',
            partition_key=dynamodb.Attribute(
                name='dev_name', type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='timestamp', type=dynamodb.AttributeType.NUMBER
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        disk_table.grant_read_data(fn)

        net_table = dynamodb.Table(
            self,
            'NetTable',
            table_name='net_metrics',
            partition_key=dynamodb.Attribute(
                name='intf_name', type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='timestamp', type=dynamodb.AttributeType.NUMBER
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        net_table.grant_read_data(fn)

        known_devices_table = dynamodb.Table(
            self,
            'KnownDevices',
            table_name='known_devices',
            partition_key=dynamodb.Attribute(
                name='device', type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        known_devices_table.grant_read_data(fn)

        known_interfaces_table = dynamodb.Table(
            self,
            'KnownInterfaces',
            table_name='known_interfaces',
            partition_key=dynamodb.Attribute(
                name='interface', type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        known_interfaces_table.grant_read_data(fn)

        alerts_table = dynamodb.Table(
            self,
            'Alerts',
            table_name='alerts',
            partition_key=dynamodb.Attribute(
                name='pk', type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='timestamp', type=dynamodb.AttributeType.NUMBER
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        alerts_table.grant_read_data(fn)

        role = iam.Role(
            self, 'DaemonRole', assumed_by=iam.ServicePrincipal('ec2.amazonaws.com')
        )
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                'AmazonSSMManagedInstanceCore'
            )
        )

        cpu_table.grant_read_write_data(role)
        ram_table.grant_read_write_data(role)
        disk_table.grant_read_write_data(role)
        net_table.grant_read_write_data(role)
        known_devices_table.grant_read_write_data(role)
        known_interfaces_table.grant_read_write_data(role)
        alerts_table.grant_read_write_data(role)

        bucket_daemon = s3.Bucket(
            self,
            'MonitordBucketDaemon',
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        bucket_daemon.grant_read(role)

        daemon_deploy = s3deploy.BucketDeployment(
            self,
            'MonitordDeployDaemon',
            sources=[
                s3deploy.Source.asset('daemon'),
            ],
            destination_bucket=bucket_daemon,
        )

        user_data = ec2.UserData.for_linux()
        user_data.add_commands(f'export DAEMON_BUCKET="{bucket_daemon.bucket_name}"')

        with open('scripts/install_daemon.sh') as f:
            user_data.add_commands(f.read())

        instance = ec2.Instance(
            self,
            'DaemonInstance',
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            role=role,
            vpc=ec2.Vpc.from_lookup(self, 'VPC', is_default=True),
            user_data=user_data,
        )

        instance.node.add_dependency(daemon_deploy)

        bucket_frontend = s3.Bucket(
            self,
            'MonitordBucketFrontend',
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        distribution = cloudfront.Distribution(
            self,
            'MonitordDistribution',
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    bucket_frontend
                )
            ),
            default_root_object='index.html',
        )

        http_api = apigw.HttpApi(
            self,
            'MonitordHttpApi',
            default_integration=integrations.HttpLambdaIntegration(
                'MonitordIntegration', fn
            ),
            cors_preflight=apigw.CorsPreflightOptions(
                allow_origins=[f'https://{distribution.distribution_domain_name}'],
                allow_methods=[apigw.CorsHttpMethod.GET],
            ),
        )

        s3deploy.BucketDeployment(
            self,
            'MonitordDeployFrontend',
            sources=[
                s3deploy.Source.asset('frontend'),
                s3deploy.Source.data(
                    'config.js', f'window.apiUrl = "{http_api.url or ""}"'
                ),
            ],
            destination_bucket=bucket_frontend,
            distribution=distribution,
            distribution_paths=['/*'],
        )

        CfnOutput(self, 'ApiUrl', value=http_api.url or '')
        CfnOutput(
            self,
            'DashboardUrl',
            value=f'https://{distribution.distribution_domain_name}',
        )
