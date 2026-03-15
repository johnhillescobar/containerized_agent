from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from langchain.agents.structured_output import ToolStrategy
from langchain.agents.middleware import (
    ToolRetryMiddleware,
    SummarizationMiddleware,
    ContextEditingMiddleware,
    ClearToolUsesEdit,
)

from langgraph.graph import StateGraph, START, END

from dto.state import AgentState, AgentResponse
from tools.feet_meters import FeetToMetersTool
from tools.meters_feet import MetersToFeetTool
from tools.celsius_farenheit import CelsiusToFarenheitTool
from tools.fahreheit_celsius import FahrenheitToCelsiusTool
from utils.middlewere_funcs import log_messages, handle_errors
from config import AGENT_PROMPT, LLM_CONFIG, LLM_CONFIG_MIDDLEWARE

load_dotenv()


def get_agent_prompt(tools: list[BaseTool]) -> str:
    return AGENT_PROMPT.format(
        tools="\n".join([tool.name + ": " + tool.description for tool in tools])
    )


def track_tool_calls(state: AgentState) -> dict:
    """Update custom state fields based on messages"""
    messages = state.messages
    last_message = messages[-1] if messages else None

    # Extract tool calls from messages
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_names = [tc["name"] for tc in last_message.tool_calls]
        return {
            "tool_calls_made": state.tool_calls_made + tool_names,
            "tool_call_count": state.tool_call_count + len(tool_names),
        }
    return {}


def main():
    print("Hello from agent-lanchain105!")

    tools = [
        FeetToMetersTool(),
        MetersToFeetTool(),
        CelsiusToFarenheitTool(),
        FahrenheitToCelsiusTool(),
    ]

    # Create LLM
    llm = ChatOpenAI(
        model=LLM_CONFIG.model,
        temperature=LLM_CONFIG.temperature,
        max_tokens=LLM_CONFIG.max_tokens,
        timeout=LLM_CONFIG.timeout,
    )

    # Create agent
    agent_subgraph = create_agent(
        model=llm,
        tools=tools,
        system_prompt=get_agent_prompt(tools),
        # Temporarily disabled ToolStrategy to test if it's causing loops
        response_format=ToolStrategy(AgentResponse),
        middleware=[
            log_messages,
            ToolRetryMiddleware(max_retries=LLM_CONFIG_MIDDLEWARE.max_retries),
            SummarizationMiddleware(
                model=LLM_CONFIG_MIDDLEWARE.model,
                trigger=("tokens", LLM_CONFIG_MIDDLEWARE.trigger),
                keep=("messages", LLM_CONFIG_MIDDLEWARE.keep),
            ),
            ContextEditingMiddleware(
                edits=[
                    ClearToolUsesEdit(
                        trigger=LLM_CONFIG_MIDDLEWARE.trigger,
                        keep=LLM_CONFIG_MIDDLEWARE.keep,
                    )
                ]
            ),
            handle_errors,
        ],
    )

    # Build parent graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_subgraph)  # Use create_agent as a node
    workflow.add_node("track_state", track_tool_calls)  # Custom state tracking
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", "track_state")
    workflow.add_edge("track_state", END)

    # Compile with max_iterations to prevent infinite loops
    compiled_agent = workflow.compile()

    # Test questions covering different conversion types and scenarios
    test_questions = [
        # Feet to Meters conversions
        "How many meters are in 185 feet?",
        "Convert 10 feet to meters",
        "What is 5280 feet in meters?",
        # Meters to Feet conversions
        "How many feet are in 100 meters?",
        "Convert 50 meters to feet",
        # Celsius to Fahrenheit conversions
        "What is 25 degrees Celsius in Fahrenheit?",
        "Convert 0 Celsius to Fahrenheit",
        "How hot is 37 Celsius in Fahrenheit?",
        # Fahrenheit to Celsius conversions
        "What is 98.6 Fahrenheit in Celsius?",
        "Convert 32 Fahrenheit to Celsius",
    ]

    # Run tests
    print("=" * 60)
    print("Running 10 test questions...")
    print("=" * 60)

    for i, question in enumerate(test_questions, 1):
        print(f"\n[Test {i}/10]")
        print(f"Question: {question}")
        print("-" * 60)

        result_dict = compiled_agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config={
                # Allow more steps so agent can finish when model is non-deterministic (e.g. in container)
                "recursion_limit": 150,
                "configurable": {"recursion_limit": 150},
            },
        )

        result = AgentState(**result_dict)

        # Print response
        print(f"Answer: {result.messages[-1].content}")

        # Print state tracking info
        if result.tool_calls_made:
            print(f"Tools used: {', '.join(result.tool_calls_made)}")
            print(f"Total tool calls: {result.tool_call_count}")

        # Note: structured_response only exists when using ToolStrategy
        # Temporarily disabled to test loop issue
        # if result.structured_response:
        #     print(f"Structured response: {result.structured_response.final_answer}")
        #     if result.structured_response.tool_calls_used:
        #         print(
        #             f"Tool calls in response: {result.structured_response.tool_calls_used}"
        #         )

        print("-" * 60)

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
