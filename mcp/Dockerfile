# mcp/Dockerfile
FROM python:3.11-alpine

WORKDIR /app

# Install dependencies
COPY mcp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server code
COPY mcp/ /app/mcp/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Run the MCP server
CMD ["uvicorn", "mcp.mcp_server:app", "--host", "0.0.0.0", "--port", "5000"]
