import os
from azure.storage.blob import BlobServiceClient

try:
  print("한국방송통신대학교 클라우드 컴퓨팅 Blob 파일 다운로드")
  connect_str = "DefaultEndpointsProtocol=https;AccountName=lvtlvt;AccountKey=2he5vxXrv+H9FkIWkv97cw5+iK3kRcrnd5XglR/LfHEJdjhcKhAEFeKBRyE8a8Yp2DAPM8CF/p8Z+AStpxJd5A==;EndpointSuffix=core.windows.net"
  blob_service_client = BlobServiceClient.from_connection_string(connect_str)
  container_name = "lvtlvtcontainer"

  remote_file_name = "generated-image.png" 
  local_file_name = "generated-image_down.png"

  blob_client = blob_service_client.get_blob_client(container=container_name, blob=remote_file_name)

  print("\nDownloading blob from Azure Storage:\n\t" + remote_file_name)

  with open(file=os.path.join('', local_file_name), mode="wb") as download_blob:
        download_stream = blob_client.download_blob()
        download_blob.write(download_stream.readall())

except Exception as ex: 
  print('Exception:')
  print(ex)