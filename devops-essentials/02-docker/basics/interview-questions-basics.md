# Docker Interview Questions - Basics

## Q1: What is Docker?
**Answer:** Docker is a containerization platform that packages applications with their dependencies into isolated containers, ensuring consistency across environments.

## Q2: Container vs Virtual Machine?
**Answer:** 
- **Container**: Shares host OS, lightweight (MBs), instant startup
- **VM**: Full OS per instance, heavy (GBs), slow startup

## Q3: What is a Docker image?
**Answer:** Read-only template containing application code, runtime, libraries, and dependencies. Used to create containers.

## Q4: What is a Docker container?
**Answer:** Running instance of a Docker image. Isolated, lightweight, and portable execution environment.

## Q5: Explain Dockerfile
**Answer:** Text file with instructions to build a Docker image. Contains commands like FROM, COPY, RUN, CMD.

## Q6: What is Docker Hub?
**Answer:** Public registry for Docker images. Hosts official and community images.

## Q7: CMD vs ENTRYPOINT?
**Answer:**
- **CMD**: Default command, easily overridden
- **ENTRYPOINT**: Main command, arguments can be appended

## Q8: What is docker-compose?
**Answer:** Tool for defining and running multi-container applications using YAML configuration.

## Q9: How to share data between containers?
**Answer:** Use Docker volumes or bind mounts to share persistent data.

## Q10: Port mapping?
**Answer:** \-p host:container\ maps container port to host port. Example: \-p 8080:80\

**Previous:** [â† Basic Commands](05-basic-commands.md) | **Next:** [Multi-stage Builds â†’](../intermediate/06-multistage-builds.md)
