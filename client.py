import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient, load_mcp_tools
import traceback
import sys
import os

async def main():
    """Simplified client for debugging the SSE connection."""
    
    # Configure servers with simplest possible SSE configuration
    servers_config = {
        "websearch": {
            # SSE transport configuration - matching server's simple config
            "transport": "sse",
            "url": "http://localhost:9001/sse",  # Including the SSE endpoint path
            # No auto-launch for debugging
            "wait_for_server": True,
            "launch_server": False  # Don't try to launch the server from client
        }
    }
    
    print(f"Initializing client with SSE connection to {servers_config['websearch']['url']}")
    
    # Initialize MCP client
    client = MultiServerMCPClient(servers_config)
    
    try:
        print("Attempting to create session with server...")
        async with client.session("websearch") as session:
            print("Successfully connected to server!")
            
            # Just try to load tools to verify connection is working
            tools = await load_mcp_tools(session)
            print(f"Success! Available tools: {[tool.name for tool in tools]}")
            
    except asyncio.CancelledError:
        print("Operation was cancelled")
    except Exception as e:
        print(f"Error during session: {type(e).__name__}: {str(e)}")
        print("\nDetailed error information:")
        traceback.print_exc(file=sys.stdout)
    finally:
        print("Cleaning up resources...")
        if hasattr(client, "shutdown_servers"):
            try:
                await client.shutdown_servers()
                print("Servers shut down successfully")
            except Exception as e:
                print(f"Error shutting down servers: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"Unhandled exception: {e}")
        traceback.print_exc()