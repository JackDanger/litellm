# upload caps: images/edits default ceilings and files floor-cap (LD fork R1-M6, R1-M7)

import asyncio
import io

import pytest
from fastapi import HTTPException, UploadFile

from litellm.proxy.image_endpoints.endpoints import uploadfile_to_bytesio


class _FakeUpload(UploadFile):
    def __init__(self, payload: bytes):
        super().__init__(file=io.BytesIO(payload), filename="x.png")


def test_uploadfile_to_bytesio_small_upload_ok():
    buf = asyncio.run(uploadfile_to_bytesio(_FakeUpload(b"tiny"), max_file_size_mb=200))
    assert buf.read() == b"tiny"


def test_uploadfile_to_bytesio_oversized_raises_413():
    payload = b"x" * (201 * 1024 * 1024)

    class Oversized(_FakeUpload):
        def __init__(self):
            super().__init__(payload)

    u = Oversized()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(uploadfile_to_bytesio(u, max_file_size_mb=200))
    assert int(getattr(exc.value, "status_code", 0)) == 413


def test_uploadfile_to_bytesio_at_limit_passes():
    payload = b"x" * (1 * 1024 * 1024)
    buf = asyncio.run(uploadfile_to_bytesio(_FakeUpload(payload), max_file_size_mb=200))
    assert len(buf.read()) == 1 * 1024 * 1024

# upload caps: images/edits default ceilings and files floor-cap (LD fork R1-M6, R1-M7)

import asyncio
import io

import pytest
from fastapi import HTTPException, UploadFile

from litellm.proxy.image_endpoints.endpoints import uploadfile_to_bytesio


class _FakeUpload(UploadFile):
    def __init__(self, payload: bytes):
        super().__init__(file=io.BytesIO(payload), filename="x.png")


def test_uploadfile_to_bytesio_small_upload_ok():
    buf = asyncio.run(uploadfile_to_bytesio(_FakeUpload(b"tiny"), max_file_size_mb=200))
    assert buf.read() == b"tiny"


def test_uploadfile_to_bytesio_oversized_raises_413():
    payload = b"x" * (201 * 1024 * 1024)

    class Oversized(_FakeUpload):
        def __init__(self):
            super().__init__(payload)

    u = Oversized()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(uploadfile_to_bytesio(u, max_file_size_mb=200))
    assert int(getattr(exc.value, "status_code", 0)) == 413


def test_uploadfile_to_bytesio_at_limit_passes():
    payload = b"x" * (1 * 1024 * 1024)
    buf = asyncio.run(uploadfile_to_bytesio(_FakeUpload(payload), max_file_size_mb=200))
    assert len(buf.read()) == 1 * 1024 * 1024
