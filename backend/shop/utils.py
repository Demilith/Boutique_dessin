from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import boto3
from django.conf import settings
from datetime import datetime


def upload_buffer_to_s3(buffer, key, content_type='application/pdf'):
    # buffer: file-like object positioned at start
    s3 = boto3.client(
        's3',
        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', None)
    )
    bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
    if not bucket:
        raise RuntimeError('S3 bucket not configured')
    buffer.seek(0)
    s3.put_object(Bucket=bucket, Key=key, Body=buffer.read(), ContentType=content_type)
    # construct public url (assuming public-read or bucket policy)
    region = getattr(settings, 'AWS_S3_REGION_NAME', '')
    if region:
        return f'https://{bucket}.s3.{region}.amazonaws.com/{key}'
    return f'https://{bucket}.s3.amazonaws.com/{key}'

def generate_invoice_pdf(order):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    # Header with optional logo and titles
    logo_path = getattr(settings, 'INVOICE_LOGO_PATH', None)
    if logo_path:
        try:
            c.drawImage(logo_path, 40, height - 100, width=120, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    c.setFont('Helvetica-Bold', 18)
    c.drawString(40, height - 120, 'Invoice')

    c.setFont('Helvetica', 11)
    y = height - 150
    c.drawString(40, y, f'Date: {datetime.utcnow().strftime("%Y-%m-%d")}')
    y -= 18
    c.drawString(40, y, f'Order ID: {order.id}')
    y -= 24

    # Platform billing details (from settings)
    platform_name = getattr(settings, 'PLATFORM_BILLING_NAME', None)
    platform_address = getattr(settings, 'PLATFORM_BILLING_ADDRESS', None)
    platform_vat = getattr(settings, 'PLATFORM_BILLING_VAT', None)
    if platform_name:
        c.setFont('Helvetica-Bold', 10)
        c.drawString(40, y, platform_name)
        y -= 12
    if platform_address:
        c.setFont('Helvetica', 9)
        for line in platform_address.split('\n'):
            c.drawString(40, y, line)
            y -= 12
    if platform_vat:
        c.drawString(40, y, f'VAT: {platform_vat}')
        y -= 18

    # Artist billing information
    if order.product and order.product.artist:
        artist = order.product.artist
        c.setFont('Helvetica-Bold', 11)
        c.drawString(300, height - 150, 'Seller:')
        c.setFont('Helvetica', 10)
        ay = height - 168
        c.drawString(300, ay, artist.display_name or '')
        ay -= 12
        if artist.user and artist.user.email:
            c.drawString(300, ay, artist.user.email)
            ay -= 12
        # leave a small gap
        y = min(y, ay - 12)

    # Line items
    if order.product:
        c.setFont('Helvetica-Bold', 12)
        c.drawString(40, y, 'Item')
        c.drawString(300, y, 'Qty')
        c.drawString(360, y, 'Unit')
        c.drawString(430, y, 'Amount')
        y -= 16
        c.setFont('Helvetica', 11)
        c.drawString(40, y, order.product.title)
        c.drawString(300, y, '1')
        c.drawString(360, y, f'€{(order.amount_cents/100):.2f}')
        c.drawString(430, y, f'€{(order.amount_cents/100):.2f}')
        y -= 22

    # Taxes placeholder (no tax calculations by default)
    tax_percent = getattr(settings, 'INVOICE_TAX_PERCENT', 0)
    subtotal = order.amount_cents/100
    tax_amount = subtotal * (tax_percent / 100.0)
    total = subtotal + tax_amount

    c.drawString(360, y, 'Subtotal:')
    c.drawString(430, y, f'€{subtotal:.2f}')
    y -= 18
    if tax_percent:
        c.drawString(360, y, f'Tax ({tax_percent}%):')
        c.drawString(430, y, f'€{tax_amount:.2f}')
        y -= 18
    c.setFont('Helvetica-Bold', 12)
    c.drawString(360, y, 'Total:')
    c.drawString(430, y, f'€{total:.2f}')

    y -= 40
    c.setFont('Helvetica', 10)
    # Buyer info
    if order.buyer_email:
        c.drawString(40, y, f'Buyer: {order.buyer_email}')
        y -= 14
    c.drawString(40, y, 'Thank you for your purchase!')

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
