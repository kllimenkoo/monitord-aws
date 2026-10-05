#!/usr/bin/env python3

import os

import aws_cdk as cdk

from monitord_aws.monitord_aws_stack import MonitordAwsStack

app = cdk.App()
MonitordAwsStack(
    app,
    'MonitordAwsStack',
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region='eu-north-1'),
)

app.synth()
