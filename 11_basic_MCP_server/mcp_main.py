import random
from fastmcp import FastMCP

# Create a FastMCP server instance
mcp = FastMCP(name="FastMCP Demo Server")

@mcp.tool
def roll_dice(n_dice: int = 1) -> list[int]:
    """Roll n_dice 6-sided dice and return the results."""
    return [random.randint(1, 6) for _ in range(n_dice)]

@mcp.tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    mcp.run()

# Test the server locally http://localhost:6274/   make sure config file is saved and claude is looking in same location
# uv run fastmcp dev inspector 11_basic_MCP_server/mcp_main.py

# to connect with claude desktop
# uv run fastmcp install claude-desktop 11_basic_MCP_server/mcp_main.py