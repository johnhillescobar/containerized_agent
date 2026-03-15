# BaseTool Implementation and RunnableConfig

This doc explains how LangChain’s **BaseTool** works and why (and how) to use **RunnableConfig** in your tool’s `_run` and `_arun` methods.

---

## What is BaseTool?

`BaseTool` (from `langchain.tools` / `langchain_core.tools`) is the base class for defining tools that an agent can call. Your tool:

- Declares **name**, **description**, and **args_schema** (a Pydantic model) so the LLM knows when and how to call it.
- Implements **`_run`** (sync) and optionally **`_arun`** (async) to do the actual work.

The framework never passes tool inputs (e.g. `celsius`) into the schema; only the fields of your `args_schema` are sent to the model. Other parameters can be **injected at runtime**—including **RunnableConfig**.

---

## How execution flows

When the agent invokes a tool:

1. The caller uses **`tool.run(tool_input, config=config)`** or **`tool.arun(tool_input, config=config)`** (or equivalent via the runnable API).
2. **`run` / `arun`** receive `config: RunnableConfig | None` along with the serialized tool input.
3. The base class turns `tool_input` into args/kwargs via **`_to_args_and_kwargs`** (using your **args_schema**).
4. It then calls your **`_run`** or **`_arun`** with those args/kwargs and, if detected, **injects the current `config`** into a parameter you define (see below).

So: **config is available to the public API; to use it inside your tool you must declare it in `_run`/`_arun` and have it injected.**

---

## What is RunnableConfig?

`RunnableConfig` is a TypedDict that carries per-invocation configuration through the LangChain/LangGraph pipeline. It typically includes:

| Key | Purpose |
|-----|--------|
| **`callbacks`** | Callback handlers (e.g. logging, tracing, LangSmith). |
| **`metadata`** | Custom key/value metadata for the run. |
| **`tags`** | Tags for filtering or grouping runs. |
| **`run_id`** / **`run_name`** | Identity of the current run. |
| **`configurable`** | Custom key/value dict for per-invocation overrides (user id, feature flags, tenant, etc.). |

When you pass `config` into the agent (e.g. `agent.invoke(..., config={"configurable": {"user_id": "123"}})`), that same config is passed to `tool.run(..., config=...)`. If your `_run`/`_arun` declare a parameter typed as **`RunnableConfig`**, the base class will inject that config into your method so you can read callbacks, metadata, or configurable values inside the tool.

---

## How to get RunnableConfig in _run and _arun

The base implementation in `langchain_core.tools.base` uses a helper **`_get_runnable_config_param`** that looks for a parameter whose **type hint is exactly `RunnableConfig`**. If it finds one, it injects the current `config` into that parameter by name.

- **Parameter name** does not matter (e.g. `config`, `run_config`, `runnable_config` all work).
- **Type hint must be exactly `RunnableConfig`** (not `RunnableConfig | None`), or the parameter is not detected and config is not injected.

### Example (from this repo)

```python
from langchain.tools import BaseTool
from langchain_core.runnables import RunnableConfig

class CelsiusToFarenheitTool(BaseTool):
    name: str = "celsius_to_farenheit"
    description: str = "Convert Celsius to Farenheit"
    args_schema: type[BaseModel] = CelsiusToFarenheit

    def _run(self, config: RunnableConfig, **kwargs: dict) -> CelsiusToFarenheitResponse:
        # config is injected by BaseTool; use it for callbacks, metadata, configurable, etc.
        validated_input = CelsiusToFarenheit(**kwargs)
        # ... do work ...
        return CelsiusToFarenheitResponse(...)

    async def _arun(self, config: RunnableConfig, **kwargs: dict) -> CelsiusToFarenheitResponse:
        validated_input = CelsiusToFarenheit(**kwargs)
        # ... same logic, can use config for async flows ...
        return CelsiusToFarenheitResponse(...)
```

- **`**kwargs`** are the tool arguments (e.g. `celsius`) derived from the schema; they are not part of the tool’s JSON schema for the LLM.
- **`config`** is injected by the framework and is not part of the tool schema, so the model never sees or passes it.

---

## Why include RunnableConfig in your tools?

1. **Consistent context**  
   Use the same run context (callbacks, metadata, `configurable`) as the rest of the chain. For example, pass a user or tenant id in `config["configurable"]` and read it inside the tool for logging or authorization.

2. **Tracing and callbacks**  
   The same callbacks used for the agent (e.g. LangSmith) are passed in `config["callbacks"]`. If your tool does sub-runs or needs to log, you can forward this config to other runnables.

3. **Feature flags and overrides**  
   Store feature flags or environment overrides in `config["configurable"]` and branch inside the tool (e.g. use a different API or limit based on tenant).

4. **Future-proofing**  
   As the framework evolves, more behavior may depend on config (e.g. rate limits, retries, tenant-specific models). Tools that already accept `RunnableConfig` can use these without signature changes.

---

## Summary

| Topic | Detail |
|--------|--------|
| **Where config comes from** | `run(tool_input, config=...)` / `arun(tool_input, config=...)` on the tool (or equivalent invoke/stream API). |
| **How it reaches your code** | Declare a parameter with type **`RunnableConfig`** in `_run` and/or `_arun`; the base class injects the current config into that parameter. |
| **Type hint** | Use **`config: RunnableConfig`** (exactly); optional types like `RunnableConfig \| None` may not be detected. |
| **Schema** | The config parameter is not part of the tool’s `args_schema`, so the LLM never sees or sends it. |

For a full example in this repo, see **`tools/celsius_farenheit.py`**, which uses `RunnableConfig` in both `_run` and `_arun`.
