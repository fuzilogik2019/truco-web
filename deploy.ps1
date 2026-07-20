# Deploy del sitio de Truco Argentino a un bucket S3 con static website hosting.
# Uso:
#   .\deploy.ps1 -Bucket mi-bucket-truco [-Region us-east-1] [-Profile default] [-Create]
#
#   -Create : crea el bucket, habilita website hosting y aplica la policy publica.
#             Sin -Create solo sincroniza los archivos (deploy incremental).

param(
    [Parameter(Mandatory = $true)][string]$Bucket,
    [string]$Region = "us-east-1",
    [string]$Profile = "",
    [switch]$Create
)

$ErrorActionPreference = "Stop"
$profileArgs = @()
if ($Profile) { $profileArgs = @("--profile", $Profile) }

$siteDir = $PSScriptRoot

if ($Create) {
    Write-Host "Creando bucket s3://$Bucket en $Region..." -ForegroundColor Cyan
    if ($Region -eq "us-east-1") {
        aws s3api create-bucket --bucket $Bucket --region $Region @profileArgs
    } else {
        aws s3api create-bucket --bucket $Bucket --region $Region `
            --create-bucket-configuration LocationConstraint=$Region @profileArgs
    }

    Write-Host "Deshabilitando Block Public Access (requisito para website hosting publico)..." -ForegroundColor Cyan
    aws s3api put-public-access-block --bucket $Bucket @profileArgs `
        --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

    Write-Host "Aplicando bucket policy de lectura publica..." -ForegroundColor Cyan
    $policy = @{
        Version   = "2012-10-17"
        Statement = @(@{
            Sid       = "PublicReadGetObject"
            Effect    = "Allow"
            Principal = "*"
            Action    = "s3:GetObject"
            Resource  = "arn:aws:s3:::$Bucket/*"
        })
    } | ConvertTo-Json -Depth 5 -Compress
    $policyFile = Join-Path $env:TEMP "truco-web-policy.json"
    [System.IO.File]::WriteAllText($policyFile, $policy)
    aws s3api put-bucket-policy --bucket $Bucket --policy "file://$policyFile" @profileArgs

    Write-Host "Habilitando static website hosting..." -ForegroundColor Cyan
    aws s3 website "s3://$Bucket" --index-document index.html --error-document index.html @profileArgs
}

Write-Host "Sincronizando sitio..." -ForegroundColor Cyan
# Solo lo necesario llega al bucket. Estos excludes son el espejo de .gitignore:
# infra del repo (ps1/README/gitignore), herramientas locales (py/bat/aseprite)
# y los assets sin usar que quedan en local.
# Assets pixel art: inmutables en la practica -> cache largo. HTML: cache corto -> se actualiza.
aws s3 sync $siteDir "s3://$Bucket" @profileArgs `
    --exclude "*.ps1" --exclude "README.md" --exclude ".gitignore" --exclude "index.html" `
    --exclude "*.py" --exclude "*.bat" --exclude "*.aseprite" --exclude ".git/*" `
    --exclude "assets/logo4.png" `
    --exclude "assets/mesa_de_truco_top.png" `
    --exclude "assets/mc/lana_verde.png" --exclude "assets/mc/tablones.png" `
    --cache-control "public, max-age=604800" --delete

aws s3 cp (Join-Path $siteDir "index.html") "s3://$Bucket/index.html" @profileArgs `
    --cache-control "public, max-age=300" --content-type "text/html; charset=utf-8"

Write-Host ""
Write-Host "Listo. El sitio queda en:" -ForegroundColor Green
Write-Host "  http://$Bucket.s3-website-$Region.amazonaws.com" -ForegroundColor Yellow
if ($Region -eq "us-east-1") {
    Write-Host "  (en us-east-1 tambien puede ser http://$Bucket.s3-website.us-east-1.amazonaws.com)"
}
