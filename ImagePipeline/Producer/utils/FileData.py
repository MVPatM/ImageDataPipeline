from PIL import Image, ImageFile
from io import BytesIO
import os, aiofiles

class FileData():
    def __init__(self, img_byte: bytes, file_name: str):
        self.imgbyte = img_byte
        self.file_name = file_name
        self.file_format = Image.open(BytesIO(self.imgbyte)).format.lower()
    
    def get_imgfile(self) -> ImageFile:
        return Image.open(BytesIO(self.imgbyte))
    
    def get_imgbyte(self) -> bytes:
        return self.imgbyte
    
    def get_imgBytesIO(self) -> BytesIO:
        return BytesIO(self.imgbyte)
    
    def get_filename(self) -> str:
        return self.file_name
    
    def get_file_fullname(self) -> str:
        return self.get_filename() + "." + self.get_fileformat()
    
    def get_fileformat(self) -> str:
        return self.file_format
