# Terraform with AWS SSO Helper Script
# Run this script before using terraform commands

# Set the AWS profile
$env:AWS_PROFILE = "terraform_practice"

Write-Host "🔐 Logging into AWS SSO..." -ForegroundColor Cyan
aws sso login --profile terraform_practice

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSO Login successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Your AWS Identity:" -ForegroundColor Yellow
    aws sts get-caller-identity --profile terraform_practice
    Write-Host ""
    Write-Host "✅ You can now run terraform commands:" -ForegroundColor Green
    Write-Host "   - terraform init" -ForegroundColor White
    Write-Host "   - terraform plan" -ForegroundColor White
    Write-Host "   - terraform apply" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ SSO Login failed. Please check your configuration." -ForegroundColor Red
}
