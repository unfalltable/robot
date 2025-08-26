# Trading Robot Docker Setup Guide

## 🚀 Quick Start for End Users

This trading robot is fully containerized with Docker. Users only need to install Docker Desktop to run the entire application.

### Prerequisites

1. **Install Docker Desktop**
   - Windows: Download from [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - Make sure Docker Desktop is running before proceeding

### Installation Steps

1. **Download the Trading Robot package**
   - Extract all files to a folder (e.g., `C:\trading-robot\`)

2. **Run the Control Panel**
   ```cmd
   cmd /c menu.bat
   ```

3. **Choose Startup Option**
   - **Option 4: Reliable Start** (Recommended for distribution)
   - This option handles network issues and provides retry logic

### Available Startup Options

| Option | Description | Best For |
|--------|-------------|----------|
| 1. Quick Start | Fast one-click startup | Daily use |
| 2. Full Start | Detailed startup process | First-time setup |
| 3. Development Mode | Manual service control | Developers |
| **4. Reliable Start** | **Network-resilient startup** | **Distribution** |
| 5. Check Status | View service health | Monitoring |
| 6. View Logs | Debug information | Troubleshooting |
| 7. Stop Services | Clean shutdown | Maintenance |

### Access URLs

After successful startup:
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000

### Troubleshooting

#### Network Issues
If you encounter Docker image download problems:

1. **Setup Docker Mirror** (Option 11)
   - Configures faster image sources
   - Especially useful in China

2. **Fix Network Issues** (Option 12)
   - Provides network diagnostics
   - Multiple solution strategies

#### Common Issues

**Docker not starting:**
- Ensure Docker Desktop is installed and running
- Check system requirements for Docker Desktop

**Port conflicts:**
- Make sure ports 3000, 8000, 5432, 6379 are not in use
- Stop other applications using these ports

**Slow startup:**
- First run downloads Docker images (may take 5-10 minutes)
- Subsequent runs are much faster

### For Developers

#### Project Structure
```
trading-robot/
├── backend/           # Python FastAPI backend
├── frontend/          # Next.js frontend
├── nginx/            # Nginx configuration
├── docker-compose.yml # Main Docker configuration
├── docker-compose.reliable.yml # Reliable configuration
├── menu.bat          # Control panel
└── start-reliable.bat # Reliable startup script
```

#### Development Commands
```bash
# View all containers
docker-compose -f docker-compose.reliable.yml ps

# View logs
docker-compose -f docker-compose.reliable.yml logs -f [service_name]

# Restart a service
docker-compose -f docker-compose.reliable.yml restart [service_name]

# Access container shell
docker exec -it trading_robot_backend bash
```

### Distribution Checklist

When distributing this application:

- [ ] Include all batch files and Docker configurations
- [ ] Test with `start-reliable.bat` on clean system
- [ ] Provide Docker Desktop installation instructions
- [ ] Include this README file
- [ ] Test network resilience features

### Support

For issues:
1. Check Docker Desktop is running
2. Try "Reliable Start" option (Option 4)
3. Use network troubleshooting tools (Options 11-12)
4. Check logs via menu option 6

---

**Note**: This application is designed to work entirely within Docker containers, making it easy to distribute and run on any system with Docker Desktop installed.
