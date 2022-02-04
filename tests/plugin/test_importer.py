from steamship import ImportRequest, ImportResponse
from steamship.plugin.service import PluginRequest, PluginResponse

__copyright__ = "Steamship"
__license__ = "MIT"

from ..demo_apps.plugin_importer import TestImporterPlugin, TEST_DOC

TEST_REQ = ImportRequest(
    value="Hi there."
)
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_REQ_DICT = TEST_PLUGIN_REQ.to_dict()


def _test_resp(res):
    assert (type(res) == PluginResponse)
    assert (type(res.data) == ImportResponse)
    assert (res.data.data == TEST_DOC)


def test_importer():
    importer = TestImporterPlugin()
    res = importer.run(TEST_PLUGIN_REQ)
    _test_resp(res)