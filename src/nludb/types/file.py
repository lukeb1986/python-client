import logging
import json
import re

from nludb import __version__
from typing import Union, List, Dict, Tuple
from typing import List
from dataclasses import dataclass
from nludb.api.base import ApiBase
from nludb.types.base import Request, NludbResponse, Response
from nludb.types.conversion import ConvertRequest, ConvertResponse
from nludb.types.block import Block
from nludb.types.model import ModelTargetType
from nludb.types.parsing import DependencyMatcher, ParseRequest, PhraseMatcher, TokenMatcher, ParseResponse
from nludb.types.parsing_models import ParsingModels
from nludb.types.embedding_models import EmbeddingModels
from nludb.types.tag import *
from nludb.embedding_index import EmbeddingIndex
from nludb.types.embedding_index import IndexItem
from nludb.types.tag import TagObjectRequest

class FileUploadType:
  file = "file"
  url = "url"

_logger = logging.getLogger(__name__)

def parseDquery(query: str) -> List[Tuple[str, str, str]]:
  query = re.sub(' +', ' ', query.strip())
  parts = re.split(r'\s*(?=[@#])', query)
  ret = []

  for s in parts:
    s = s.strip()
    if not s:
      continue

    command = ''
    if s[0] in ['@', '#']:
      command = s[0]
      s = s[1:]
    
    if command == '':
      ret.append((command, None, s))
      continue

    if '"' not in s and ":" not in s:
      if command == '#':
        ret.append((command, 'contains', s))
      else:
        ret.append((command, s, None))
      continue

    modifier = None
    if ':' in s:
      ss = s.split(':')
      modifier = ss[0]
      s = ss[1]
    
    content = s
    if '"' in s:
      i = s.index('"')
      content = s[1+i:-1]
      if modifier is None:
        s = s[:i]
        modifier = s
        if modifier == '':
          modifier = None
    
    ret.append((command, modifier, content))
  return ret
  
@dataclass
class FileDeleteRequest(Request):
  fileId: str

@dataclass
class FileUploadRequest(Request):
  type: str
  corpusId: str = None
  name: str = None
  url: str = None
  fileFormat: str = None
  convert: bool = False



@dataclass
class FileDeleteResponse(Response):
  fileId: str

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "FileDeleteResponse":
    return FileDeleteResponse(
      fileId = d.get('fileId', None)
    )

@dataclass
class FileClearRequest(Request):
  fileId: str

@dataclass
class FileClearResponse(Response):
  fileId: str

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "FileDeleteResponse":
    return FileDeleteResponse(
      fileId = d.get('fileId', None)
    )

@dataclass
class FileTagRequest(Request):
  fileId: str
  model: str = None

@dataclass
class FileTagResponse(Response):
  fileId: str
  tagResult: ParseResponse

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "FileTagResponse":
    return FileTagResponse(
      fileId = d.get('fileId', None),
      tagResult = ParseResponse.safely_from_dict(d.get('tagResult', {}))
    )



@dataclass
class SpanQuery:
  text: str = None
  label: str = None
  spanType: str = None

@dataclass
class FileQueryRequest(Request):
  fileId: str
  blockType: str = None
  hasSpans: List[SpanQuery] = None
  text: str = None
  textMode: str = None
  isQuote: bool = None

@dataclass
class FileQueryResponse(Response):
  fileId: str
  blocks: List[Block]

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "FileQueryResponse":
    return FileQueryResponse(
      fileId = d.get('fileId', None),
      blocks = [Block.safely_from_dict(block) for block in d.get('blocks', None)]
    )

@dataclass
class FileRawRequest(Request):
  fileId: str

@dataclass
class ListFilesRequest(Request):
  corpusId: str = None

@dataclass
class ListFilesResponse(Response):
  files: List["File"]

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "ListFilesResponse":
    return ListFilesResponse(
      files = [File.safely_from_dict(f, client = client) for f in d.get('files', [])]
    )

@dataclass
class File(Response):
  """A file.
  """

  id: str = None
  name: str = None
  handle: str = None
  format: str = None
  spaceId: str = None
  corpusId: str = None

  def __init__(self, client: ApiBase, id: str, name: str, handle: str = None, format: str = None, corpusId: str = None, spaceId: str = None):
    self.client = client
    self.name = name
    self.handle = handle
    self.id = id
    self.format = format
    self.corpusId = corpusId
    self.spaceId = spaceId
  
  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "File":
    return File(
      client=client,
      id=d.get('id', None),
      handle=d.get('handle', None),
      name=d.get('name', None),
      format=d.get('format', None),
      corpusId=d.get('corpusId', None),
      spaceId=d.get('spaceId', None)
    )

  def delete(
    self,
    spaceId: str = None,
    spaceHandle: str = None) -> NludbResponse[FileDeleteResponse]:
    req = FileDeleteRequest(
      self.id
    )
    return self.client.post(
      'file/delete',
      req,
      expect=FileDeleteResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def clear(
    self,
    spaceId: str = None,
    spaceHandle: str = None) -> NludbResponse[FileClearResponse]:
    req = FileClearRequest(
      self.id
    )
    return self.client.post(
      'file/clear',
      req,
      expect=FileClearResponse,
      if_d_query=self,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  @staticmethod
  def upload(
    client: ApiBase,
    filename: str = None,
    name: str = None,
    content: str = None,
    format: str = None,
    corpusId: str = None,
    convert: bool = False,
    spaceId: str = None,
    spaceHandle: str = None
    ) -> "File":

    if filename is None and name is None and content is None:
      raise Exception("Either filename or name + content must be provided.")
    
    if filename is not None:
      with open(filename, 'rb') as f:
        content = f.read()
        name = filename

    req = FileUploadRequest(
      type=FileUploadType.file,
      corpusId=corpusId,
      name=name,
      fileFormat=format,
      convert=convert
    )

    return client.post(
      'file/create',
      payload=req,
      file=(name, content, "multipart/form-data"),
      expect=File,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  @staticmethod
  def list(
    client: ApiBase,
    corpusId: str = None,
    spaceId: str = None,
    spaceHandle: str = None
  ):
    req = ListFilesRequest(
      corpusId=corpusId
    )
    res = client.post(
      'file/list',
      payload=req,
      expect=ListFilesResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    ) 
    return res

  @staticmethod
  def scrape(
    client: ApiBase,
    url: str,
    name: str = None,
    corpusId: str = None,
    convert: bool = False,
    spaceId: str = None,
    spaceHandle: str = None) -> "File":
    if name is None:
      name = url
    req = FileUploadRequest(
      type=FileUploadType.url,
      name=name,
      url=url,
      corpusId=corpusId,
      convert=convert
    )

    return client.post(
      'file/create',
      payload=req,
      expect=File,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def convert(
    self, 
    model: str = None, 
    spaceId: str = None,
    spaceHandle: str = None):
    req = ConvertRequest(
      id=self.id,
      type=ModelTargetType.file,
      model = model
    )

    return self.client.post(
      'model/convert',
      payload=req,
      expect=ConvertResponse,
      asynchronous=True,
      if_d_query=self,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def parse(
    self,
    model: str = ParsingModels.EN_DEFAULT,
    tokenMatchers: List[TokenMatcher] = None,
    phraseMatchers: List[PhraseMatcher] = None,
    dependencyMatchers: List[DependencyMatcher] = None,
    spaceId: str = None,
    spaceHandle: str = None
  ):
    req = ParseRequest(
      fileId=self.id,
      model = model,
      tokenMatchers = tokenMatchers,
      phraseMatchers = phraseMatchers,
      dependencyMatchers = dependencyMatchers
    )

    return self.client.post(
      'file/parse',
      payload=req,
      expect=ParseResponse,
      asynchronous=True,
      if_d_query=self,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def tag(
    self,
    model: str = ParsingModels.EN_DEFAULT,
    spaceId: str = None,
    spaceHandle: str = None
  ):
    req = FileTagRequest(
      fileId=self.id,
      model = model
    )

    return self.client.post(
      'file/tag',
      payload=req,
      expect=FileTagResponse,
      asynchronous=True,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def dquery(
    self, 
    dQuery: str,
    spaceId: str = None,
    spaceHandle: str = None):
    blockType = None
    hasSpans = []
    text = None
    isQuote = None
    textMode = None

    for tup in parseDquery(dQuery):
      (cmd, subcmd, content) = tup
      if cmd == '':
        blockType = content
      elif cmd == '#':
        text = content
        textMode = subcmd
      elif cmd == '@':
        hasSpans.append(SpanQuery(label=subcmd, text=content))

    return self.query(
      blockType=blockType, 
      hasSpans=hasSpans,
      text=text,
      textMode=textMode,
      isQuote=isQuote,
      pd=True,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def query(
    self, 
    blockType:str = None, 
    hasSpans: List[SpanQuery] = None,
    text: str = None,
    textMode: str = None,
    isQuote: bool = None,
    pd: bool = False,
    spaceId: str = None,
    spaceHandle: str = None
    ):


    req = FileQueryRequest(
      fileId=self.id,
      blockType=blockType,
      hasSpans=hasSpans,
      text=text,
      textMode=textMode,
      isQuote=isQuote
    )

    res = self.client.post(
      'file/query',
      payload=req,
      expect=FileQueryResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )
    if not self.client.d_query:
      return res
    else:
      if pd is False:
        return res.data.blocks
      else:
        import pandas as pd    
        return pd.DataFrame([(block.type, block.value) for block in res.data.blocks], columns =['Type', 'Value'])


  def index(
    self, 
    model:str = EmbeddingModels.QA, 
    indexName: str = None, 
    blockType: str = None, 
    indexId: str = None, 
    index: "EmbeddingIndex" = None, 
    upsert: bool = True, 
    reindex: bool = True,
    spaceId: str = None,
    spaceHandle: str = None) -> "EmbeddingIndex":
    # TODO: This should really be done all on the server, but for now we'll do it in the client
    # to facilitate demos.

    if indexId is None and index is not None:
      indexId = index.id
    
    if indexName is None:
      indexName = "{}-{}".format(self.id, model)

    if indexId is None and index is None:
      index = self.client.create_index(
        name=indexName,
        model=model,
        upsert=True,
        spaceId=spaceId,
        spaceHandle=spaceHandle
      )
    elif index is None:
      index = EmbeddingIndex(
        client=self.client, 
        indexId = indexId
      )
    
    # We have an index available to us now. Perform the query.
    blocks = self.query(
      blockType = blockType,
      spaceId=spaceId,
      spaceHandle=spaceHandle      
    )
    if not self.client.d_query:
      blocks = blocks.data.blocks

    items = []
    for block in blocks:
      item = IndexItem(
        value=block.value,
        externalId=block.blockId,
        externalType="block"
      )
      items.append(item)
    
    insert_task = index.insert_many(
      items, 
      reindex=reindex,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

    if self.client.d_query:
      insert_task.wait()
      return index
    return insert_task

  def raw(
    self,
    spaceId: str = None,
    spaceHandle: str = None):
    req = FileRawRequest(
      fileId=self.id,
    )

    return self.client.post(
      'file/raw',
      payload=req,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def add_tags(
    self, 
    tags = List[Union[str, CreateTagRequest]],
    spaceId: str = None,
    spaceHandle: str = None):
    tagsNew = []
    for tag in tags:
      if type(tag) == str:
        tagsNew.append(CreateTagRequest(name=tag, upsert=True))
      elif type(tag) == CreateTagRequest:
        tagsNew.append(tag)
      else:
        raise(Exception("Unable to add tag of type: {}".format(type(tag))))

    req = TagObjectRequest(
      tags = tagsNew,
      objectType='File',
      objectId = self.id
    )

    return self.client.post(
      'tag/create',
      payload=req,
      expect=TagObjectRequest,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def remove_tags(
    self, 
    tags = List[Union[str, DeleteTagRequest]],
    spaceId: str = None,
    spaceHandle: str = None):
    tagsNew = []
    for tag in tags:
      if type(tag) == str:
        tagsNew.append(DeleteTagRequest(name=tag))
      elif type(tag) == DeleteTagRequest:
        tagsNew.append(tag)
      else:
        raise(Exception("Unable to remove tag of type: {}".format(type(tag))))

    req = TagObjectRequest(
      tags = tagsNew,
      objectType='File',
      objectId = self.id
    )

    return self.client.post(
      'tag/delete',
      payload=req,
      expect=TagObjectRequest,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def list_tags(
    self,
    spaceId: str = None,
    spaceHandle: str = None):
    req = ListTagsRequest(
      objectType='File',
      objectId = self.id
    )

    return self.client.post(
      'tag/list',
      payload=req,
      expect=TagObjectRequest,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )