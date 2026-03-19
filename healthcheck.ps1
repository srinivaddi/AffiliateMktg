$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 15
if ($response.StatusCode -eq 200) {
    Write-Host "✅ Uvicorn API is running."
    exit
} else {
    Write-Host "❌ API responded with status code: $($response.StatusCode)"
    pause
}
