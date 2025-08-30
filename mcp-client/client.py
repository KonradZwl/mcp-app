import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import ollama
import os
from dotenv import load_dotenv

load_dotenv()
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

session = None
messages = []


async def main():
    global session
    global messages

    # Connect to MCP server using sse
    async with sse_client(f"{MCP_SERVER_URL}/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as s:
            session = s
            await session.initialize()

            # List available tools from mcp server
            tools_result = await session.list_tools()

            # Build a simple dispatcher instead of fragile closures
            tool_functions = {}

            for tool_meta in tools_result.tools:
                async def make_tool_call(meta=tool_meta, **kwargs):
                    return await session.call_tool(meta.name, kwargs)

                make_tool_call.__name__ = tool_meta.name
                make_tool_call.__doc__ = tool_meta.description or "No description provided"
                tool_functions[tool_meta.name] = make_tool_call

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
                    tools=list(tool_functions.values())
                )

                # Print response with tool calls
                print("Response with tool calls:")
                for tool_call in response.message.tool_calls or []:
                    print(f" - {tool_call.function.name}: {tool_call.function.arguments}")

                results_text = []

                # Execute all tool calls sequentially
                for tool_call in response.message.tool_calls or []:
                    func_name = tool_call.function.name
                    args = tool_call.function.arguments or {}

                    func = tool_functions.get(func_name)
                    if func is None:
                        print(f"Warning: tool {func_name} not found.")
                        continue

                    try:
                        result = await func(**args)
                        if result.content and result.content[0].text:
                            results_text.append(result.content[0].text)
                    except Exception as e:
                        print(f"Error calling tool {func_name}: {e}")

                # If multiple results, combine them
                combined_results = "\n".join(results_text)
                if combined_results:
                    print(combined_results)
                    # Append using the *actual tool name* if only one tool was called, else generic
                    tool_role_name = (
                        response.message.tool_calls[0].function.name
                        if len(response.message.tool_calls or []) == 1
                        else "multiple_tools"
                    )
                    messages.append({'role': 'tool', 'name': tool_role_name, 'content': combined_results})

                # Feed back to Ollama
                followup = ollama.chat(
                    model='qwen2.5:7b-instruct',
                    messages=messages,
                    options={"max_tokens": 300}
                )

                print("\nFinal response:", followup.message.content)

if __name__ == "__main__":
    asyncio.run(main())