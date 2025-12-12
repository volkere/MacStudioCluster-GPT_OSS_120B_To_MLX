# GitHub Repository erstellen und pushen

## Schritt 1: GitHub Repository erstellen

1. Gehe zu https://github.com/new
2. Repository-Name: `MacStudioCluster-GPT_OSS_120B_To_MLX`
3. Beschreibung: "GPT-OSS-120B to MLX conversion for Apple Silicon - Face Tagging System"
4. Wähle **Private** oder **Public** (je nach Präferenz)
5. **NICHT** "Initialize with README" ankreuzen (wir haben bereits einen)
6. Klicke auf **"Create repository"**

## Schritt 2: Repository pushen

Führe die folgenden Befehle aus:

```bash
cd /Users/blaubaer/Documents/Aphrodite/MacStudioCluster

# Remote hinzufügen (ersetze USERNAME mit deinem GitHub-Username)
git remote add origin https://github.com/USERNAME/MacStudioCluster-GPT_OSS_120B_To_MLX.git

# Oder mit SSH (wenn SSH-Keys konfiguriert sind):
# git remote add origin git@github.com:USERNAME/MacStudioCluster-GPT_OSS_120B_To_MLX.git

# Branch auf main setzen (falls nicht bereits geschehen)
git branch -M main

# Pushen
git push -u origin main
```

## Schritt 3: Submodule pushen

Falls exo als Submodule hinzugefügt wurde:

```bash
# Submodule-Commits pushen
git push --recurse-submodules=on-demand
```

## Alternative: Mit GitHub CLI

Falls `gh` CLI installiert ist:

```bash
# Repository erstellen und pushen in einem Schritt
gh repo create MacStudioCluster-GPT_OSS_120B_To_MLX --public --source=. --remote=origin --push
```

## Troubleshooting

### Problem: "Repository not found"
- Prüfe, ob der Repository-Name korrekt ist
- Prüfe, ob du die richtigen Berechtigungen hast

### Problem: "Authentication failed"
- Verwende Personal Access Token statt Passwort
- Oder konfiguriere SSH-Keys

### Problem: "Submodule not pushed"
```bash
git push --recurse-submodules=on-demand
```

## Nach dem Push

Das Repository sollte jetzt unter:
`https://github.com/USERNAME/MacStudioCluster-GPT_OSS_120B_To_MLX`

verfügbar sein.

