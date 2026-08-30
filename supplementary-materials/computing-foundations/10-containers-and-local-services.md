# Containers and local services

The production monitoring laboratory runs several long-lived programs at once.
Docker Compose gives those programs reproducible filesystems, networks, and
startup configuration. This guide explains the machinery before asking you to
operate it.

## The vocabulary

- A **container image** is an immutable template containing a filesystem and
  startup instruction.
- A **container** is a running or stopped instance of an image.
- A **Containerfile** is reviewed source describing how to build an image.
- A **registry** stores and distributes named images.
- A **service** is one role in a Compose application, such as `api` or
  `prometheus`.
- A **port mapping** connects a port on your laptop to a port inside a
  container. `3000:3000` means host port 3000 forwards to container port 3000.
- A **volume** preserves data independently of one container instance.
- A **bind mount** exposes a selected host path inside a container.
- A **health check** asks whether a process is ready for its intended work. A
  running container is not necessarily a ready service.

An image is not a virtual machine snapshot and a container is not a Python
virtual environment. `.venv` isolates Python packages for local processes;
containers isolate a larger process filesystem and network boundary.

## Host names and ports

Your browser runs on the **host** computer. It reaches Grafana at
`http://localhost:3000` because Compose publishes Grafana's port 3000.

Containers on the private Compose network use service names. The API exports
traces to `http://alloy:4318`, not `localhost:4318`. Inside the API container,
`localhost` means the API container itself. Compose DNS resolves `alloy` to the
Alloy service. This distinction explains many apparently mysterious connection
errors.

## Install and verify

Docker Desktop is the simplest supported route on Windows and macOS and is also
available on Linux. A Linux Docker Engine with the Compose plugin is equally
valid. Follow the current installation instructions from
[Docker](https://docs.docker.com/get-started/get-docker/), start the Docker
application or daemon, and verify:

```text
docker version
docker compose version
```

Both commands must show client and server information. If `docker version`
shows a client but cannot contact the daemon, Docker is installed but not
running or the current account lacks permission.

On Windows, use the same PowerShell terminal for Git, `uv`, and Docker unless
the course explicitly adopts WSL. Mixing a Windows repository path with a WSL
Docker context adds a second filesystem boundary and complicates diagnosis.

## Read a Compose command

The laboratory starts with:

```text
docker compose -f projects/production-monitoring-lab/compose.yaml up --build -d
```

- `compose` selects the multi-service interface;
- `-f` names the reviewed configuration;
- `up` reconciles the declared services with local runtime state;
- `--build` rebuilds the course API image if needed; and
- `-d` leaves services running in the background.

Inspect state rather than guessing:

```text
docker compose -f projects/production-monitoring-lab/compose.yaml ps
docker compose -f projects/production-monitoring-lab/compose.yaml logs api
docker compose -f projects/production-monitoring-lab/compose.yaml logs prometheus
```

Logs from the container runtime help diagnose startup. They are distinct from
the structured application events deliberately collected by the laboratory.

## Ports used by the laboratory

| Host port | Service | Purpose |
| ---: | --- | --- |
| 8000 | API | prediction endpoints and API documentation |
| 3000 | Grafana | dashboards and evidence exploration |
| 9090 | Prometheus | metric queries, targets, rules, and alerts |
| 3100 | Loki | log-store API |
| 3200 | Tempo | trace-store API |
| 12345 | Alloy | collector status |

If a port is already occupied, stop the conflicting local process or use a
course-approved port override. Do not edit several URLs independently: host
ports are an interface shared by documentation, health checks, and clients.

## Storage and cleanup

Compose creates named volumes for monitoring data and bind-mounts the lab's
ignored `runtime/` directory for the SQLite database, incident control file,
and JSON Lines application log.

```text
docker compose -f projects/production-monitoring-lab/compose.yaml down
```

This removes the lab containers and private network but retains named volumes.
Adding `--volumes` removes this lab's named monitoring data. It does not remove
images or unrelated Docker projects, but it is still a destructive reset and
should be used deliberately.

## A reliable troubleshooting order

1. Run `docker version`; confirm the server is reachable.
2. Run `docker compose ... config -q`; confirm the configuration parses.
3. Run `docker compose ... ps`; distinguish absent, starting, unhealthy, and
   running services.
4. Read the first relevant service log, not every log at once.
5. Check whether the required host port is already occupied.
6. Run the laboratory's `check_stack.py` and preserve its first failure.
7. If images cannot download, check network, VPN, proxy, disk space, and registry
   access before changing source code.

On first use, image downloads and the API build can take several minutes and
consume multiple gigabytes of disk. A slow first build is not evidence that the
Python model is slow.

## Resource or policy limitations

Some managed laptops prohibit Docker, and some machines cannot comfortably run
the full stack. Use the laboratory's committed `offline-evidence/` case in that
situation. The fallback preserves the diagnostic questions and evidence
boundaries. It does not provide practice starting services, following live
telemetry, or verifying a mitigation, so record that limitation in the lab
submission.

## Check your understanding

1. Why does the API contact `alloy:4318` while your browser contacts
   `localhost:3000`?
2. What survives `docker compose down`, and what additional state is removed by
   `down --volumes`?
3. Why can a container be running while its service is not ready?
4. Which evidence would distinguish an occupied host port from a Python import
   failure inside the API container?
