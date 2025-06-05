from fastmcp import FastMCP
import httpx
import json
import asyncio
import os

# Get port from environment or use default 9001
PORT = int(os.getenv("PORT", 9001))

print(f"Initializing server on port {PORT} with SSE transport...")

# Initialize the MCP server with SSE transport
# Using the simplest configuration for FastMCP v2.6.1
mcp = FastMCP(
    "WebSearch Server", 
    version="1.0.0",
    transport="sse",  # Use single transport type
    port=PORT
)

@mcp.tool()
async def web_search(
    query: str, 
    num_results: int = 10,
    safe_search: str = "moderate"
) -> str:
    """
    Search the web for current information using Brave Search API.
    
    Args:
        query: The search term to look up
        num_results: Number of results to return (1-20)
        safe_search: Safe search setting (strict, moderate, off)
    """
    
    # Validate parameters
    if not query.strip():
        raise ValueError("Query cannot be empty")
    
    if not 1 <= num_results <= 20:
        raise ValueError("num_results must be between 1 and 20")
    
    # Get API key from environment
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return "Error: BRAVE_API_KEY environment variable not set"
    
    try:
        # Brave Search API endpoint
        url = "https://api.search.brave.com/res/v1/web/search"
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }
        
        params = {
            "q": query,
            "count": num_results,
            "safe_search": safe_search,
            "text_decorations": False,
            "search_lang": "en"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Format results
            results = []
            if "web" in data and "results" in data["web"]:
                for item in data["web"]["results"]:
                    result = {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", ""),
                        "published": item.get("age", "")
                    }
                    results.append(result)
            
            # Format output as structured text
            formatted_results = f"Web search results for '{query}':\n\n"
            for i, result in enumerate(results, 1):
                formatted_results += f"{i}. {result['title']}\n"
                formatted_results += f"   URL: {result['url']}\n"
                formatted_results += f"   Description: {result['description']}\n"
                if result['published']:
                    formatted_results += f"   Published: {result['published']}\n"
                formatted_results += "\n"
            
            return formatted_results
            
    except httpx.TimeoutException:
        return "Error: Search request timed out"
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_page_content(url: str, max_chars: int = 5000) -> str:
    """
    Fetch and extract text content from a web page.
    
    Args:
        url: The URL to fetch content from
        max_chars: Maximum characters to return
    """
    
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    
    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            headers={"User-Agent": "Mozilla/5.0 (compatible; MCP-WebSearch/1.0)"}
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Simple text extraction (you could use BeautifulSoup for better parsing)
            content = response.text
            
            # Basic HTML tag removal
            import re
            text = re.sub(r'<[^>]+>', '', content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Truncate if needed
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            return f"Content from {url}:\n\n{text}"
            
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"

if __name__ == "__main__":
    # Run the server
    print(f"Starting WebSearch Server on port {PORT} with SSE transport...")
    mcp.run(transport="sse")