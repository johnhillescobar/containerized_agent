from datetime import datetime
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeetToMeters(BaseModel):
    feet: float | None = Field(description="The length in feet")
    miles: float | None = Field(description="The length in miles")
    expressed_in_miles: bool | None = Field(
        description="If True, the length is expressed in miles, if False, the length is expressed in feet"
    )
    expressed_in_feet: bool | None = Field(
        description="If True, the length is expressed in feet, if False, the length is expressed in miles"
    )


class FeetToMetersResponse(BaseModel):
    input_value: float | None = Field(description="The input value")
    input_unit: str | None = Field(description="The input unit")
    output_value: float | None = Field(description="The output value")
    output_unit: str | None = Field(description="The output unit")
    timestamp: datetime | None = Field(description="The timestamp of the conversion")


class FeetToMetersTool(BaseTool):
    """Convert Feet to Meters"""

    name: str = "feet_to_meters"
    description: str = "Convert Feet to Meters"
    args_schema: type[BaseModel] = FeetToMeters

    def _run(
        self,
        **kwargs: dict,
    ) -> float:
        validated_input = FeetToMeters(**kwargs)
        feet = validated_input.feet
        miles = validated_input.miles
        expressed_in_miles = validated_input.expressed_in_miles
        expressed_in_feet = validated_input.expressed_in_feet

        logger.info(f"Converting Feet to Meters: {feet}")

        if feet is not None:
            meters = feet * 0.3048

            if expressed_in_miles:
                meters = meters / 1609.34

            logger.info(f"Meters: {meters}")
            return FeetToMetersResponse(
                input_value=feet,
                input_unit="feet",
                output_value=meters,
                output_unit="meters",
                timestamp=datetime.now(),
            )

        elif miles is not None:
            kilometers = miles * 1.60934

            if expressed_in_feet:
                kilometers = kilometers * 0.621371

            logger.info(f"Kilometers: {kilometers}")
            return FeetToMetersResponse(
                input_value=feet,
                input_unit="feet",
                output_value=kilometers,
                output_unit="kilometers",
                timestamp=datetime.now(),
            )

        else:
            raise ValueError("Feet or Miles is required")

    async def _arun(
        self,
        **kwargs: dict,
    ) -> float:
        validated_input = FeetToMeters(**kwargs)
        feet = validated_input.feet
        miles = validated_input.miles
        expressed_in_miles = validated_input.expressed_in_miles
        expressed_in_feet = validated_input.expressed_in_feet

        logger.info(f"Converting Feet to Meters: {feet}")

        if feet is not None:
            meters = feet * 0.3048

            if expressed_in_miles:
                meters = meters / 1609.34

            logger.info(f"Meters: {meters}")
            return FeetToMetersResponse(
                input_value=feet,
                input_unit="feet",
                output_value=meters,
                output_unit="meters",
                timestamp=datetime.now(),
            )

        elif miles is not None:
            kilometers = miles * 1.60934

            if expressed_in_feet:
                kilometers = kilometers * 0.621371

            logger.info(f"Kilometers: {kilometers}")
            return FeetToMetersResponse(
                input_value=feet,
                input_unit="feet",
                output_value=kilometers,
                output_unit="kilometers",
                timestamp=datetime.now(),
            )

        else:
            raise ValueError("Feet or Miles is required")
