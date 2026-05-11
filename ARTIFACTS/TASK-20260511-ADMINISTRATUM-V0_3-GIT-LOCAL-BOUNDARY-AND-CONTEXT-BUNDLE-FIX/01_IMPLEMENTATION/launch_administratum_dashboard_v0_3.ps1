$ErrorActionPreference = "Stop"

$RepoRoot = "E:\IMPERIUM"
$Port = 8793
$StateRoot = "E:\IMPERIUM\CURRENT_STATE\ADMINISTRATUM_ANALYZER_V0_3"
$BundleRoot = "E:\IMPERIUM\CHAT_COMPILATIONS_LOCAL"
$GitHubUrl = "https://github.com/SoulsLike2313/Imperium-"

New-Item -ItemType Directory -Force $StateRoot, $BundleRoot | Out-Null

function Write-Utf8Bom {
    param([string]$Path, [string]$Content)

    $Dir = Split-Path -Parent $Path
    if ($Dir -and !(Test-Path $Dir)) {
        New-Item -ItemType Directory -Force $Dir | Out-Null
    }

    $Utf8Bom = New-Object System.Text.UTF8Encoding($true)
    [System.IO.File]::WriteAllText($Path, $Content.Replace("`n","`r`n"), $Utf8Bom)
}

function Invoke-Git {
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$GitArgs
    )

    $Output = (& git -C $RepoRoot @GitArgs 2>&1 | Out-String).Trim()

    if ($LASTEXITCODE -ne 0) {
        return "GIT_ERROR exit=$LASTEXITCODE args=$($GitArgs -join ' ') output=$Output"
    }

    return $Output
}

function Send-Text {
    param($Context, [string]$Text, [string]$ContentType)

    $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $Context.Response.ContentType = $ContentType
    $Context.Response.ContentEncoding = [System.Text.Encoding]::UTF8
    $Context.Response.ContentLength64 = $Bytes.Length
    $Context.Response.OutputStream.Write($Bytes, 0, $Bytes.Length)
    $Context.Response.OutputStream.Close()
}

function Send-Json {
    param($Context, $Object)

    $Json = $Object | ConvertTo-Json -Depth 20
    Send-Text -Context $Context -Text $Json -ContentType "application/json; charset=utf-8"
}

function Get-LocalOnlyInventory {
    $Paths = @(
        @{ name="ARCHIVE"; path="E:\IMPERIUM\ARCHIVE"; purpose="Old bulk archive; must stay local unless curated." },
        @{ name="SSH_COMMAND_LIBRARY"; path="E:\IMPERIUM\SSH_COMMAND_LIBRARY"; purpose="Private command/address library; never commit raw contents." },
        @{ name="CHAT_COMPILATIONS_LOCAL"; path="E:\IMPERIUM\CHAT_COMPILATIONS_LOCAL"; purpose="Local-only handoff bundles for ChatGPT/Logos." },
        @{ name="PRIVATE_CONTEXT_LOCAL"; path="E:\IMPERIUM\PRIVATE_CONTEXT_LOCAL"; purpose="Private local context; not Git." },
        @{ name="RUNTIME_LOCAL"; path="E:\IMPERIUM\RUNTIME_LOCAL"; purpose="Runtime scratch/local state; not Git." },
        @{ name="BUNDLES_LOCAL"; path="E:\IMPERIUM\BUNDLES_LOCAL"; purpose="Local transfer bundles; not Git." },
        @{ name="OBSERVED_THRONE_COPY"; path="E:\IMPERIUM\OBSERVED\THRONE_REPO_COPY"; purpose="Observed legacy repo copy; not Git." },
        @{ name="OBSERVED_VM3_COPY"; path="E:\IMPERIUM\OBSERVED\VM3_REPO_COPY"; purpose="Observed legacy repo copy; not Git." }
    )

    $Result = @()

    foreach ($P in $Paths) {
        $Exists = Test-Path $P.path
        $FileCount = 0
        $TotalBytes = 0

        if ($Exists) {
            $Files = @(Get-ChildItem $P.path -Recurse -File -ErrorAction SilentlyContinue)
            $FileCount = $Files.Count
            $TotalBytes = ($Files | Measure-Object Length -Sum).Sum
            if ($null -eq $TotalBytes) { $TotalBytes = 0 }
        }

        $Result += [ordered]@{
            name = $P.name
            path = $P.path
            purpose = $P.purpose
            exists = $Exists
            file_count = $FileCount
            total_bytes = [int64]$TotalBytes
            git_policy = "LOCAL_ONLY_OR_INDEX_ONLY"
        }
    }

    return $Result
}

function Run-AdministratumAnalysis {
    $Ts = Get-Date -Format "yyyyMMdd_HHmmss"

    $LocalHead = Invoke-Git -GitArgs @("rev-parse","HEAD")
    $Branch = Invoke-Git -GitArgs @("branch","--show-current")
    $OriginHead = Invoke-Git -GitArgs @("rev-parse","origin/$Branch")
    $RemoteLine = Invoke-Git -GitArgs @("ls-remote","origin","refs/heads/$Branch")
    $RemoteHead = ""
    if ($RemoteLine) {
        $RemoteHead = ($RemoteLine -split "\s+")[0]
    }

    $RemoteUrl = Invoke-Git -GitArgs @("config","--get","remote.origin.url")
    $StatusShort = Invoke-Git -GitArgs @("status","--short")
    $TrackedRaw = Invoke-Git -GitArgs @("ls-files")
    $TrackedFiles = @($TrackedRaw -split "`r?`n" | Where-Object { $_.Trim() -ne "" })

    $IgnoredSuspicious = Invoke-Git -GitArgs @("status","--ignored","--short")
    $SuspiciousPattern = "SSH_COMMAND_LIBRARY|id_rsa|id_ed25519|\.pem$|\.ppk$|\.key$|\.env$|token|secret|password|credential|cookie|session|known_hosts|authorized_keys"
    $SuspiciousLines = @($IgnoredSuspicious -split "`r?`n" | Where-Object { $_ -match $SuspiciousPattern })

    $LocalInventory = Get-LocalOnlyInventory

    $GitSynced = (
        ($LocalHead -ne "") -and
        ($OriginHead -ne "") -and
        ($RemoteHead -ne "") -and
        ($LocalHead -eq $OriginHead) -and
        ($LocalHead -eq $RemoteHead)
    )

    $WorktreeClean = ([string]::IsNullOrWhiteSpace($StatusShort))

    $Verdict = if ($GitSynced -and $WorktreeClean) {
        "PUBLIC_MEMORY_READY_LOCAL_CONTEXT_REQUIRED"
    } elseif (!$GitSynced) {
        "GIT_NOT_SYNCED_REVIEW_REQUIRED"
    } else {
        "WORKTREE_NOT_CLEAN_REVIEW_REQUIRED"
    }

    $Analysis = [ordered]@{
        schema_version = "ADMINISTRATUM_GIT_LOCAL_ANALYSIS_V0_3"
        generated_at = (Get-Date).ToString("o")
        repo_root = $RepoRoot
        github_url = $GitHubUrl
        branch = $Branch
        remote_url = $RemoteUrl
        local_head = $LocalHead
        origin_head = $OriginHead
        remote_head = $RemoteHead
        git_synced = $GitSynced
        worktree_clean = $WorktreeClean
        status_short = $StatusShort
        tracked_file_count = $TrackedFiles.Count
        local_only_inventory = $LocalInventory
        suspicious_local_or_ignored_paths = $SuspiciousLines
        verdict = $Verdict
        next_action = "BUILD_MISSING_LOCAL_CONTEXT_BUNDLE"
    }

    $AnalysisPath = Join-Path $StateRoot "GIT_LOCAL_ANALYSIS.json"
    Write-Utf8Bom $AnalysisPath ($Analysis | ConvertTo-Json -Depth 20)

    $VerdictMd = @"
# Administratum Verdict v0.3

Generated:
$($Analysis.generated_at)

GitHub:
$GitHubUrl

Branch:
$Branch

Local HEAD:
$LocalHead

Origin HEAD:
$OriginHead

Remote HEAD:
$RemoteHead

Git synced:
$GitSynced

Worktree clean:
$WorktreeClean

Tracked public files:
$($TrackedFiles.Count)

Verdict:
$Verdict

Meaning:
- GitHub is the public code/memory source.
- Local-only bundle must provide private/local context that must not be committed.
- Bundle plus GitHub link is the intended full handoff context.

Next action:
$($Analysis.next_action)
"@

    Write-Utf8Bom (Join-Path $StateRoot "VERDICT.md") $VerdictMd

    return $Analysis
}

function Build-MissingLocalBundle {
    $AnalysisPath = Join-Path $StateRoot "GIT_LOCAL_ANALYSIS.json"
    if (!(Test-Path $AnalysisPath)) {
        $null = Run-AdministratumAnalysis
    }

    $Analysis = Get-Content -Encoding UTF8 $AnalysisPath -Raw | ConvertFrom-Json

    $Ts = Get-Date -Format "yyyyMMdd_HHmmss"
    $BuildRoot = Join-Path $BundleRoot "_BUILD\FULL_IMPERIUM_CONTEXT_$Ts"
    $ZipPath = Join-Path $BundleRoot "FULL_IMPERIUM_CONTEXT_$Ts.zip"

    if (Test-Path $BuildRoot) {
        Remove-Item $BuildRoot -Recurse -Force
    }

    New-Item -ItemType Directory -Force $BuildRoot | Out-Null

    Copy-Item $StateRoot (Join-Path $BuildRoot "ADMINISTRATUM_ANALYZER_V0_3") -Recurse -Force

    Write-Utf8Bom (Join-Path $BuildRoot "GITHUB_REPOSITORY_LINK.txt") $GitHubUrl

    $Readme = @"
# Full Imperium Context Bundle

This bundle is local-only and must not be committed to Git.

Use together with GitHub repository:
$GitHubUrl

Purpose:
- GitHub provides public code and public project memory.
- This bundle provides local-only context indexes, analyzer reports, current Git/local boundary, and handoff orientation.

Policy:
- This bundle does not intentionally include raw SSH private keys, passwords, tokens, or full SSH_COMMAND_LIBRARY contents.
- If raw private operational files are required, Owner must provide them explicitly in a separate manual bundle.

Recommended use in new chat:
1. Give Logos-Prime the GitHub repository link.
2. Upload this zip.
3. Ask Logos-Prime to read Git first, then use this bundle to understand local/private boundaries.
"@

    Write-Utf8Bom (Join-Path $BuildRoot "README_FOR_LOGOS_PRIME.md") $Readme

    $Boundary = [ordered]@{
        schema_version = "ADMINISTRATUM_PUBLIC_PRIVATE_BOUNDARY_V0_3"
        github_url = $GitHubUrl
        public_memory = "GitHub repository"
        local_bundle = $ZipPath
        local_only_inventory = $Analysis.local_only_inventory
        rule = "GitHub plus this local-only bundle is the full handoff context. Do not commit this zip."
        generated_at = (Get-Date).ToString("o")
    }

    Write-Utf8Bom (Join-Path $BuildRoot "PUBLIC_PRIVATE_BOUNDARY.json") ($Boundary | ConvertTo-Json -Depth 20)

    if (Test-Path $ZipPath) {
        Remove-Item $ZipPath -Force
    }

    Compress-Archive -Path (Join-Path $BuildRoot "*") -DestinationPath $ZipPath -Force

    $Hash = (Get-FileHash -Algorithm SHA256 $ZipPath).Hash.ToLower()
    $Size = (Get-Item $ZipPath).Length

    $Receipt = [ordered]@{
        schema_version = "ADMINISTRATUM_CONTEXT_BUNDLE_RECEIPT_V0_3"
        zip_path = $ZipPath
        sha256 = $Hash
        size_bytes = $Size
        github_url = $GitHubUrl
        committed_to_git = $false
        status = "PASS_WITH_LIMITATIONS"
        limitations = @(
            "Local-only context bundle.",
            "Does not include raw secrets by default.",
            "Use with GitHub repository link for full context."
        )
        generated_at = (Get-Date).ToString("o")
    }

    Write-Utf8Bom (Join-Path $StateRoot "LATEST_CONTEXT_BUNDLE_RECEIPT.json") ($Receipt | ConvertTo-Json -Depth 20)

    return $Receipt
}

$Html = @"
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>IMPERIUM · Administratum Dashboard v0.3</title>
<style>
body {
  margin: 0;
  background: #070b15;
  color: #eef4ff;
  font-family: Segoe UI, Arial, sans-serif;
}
.wrap {
  max-width: 1180px;
  margin: 0 auto;
  padding: 28px;
}
.hero {
  border: 1px solid #26395e;
  background: linear-gradient(135deg, #0d1426, #111a31);
  border-radius: 24px;
  padding: 28px;
  margin-bottom: 18px;
}
h1 {
  margin: 0 0 10px 0;
  font-size: 40px;
}
.sub {
  color: #a9bce8;
  font-size: 16px;
  line-height: 1.55;
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.card {
  border: 1px solid #26395e;
  background: #0d1426;
  border-radius: 18px;
  padding: 18px;
}
.status {
  border: 1px solid #26395e;
  background: #090f1d;
  border-radius: 18px;
  padding: 18px;
  margin-top: 18px;
}
button {
  background: #13a9b8;
  color: white;
  border: 0;
  border-radius: 14px;
  padding: 14px 20px;
  font-weight: 700;
  cursor: pointer;
  margin-right: 10px;
  margin-top: 14px;
}
button.secondary {
  background: #5a3df0;
}
button:disabled {
  background: #263044;
  color: #8c99b7;
  cursor: not-allowed;
}
pre {
  white-space: pre-wrap;
  overflow: auto;
  background: #050912;
  border: 1px solid #1f2f4e;
  border-radius: 14px;
  padding: 16px;
  color: #dce8ff;
  max-height: 360px;
}
.good { color: #7dffbd; }
.bad { color: #ff8d8d; }
.warn { color: #ffd27d; }
.modal {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.72);
  z-index: 10;
  align-items: center;
  justify-content: center;
}
.panel {
  width: 760px;
  max-width: 92vw;
  border: 1px solid #3b58ff;
  background: #0b1020;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 0 60px rgba(76, 102, 255, .35);
}
.pulse {
  width: 14px;
  height: 14px;
  background: #13a9b8;
  border-radius: 50%;
  display: inline-block;
  margin-right: 8px;
  animation: pulse 1s infinite;
}
@keyframes pulse {
  0% { transform: scale(1); opacity: .55; }
  50% { transform: scale(1.5); opacity: 1; }
  100% { transform: scale(1); opacity: .55; }
}
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <h1>Administratum · Git / Local Boundary v0.3</h1>
    <div class="sub">
      Администратум проверяет публичную память GitHub и локальную память ПК.
      После анализа он собирает недостающий local-only bundle.
      Итоговая формула: <b>GitHub repository link + local context bundle = full IMPERIUM handoff context</b>.
    </div>
    <button onclick="runAnalysis()">Build Pack: сначала проверить Git и Local</button>
    <button id="buildBtn" class="secondary" onclick="buildBundle()" disabled>Собрать недостающее в bundle</button>
  </div>

  <div class="grid">
    <div class="card">
      <h2>GitHub / public memory</h2>
      <p>Публичный код, scripts, dashboards, receipts, artifacts, docs.</p>
      <pre id="gitBox">not checked yet</pre>
    </div>
    <div class="card">
      <h2>Local-only memory</h2>
      <p>Локальные индексы, приватный контекст, bundle-зона, runtime, архивы.</p>
      <pre id="localBox">not checked yet</pre>
    </div>
  </div>

  <div class="status">
    <h2>Verdict</h2>
    <pre id="verdictBox">not checked yet</pre>
  </div>

  <div class="status">
    <h2>Result</h2>
    <pre id="resultBox">not run yet</pre>
  </div>
</div>

<div id="modal" class="modal">
  <div class="panel">
    <h2><span class="pulse"></span><span id="modalTitle">Administratum is working</span></h2>
    <pre id="modalLog">starting...</pre>
  </div>
</div>

<script>
function showModal(title) {
  document.getElementById("modalTitle").innerText = title;
  document.getElementById("modalLog").innerText = "";
  document.getElementById("modal").style.display = "flex";
}
function logModal(text) {
  const box = document.getElementById("modalLog");
  box.innerText += text + "\n";
}
function hideModalLater() {
  setTimeout(() => {
    document.getElementById("modal").style.display = "none";
  }, 900);
}
async function runAnalysis() {
  showModal("Administratum checks Git and local state");
  logModal("1. Checking Git HEAD / origin / remote...");
  logModal("2. Checking worktree status...");
  logModal("3. Checking local-only directories...");
  logModal("4. Checking suspicious local/ignored names...");

  const res = await fetch("/api/analyze", { method: "POST" });
  const data = await res.json();

  document.getElementById("gitBox").innerText =
    "GitHub: " + data.github_url + "\n" +
    "Branch: " + data.branch + "\n" +
    "Local HEAD: " + data.local_head + "\n" +
    "Origin HEAD: " + data.origin_head + "\n" +
    "Remote HEAD: " + data.remote_head + "\n" +
    "Git synced: " + data.git_synced + "\n" +
    "Worktree clean: " + data.worktree_clean + "\n" +
    "Tracked public files: " + data.tracked_file_count;

  document.getElementById("localBox").innerText =
    JSON.stringify(data.local_only_inventory, null, 2);

  document.getElementById("verdictBox").innerText =
    "Verdict: " + data.verdict + "\n" +
    "Next action: " + data.next_action + "\n\n" +
    "Suspicious local/ignored paths:\n" +
    JSON.stringify(data.suspicious_local_or_ignored_paths, null, 2);

  if (data.next_action === "BUILD_MISSING_LOCAL_CONTEXT_BUNDLE") {
    document.getElementById("buildBtn").disabled = false;
    logModal("PASS: analysis complete. Bundle button enabled.");
  } else {
    document.getElementById("buildBtn").disabled = true;
    logModal("BLOCKED: review Git/worktree before bundle.");
  }

  hideModalLater();
}
async function buildBundle() {
  showModal("Administratum builds local context bundle");
  logModal("1. Copying analyzer reports...");
  logModal("2. Writing GitHub link...");
  logModal("3. Writing public/private boundary...");
  logModal("4. Compressing local-only handoff bundle...");

  const res = await fetch("/api/build", { method: "POST" });
  const data = await res.json();

  document.getElementById("resultBox").innerText =
    "Bundle path: " + data.zip_path + "\n" +
    "SHA256: " + data.sha256 + "\n" +
    "Size bytes: " + data.size_bytes + "\n" +
    "GitHub: " + data.github_url + "\n" +
    "Status: " + data.status;

  logModal("PASS: bundle created.");
  hideModalLater();
}
</script>
</body>
</html>
"@

$Listener = New-Object System.Net.HttpListener
$Prefix = "http://127.0.0.1:$Port/"
$Listener.Prefixes.Add($Prefix)
$Listener.Start()

Start-Process $Prefix

Write-Host "Administratum Dashboard v0.3 running:"
Write-Host $Prefix
Write-Host "Press Ctrl+C to stop."

while ($Listener.IsListening) {
    $Context = $Listener.GetContext()
    $Path = $Context.Request.Url.AbsolutePath

    try {
        if ($Path -eq "/api/analyze") {
            $Result = Run-AdministratumAnalysis
            Send-Json -Context $Context -Object $Result
        }
        elseif ($Path -eq "/api/build") {
            $Result = Build-MissingLocalBundle
            Send-Json -Context $Context -Object $Result
        }
        else {
            Send-Text -Context $Context -Text $Html -ContentType "text/html; charset=utf-8"
        }
    }
    catch {
        $ErrorObject = [ordered]@{
            ok = $false
            error = $_.Exception.Message
            generated_at = (Get-Date).ToString("o")
        }
        Send-Json -Context $Context -Object $ErrorObject
    }
}