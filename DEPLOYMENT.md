# Deployment Process

## Architecture

```
[Local Mac] → git push → [GitHub] → webhook → [Jenkins on strider-pi]
                                                    │
                                                    ├── Stage 1: SSH to host → git pull
                                                    │   (updates .claude/ mounted volume)
                                                    │
                                                    └── Stage 2: docker compose build
                                                        (updates Python scripts in image)
                                                    │
                                              [n8n on strider-pi]
                                              triggers workflows on schedule via SSH → Docker
```

## Fully Automated — Just Push

Everything is automated. After `git push`, Jenkins handles both:

1. **`git pull` on host** — updates `.claude/` files (commands, reference, templates, agents) that Docker mounts as a volume
2. **Docker image rebuild** — updates Python scripts (`n8n-workflows/`) and Garmin client (`garminconnect/`) baked into the image

No manual SSH or commands needed on the server.

## Why Two Updates Are Needed

Docker mounts `~/garminconnector/.claude/` from the host filesystem into the container at `/app/.claude/`. This is necessary because:

- The `update_baselines.py` script regenerates reference files every night at 9pm
- Docker containers are disposable (`--rm`) — files inside are lost after each run
- The mount persists data between container runs so the next workflow reads fresh baselines

This means the container gets files from **two sources**:
| Source | What | Updated by |
|--------|------|-----------|
| Docker image (`COPY`) | Python scripts, garminconnect library | `docker compose build` |
| Host mount (`volumes:`) | .claude/ (commands, reference, templates, agents) | `git pull` |

## How Jenkins Makes This Work

Jenkins runs inside a Docker container (`jenkins-agent`) on strider-pi. The challenge was:
- Jenkins builds the Docker image in its own workspace (`/home/jenkins/agent/workspace/`)
- But n8n runs containers from `~/garminconnector/` on the host
- Jenkins container can't directly access the host filesystem

**Solution**: Jenkins SSHs from its container to `strider@192.168.1.199` (the host) using the Jenkins agent's RSA key (`/home/jenkins/.ssh/id_rsa`), which was added to strider's `authorized_keys`.

### Jenkinsfile Pipeline
```groovy
stage('Sync Host Repo') {
    // SSH from Jenkins container → host, pull latest code
    sh 'ssh -i /home/jenkins/.ssh/id_rsa strider@192.168.1.199
         "cd ~/garminconnector && git checkout -- . && git pull"'
}
stage('Build Docker Image') {
    // Rebuild image with latest Python scripts
    sh 'docker compose -p garminconnector build --no-cache garmin-report'
}
```

### SSH Key Setup
- Jenkins agent container has `/home/jenkins/.ssh/id_rsa` (RSA key)
- This public key is in `/home/strider/.ssh/authorized_keys` on the host
- Jenkins runs as `jenkins` user but SSH works because the key is explicitly specified with `-i`

## Testing

### Local testing (before push)
Use slash commands to test each workflow locally:
```
/n8n-daily-report-930pm          (script + AI coaching)
/n8n-morning-readiness-8am       (script + AI coaching)
/n8n-store-daily-metrics-9pm     (script only)
/n8n-hr-health-monitor-3h        (script only)
/n8n-weekly-trainer-report-thu-8am (script only, needs Docker for matplotlib)
```
These commands are local-only (gitignored via `.claude/commands/n8n-*.md`).

### Server testing (after deploy)
Test from the n8n UI — click "Test Workflow" for each workflow:
- Store Daily Metrics: scheduled 9pm daily
- Daily Report: scheduled 9:30pm daily
- Morning Readiness: scheduled 8am daily (Sat 9am)
- HR Health Monitor: every 3 hours
- Weekly Trainer Report: Thursday 8am

## What Changes Require What

Both are handled automatically by Jenkins. This table is for reference only:

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

## Manual Deploy (fallback)
If Jenkins is down, run this from your Mac:
```bash
ssh strider@strider-pi.local "cd ~/garminconnector && git checkout -- . && git pull && docker compose build --no-cache garmin-report"
```
