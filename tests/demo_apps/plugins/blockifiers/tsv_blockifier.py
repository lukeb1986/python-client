"""CSV Blockifier - Steamship Plugin."""

from typing import Any, Dict

from steamship.app import App, Response, create_handler, post
from steamship.plugin.blockifier import Blockifier
from tests.demo_apps.plugins.blockifiers.csv_blockifier import CsvBlockifier


class TsvBlockifier(CsvBlockifier, Blockifier, App):
    """Converts TSV into Tagged Steamship Blocks.

    Implementation is only here to demonstrate how plugins can be built through inheritance.
    """

    def __init__(self, client=None, config: Dict[str, Any] = None):
        super().__init__(client, config)
        self.config.delimiter = "\t"


handler = create_handler(TsvBlockifier)