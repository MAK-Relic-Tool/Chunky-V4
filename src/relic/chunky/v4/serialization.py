"""
Serializers and Handlers to convert to/from Bytes and the ChunkyFS
"""
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
    ChunkCollectionHandler,
    ChunkyFSSerializer,
)

from relic.chunky.v4.definitions import version as version_4p1, ChunkHeader


@dataclass
class ChunkHeaderSerializer(StreamSerializer[ChunkHeader]):
    """
    Serializes a ChunkHeader to/from a binary stream.
    """

    chunk_type_serializer: ChunkTypeSerializer
    chunk_cc_serializer: ChunkFourCCSerializer
    layout: Struct

    def unpack(self, stream: BinaryIO) -> ChunkHeader:
        chunk_type = self.chunk_type_serializer.unpack(stream)
        chunk_cc = self.chunk_cc_serializer.unpack(stream)
        version, size, name_size = self.layout.unpack_stream(stream)
        name_buffer = stream.read(name_size)
        try:
            name = name_buffer.rstrip(b"\0").decode("ascii")
        except UnicodeDecodeError as exc:
            raise ChunkNameError(name_buffer) from exc
        return ChunkHeader(chunk_type, chunk_cc, version, size, name)

    def pack(self, stream: BinaryIO, packable: ChunkHeader) -> int:
        written = 0
        written += self.chunk_type_serializer.pack(stream, packable.type)
        name_buffer = packable.name.encode("ascii")
        args = packable.cc, packable.version, packable.type, len(name_buffer)
        written += self.layout.pack(args)
        written += stream.write(name_buffer)
        return written


chunk_header_serializer = ChunkHeaderSerializer(
    chunk_type_serializer,
    chunk_cc_serializer,
    Struct("<3L"),  # replace with proper Struct
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


class _NoneHeaderSerializer(StreamSerializer[None]):
    def unpack(self, stream: BinaryIO) -> None:
        return None

    def pack(self, stream: BinaryIO, packable: None) -> int:
        return 0


def _noneHeader2Meta(_: None) -> Dict[str, object]:
    return {}


def _noneMeta2Header(_: Dict[str, object]) -> None:
    return None


_chunk_collection_handler = ChunkCollectionHandler(
    header_serializer=chunk_header_serializer,
    header2meta=_chunkHeader2meta,
    meta2header=_meta2chunkHeader,
)

chunky_fs_serializer = ChunkyFSSerializer(
    version=version_4p1,
    chunk_serializer=_chunk_collection_handler,
    header_serializer=_NoneHeaderSerializer(),
    # Replace with a NoneSerializer or a serializer which serializes a header
    header2meta=_noneHeader2Meta,  # Replace with a header -> Dict funciton
    meta2header=_noneMeta2Header,  # Replace with a Dict -> header function
)

__all__ = [
    "chunky_fs_serializer",
]
