# PayPilot — PayPal Sandbox self-test (Windows PowerShell)
# ================================================================
# Script chay HOAN TOAN tren may cua ban.
# Client Secret KHONG BAO GIO roi khoi may ban.
# Chi gui lai phan RESULT cho tro ly (khong chua secret).
#
# Cach dung:
#   1. Mo PowerShell
#   2. Chay:  powershell -ExecutionPolicy Bypass -File sandbox-selftest.ps1
#   3. Lam theo huong dan tren man hinh

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "PayPilot PayPal Sandbox self-test" -ForegroundColor Cyan
Write-Host "Keys stay on YOUR machine. Only the RESULT is shared." -ForegroundColor DarkGray
Write-Host ""

# --- Nhap keys (chi tren may ban) ---
$clientId = Read-Host "1) Paste PayPal Sandbox Client ID"
$secStr = Read-Host "2) Paste PayPal Sandbox Client Secret" -AsSecureString
$clientSecret = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secStr))
$secStr = $null

$base = "https://api-m.sandbox.paypal.com"

try {
    # --- Buoc 1: lay access token ---
    Write-Host ""
    Write-Host "[1/3] Getting access token..." -ForegroundColor Yellow
    $pair = "${clientId}:${clientSecret}"
    $basic = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
    $tokenResp = Invoke-RestMethod -Uri "$base/v1/oauth2/token" -Method Post `
        -Headers @{ Authorization = "Basic $basic" } `
        -Body "grant_type=client_credentials" `
        -ContentType "application/x-www-form-urlencoded"
    $accessToken = $tokenResp.access_token
    Write-Host "      token OK" -ForegroundColor Green

    # --- Buoc 2: tao order $1.00 (tien ao sandbox) ---
    Write-Host "[2/3] Creating test order (USD 1.00, sandbox only)..." -ForegroundColor Yellow
    $orderBody = @{
        intent         = "CAPTURE"
        purchase_units = @(@{
                amount      = @{ currency_code = "USD"; value = "1.00" }
                description = "PayPilot sandbox self-test"
            })
        application_context = @{
            return_url  = "https://example.com/success"
            cancel_url  = "https://example.com/cancel"
            user_action = "PAY_NOW"
        }
    } | ConvertTo-Json -Depth 6

    $order = Invoke-RestMethod -Uri "$base/v2/checkout/orders" -Method Post `
        -Headers @{ Authorization = "Bearer $accessToken"; "Content-Type" = "application/json" } `
        -Body $orderBody
    Write-Host "      order created: $($order.id) [$($order.status)]" -ForegroundColor Green

    $approveUrl = ($order.links | Where-Object { $_.rel -eq "approve" }).href
    Write-Host ""
    Write-Host "      Mo URL nay tren trinh duyet, dang nhap bang" -ForegroundColor Cyan
    Write-Host "      tai khoan SANDBOX buyer (Dashboard > Sandbox > Accounts)," -ForegroundColor Cyan
    Write-Host "      bam Approve, roi quay lai day." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "      $approveUrl" -ForegroundColor White
    Write-Host ""
    Read-Host "      Nhan Enter sau khi da Approve"

    # --- Buoc 3: capture ---
    Write-Host "[3/3] Capturing payment..." -ForegroundColor Yellow
    $capture = Invoke-RestMethod `
        -Uri "$base/v2/checkout/orders/$($order.id)/capture" -Method Post `
        -Headers @{ Authorization = "Bearer $accessToken"; "Content-Type" = "application/json" } `
        -Body "{}"

    $capInfo = $capture.purchase_units[0].payments.captures[0]
    Write-Host ""
    Write-Host "===== RESULT (an toan de chia se) =====" -ForegroundColor Cyan
    Write-Host "order_id:       $($order.id)"
    Write-Host "capture_status: $($capture.status)"
    if ($capInfo) {
        Write-Host "amount:         $($capInfo.amount.value) $($capInfo.amount.currency_code)"
        Write-Host "capture_id:     $($capInfo.id)"
    }
    Write-Host "=======================================" -ForegroundColor Cyan
}
catch {
    Write-Host ""
    Write-Host "LOI:" -ForegroundColor Red
    $msg = $_.Exception.Message
    if ($_.ErrorDetails.Message) { $msg += " | " + $_.ErrorDetails.Message }
    # Khong bao gio in secret: chi cat ngan thong diep loi
    Write-Host ($msg.Substring(0, [Math]::Min($msg.Length, 500)))
}
finally {
    # Xoa sach bien nhay cam khoi bo nho
    $clientId = $null; $clientSecret = $null; $accessToken = $null
    $basic = $null; $pair = $null
    [GC]::Collect()
    Write-Host ""
    Write-Host "Da xoa keys khoi bo nho phien nay." -ForegroundColor DarkGray
}
