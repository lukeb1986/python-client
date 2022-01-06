from typing import List
from dataclasses import dataclass
from nludb.types.base import Request, Response
from nludb.api.base import ApiBase 

@dataclass
class Space(Response):
  client: ApiBase = None
  id: str = None
  name: str = None
  handle: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase) -> "Space":
    return Space(
      client = client,
      id = d.get('id', None),
      name = d.get('name', None),
      handle = d.get('handle', None)
    )

  @staticmethod
  def create(
    client: ApiBase,
    name: str,
    handle: str,
    externalId: str = None,
    externalType: str = None,
    metadata: any = None,
    upsert: bool = True
  ) -> "Space":
    req = CreateSpace(
      name=name,
      handle=handle,
      upsert=upsert,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata,
    )
    res = client.post(
      'space/create', 
      req
    )
    return Space.safely_from_dict(res.data, client=client)

@dataclass
class CreateSpace(Request):
  id: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class DeletSpaceRequest(Request):
  spaceId: str

@dataclass
class ListPrivateSpacesRequest(Request):
  pass
