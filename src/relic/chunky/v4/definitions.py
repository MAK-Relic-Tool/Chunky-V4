"""
Definitions used to handle Chunky v5.X
"""
from __future__ import annotations

from dataclasses import dataclass

from relic.chunky.core.definitions import Version, ChunkType, ChunkFourCC
from relic.chunky.core.serialization import MinimalChunkHeader

version = Version(4)


@dataclass
class ChunkHeader(MinimalChunkHeader):
    """
    Header for a Data/Folder Chunk.

    CC helps determine the format of the chunk's contents.
    Version helps differentiate different versions of a 4CC format.
    Size is the size of the chunk in bytes.
    Name is the name of the chunk; this is typically empty.
    """

    type: ChunkType
    cc: ChunkFourCC
    version: int
    size: int
    name: str


__all__ = ["version", "ChunkHeader"]
