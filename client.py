import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient, load_mcp_tools
import traceback
import sys
import os
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

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
            
            # Load all available tools from the server
            tools = await load_mcp_tools(session)
            print(f"Success! Available tools: {[tool.name for tool in tools]}")

            # Create a ReAct agent with LangGraph if an OpenAI API key is set
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                llm = ChatOpenAI(api_key=openai_key, model="gpt-3.5-turbo")
                agent = create_react_agent(model=llm, tools=tools)
                print("Running agent with a sample prompt...")
                result = await agent.ainvoke({
                    "messages": [{"role": "user", "content": "Hello"}]
                })
                print(f"Agent result: {result}")
            else:
                print("OPENAI_API_KEY not set, skipping agent run")
            
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
