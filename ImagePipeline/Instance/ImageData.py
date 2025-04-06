class ImageData():
    def __init__(self, NumberOfSegment: int, SegmentOrder: int , Image: bytes) -> None:
        self.NumberOfSegment = NumberOfSegment
        self.SegmentOrder = SegmentOrder
        self.Image = Image
        
    def __call__(self):
        return self

class ImageDataFactory():
    def CreateImageData(self, NumberOfSegment: int, SegmentOrder: int , Image: bytes) -> ImageData:
        return ImageData(NumberOfSegment, SegmentOrder, Image)
    
    @staticmethod
    def ToDict(img: ImageData, ctx) -> dict:
        return dict(NumberOfSegment = img.NumberOfSegment, 
                    SegmentOrder = img.SegmentOrder, 
                    Image = img.Image)
    
    @staticmethod
    def FromDict(img: dict, ctx) -> ImageData:
        return ImageData(img.get('NumberOfSegment'), 
                         img.get('SegmentOrder'),
                         img.get('Image'))
