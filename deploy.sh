#!/bin/bash

# ========================================
# GASsstro.com - Production Deployment Script
# ========================================

set -e  # Exit on error

echo "🚀 Starting GASsstro.com Production Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Do not run this script as root${NC}"
    exit 1
fi

# 1. Check Python version
echo -e "\n${YELLOW}📋 Checking Python version...${NC}"
python3 --version || { echo -e "${RED}❌ Python 3 not found${NC}"; exit 1; }

# 2. Create logs directory
echo -e "\n${YELLOW}📁 Creating logs directory...${NC}"
mkdir -p logs
echo -e "${GREEN}✅ Logs directory created${NC}"

# 3. Install dependencies
echo -e "\n${YELLOW}📦 Installing Python dependencies...${NC}"
pip3 install -r requirements.txt || { echo -e "${RED}❌ Failed to install dependencies${NC}"; exit 1; }
echo -e "${GREEN}✅ Dependencies installed${NC}"

# 4. Check .env file
echo -e "\n${YELLOW}🔐 Checking .env configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create .env file with production settings"
    exit 1
fi

# Check critical env vars
source .env
if [ "$ADMIN_TOKEN" == "CHANGE_ME_IN_PROD" ]; then
    echo -e "${RED}❌ ADMIN_TOKEN not configured!${NC}"
    echo "Please set a secure ADMIN_TOKEN in .env"
    exit 1
fi

if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo -e "${RED}❌ STRIPE_SECRET_KEY not configured!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment configuration OK${NC}"

# 5. Database initialization
echo -e "\n${YELLOW}🗄️  Initializing database...${NC}"
python3 -c "from server import init_db; init_db()" || { echo -e "${RED}❌ Database init failed${NC}"; exit 1; }
echo -e "${GREEN}✅ Database initialized${NC}"

# 6. Security check
echo -e "\n${YELLOW}🔒 Running security checks...${NC}"

# Check if debug mode is disabled
if grep -q "debug=True" server.py; then
    echo -e "${RED}⚠️  WARNING: Debug mode is enabled in server.py${NC}"
    echo "This is a security risk in production!"
fi

# Check CORS settings
if grep -q "ALLOWED_ORIGINS.*\*" .env; then
    echo -e "${RED}⚠️  WARNING: CORS is set to allow all origins (*)${NC}"
    echo "Please restrict ALLOWED_ORIGINS to your domain"
fi

echo -e "${GREEN}✅ Security checks completed${NC}"

# 7. Kill existing Gunicorn processes
echo -e "\n${YELLOW}🔄 Stopping existing server...${NC}"
pkill -f gunicorn || echo "No existing Gunicorn process found"

# 8. Start Gunicorn
echo -e "\n${YELLOW}🚀 Starting Gunicorn server...${NC}"
gunicorn -c gunicorn.conf.py server:app &

# Wait for server to start
sleep 3

# 9. Health check
echo -e "\n${YELLOW}🏥 Running health check...${NC}"
if curl -s http://localhost:5000/api/health | grep -q "ok"; then
    echo -e "${GREEN}✅ Server is running and healthy!${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}=============================================="
echo -e "✅ Deployment completed successfully!"
echo -e "==============================================\n${NC}"

echo "📊 Server Status:"
echo "  - API: http://localhost:5000"
echo "  - Logs: ./logs/"
echo "  - PID: $(cat gunicorn.pid)"

echo -e "\n📝 Useful commands:"
echo "  - View logs: tail -f logs/error.log"
echo "  - Stop server: pkill -f gunicorn"
echo "  - Restart: ./deploy.sh"

echo -e "\n⚠️  Production Checklist:"
echo "  [ ] Configure HTTPS/SSL certificate"
echo "  [ ] Set up reverse proxy (Nginx/Apache)"
echo "  [ ] Configure firewall rules"
echo "  [ ] Set up automated backups"
echo "  [ ] Configure monitoring/alerts"
echo "  [ ] Update Stripe webhook URL"
