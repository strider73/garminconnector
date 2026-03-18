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

### Why a Sync Stage Was Added

The `.claude/` folder (commands, reference files, templates, agents) is mounted from the host filesystem into Docker containers. When code is pushed, Jenkins rebuilds the Docker image (which updates Python scripts), but the host's `~/garminconnector/` folder still has the old `.claude/` files. Without syncing, the mounted files would be stale.

To eliminate manual `git pull` on the server, a `Sync Host Repo` stage was added to the Jenkinsfile that runs `git pull` on the host automatically before building the Docker image.

### Why SSH Is Needed

Jenkins agent runs inside a Docker container on strider-pi. It cannot directly access the host filesystem (`/home/strider/garminconnector/`). The only way to run `git pull` on the host is to SSH out of the container and into the host.

### Jenkins Agent able to git pull now as strider  — Make Jenkins Agent able to login as strider on Pi1

**Concept**: SSH authentication works by key pairs. If the server (Pi1) has your public key in its `authorized_keys` file, you can log in without a password.

**What was done**:
1. The Jenkins agent container already had an RSA key pair at `/home/jenkins/.ssh/id_rsa` (originally created for master-agent pairing, reused here)
2. Copied the public key from inside the Jenkins agent container and added it to strider's trusted keys on Pi1:
   ```bash
   docker exec jenkins-agent cat /home/jenkins/.ssh/id_rsa.pub >> /home/strider/.ssh/authorized_keys
   ```
   This one command tells Pi1: "When someone connects with this key, let them in as strider."
3. In the Jenkinsfile, `-i /home/jenkins/.ssh/id_rsa` explicitly points to the key file because the Jenkins process may run as `root` (who has no keys in `/root/.ssh/`), not as the `jenkins` user

**Two SSH keys involved in the full pipeline**:
| Key | Location | Purpose |
|-----|----------|---------|
| Jenkins agent's `id_rsa` | `/home/jenkins/.ssh/id_rsa` (inside container) | Jenkins container → Pi1 host (to run `git pull`) |
| strider's `id_ed25519` | `/home/strider/.ssh/id_ed25519` (on Pi1 host) | Pi1 host → GitHub (to pull code) |

**Jenkinsfile pipeline**:
```groovy
stage('Sync Host Repo') {
    // Jenkins container SSHs into Pi1 as strider, then strider pulls from GitHub
    sh 'ssh -i /home/jenkins/.ssh/id_rsa -o StrictHostKeyChecking=no strider@192.168.1.199 "cd ~/garminconnector && git checkout -- . && git pull"'
}
stage('Build Docker Image') {
    sh 'docker compose -p garminconnector build --no-cache garmin-report'
}

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
