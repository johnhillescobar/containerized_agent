from datetime import datetime
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FahrenheitToCelsius(BaseModel):
    fahrenheit: float | None = Field(description="The temperature in Fahrenheit")


class FahrenheitToCelsiusResponse(BaseModel):
    input_value: float | None = Field(description="The input value")
    input_unit: str | None = Field(description="The input unit")
    output_value: float | None = Field(description="The output value")
    output_unit: str | None = Field(description="The output unit")
    timestamp: datetime | None = Field(description="The timestamp of the conversion")


class FahrenheitToCelsiusTool(BaseTool):
    """Convert Fahrenheit to Celsius"""

    name: str = "fahrenheit_to_celsius"
    description: str = "Convert Fahrenheit to Celsius"
    args_schema: type[BaseModel] = FahrenheitToCelsius

    def _run(self, **kwargs: dict) -> float:
        validated_input = FahrenheitToCelsius(**kwargs)
        fahrenheit = validated_input.fahrenheit

        logger.info(f"Converting Fahrenheit to Celsius: {fahrenheit}")

        if fahrenheit is None:
            raise ValueError("Fahrenheit is required")

        celsius = (fahrenheit - 32) * 5 / 9

        logger.info(f"Celsius: {celsius}")
        return FahrenheitToCelsiusResponse(
            input_value=fahrenheit,
            input_unit="fahrenheit",
            output_value=celsius,
            output_unit="celsius",
            timestamp=datetime.now(),
        )

    async def _arun(self, **kwargs: dict) -> float:
        validated_input = FahrenheitToCelsius(**kwargs)
        fahrenheit = validated_input.fahrenheit

        logger.info(f"Converting Fahrenheit to Celsius: {fahrenheit}")

        if fahrenheit is None:
            raise ValueError("Fahrenheit is required")

        celsius = (fahrenheit - 32) * 5 / 9

        logger.info(f"Celsius: {celsius}")
        return FahrenheitToCelsiusResponse(
            input_value=fahrenheit,
            input_unit="fahrenheit",
            output_value=celsius,
            output_unit="celsius",
            timestamp=datetime.now(),
        )
