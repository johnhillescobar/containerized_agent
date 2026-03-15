from langchain.agents.middleware import wrap_tool_call, before_model
from langchain_core.messages import ToolMessage


@before_model
def log_messages(state, runtime):
    print(f"About to call model with {len(state['messages'])} messages")
    return None  # No changes


@wrap_tool_call
def handle_errors(request, handler):
    try:
        return handler(request)  # Execute tool normally
    except Exception as e:
        return ToolMessage(content=f"Error: {e}")  # Return error instead
