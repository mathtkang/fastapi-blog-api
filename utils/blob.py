from boto3.session import Session
from mypy_boto3_s3.client import S3Client


def get_blob_client() -> S3Client:
    return Session().client("s3")