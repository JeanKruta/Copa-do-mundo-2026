# Atualiza a tabela em produção.
# Uso: clique direito > "Executar com PowerShell", ou no terminal: .\atualizar.ps1
#
# Passos: valida a CHAVE_ACESSO do .env -> calcula os JSON -> envia para o GitHub.
# O resultados.csv e o .env NÃO sobem (estão no .gitignore).

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# ---- 1. Lê a chave do .env ----
if (-not (Test-Path ".env")) {
    Write-Host "ERRO: arquivo .env não encontrado. Crie um a partir do .env.example." -ForegroundColor Red
    exit 1
}

$chaveCorreta = $null
foreach ($linha in Get-Content ".env") {
    $l = $linha.Trim()
    if ($l -eq "" -or $l.StartsWith("#")) { continue }
    if ($l -match "^CHAVE_ACESSO\s*=\s*(.+)$") {
        $chaveCorreta = $Matches[1].Trim()
    }
}

if ([string]::IsNullOrWhiteSpace($chaveCorreta)) {
    Write-Host "ERRO: CHAVE_ACESSO não definida no .env." -ForegroundColor Red
    exit 1
}

# ---- 2. Pede e valida a chave ----
$entrada = Read-Host "Digite a chave de acesso"
if ($entrada -ne $chaveCorreta) {
    Write-Host "Chave incorreta. Atualização cancelada." -ForegroundColor Red
    exit 1
}
Write-Host "Chave OK." -ForegroundColor Green

# ---- 3. Calcula os JSON ----
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) {
    Write-Host "ERRO: Python não encontrado. Instale em https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

Write-Host "Calculando classificação..." -ForegroundColor Cyan
& $python.Source (Join-Path $PSScriptRoot "fonte\gerar.py")
if ($LASTEXITCODE -ne 0) {
    Write-Host "Falha ao gerar os dados. Corrija o fonte\resultados.csv e tente de novo." -ForegroundColor Red
    exit 1
}

# ---- 4. Envia para o GitHub (somente arquivos públicos) ----
Write-Host "Enviando para produção..." -ForegroundColor Cyan
git add docs
git commit -m ("Atualiza placares - {0}" -f (Get-Date -Format "dd/MM/yyyy HH:mm"))
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nada novo para enviar (nenhuma mudança nos placares)." -ForegroundColor Yellow
    exit 0
}
git push

Write-Host "Pronto! Em ~1 minuto o site no ar estará atualizado." -ForegroundColor Green
