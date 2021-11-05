import os

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_ecs as ecs,
                     aws_ecr as ecr,
                     aws_logs as logs)

class ExchangeBase(cdk.Construct):

    def __init__(self, scope: cdk.Construct, id:str,
                exchnage_name:str,
                binary_path:str,
                repo_arn:str,
                bucket:s3.Bucket,
                cluster:ecs.Cluster,
                topic: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service_prefix = exchnage_name.lower()

        task_id = (f'{service_prefix}-td-{topic}').replace('.','-')
        log_id = f'{exchnage_name}ServicesLogGroup'
        log_group_name = (f'/ecs/{service_prefix}-{topic}-log-group').replace('.','-')
        container_id = (f'{service_prefix}-{topic}-container').replace('.','-')
        stream_prefix = "ecs"

        task_definition = ecs.FargateTaskDefinition( self, task_id,
                cpu=256, memory_limit_mib=512)

        repo = ecr.Repository.from_repository_arn(self, f'{service_prefix}-repo', repo_arn)

        image = ecs.ContainerImage.from_ecr_repository(repo)
        access_key_id       = os.environ["EXCHANGE_ACCESS_KEY_ID"]
        access_secret_key   = os.environ["EXCHANGE_SECRET_ACCESS_KEY"]
        environment = {
                    "EXCHANGE": exchnage_name,
                    "C_BINARY_PATH": binary_path,
                    "TOPIC": topic,
                    "AWS_ACCESS_KEY_ID": access_key_id,
                    "AWS_SECRET_ACCESS_KEY": access_secret_key,
                    "BUCKET_NAME": bucket.bucket_name
                }
        
        logDetail = logs.LogGroup(self, log_id, log_group_name=log_group_name, retention=logs.RetentionDays.SIX_MONTHS, removal_policy=cdk.RemovalPolicy.DESTROY)
        logging = ecs.LogDriver.aws_logs(stream_prefix = stream_prefix, log_group=logDetail)
        container = task_definition.add_container( container_id, image=image,
                environment=environment,
                logging = logging
                )

        service = ecs.FargateService(self, id,
            task_definition=task_definition,
            assign_public_ip=True,
            cluster=cluster)