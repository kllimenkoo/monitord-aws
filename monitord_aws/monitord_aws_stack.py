from aws_cdk import (
    BundlingOptions,
    CfnOutput,
    Duration,
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
    aws_lambda as lambda_,
)
from aws_cdk import (
    aws_s3 as s3,
)
from aws_cdk import aws_s3_deployment as s3deploy
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
                        ' && python seed.py'
                        ' && cp -au . /asset-output',
                    ],
                ),
            ),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={'MONITORD_DB': '/tmp/monitord.db'},
        )

        bucket = s3.Bucket(self, 'MonitordBucket')

        distribution = cloudfront.Distribution(
            self,
            'MonitordDistribution',
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket)
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
            'MonitordDeployFiles',
            sources=[
                s3deploy.Source.asset('frontend'),
                s3deploy.Source.data(
                    'config.js', f'window.apiUrl = "{http_api.url or ""}"'
                ),
            ],
            destination_bucket=bucket,
            distribution=distribution,
            distribution_paths=['/*'],
        )

        CfnOutput(self, 'ApiUrl', value=http_api.url or '')
        CfnOutput(
            self,
            'DashboardUrl',
            value=f'https://{distribution.distribution_domain_name}',
        )
