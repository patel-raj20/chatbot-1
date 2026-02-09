# Docker Deployment Guide

This guide explains how to run your Chat Bot project on any computer using Docker.

## Prerequisites

Before starting, make sure you have installed:
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (usually included with Docker Desktop)

Download Docker Desktop from: https://www.docker.com/products/docker-desktop/

## Quick Start (3 Simple Steps)

### 1. Clone/Copy the Project
```bash
# Copy the entire Chat_bot folder to your new computer
```

### 2. Configure Environment (Optional)
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env if you want to change default passwords/settings
```

### 3. Start Everything
```bash
# Navigate to project directory
cd Chat_bot

# Start all services with one command
docker-compose up -d
```

That's it! The application will start automatically.

## What Gets Started

When you run `docker-compose up -d`, the following services start:

1. **PostgreSQL** - Database (Port 5432)
2. **Ollama** - AI/LLM service (Port 11434)
3. **Milvus** - Vector database (Port 19530)
4. **MinIO** - Object storage (Ports 9000, 9001)
5. **Etcd** - Milvus dependency (Port 2379)
6. **Attu** - Milvus admin UI (Port 3001)
7. **Backend API** - FastAPI server (Port 8000)
8. **Frontend** - Next.js app (Port 3000)

## Accessing the Application

After starting (wait 1-2 minutes for all services to initialize):

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **Milvus Admin (Attu)**: http://localhost:3001

## Common Commands

### Start all services
```bash
docker-compose up -d
```

### Stop all services
```bash
docker-compose down
```

### Stop and remove all data (fresh start)
```bash
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart a specific service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Check service status
```bash
docker-compose ps
```

### Rebuild after code changes
```bash
# Rebuild and restart specific service
docker-compose up -d --build backend

# Rebuild all services
docker-compose up -d --build
```

## Initial Setup Tasks

### 1. Pull Ollama Model
After first startup, you need to download the AI model:

```bash
# Enter the ollama container
docker exec -it chatbot-ollama ollama pull llama2

# Or use your preferred model
docker exec -it chatbot-ollama ollama pull mistral
```

## Transferring to a New Computer

### Method 1: Git Repository (Recommended)
```bash
# On old computer - push code
git add .
git commit -m "Update"
git push

# On new computer - pull code
git clone <your-repo-url>
cd Chat_bot
docker-compose up -d
```

### Method 2: Direct Copy
1. Copy the entire `Chat_bot` folder to USB/cloud storage
2. Transfer to new computer
3. Run `docker-compose up -d`

**Note**: Docker will automatically download all required images on first run (may take 5-10 minutes depending on internet speed).

## Troubleshooting

### Port Already in Use
If you get port conflicts, edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "8001:8000"  # Changed from 8000:8000
```

### Services Won't Start
```bash
# Check logs for errors
docker-compose logs

# Restart everything
docker-compose down
docker-compose up -d
```

### Out of Disk Space
```bash
# Remove unused Docker images and volumes
docker system prune -a

# Remove all project volumes (WARNING: deletes all data)
docker-compose down -v
```

### Backend Can't Connect to Database
Wait 30 seconds for PostgreSQL to fully initialize, then:
```bash
docker-compose restart backend
```

### Reset Everything
```bash
# Stop and remove everything including data
docker-compose down -v

# Start fresh
docker-compose up -d
```

## Development Mode

For development with live code reloading:

1. The backend automatically reloads when you edit Python files (volume mounted)
2. For frontend, you may want to run it locally:
   ```bash
   # Stop frontend container
   docker-compose stop frontend
   
   # Run frontend locally
   cd frontend
   npm install
   npm run dev
   ```

## Production Deployment

For production on a server:

1. Update `.env` with strong passwords
2. Remove volume mounts in docker-compose.yml (lines with `./backend:/app`)
3. Use a reverse proxy (nginx/traefik) for HTTPS
4. Set proper CORS origins in backend

## Data Persistence

All data is stored in Docker volumes:
- `postgres_data` - Database
- `ollama_data` - AI models
- `milvus_data` - Vector embeddings
- `minio_data` - Uploaded files

These volumes persist even after `docker-compose down`. Only `docker-compose down -v` removes them.

## Resource Requirements

Minimum recommended:
- **RAM**: 8GB (16GB recommended)
- **Disk**: 20GB free space
- **CPU**: 4 cores

## Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify all services are running: `docker-compose ps`
3. Check Docker Desktop is running and has enough resources allocated

---

**Quick Reference Card**
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Fresh Start
docker-compose down -v && docker-compose up -d
```
