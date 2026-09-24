# AI Small Business Operations Agent - Startup Script
# Starts n8n with proper configuration

echo "=========================================="
echo "  AI Business Operations Agent - Startup"
echo "=========================================="
echo ""

# Check if n8n is installed
if ! command -v n8n &> /dev/null; then
    echo "ERROR: n8n not found. Install with: npm install -g n8n"
    exit 1
fi

echo "n8n version: $(n8n --version)"
echo "Node version: $(node --version)"
echo ""

# Set environment variables
export N8N_PORT=5678
export N8N_PROTOCOL=http
export N8N_HOST=localhost

# Load .env if exists
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    set -a
    source .env
    set +a
fi

echo "Starting n8n on http://localhost:${N8N_PORT}"
echo "Workflow endpoint: http://localhost:${N8N_PORT}/webhook/order-request"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start n8n
n8n start
