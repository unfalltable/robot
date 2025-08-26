# Trading Robot Configuration Guide

## 📋 Configuration Files Overview

This project uses several configuration files that contain sensitive information and should not be committed to version control.

### 🔒 Protected Files (Not in Git)

The following files are automatically ignored by Git and should be configured locally:

- `.env` - Main application configuration
- `backend/monitoring.env` - Monitoring system configuration
- `logs/` - Application log files
- `data/` - Application data files
- `*.db` - Database files

### 📝 Template Files (In Git)

Template files are provided for easy setup:

- `.env.example` - Template for main configuration
- `backend/monitoring.env.example` - Template for monitoring configuration

## 🚀 Quick Setup

### 1. Create Main Configuration

Copy the template and customize:

```bash
# Copy the template
cp .env.example .env

# Edit the configuration
# Windows: notepad .env
# Linux/Mac: nano .env
```

### 2. Create Monitoring Configuration

```bash
# Copy the template
cp backend/monitoring.env.example backend/monitoring.env

# Edit the monitoring configuration
# Windows: notepad backend/monitoring.env
# Linux/Mac: nano backend/monitoring.env
```

## ⚙️ Configuration Sections

### Main Application (.env)

#### Database Configuration
```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/trading_robot
```

#### Security Settings
```env
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
```

#### Trading API Keys
```env
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here
```

### Monitoring Configuration (backend/monitoring.env)

#### System Thresholds
```env
MONITORING_CPU_WARNING_THRESHOLD=80.0
MONITORING_MEMORY_WARNING_THRESHOLD=85.0
```

#### Notification Settings
```env
MONITORING_EMAIL_ENABLED=true
MONITORING_EMAIL_USERNAME=your-email@gmail.com
```

## 🔐 Security Best Practices

### 1. Never Commit Secrets
- Always use `.env` files for sensitive data
- Never hardcode API keys in source code
- Use different keys for development and production

### 2. Environment-Specific Configuration
```env
# Development
DEBUG=true
LOG_LEVEL=DEBUG

# Production
DEBUG=false
LOG_LEVEL=INFO
```

### 3. API Key Management
- Use separate API keys for different environments
- Regularly rotate API keys
- Use read-only keys when possible
- Enable IP restrictions on exchange APIs

## 🛠️ Development Setup

### For Developers

1. **Copy all template files:**
   ```bash
   cp .env.example .env
   cp backend/monitoring.env.example backend/monitoring.env
   ```

2. **Configure development settings:**
   ```env
   # .env
   DEBUG=true
   LOG_LEVEL=DEBUG
   DATABASE_URL=postgresql://postgres:password@localhost:5432/trading_robot_dev
   ```

3. **Use test API keys:**
   ```env
   # Use testnet/sandbox API keys for development
   BINANCE_API_KEY=your_testnet_api_key
   BINANCE_SECRET_KEY=your_testnet_secret_key
   ```

## 📦 Distribution Setup

### For End Users

The startup scripts automatically handle configuration:

1. **Run the menu:**
   ```cmd
   cmd /c menu.bat
   ```

2. **Choose option 1:** "Start Trading Robot"
   - Automatically creates `.env` from template
   - Uses safe default values
   - Prompts for required settings

3. **Configure your API keys:**
   - Edit `.env` file after first run
   - Add your exchange API keys
   - Restart the application

## 🔍 Configuration Validation

### Check Configuration
The application validates configuration on startup:

- ✅ Required environment variables
- ✅ Database connectivity
- ✅ Redis connectivity
- ✅ API key format (basic validation)

### Common Issues

#### Missing Configuration
```
Error: DATABASE_URL not found in environment
Solution: Copy .env.example to .env and configure
```

#### Invalid API Keys
```
Error: Invalid Binance API key format
Solution: Check API key format and permissions
```

#### Database Connection
```
Error: Could not connect to database
Solution: Check DATABASE_URL and ensure PostgreSQL is running
```

## 📚 Environment Variables Reference

### Required Variables
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Application secret key

### Optional Variables
- `DEBUG` - Enable debug mode (default: false)
- `LOG_LEVEL` - Logging level (default: INFO)
- `API_PORT` - API server port (default: 8000)

### Trading Variables
- `BINANCE_API_KEY` - Binance API key
- `BINANCE_SECRET_KEY` - Binance secret key
- `DEFAULT_TRADING_PAIR` - Default trading pair (default: BTC/USDT)

## 🆘 Troubleshooting

### Reset Configuration
If configuration is corrupted:

```bash
# Backup current config
cp .env .env.backup

# Reset to template
cp .env.example .env

# Edit with correct values
```

### Check Configuration
```bash
# View current configuration (without secrets)
docker-compose config

# Test database connection
docker-compose exec backend python -c "from app.database import engine; print('DB OK')"
```

---

**⚠️ Important:** Never share your `.env` files or commit them to version control. They contain sensitive information that could compromise your trading accounts.
