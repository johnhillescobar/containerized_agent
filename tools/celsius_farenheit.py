from datetime import datetime
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CelsiusToFarenheit(BaseModel):
    celsius: float | None = Field(description="The temperature in Celsius")


class CelsiusToFarenheitResponse(BaseModel):
    input_value: float | None = Field(description="The input value")
    input_unit: str | None = Field(description="The input unit")
    output_value: float | None = Field(description="The output value")
    output_unit: str | None = Field(description="The output unit")
    timestamp: datetime | None = Field(description="The timestamp of the conversion")


class CelsiusToFarenheitTool(BaseTool):
    """Convert Celsius to Farenheit"""

    name: str = "celsius_to_farenheit"
    description: str = "Convert Celsius to Farenheit"
    args_schema: type[BaseModel] = CelsiusToFarenheit

    def _run(self, **kwargs: dict) -> CelsiusToFarenheitResponse:
        validated_input = CelsiusToFarenheit(**kwargs)
        celsius = validated_input.celsius

        logger.info(f"Converting Celsius to Farenheit: {celsius}")
        if celsius is None:
            raise ValueError("Celsius is required")

        farenheit = (celsius * 9 / 5) + 32

        logger.info(f"Farenheit: {farenheit}")
        return CelsiusToFarenheitResponse(
            input_value=celsius,
            input_unit="celsius",
            output_value=farenheit,
            output_unit="farenheit",
            timestamp=datetime.now(),
        )

    async def _arun(self, **kwargs: dict) -> CelsiusToFarenheitResponse:
        validated_input = CelsiusToFarenheit(**kwargs)
        celsius = validated_input.celsius

        logger.info(f"Converting Celsius to Farenheit: {celsius}")
        if celsius is None:
            raise ValueError("Celsius is required")

        farenheit = (celsius * 9 / 5) + 32

        logger.info(f"Farenheit: {farenheit}")
        return CelsiusToFarenheitResponse(
            input_value=celsius,
            input_unit="celsius",
            output_value=farenheit,
            output_unit="farenheit",
            timestamp=datetime.now(),
        )
