import os
import tempfile
from tqdm import tqdm
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import (
    PDFReader,
    DocxReader,
    UnstructuredReader,
    FlatReader,
    HTMLTagReader,
)
from typing import Optional, Tuple
import nest_asyncio
import json

wslib.download_file("utils.py")
import utils

nest_asyncio.apply()

def load_data_with_custom_limit(reader_instance, num_files_limit: Optional[int] = None, show_progress: bool = False):
    async def write_file_to_dir(file_name, dir, pbar: Optional[tqdm] = None):
        data = await reader_instance.aget_file_data(file_name)
        with open(os.path.join(dir, file_name), "wb") as f:
            f.write(data)
        if pbar is not None:
            pbar.update()
        return data

    async def aload_data(show_progress: bool = False, num_files_limit: Optional[int] = None):
        if num_files_limit is None:
            file_names = reader_instance.list_files()
        else:
            file_names = reader_instance.list_files()[:num_files_limit]

        with tempfile.TemporaryDirectory() as temp_dir:
            with tqdm(
                total=len(file_names),
                disable=not show_progress,
                desc="Downloading files to temp dir",
            ) as pbar:
                tasks = [
                    write_file_to_dir(file_name, temp_dir, pbar)
                    for file_name in file_names
                ]
                try:
                    await asyncio.gather(*tasks)
                finally:
                    if hasattr(reader_instance, "_async_session"):
                        await reader_instance._async_session.close()
                        del reader_instance._async_session

            reader = SimpleDirectoryReader(
                temp_dir,
                file_extractor=reader_instance.file_extractor,
                num_files_limit=num_files_limit,
            )
            documents = reader.load_data(show_progress=show_progress)

        return documents

    # Set the custom limit
    reader_instance.num_files_limit = num_files_limit

    try:
        # Call the aload_data method
        return asyncio.get_event_loop().run_until_complete(aload_data(show_progress, num_files_limit))
    finally:
        # Reset the num_files_limit attribute
        reader_instance.num_files_limit = None


DEFAULT_READERS = {
    ".pdf": PDFReader(),
    ".docx": DocxReader(),
    ".pptx": UnstructuredReader(),
    ".txt": FlatReader(),
    ".html": HTMLTagReader(),
}

### Connect to Cloud Object Storage
cos_connection_dict = wslib.get_connection("CloudObjectStorage")
cos_auth_dict = json.loads(cos_connection_dict["credentials"])

cos_reader = utils.CloudObjectStorageReader(
    bucket_name=cos_connection_dict["bucket"],
    credentials={
        "apikey": cos_auth_dict["apikey"],
        "service_instance_id": cos_auth_dict["resource_instance_id"],
    },
    hostname=f"https://{cos_connection_dict['url']}",
    file_extractor=DEFAULT_READERS,
    num_files_limit=50
)
## usage of the custom function
documents = load_data_with_custom_limit(cos_reader, num_files_limit=50, show_progress=True)



