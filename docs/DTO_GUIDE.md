# Data Transfer Objects (DTOs) in LangChain/LangGraph Agents: A Complete Guide

## Table of Contents
1. [What Are DTOs and Why Use Them?](#what-are-dtos-and-why-use-them)
2. [Why DTOs Are Critical for Agents](#why-dtos-are-critical-for-agents)
3. [Lessons Learned from This Project](#lessons-learned-from-this-project)
4. [Step-by-Step Blueprint: Building Agents from Scratch](#step-by-step-blueprint-building-agents-from-scratch)
5. [DTO Implementation Patterns](#dto-implementation-patterns)
6. [Best Practices](#best-practices)
7. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
8. [Architecture Decisions](#architecture-decisions)

---

## What Are DTOs and Why Use Them?

**Data Transfer Objects (DTOs)** are simple objects that carry data between different layers of an application. In Python, we typically use **Pydantic models** or **TypedDict** to define DTOs.

### Key Characteristics:
- **Structured**: Define exact shape and types of data
- **Validated**: Automatic type checking and validation
- **Self-documenting**: Field descriptions explain purpose
- **Type-safe**: IDE autocomplete and static type checking

### Example:
```python
from pydantic import BaseModel, Field

class ConversionInput(BaseModel):
    """Input DTO for unit conversion."""
    value: float = Field(description="The value to convert")
    unit_from: str = Field(description="Source unit")
    unit_to: str = Field(description="Target unit")
```

---

## Why DTOs Are Critical for Agents

### 1. **Tool Input Validation**
Agents call tools with parameters extracted from natural language. DTOs ensure:
- ✅ Correct data types (no "37" strings when you need 37.0)
- ✅ Required fields are present
- ✅ Invalid values are caught before execution
- ✅ Clear error messages when validation fails

**Without DTOs**: Agent might pass `{"feet": "ten"}` → Tool crashes  
**With DTOs**: Agent passes `{"feet": "ten"}` → Validation error: "feet must be a float"

### 2. **Structured Output Control**
Agents need to return consistent, parseable responses. DTOs provide:
- ✅ Predictable response format
- ✅ Easy parsing and processing
- ✅ Type safety for downstream code
- ✅ Clear contracts between components

**Example**: Instead of free-form text, you get:
```python
class AgentResponse(BaseModel):
    final_answer: str
    tool_calls_used: list[str]
    confidence: float | None
```

### 3. **State Management in LangGraph**
LangGraph uses state schemas to manage conversation flow. DTOs define:
- ✅ What data flows through the graph
- ✅ How state updates are merged
- ✅ Type safety across nodes
- ✅ Clear state contracts

### 4. **Configuration Management**
Agent configuration becomes type-safe and validated:
- ✅ Invalid config values caught at startup
- ✅ IDE autocomplete for all settings
- ✅ Default values and validation rules
- ✅ Clear documentation of options

### 5. **Debugging and Observability**
DTOs make debugging easier:
- ✅ Clear structure shows what data is flowing
- ✅ Validation errors pinpoint exact issues
- ✅ Type hints help IDE debugging
- ✅ Self-documenting code

---

## Lessons Learned from This Project

### Lesson 1: Always Use `args_schema` for Tool Inputs

**Problem**: Tools had Pydantic models defined but weren't connected to the tools.

**Solution**: Set `args_schema` attribute on `BaseTool`:
```python
class FeetToMetersTool(BaseTool):
    name: str = "feet_to_meters"
    args_schema: type[BaseModel] = FeetToMeters  # ← Critical!
    
    def _run(self, **kwargs) -> float:
        validated_input = FeetToMeters(**kwargs)  # ← Validated!
        # ... use validated_input.feet, validated_input.miles
```

**Why**: LangChain validates inputs against the schema before calling `_run()`, catching errors early.

### Lesson 2: Return Types Must Match Actual Returns

**Problem**: Tool return type said `-> float` but returned `CelsiusToFarenheitResponse` object.

**Solution**: Match return type annotation:
```python
def _run(self, **kwargs) -> CelsiusToFarenheitResponse:  # ← Match actual return
    return CelsiusToFarenheitResponse(...)
```

**Why**: Type mismatches confuse the agent and can cause infinite loops.

### Lesson 3: LangGraph State Should Use TypedDict (Usually)

**Problem**: Used Pydantic `BaseModel` for state, but LangGraph prefers `TypedDict`.

**Solution**: Use `TypedDict` for state schemas:
```python
from typing import TypedDict, Annotated, Sequence
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    tool_calls_made: list[str]
    # ... other fields
```

**Why**: 
- Better performance (no validation overhead)
- Simpler state updates (just return dicts)
- More idiomatic for LangGraph

**Exception**: Use Pydantic if you need runtime validation of state updates.

### Lesson 4: Always Set `recursion_limit` to Prevent Infinite Loops

**Problem**: Agent got stuck calling the same tool repeatedly.

**Solution**: Set recursion limit in invoke:
```python
result = compiled_agent.invoke(
    {"messages": [...]},
    config={"recursion_limit": 50}  # ← Critical safety measure
)
```

**Why**: Agents can loop infinitely without limits. Always set a reasonable limit.

### Lesson 5: Structured Output Requires Clear Stopping Instructions

**Problem**: Agent kept calling tools even after getting results.

**Solution**: Improve system prompt:
```python
AGENT_PROMPT = """
1. When the user asks for a conversion, use the appropriate tool ONCE
2. After receiving the tool result, provide your final answer and STOP
3. Do NOT call the same tool multiple times
"""
```

**Why**: Agents need explicit instructions about when to stop, especially with structured output.

### Lesson 6: Wrap `create_agent` in LangGraph for Custom State

**Problem**: `create_agent` has fixed state schema (just messages).

**Solution**: Wrap it as a subgraph node:
```python
agent_subgraph = create_agent(...)  # Returns compiled graph

workflow = StateGraph(AgentState)  # Your custom state
workflow.add_node("agent", agent_subgraph)  # Use as node
workflow.add_node("track_state", track_tool_calls)  # Custom tracking
```

**Why**: You get benefits of `create_agent` (middleware, structured output) plus custom state tracking.

### Lesson 7: State Updates Return Dictionaries, Not Objects

**Problem**: Tried to return Pydantic objects from state update functions.

**Solution**: Return dictionaries with partial updates:
```python
def track_tool_calls(state: AgentState) -> dict:  # ← Returns dict
    return {
        "tool_calls_made": state.tool_calls_made + new_tools,
        "tool_call_count": state.tool_call_count + len(new_tools)
    }
```

**Why**: LangGraph merges dict updates into state. Return only fields you want to update.

---

## Step-by-Step Blueprint: Building Agents from Scratch

### Phase 1: Define Your DTOs

#### Step 1.1: Tool Input DTOs
Create Pydantic models for each tool's inputs:

```python
# tools/conversion_input.py
from pydantic import BaseModel, Field

class ConversionInput(BaseModel):
    """Input schema for unit conversion."""
    value: float = Field(description="The numeric value to convert")
    unit_from: str = Field(description="Source unit name")
    unit_to: str = Field(description="Target unit name")
```

#### Step 1.2: Tool Output DTOs
Define what tools return:

```python
# tools/conversion_output.py
from pydantic import BaseModel, Field
from datetime import datetime

class ConversionResult(BaseModel):
    """Result of a unit conversion."""
    input_value: float
    input_unit: str
    output_value: float
    output_unit: str
    timestamp: datetime = Field(default_factory=datetime.now)
```

#### Step 1.3: Agent Response DTO
Define structured output format:

```python
# dto/response.py
from pydantic import BaseModel

class AgentResponse(BaseModel):
    """Structured response from the agent."""
    final_answer: str
    tool_calls_used: list[str] = []
    confidence: float | None = None
```

#### Step 1.4: State Schema DTO
Define LangGraph state:

```python
# dto/state.py
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """State schema for the agent graph."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    tool_calls_made: list[str]
    tool_call_count: int
    errors: list[str]
    metadata: dict
```

#### Step 1.5: Configuration DTOs
Convert config dicts to Pydantic:

```python
# config.py
from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.1, ge=0, le=2)
    max_tokens: int = Field(default=50000, gt=0)
    timeout: int = Field(default=30, gt=0)

LLM_CONFIG = LLMConfig()  # Instantiate with defaults or override
```

### Phase 2: Create Tools

#### Step 2.1: Implement BaseTool Subclass
```python
# tools/my_tool.py
from langchain.tools import BaseTool
from pydantic import BaseModel
from .conversion_input import ConversionInput
from .conversion_output import ConversionResult

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "What this tool does"
    args_schema: type[BaseModel] = ConversionInput  # ← Connect DTO
    
    def _run(self, **kwargs) -> ConversionResult:
        # Validate input
        validated_input = ConversionInput(**kwargs)
        
        # Do work
        result = perform_conversion(validated_input)
        
        # Return structured output
        return ConversionResult(
            input_value=validated_input.value,
            input_unit=validated_input.unit_from,
            output_value=result,
            output_unit=validated_input.unit_to
        )
    
    async def _arun(self, **kwargs) -> ConversionResult:
        # Same as _run but async
        return self._run(**kwargs)
```

**Key Points**:
- ✅ Always set `args_schema`
- ✅ Use `**kwargs` in `_run` signature
- ✅ Validate inputs with your DTO
- ✅ Return structured DTOs, not primitives

### Phase 3: Configure the Agent

#### Step 3.1: Create LLM Instance
```python
from langchain_openai import ChatOpenAI
from config import LLM_CONFIG

llm = ChatOpenAI(
    model=LLM_CONFIG.model,
    temperature=LLM_CONFIG.temperature,
    max_tokens=LLM_CONFIG.max_tokens,
    timeout=LLM_CONFIG.timeout,
)
```

#### Step 3.2: Define System Prompt
```python
AGENT_PROMPT = """
You are a helpful assistant with access to these tools:
{tools}

Instructions:
1. Use tools when needed to answer questions
2. Call each tool ONCE per question
3. After getting tool results, provide final answer and STOP
4. Format responses clearly
"""
```

#### Step 3.3: Create Agent with Structured Output
```python
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from dto.response import AgentResponse

agent_subgraph = create_agent(
    model=llm,
    tools=[MyTool(), AnotherTool()],
    system_prompt=AGENT_PROMPT,
    response_format=ToolStrategy(AgentResponse),  # ← Structured output
    middleware=[
        # Add middleware here
    ],
)
```

### Phase 4: Build LangGraph (Optional but Recommended)

#### Step 4.1: Create State Tracking Nodes
```python
from dto.state import AgentState

def track_tool_calls(state: AgentState) -> dict:
    """Update custom state fields."""
    messages = state["messages"]
    last_message = messages[-1] if messages else None
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_names = [tc["name"] for tc in last_message.tool_calls]
        return {
            "tool_calls_made": state["tool_calls_made"] + tool_names,
            "tool_call_count": state["tool_call_count"] + len(tool_names),
        }
    return {}
```

#### Step 4.2: Build Graph
```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_subgraph)
workflow.add_node("track_state", track_tool_calls)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", "track_state")
workflow.add_edge("track_state", END)

compiled_agent = workflow.compile()
```

#### Step 4.3: Invoke with Safety Limits
```python
result = compiled_agent.invoke(
    {"messages": [{"role": "user", "content": "Your question"}]},
    config={"recursion_limit": 50}  # ← Always set this!
)
```

---

## DTO Implementation Patterns

### Pattern 1: Tool Input Validation
```python
class ToolInput(BaseModel):
    param1: float = Field(description="...", gt=0)  # Must be positive
    param2: str = Field(description="...", min_length=1)  # Non-empty

class MyTool(BaseTool):
    args_schema: type[BaseModel] = ToolInput
    
    def _run(self, **kwargs):
        validated = ToolInput(**kwargs)  # Validates automatically
        # Use validated.param1, validated.param2
```

### Pattern 2: Structured Tool Outputs
```python
class ToolOutput(BaseModel):
    result: float
    units: str
    metadata: dict = Field(default_factory=dict)

def _run(self, **kwargs) -> ToolOutput:
    # ... computation ...
    return ToolOutput(result=value, units="meters")
```

### Pattern 3: Agent Response Format
```python
class AgentResponse(BaseModel):
    answer: str
    sources: list[str] = []
    confidence: float | None = None

agent = create_agent(
    ...,
    response_format=ToolStrategy(AgentResponse)
)
```

### Pattern 4: LangGraph State Schema
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    custom_field: str
    counter: int

def update_state(state: AgentState) -> dict:
    return {"counter": state["counter"] + 1}  # Partial update
```

### Pattern 5: Configuration as DTOs
```python
class Config(BaseModel):
    value: int = Field(default=10, ge=0)
    name: str = Field(default="default")

CONFIG = Config()  # Use CONFIG.value, CONFIG.name
```

---

## Best Practices

### ✅ DO:

1. **Always use `args_schema`** for tool inputs
2. **Match return type annotations** to actual return values
3. **Use TypedDict for LangGraph state** (unless you need Pydantic validation)
4. **Set `recursion_limit`** in invoke config
5. **Return dicts from state update functions** (not objects)
6. **Validate inputs** with DTOs before processing
7. **Use Field descriptions** to help the LLM understand parameters
8. **Keep DTOs focused** - one responsibility per DTO
9. **Use default values** for optional fields
10. **Document DTOs** with docstrings

### ❌ DON'T:

1. **Don't skip `args_schema`** - tools won't validate inputs
2. **Don't mismatch return types** - causes confusion
3. **Don't use Pydantic for state** unless you need validation
4. **Don't forget recursion limits** - infinite loops await
5. **Don't return full objects** from state updates
6. **Don't use plain dicts** when DTOs would help
7. **Don't skip Field descriptions** - LLM needs context
8. **Don't make DTOs too complex** - keep them simple
9. **Don't forget defaults** for optional fields
10. **Don't ignore validation errors** - fix the root cause

---

## Common Pitfalls and Solutions

### Pitfall 1: Infinite Loops
**Symptom**: Agent calls same tool repeatedly  
**Cause**: No recursion limit or unclear stopping condition  
**Solution**: 
```python
config={"recursion_limit": 50}  # Set limit
# Plus: Clear system prompt about when to stop
```

### Pitfall 2: Type Mismatch Errors
**Symptom**: `ValidationError` or `TypeError`  
**Cause**: Return type annotation doesn't match actual return  
**Solution**: Match annotation to actual return:
```python
def _run(self, **kwargs) -> ConversionResult:  # Match actual return
    return ConversionResult(...)  # Not float!
```

### Pitfall 3: State Update Not Working
**Symptom**: State fields not updating  
**Cause**: Returning objects instead of dicts  
**Solution**: Return dict with partial updates:
```python
def update(state: AgentState) -> dict:  # Returns dict
    return {"field": new_value}  # Not AgentState(...)
```

### Pitfall 4: Tool Input Validation Failing
**Symptom**: Tool receives wrong types  
**Cause**: `args_schema` not set or wrong schema  
**Solution**: Always set `args_schema`:
```python
class MyTool(BaseTool):
    args_schema: type[BaseModel] = MyInputSchema  # Required!
```

### Pitfall 5: Can't Access State Fields
**Symptom**: `AttributeError` or `KeyError`  
**Cause**: Using wrong access pattern  
**Solution**: 
- TypedDict: `state["field"]`
- Pydantic: `state.field`

---

## Architecture Decisions

### Why Wrap `create_agent` in LangGraph?

**Decision**: Use `create_agent` as a subgraph node instead of building from scratch.

**Rationale**:
- ✅ Get all `create_agent` features (middleware, structured output)
- ✅ Add custom state tracking on top
- ✅ Best of both worlds

**Alternative**: Build LangGraph manually (more control, more work)

### Why TypedDict for State?

**Decision**: Use `TypedDict` for `AgentState` instead of Pydantic.

**Rationale**:
- ✅ Better performance (no validation overhead)
- ✅ Simpler updates (just return dicts)
- ✅ More idiomatic for LangGraph
- ✅ LangGraph handles merging automatically

**Exception**: Use Pydantic if you need runtime validation.

### Why Separate DTOs for Input/Output?

**Decision**: Separate DTOs for tool inputs vs outputs.

**Rationale**:
- ✅ Clear separation of concerns
- ✅ Different validation rules
- ✅ Easier to evolve independently
- ✅ Better documentation

### Why Configuration as DTOs?

**Decision**: Convert config dicts to Pydantic models.

**Rationale**:
- ✅ Type safety
- ✅ Validation at startup
- ✅ IDE autocomplete
- ✅ Self-documenting

---

## Summary: The DTO Advantage

Using DTOs in your agent architecture provides:

1. **Type Safety**: Catch errors before runtime
2. **Validation**: Ensure data integrity
3. **Documentation**: Self-documenting code
4. **Debugging**: Clear error messages
5. **Maintainability**: Easier to evolve and refactor
6. **Reliability**: Fewer runtime errors
7. **Observability**: Clear data flow

**The Bottom Line**: DTOs transform your agent from a fragile, hard-to-debug system into a robust, type-safe, maintainable application.

---

## Quick Reference Checklist

When building a new agent, ensure you have:

- [ ] Tool input DTOs with `args_schema` set
- [ ] Tool output DTOs matching return types
- [ ] Agent response DTO for structured output
- [ ] State schema DTO (TypedDict or Pydantic)
- [ ] Configuration DTOs (if using config)
- [ ] `recursion_limit` set in invoke config
- [ ] Clear system prompt with stopping instructions
- [ ] State update functions returning dicts
- [ ] Proper error handling middleware
- [ ] Tests covering all conversion scenarios

---

*This guide is based on lessons learned from building a unit conversion agent with LangChain and LangGraph. Use it as a blueprint for your own agent projects.*
