from pydantic import BaseModel, Field
from typing import Sequence, Annotated
from datetime import datetime
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentResponse(BaseModel):
    final_answer: str
    tool_calls_used: list[str] = []
    confidence: float | None = None


class AgentState(BaseModel):
    # Required: Messages for conversation
    messages: Annotated[Sequence[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="The messages in the conversation",
        add_messages=True,
    )

    # Tool tracking
    tool_calls_made: list[str] = Field(
        default_factory=list, description="The tools that have been called"
    )
    tool_call_count: int = Field(
        default=0, description="The number of tools that have been called"
    )
    current_tool: str | None = Field(
        default=None, description="The current tool that is being called"
    )

    # Results tracking
    last_conversion_result: dict | None = Field(
        default=None, description="The last conversion result"
    )

    # Error handling
    errors: list[str] = Field(
        default_factory=list, description="The errors that have occurred"
    )
    has_errors: bool = Field(default=False, description="Whether there are errors")

    # Conversation metadata
    turn_count: int = Field(
        default=0, description="The number of turns in the conversation"
    )
    conversation_started_at: datetime | None = Field(
        default=None, description="The start time of the conversation"
    )

    # Structured output (if you want to store AgentResponse)
    structured_response: AgentResponse | None = Field(
        default=None, description="The structured response"
    )

    # Flexible metadata
    metadata: dict = Field(default_factory=dict, description="The metadata")
