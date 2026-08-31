from django.test import TestCase
from shop.utils import upload_buffer_to_s3
from io import BytesIO
from moto import mock_s3
import boto3
from django.conf import settings

class S3UploadTest(TestCase):
    @mock_s3
    def test_upload_buffer_to_s3_returns_url(self):
        # configure test bucket
        bucket = 'test-bucket'
        settings.AWS_STORAGE_BUCKET_NAME = bucket
        settings.AWS_S3_REGION_NAME = 'us-east-1'

        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket=bucket)

        buf = BytesIO(b'PDFDATA')
        url = upload_buffer_to_s3(buf, 'invoices/test.pdf')
        self.assertIn(bucket, url)
        self.assertTrue(url.endswith('invoices/test.pdf'))
