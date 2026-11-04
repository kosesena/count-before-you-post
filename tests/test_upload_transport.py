import unittest
from cbyp.meta import httpx, _chunk_upload, UPLOAD_CHUNK_BYTES

class UploadTransport(unittest.TestCase):
 def test_large_payload_is_identical_replayable_and_bounded(self):
  body=bytes(range(256))*1000
  request=httpx.Request('POST','https://api.meta.ai/v1/responses',content=body)
  headers=dict(request.headers)
  _chunk_upload(request)
  for attempt in range(2):
   chunks=list(request.stream)
   self.assertEqual(b''.join(chunks),body)
   self.assertLessEqual(max(map(len,chunks)),UPLOAD_CHUNK_BYTES)
  self.assertEqual(dict(request.headers),headers)
  self.assertEqual(int(request.headers['content-length']),len(body))
 def test_small_request_unchanged(self):
  request=httpx.Request('POST','https://api.meta.ai/v1/responses',content=b'{}')
  stream=request.stream
  _chunk_upload(request)
  self.assertIs(request.stream,stream)
