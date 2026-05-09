param(
  [Parameter(Mandatory = $true)]
  [string]$BaseUrl,

  [Parameter(Mandatory = $true)]
  [string]$WebhookSecret,

  [Parameter(Mandatory = $true)]
  [string]$AppUserId,

  [ValidateSet("INITIAL_PURCHASE", "RENEWAL", "NON_RENEWING_PURCHASE", "PRODUCT_CHANGE", "UNCANCELLATION", "CANCELLATION", "EXPIRATION", "BILLING_ISSUE")]
  [string]$EventType = "INITIAL_PURCHASE",

  [switch]$DowngradeToFree
)

$normalizedBase = $BaseUrl.TrimEnd("/")
$targetPlan = if ($DowngradeToFree) { "free" } else { "premium" }
$eventTypeToSend = if ($DowngradeToFree) { "CANCELLATION" } else { $EventType }
$entitlementIds = if ($DowngradeToFree) { @() } else { @("premium") }

$headers = @{
  Authorization = "Bearer $WebhookSecret"
  "Content-Type" = "application/json"
}

$body = @{
  event = @{
    type = $eventTypeToSend
    app_user_id = $AppUserId
    entitlement_ids = $entitlementIds
  }
} | ConvertTo-Json -Depth 6

Write-Host "POST $normalizedBase/v1/webhooks/revenuecat"
Write-Host "User: $AppUserId | Expected Plan: $targetPlan"

try {
  $response = Invoke-RestMethod -Method Post -Uri "$normalizedBase/v1/webhooks/revenuecat" -Headers $headers -Body $body
  $response | ConvertTo-Json -Depth 10
} catch {
  Write-Error "Webhook call failed: $($_.Exception.Message)"
  if ($_.ErrorDetails.Message) {
    Write-Error $_.ErrorDetails.Message
  }
  exit 1
}

