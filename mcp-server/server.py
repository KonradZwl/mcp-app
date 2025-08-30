from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import requests
import os

load_dotenv()
API_URL = os.getenv("API_URL")

mcp = FastMCP(
    name="MyMCPServer",
    host="0.0.0.0",
    port=8050
)

@mcp.tool()
def get_weatherforecast():
    """ Get the weather forecast for today """
    resp = requests.get(f"{API_URL}/weatherforecast")
    return resp.text

@mcp.tool()
def get_weatherforecastbycity(city: str):
    """ Get the weather forecast for a specific city """
    resp = requests.get(f"{API_URL}/weatherforecast/city?city={city}")
    return resp.text

if __name__ == "__main__":
    transport = "sse"
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        mcp.run(transport=transport)
    else:
        raise ValueError(f"Unknown transport: {transport}")