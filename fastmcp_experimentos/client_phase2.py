import asyncio
from fastmcp import FastMCP

async def run_client():
    # Connect to the server
    # Note: FastMCP client can connect to a server script directly for testing
    client = FastMCP("Client Phase 2")
    
    # In a real scenario, we'd use a transport, but for local testing within FastMCP:
    # We can use the server object if it's in the same process, but here we want to test
    # the MCP protocol interaction. 
    # For simplicity in this demo, we'll use the server's tools directly through the mcp object
    # if we import it, or use the connect method if available.
    
    # Actually, the best way to test is to run the server in a separate process
    # but for this script, let's try to initialize the server and call tools
    # as if we were a client.
    
    from document_reader_server import list_files_logic, read_file_logic, search_text_logic
    
    print("--- Testing List Files ---")
    files = await list_files_logic(".")
    print(files)
    
    print("\n--- Testing Read File (README.md) ---")
    # Using README.md which is in the parent directory
    content = await read_file_logic("README.md")
    print(content[:200] + f"... [Length: {len(content)}]") 
    
    print("\n--- Testing Search Text ('Kokoro') ---")
    # Search in the root directory (one level up)
    search_results = await search_text_logic("..", "Kokoro")
    print(search_results)

if __name__ == "__main__":
    asyncio.run(run_client())
