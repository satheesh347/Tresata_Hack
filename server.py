from mcp.server.fastmcp import FastMCP
import os
import subprocess
import sys

mcp = FastMCP("TresataDataProcessor")

@mcp.tool()
def list_files() -> str:
    """Lists available CSV files in Training_data."""
    try:
        # Correct folder: Training_data
        files = [f for f in os.listdir('Training_data') if f.endswith('.csv')]
        return "\n".join(files) if files else "No CSV files found."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def predict_column(filename: str, column_name: str) -> str:
    """Predicts column type (Phone, Company, etc.)."""
    # Correct folder: Training_data
    file_path = os.path.join("Training_data", filename)
    if not os.path.exists(file_path): return "Error: File not found."
        
    try:
        result = subprocess.run(
            [sys.executable, "predict.py", "--input", file_path, "--column", column_name],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e: return f"Error: {str(e)}"

@mcp.tool()
def parse_file(filename: str) -> str:
    """Parses file and saves to output.csv."""
    # FIXED: Changed "outputs" to "Training_data"
    file_path = os.path.join("Training_data", filename)
    
    if not os.path.exists(file_path): 
        return f"Error: File '{filename}' not found in Training_data."

    try:
        result = subprocess.run(
            [sys.executable, "parser.py", "--input", file_path],
            capture_output=True, text=True
        )
        if result.returncode == 0: return "Success. Saved to output.csv."
        else: return f"Error: {result.stderr}"
    except Exception as e: return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
