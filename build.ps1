param(
    [switch]$OneDir
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSCommandPath
Set-Location $projectRoot

function Get-PythonLauncher {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @{
            Command = "py"
            Args = @("-3")
        }
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @{
            Command = "python"
            Args = @()
        }
    }

    throw "Python 3 was not found in PATH."
}

$pythonLauncher = Get-PythonLauncher
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$distRoot = Join-Path $projectRoot "dist"
$iconPath = Join-Path $projectRoot "assets\creative_factory.ico"
$versionFilePath = Join-Path $projectRoot "packaging\windows_version_info.txt"
$targetPath = if ($OneDir) {
    Join-Path $distRoot "ModbusApp"
} else {
    Join-Path $distRoot "ModbusApp.exe"
}
$outputPath = if ($OneDir) {
    Join-Path $targetPath "ModbusApp.exe"
} else {
    $targetPath
}

function Remove-BuildTarget {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        return
    }

    $resolvedPath = (Resolve-Path -LiteralPath $Path).Path
    if (-not $resolvedPath.StartsWith($distRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a path outside the dist directory: $resolvedPath"
    }

    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            Remove-Item -LiteralPath $resolvedPath -Recurse -Force
            return
        } catch {
            if ($attempt -eq 5) {
                throw "Unable to replace '$resolvedPath'. Close any running copy of ModbusApp and run .\build.ps1 again."
            }
            Start-Sleep -Seconds 1
        }
    }
}

if (-not (Test-Path $venvPython)) {
    & $pythonLauncher.Command @($pythonLauncher.Args + @("-m", "venv", ".venv"))
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt -r requirements-build.txt
& $venvPython .\tools\generate_brand_assets.py
Remove-BuildTarget -Path $targetPath

$pyInstallerArgs = @(
    "-m",
    "PyInstaller",
    "--noconfirm",
    "--clean",
    "--distpath",
    "dist",
    "--workpath",
    "build",
    "--specpath",
    "build",
    "--windowed",
    "--name",
    "ModbusApp",
    "--icon",
    $iconPath,
    "--version-file",
    $versionFilePath,
    "--paths",
    "src"
)

if (-not $OneDir) {
    $pyInstallerArgs += "--onefile"
}

$pyInstallerArgs += "main.py"

& $venvPython @pyInstallerArgs

Write-Host "Build complete: $outputPath"
