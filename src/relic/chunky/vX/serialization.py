from dataclasses import dataclass
from typing import BinaryIO, Dict, cast
from serialization_tools.structx import Struct

from relic.chunky.core.definitions import ChunkFourCC
from relic.chunky.core.errors import ChunkNameError
from relic.chunky.core.protocols import StreamSerializer
from relic.chunky.core.serialization import (
    ChunkTypeSerializer,
    chunk_type_serializer,
    ChunkFourCCSerializer,
    chunk_cc_serializer,
    ChunkCollectionHandler, ChunkyFSSerializer
)

from relic.chunky.v1.definitions import version, ChunkHeader


@dataclass
class ChunkHeaderSerializer(StreamSerializer[ChunkHeader]):
    chunk_type_serializer: ChunkTypeSerializer # Generally included
    chunk_cc_serializer: ChunkFourCCSerializer # Generally included
    layout: Struct

    def unpack(self, stream: BinaryIO) -> ChunkHeader:
        raise NotImplementedError

    def pack(self, stream: BinaryIO, packable: ChunkHeader) -> int:
        raise NotImplementedError



chunk_header_serializer = ChunkHeaderSerializer(
    chunk_type_serializer, 
    chunk_cc_serializer,
    None # replace with proper Struct
)



def _chunkHeader2meta(header: ChunkHeader) -> Dict[str, object]:
    return {
        "name": header.name,
        "version": header.version,
        "4cc": str(header.cc),
        # Add additional metadata from the header
    }


def _meta2chunkHeader(meta: Dict[str, object]) -> ChunkHeader:
    fourcc: str = cast(str, meta["4cc"])
    version: int = cast(int, meta["version"])
    name: str = cast(str, meta["name"])
    return ChunkHeader(
        name=name, 
        cc=ChunkFourCC(fourcc), 
        version=version, 
        type=None,  # type: ignore # Automatic
        size=None,  # type: ignore # Automatic
        # Add additional metadata to insert into the header
    ) 


_chunk_collection_handler = ChunkCollectionHandler(
    header_serializer=chunk_header_serializer,
    header2meta=_chunkHeader2meta,
    meta2header=_meta2chunkHeader
)

chunky_fs_serializer = ChunkyFSSerializer(
    version=version,
    chunk_serializer=_chunk_collection_handler,
    header_serializer=None, # Replace with a NoneSerializer or a serializer which serializes a header
    header2meta=None, # Replace with a header -> Dict funciton
    meta2header=None, # Replace with a Dict -> header function
)

__all__ = [
    "chunky_fs_serializer",
]
