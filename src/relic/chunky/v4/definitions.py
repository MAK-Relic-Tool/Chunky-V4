from __future__ import annotations

from dataclasses import dataclass

from relic.chunky.core.definitions import Version, ChunkType, ChunkFourCC
from relic.chunky.core.serialization import MinimalChunkHeader

version = Version(4)  # Replace None with the version the plugin is implementing


@dataclass
class ChunkHeader(MinimalChunkHeader):
    type: ChunkType
    cc: ChunkFourCC
    version: int
    size: int
    name: str
    # Add additional chunk header options for the chunky version


__all__ = ["version", "ChunkHeader"]
