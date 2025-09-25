# Fly Deployment

Your FastOpp program wants to fly!

## Overview

FastOpp provides an opinionated framework for FastAPI with the following features:

* Admin panel similar to Django 
* A Python program to work with the database
* Admin panel example with custom styling
* Django-style HTML templates with modern UI components
* Replaceable style templates to get started
* API endpoints to connect to other frontend frameworks
* Auto-generated documentation for API endpoints

 You can deploy it yourself. It needs to be able to run uvicorn and mount a persistent volume for a single SQLite file.

It does not use PostgreSQL or Nginx.

It uses Fly.io, since it's cheap, repeatable, and volume-backed. Run uvicorn directly. Store SQLite at /data/test.db.

NOTE: By default, FastOpp uses /data/test.db

## Pricing

You can deploy your app in whatever manner you need. Deploying to Fly.io is one example. It is intended to be a low-cost example.

You will be using the "Pay As You Go Plan."

You will be using Fly Machine and Fly Volume.

* Fly Machines are fast-launching VMs; they can be started and stopped at subsecond speeds.
* Fly Volumes are local persistent storage for Fly Machines.

You will be required to log in and add a payment method.

### Fly Machine Pricing

Running 24/7: ~$3.19/month for a shared-cpu-1x, 512 MB RAM machine. Swap (512 MB via swap_size_mb = 512) has no separate charge.

Stopped: $0 for CPU/RAM; you only pay $0.15/GB-month for root filesystem (rootfs). A swap file uses rootfs space (no extra line item), so if 512 MB of swap were counted in rootfs while stopped, that portion would be $0.075/month. 

### Fly Volume Pricing

Fly Volumes are billed the same whether your Machine is Running or Stopped. It's $0.15/GB-month.

## Let's Get Started

### 0) Prereqs

- **macOS** with **Homebrew** installed
- **Your FastAPI (FastOpp) repo** cloned locally

```bash
brew install flyctl
fly auth signup   # or: fly auth login
```

Opens up a webpage on fly.io. You can use Google or GitHub to create an account.

> "Your flyctl should be connected now. Feel free to close this tab"

### 1) Add deploy files to the repo

Add a `Dockerfile` to the project root:

```Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential \
  && rm -rf /var/lib/apt/lists/*

# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
```

Add a `.dockerignore`:

```gitignore
.git
.venv
__pycache__/
*.db
```

### 2) Initialize fly app (not deployed yet)

```bash
fly launch --no-deploy
# Answer:
# - App name: <enter> or custom
# - Region: choose one near you
# - Use Postgres: No
# - Create a Dockerfile: No (you already added one)
```

You should see something like this:

```bash
jcasman@MacBook-Air-6 fastcfv % fly launch --no-deploy
Scanning source code
Detected a Dockerfile app
Creating app in /Users/jcasman/Development/fastcfv
We're about to launch your app on Fly.io. Here's what you're getting:

Organization: Jesse Casman (fly launch defaults to the personal org)
Name: fastcfv (derived from your directory name)
Region: San Jose, California (US) (this is the fastest region for you)
App Machines: shared-cpu-1x, 1GB RAM (most apps need about 1GB of RAM)
Postgres: (not requested)
Redis: (not requested)
Tigris: (not requested)
```

#### Cost Reduction

To further reduce costs, you can set memory to 512MB

```toml
[[vm]]
  memory = '512mb'
  cpu_kind = 'shared'
  cpus = 1
```

To increase the stability of the system, you can also add SWAP.

### 3) Create and mount a persistent volume

Note: Pick the same region you chose above. However, just use its short code, not the full name. For example, it's not "San Jose, California (US)", it's "sjc" - You can find your region code using:

```bash
flyctl platform regions
```

Now run:

```bash
fly volumes create data --region <REGION> --size 1
```

Do not include `< >`

Note: You will get this error, you can ignore.

> Warning! Every volume is pinned to a specific physical host. You should create two or more volumes per application to avoid downtime.

It will then ask

> ? Do you still want to use the volumes feature? 

Say Yes

### 4) Edit fly.toml

Open the generated `fly.toml`. Ensure these blocks exist:

You probably have this:

```toml
app = "<your-app-name>"
primary_region = '<your-region>'

swap_size_mb = 512   <---- ADD THIS TO ADD SWAP

[build]

[http_service]
internal_port = 8000
force_https = true
auto_stop_machines = 'stop'
auto_start_machines = true
min_machines_running = 0
processes = ['app']

[[vm]]
memory = '512mb'  <----- SUGGESTED MEMORY SIZE FOR FASTOPP
cpu_kind = 'shared'
cpus = 1
```

Make sure this is included, too.

```toml
[env]
  ENVIRONMENT = "production"
  UPLOAD_DIR = "/data/uploads"

[[mounts]]
  source = "data"
  destination = "/data"

[[services]]
  internal_port = 8000
  protocol = "tcp"
  [[services.ports]]
    port = 80
    handlers = ["http"]
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

### IMPORTANT: How to Make Photo Uploads Permanent on Fly.io (FastAPI Static Files + Fly Volume)

> 📺 [Watch: Permanent Photo Uploads on Fly with FastAPI Static Files on Fly Volume (YouTube)](https://youtu.be/YKC3ZSA2Eh8?si=lKJt3r8W-gylIW3R)

When deploying FastOpp (or any FastAPI app) on Fly.io, you need to ensure that user-uploaded files like photos are stored on a persistent Fly Volume. Otherwise, uploads will be lost when your app restarts or redeploys.

**Key steps:**
- Mount a Fly Volume at `/data` (see the `[[mounts]]` block in your `fly.toml` above).
- Set your FastAPI `UPLOAD_DIR` to `/data/uploads` (see the `[env]` block).
- Serve static files from this directory in your FastAPI app.

This setup ensures that uploaded files are saved to the persistent volume and survive restarts and deploys.

### Setting Memory and Swap

In testing, I've found that 256mb may not be enough to run the current FastOpp application and the database.

You can increase the memory. You can also add swap. By all means, please test it yourself and configure your memory settings to what works for your version of the app.

Wwap is disabled by default for Fly Machines. You must explicitly configure it in your fly.toml.

I added:
`swap_size_mb = 512`

It should be included at the top level of your `fly.toml`, not nested under a [[vm]] block. Putting it inside [[vm]] won’t work.

And then in [[vm]] I increased memory from 256 to 512:
`memory = '512mb'`

You can confirm these settings using the steps in the Confirm Memory and Swap Settings section later in this document.

### 5) Set secrets and DB URL

```bash
fly secrets set SECRET_KEY=$(openssl rand -hex 32)
fly secrets set DATABASE_URL="sqlite+aiosqlite:////data/test.db"
# note, by default, FastOpp uses the name test.db
# fly secrets set DATABASE_URL="sqlite+aiosqlite:////data/test.db"
# additionally, if you want to use the AI chat demo, you must add your
# openrouter key
# OPENROUTER_API_KEY=your-key-from-openrouter
```

### 6) Deploy

```bash
fly deploy
```

You can check the status with

```bash
fly status
```

### 7) Single-machine only (SQLite requires one writer)

```bash
fly scale count 1
```

### 8) Issue an SSH certificate

You'll be sending SSH commands to fly.io.

```bash
fly ssh issue --agent
# or: fly ssh issue
```

🌶️ Hot tip: If you get an error like "error connecting to SSH server: ssh: handshake failed: ssh: unable to authenticate," please check that the app is started using `fly status`

### 9) Setup up your database using oppman.py

```bash
# upgrade schema
fly ssh console -C "uv run python oppman.py init"
```

If you want to run the webinar demo, you also need to copy the fake people pictures
from `static/uploads/photos` into `/data/uploads/photos`

```bash
# copy fake data initial photos into Fly Volume
fly ssh console
cp static/uploads/photos/* /data/uploads/photos/
```

### Confirm Memory and Swap Settings

To verify inside the instance, ssh in with:
`fly ssh console`

then check your meminfo:
`cat /proc/meminfo | grep -i swap`

```bash
root@286031ea9e5268:/app# cat /proc/meminfo | egrep 'Mem|Swap'
MemTotal:         470128 kB
MemFree:          108764 kB
MemAvailable:     316112 kB
SwapCached:            0 kB
SwapTotal:        524284 kB
SwapFree:         524284 kB
```

Details on the output above:

🖥️ Memory (RAM)

MemTotal: 470128 kB (~459 MB)
This is the total physical RAM allocated to the Fly machine. It matches our fly.toml setting of memory = "512mb", because Fly reserves a little overhead, so it's ~470 MB instead of the full 512 MB.

MemFree: 108764 kB (~106 MB)
This is memory currently unused.

MemAvailable: 316112 kB (~308 MB)
This is a better indicator of what’s actually usable. It includes free memory plus reclaimable caches/buffers. The app effectively has ~300 MB headroom before swapping would begin.

💾 Swap

SwapTotal: 524284 kB (~512 MB)
This shows swap set at 512mb (swap_size_mb = 512), so the VM has half a gig of virtual memory to fall back on. If SwapTotal is 0, you have no swap enabled. If it shows a non-zero value, swap is active.

SwapFree: 524284 kB (~512 MB)
None of it has been touched yet (good — the system isn’t under memory pressure).

SwapCached: 0 kB
Nothing swapped out and cached in RAM, confirming swap hasn’t been used at all.

✅ What this means

The Fly machine is running with ~470 MB usable RAM and ~512 MB swap.

At the moment, memory usage is well under control — there's ~300 MB available plus the entire swap untouched.

If the app ever spikes beyond ~470 MB RAM, the kernel will push data into swap instead of immediately killing our process with an Out Of Memory error. A little bit of a safety net.

## Troubleshooting

If you make changes to your Dockerfile and want to redeploy, you can make sure fly is not using a cached version by running the command

```bash
fly deploy --dockerfile Dockerfile
```

## Extra Information

### Can fly.io handle persistent storage?

Fly.io Machines provide ephemeral compute, meaning your data is lost when the machine restarts. Fly Volumes offer persistent storage by attaching a slice of an NVMe drive to a machine. This allows you to mount a volume to a specific path on your machine, enabling data persistence across restarts and deployments.

Here's a breakdown:

Fly Machines:
Fly Machines are virtual machines that run your application code. They are designed to be lightweight and scalable, but their storage is ephemeral.

Fly Volumes:
Fly Volumes are persistent storage volumes that can be attached to Fly Machines. They are like physical disks, providing a place to store data that persists even when the machine restarts.

Mounting:
When you mount a volume, you specify a path on the machine's file system where the volume's contents will be accessible.

Use Cases:
Fly Volumes are useful for storing application data that needs to persist, such as user data, configuration files, or databases.

In essence, Fly.io Machines + Mounted Volume provides a way to combine the scalability and speed of Fly Machines with the persistent storage of Fly Volumes, allowing you to build robust and scalable applications that can handle data persistence.

## What is a Dockerfile?

A Dockerfile is essentially a blueprint for building a Docker image. It's a plain text file containing a set of instructions that Docker executes in sequential order to create an image.

A Dockerfile is a simple, plain text file. You create and edit it using any text editor you prefer (like VS Code, Notepad, or even a basic text editor in your terminal like vi or nano).

Key points about creating a Dockerfile

* Plain Text File: It's a regular text file.
* No File Extension (by convention): It's usually named "Dockerfile" (with a capital "D") and has no file extension
* Contains Instructions: The Dockerfile contains a series of commands that Docker executes in order to build the image. These instructions tell Docker things like:
  * What base image to start with (FROM)
  * What files to copy into the image (COPY)
  * What commands to run during the build process (RUN)
  * The default command to execute when a container is launched from the image (CMD)
