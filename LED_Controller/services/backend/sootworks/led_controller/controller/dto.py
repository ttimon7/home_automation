from __future__ import annotations

from pydantic import BaseModel, Field


class RgbwColorDTO(BaseModel):
    # TODO media_types should be an optinal property in the future.
    red: int = Field(..., ge=0, le=255)
    green: int = Field(..., ge=0, le=255)
    blue: int = Field(..., ge=0, le=255)
    white: int = Field(..., ge=0, le=255)
