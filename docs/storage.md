S3 Media Storage (production)
--------------------------------

This project serves media from local storage in development. For production, configure S3 via `django-storages`.

1. Install dependencies:

```bash
pip install django-storages[boto3] boto3
```

2. Set environment variables:

- `USE_S3=True`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_REGION_NAME` (optional)

3. In production settings ensure `DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'`.

4. Set up proper IAM permissions and CORS settings on the S3 bucket.

Note: For local testing keep `USE_S3=False` so media are stored under `backend/media/`.
