from __future__ import annotations

from steamship.base import CamelModel
from steamship.data.file import File


class BlockAndTagPluginOutput(CamelModel):
    file: File.CreateRequest = None
