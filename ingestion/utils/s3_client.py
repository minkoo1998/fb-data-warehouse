import boto3, io
import pandas as pd

class S3Client:
    def __init__(self, bucket: str):
        self.bucket = bucket
        self.s3 = boto3.client("s3")

    def upload_csv(self, df: pd.DataFrame, key: str) -> None:
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=buf.getvalue())

    def upload_parquet(self, df: pd.DataFrame, key: str) -> None:
        buf = io.BytesIO()
        df.to_parquet(buf, index=False)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=buf.getvalue())

    def read_csv(self, key: str) -> pd.DataFrame:
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        return pd.read_csv(obj["Body"])