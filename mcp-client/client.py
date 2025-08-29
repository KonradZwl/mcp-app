import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import ollama

session = None
messages = []

async def main():
    global session
    global messages
    
    # Connect to MCP server using sse
    async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as s:
            session = s
            await session.initialize()

            # List available tools from mcp server
            tools_result = await session.list_tools()

            # Dynamically create async Python wrapper functions
            tool_functions = []

            for tool_meta in tools_result.tools:
                async def make_tool_call(meta=tool_meta, **kwargs):
                    return await session.call_tool(meta.name, kwargs)

                make_tool_call.__name__ = tool_meta.name
                make_tool_call.__doc__ = tool_meta.description or "No description provided"
                tool_functions.append(make_tool_call)
            
            # Add system message once
            messages.append({
                'role': 'system',
                'content': (
                    "If the user asks about the weather, only answer with the temperatures for the upcoming days in a short, natural sentence. "
                    "Do not add any extra explanation or commentary. For other questions, answer normally."
                )
            })
            
            while True:
                query = input('Ask a question (or type "quit" to exit): ')
                if query.strip().lower() == "quit":
                    print("Exiting.")
                    break
                if not query:
                    continue
                
                messages.append({'role': 'user', 'content': query})

                # Call local llm
                response = ollama.chat(
                    model='qwen2.5:7b-instruct',
                    messages=messages,
                    tools=tool_functions
                )

                # Print response with tool calls
                print("Response with tool calls:")
                for tool_call in response.message.tool_calls or []:
                    print(f" - {tool_call.function.name}: {tool_call.function.arguments}")

                results = []

                for tool_call in response.message.tool_calls or []:
                    func_name = tool_call.function.name
                    args = tool_call.function.arguments or {}

                    # Find the async function wrapper
                    func = next(f for f in tool_functions if f.__name__ == func_name)
                    # Call the async function
                    result = await func(**args)
                    results.append(result)
                
                results_text = [
                    r.content[0].text if r.content else ""
                    for tool_call in response.message.tool_calls or []
                    for r in [await next(f for f in tool_functions if f.__name__ == tool_call.function.name)(**(tool_call.function.arguments or {}))]
                ]

                # If multiple results, combine them
                combined_results = "\n".join(results_text)
                print(combined_results)
                messages.append({'role': 'tool', 'name': 'get_weatherforecast', 'content': combined_results})
                
                # Feed back to Ollama
                followup = ollama.chat(
                    model='qwen2.5:7b-instruct',
                    messages=messages,
                    options={"max_tokens": 300}
                )

                print("\nFinal response:", followup.message.content)

if __name__ == "__main__":
    asyncio.run(main())