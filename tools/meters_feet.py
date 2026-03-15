from datetime import datetime
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetersToFeet(BaseModel):
    meters: float | None = Field(description="The length in meters")
    kilometers: float | None = Field(description="The length in kilometers")
    expressed_in_kilometers: bool | None = Field(
        description="If True, the length is expressed in kilometers, if False, the length is expressed in meters"
    )
    expressed_in_meters: bool | None = Field(
        description="If True, the length is expressed in meters, if False, the length is expressed in kilometers"
    )


class MetersToFeetResponse(BaseModel):
    input_value: float | None = Field(description="The input value")
    input_unit: str | None = Field(description="The input unit")
    output_value: float | None = Field(description="The output value")
    output_unit: str | None = Field(description="The output unit")
    timestamp: datetime | None = Field(description="The timestamp of the conversion")


class MetersToFeetTool(BaseTool):
    """Convert Meters to Feet"""

    name: str = "meters_to_feet"
    description: str = "Convert Meters to Feet"
    args_schema: type[BaseModel] = MetersToFeet

    def _run(
        self,
        **kwargs: dict,
    ) -> float:
        validated_input = MetersToFeet(**kwargs)
        meters = validated_input.meters
        kilometers = validated_input.kilometers
        expressed_in_kilometers = validated_input.expressed_in_kilometers
        expressed_in_meters = validated_input.expressed_in_meters

        logger.info(f"Converting Meters to Feet: {meters}")

        if meters is not None:
            feet = meters * 3.28084

            if expressed_in_kilometers:
                feet = feet / 1.60934

            logger.info(f"Feet: {feet}")
            return MetersToFeetResponse(
                input_value=meters,
                input_unit="meters",
                output_value=feet,
                output_unit="feet",
                timestamp=datetime.now(),
            )

        elif kilometers is not None:
            meters = kilometers * 1000

            if expressed_in_meters:
                meters = meters / 3.28084

            logger.info(f"Meters: {meters}")
            return MetersToFeetResponse(
                input_value=kilometers,
                input_unit="kilometers",
                output_value=meters,
                output_unit="meters",
                timestamp=datetime.now(),
            )

        else:
            raise ValueError("Meters or Kilometers is required")

    async def _arun(
        self,
        **kwargs: dict,
    ) -> float:
        validated_input = MetersToFeet(**kwargs)
        meters = validated_input.meters
        kilometers = validated_input.kilometers
        expressed_in_kilometers = validated_input.expressed_in_kilometers
        expressed_in_meters = validated_input.expressed_in_meters

        logger.info(f"Converting Meters to Feet: {meters}")

        if meters is not None:
            feet = meters * 3.28084

            if expressed_in_kilometers:
                feet = feet / 1.60934

            logger.info(f"Feet: {feet}")
            return MetersToFeetResponse(
                input_value=meters,
                input_unit="meters",
                output_value=feet,
                output_unit="feet",
                timestamp=datetime.now(),
            )

        elif kilometers is not None:
            meters = kilometers * 1000

            if expressed_in_meters:
                meters = meters / 3.28084

            logger.info(f"Meters: {meters}")
            return MetersToFeetResponse(
                input_value=kilometers,
                input_unit="kilometers",
                output_value=meters,
                output_unit="meters",
                timestamp=datetime.now(),
            )

        else:
            raise ValueError("Meters or Kilometers is required")
