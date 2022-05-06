from dataclasses import asdict

from steamship.data.user import User

from steamship.app.response import Response
from steamship.base.mime_types import MimeTypes
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.data.file import File

__copyright__ = "Steamship"
__license__ = "MIT"

def check_mime(d: dict, mime: str):
    assert (d.get('http', dict()).get('headers', dict()).get('Content-Type', None) == mime)

def check_type(d: dict, type: any):
    data = d.get('data', None)
    assert (isinstance(data, type))

def check_val(d: dict,  val: any):
    data = d.get('data', None)
    assert (data == val)

def test_text_response():
    """Test test response"""
    r = Response.from_obj("Hi there")
    d = r.to_dict()
    check_mime(d, MimeTypes.TXT)
    check_type(d, str)
    check_val(d, "Hi there")

def test_dict_response():
    """Test test response"""
    r = Response.from_obj(dict(a=1))
    d = r.to_dict()
    check_mime(d, MimeTypes.JSON)
    check_type(d, dict)
    check_val(d, dict(a=1))

def test_resp_response():
    """Test test response"""
    o = BlockAndTagPluginOutput(file=File.CreateRequest(value="Foo"))
    r = Response(json=o)
    d = r.to_dict()
    check_mime(d, MimeTypes.JSON)
    check_type(d, dict)
    check_val(d, asdict(o))

def test_resp_response():
    """Test test response"""
    o = BlockAndTagPluginOutput(file=File.CreateRequest(value="Foo"))
    r = Response(json=o)
    d = r.to_dict()
    check_mime(d, MimeTypes.JSON)
    check_type(d, dict)
    check_val(d, asdict(o))

