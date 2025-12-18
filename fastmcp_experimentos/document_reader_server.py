import os
from pathlib import Path
from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Document Reader")

async def list_files_logic(directory: str = ".") -> str:
    """Lists all files and directories in the specified path."""
    try:
        # If directory is relative, make it relative to the current working directory of the server
        path = Path(directory)
        if not path.is_dir():
            return f"Error: {directory} is not a directory."
        
        items = os.listdir(directory)
        return "\n".join(items) if items else "The directory is empty."
    except Exception as e:
        return f"Error listing files: {str(e)}"

async def read_file_logic(filepath: str) -> str:
    """Reads the content of a text file."""
    try:
        path = Path(filepath)
        if not path.is_file():
            # Check relative to root of project if needed
            if not path.is_absolute():
                # Try relative to one level up (where README.md usually is)
                alt_path = Path("..") / filepath
                if alt_path.is_file():
                    path = alt_path
                else:
                    return f"Error: {filepath} is not a file."
        
        # For security and simplicity, we'll try to read as UTF-8
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "Error: File is not a plain text file or uses unsupported encoding."
    except Exception as e:
        return f"Error reading file: {str(e)}"

async def search_text_logic(directory: str, query: str) -> str:
    """Searches for a specific query string within all files in a directory."""
    try:
        results = []
        target_dir = Path(directory)
        if not target_dir.is_dir():
            # Try one level up
            alt_dir = Path("..") / directory
            if alt_dir.is_dir():
                target_dir = alt_dir
            else:
                return f"Error: {directory} is not a directory."

        for root, dirs, files in os.walk(target_dir):
            for file in files:
                file_path = Path(root) / file
                try:
                    # Skip binary files/errors
                    content = file_path.read_text(encoding="utf-8")
                    if query.lower() in content.lower():
                        results.append(str(file_path))
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        if not results:
            return f"No matches found for '{query}' in {directory}."
        return "Matches found in:\n" + "\n".join(results)
    except Exception as e:
        return f"Error searching text: {str(e)}"

# Register tools
mcp.tool(name="list_files")(list_files_logic)
mcp.tool(name="read_file")(read_file_logic)
mcp.tool(name="search_text")(search_text_logic)

if __name__ == "__main__":
    mcp.run()
