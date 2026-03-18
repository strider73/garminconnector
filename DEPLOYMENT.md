# Deployment Process

## Architecture

```
[Local Mac] → git push → [GitHub] → webhook → [Jenkins] → build Docker image
                                                    ↓
                                              [strider-pi]
                                              ├── Docker image (Python scripts)
                                              ├── ~/garminconnector/.claude/ (mounted volume)
                                              └── n8n triggers workflows via SSH
```

## Two things that need updating on the server

| What | Where | How it updates |
|------|-------|---------------|
| Python scripts | Inside Docker image | Jenkins rebuilds image after push |
| .claude/ files (commands, reference, templates, agents) | Host filesystem (mounted volume) | `git pull` on strider-pi |

Docker mounts `~/garminconnector/.claude/` into the container at `/app/.claude/`. So the container always uses the **host's** version of `.claude/` files, not what's baked into the image.

## Deploy Steps

### After pushing code changes:

1. **Push to GitHub**
   ```bash
   git add <files> && git commit -m "message" && git push
   ```

2. **Update server repo (git pull)**
   ```bash
   ssh strider@strider-pi.local "cd ~/garminconnector && git checkout -- . && git pull"
   ```
   This updates the `.claude/` mounted volume files. Required when you change:
   - `.claude/commands/` (coaching prompts)
   - `.claude/reference/` (athlete data)
   - `.claude/templates/` (baseline templates)
   - `.claude/agents/` (agent scripts)

3. **Rebuild Docker image**
   ```bash
   ssh strider@strider-pi.local "cd ~/garminconnector && docker compose build --no-cache garmin-report"
   ```
   This updates the Python scripts inside the image. Required when you change:
   - `n8n-workflows/*/` (workflow Python scripts)
   - `garminconnect/` (Garmin API client)
   - `Dockerfile`

### Quick deploy (does both):
```bash
ssh strider@strider-pi.local "cd ~/garminconnector && git checkout -- . && git pull && docker compose build --no-cache garmin-report"
```

### Jenkins (automated but incomplete)
Jenkins auto-triggers on push via GitHub webhook and rebuilds the Docker image. However:
- Jenkins runs on `jenkins-agent` (Docker container on strider-pi)
- It builds the image in its own workspace, NOT in `~/garminconnector`
- The `git pull` stage in Jenkinsfile needs SSH from jenkins container to host (not yet working)
- **For now: run the quick deploy command manually after pushing**

## Testing

### Local testing (before push)
Use slash commands to test each workflow locally:
```
/n8n-daily-report-930pm
/n8n-morning-readiness-8am
/n8n-store-daily-metrics-9pm
/n8n-hr-health-monitor-3h
/n8n-weekly-trainer-report-thu-8am
```

### Server testing (after deploy)
Test from the n8n UI — click "Test Workflow" for each workflow. Or check latest executions:
- Store Daily Metrics: runs at 9pm daily
- Daily Report: runs at 9:30pm daily
- Morning Readiness: runs at 8am daily (Sat 9am)
- HR Health Monitor: runs every 3 hours
- Weekly Trainer Report: runs Thursday 8am

## What changes require what

| Changed file | git pull needed? | Docker rebuild needed? |
|-------------|-----------------|----------------------|
| `n8n-workflows/*.py` | No | Yes |
| `.claude/commands/*.md` | Yes | No |
| `.claude/reference/*.md` | Yes | No |
| `.claude/templates/*.md` | Yes | No |
| `.claude/agents/**` | Yes | No |
| `garminconnect/*.py` | No | Yes |
| `Dockerfile` | No | Yes |
| `docker-compose.yml` | Yes | Yes |
| `Jenkinsfile` | No | No (Jenkins reads from GitHub) |
| n8n workflow (in n8n UI) | No | No |
