import uvicorn
import os
import sys

# Add the parent directory to sys.path to ensure module resolution if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print("🚀 Starting Janani Execution Agent on Port 8001...")
    uvicorn.run("execution_agent.main:app", host="0.0.0.0", port=8001, reload=True)
