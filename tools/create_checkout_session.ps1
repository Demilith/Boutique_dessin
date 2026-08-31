Param(
  [int]$ProductId = 1,
  [string]$Host = "http://localhost:8000"
)

$endpoint = "$Host/api/stripe/checkout/$ProductId/"
Write-Host "Creating checkout session for product $ProductId via $endpoint"
try {
  $res = Invoke-RestMethod -Method Post -Uri $endpoint -UseBasicParsing
  if ($res.url) {
    Write-Host "Checkout URL: $($res.url)"
    Start-Process $res.url
  } else {
    Write-Host "No session URL returned. Response:`n$res"
  }
} catch {
  Write-Host "Request failed: $_"
}
