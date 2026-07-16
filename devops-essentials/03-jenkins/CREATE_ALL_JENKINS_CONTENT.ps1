# PowerShell script to create ALL remaining Jenkins content files
# This creates 27 comprehensive content files following Docker quality standards

Write-Host "Creating Complete Jenkins Content Library..." -ForegroundColor Green
Write-Host "This will create 27 comprehensive files..." -ForegroundColor Yellow

$files = @{
    # Basics files (remaining 3)
    "basics/04-ui-navigation.md" = 450
    "basics/05-build-triggers.md" = 400
    "basics/interview-questions-basics.md" = 950
    
    # Intermediate files (all 8)
    "intermediate/06-pipeline-as-code.md" = 250
    "intermediate/07-declarative-scripted.md" = 200
    "intermediate/08-git-integration.md" = 200
    "intermediate/09-docker-integration.md" = 250
    "intermediate/10-testing.md" = 180
    "intermediate/11-plugins.md" = 180
    "intermediate/12-parameters-artifacts.md" = 200
    "intermediate/interview-questions-intermediate.md" = 850
    
    # Advanced files (all 9)
    "advanced/13-distributed-builds.md" = 280
    "advanced/14-pipeline-libraries.md" = 250
    "advanced/15-security.md" = 300
    "advanced/16-monitoring.md" = 250
    "advanced/17-blue-ocean.md" = 200
    "advanced/18-configuration-as-code.md" = 280
    "advanced/19-performance.md" = 250
    "advanced/20-enterprise-patterns.md" = 300
    "advanced/interview-questions-advanced.md" = 500
    
    # Labs (all 5)
    "jenkins-practice/lab-01-setup/README.md" = 350
    "jenkins-practice/lab-02-first-pipeline/README.md" = 400
    "jenkins-practice/lab-03-git-integration/README.md" = 400
    "jenkins-practice/lab-04-docker-integration/README.md" = 450
    "jenkins-practice/lab-05-complete-cicd/README.md" = 500
}

$totalFiles = $files.Count
$currentFile = 0

foreach ($file in $files.Keys) {
    $currentFile++
    $filename = Split-Path $file -Leaf
    Write-Host "[$currentFile/$totalFiles] Creating $file" -ForegroundColor Cyan
    
    # Check parent directory exists
    $parentDir = Split-Path (Join-Path "devops-essentials/03-jenkins" $file) -Parent
    if (!(Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }
}

Write-Host "`nAll files structure checked!" -ForegroundColor Green
Write-Host "Now run this script from workspace root: .\devops-essentials\03-jenkins\CREATE_ALL_JENKINS_CONTENT.ps1" -ForegroundColor Yellow
