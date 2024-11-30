from fpdf import FPDF
from PIL import Image

class PdfHelper():
    def __init__(self):
        super().__init__()
        self.DPI = 96
        self.MM_IN_INCH = 25.4
        self.A4_WIDTH = 210
        self.A4_HEIGHT = 297
        self.MAX_WIDTH = 700
        self.MAX_HEIGHT = 1000

    def pixelsToMM(self, pixel):
        return pixel * self.MM_IN_INCH / self.DPI

    def resizeToFit(self, imageFileName):
        im = Image.open(imageFileName)
        width, height = im.size
        widthScale = self.MAX_WIDTH / width
        heightScale = self.MAX_HEIGHT / height
        scale = min(widthScale, heightScale)
        return (
            round(self.pixelsToMM(scale * width)),
            round(self.pixelsToMM(scale * height))
        )

    def centreImage(self, pdf, imageFileName):
        width, height = self.resizeToFit(imageFileName)
        pdf.image(imageFileName, (self.A4_WIDTH - width) / 2,
                   (self.A4_HEIGHT - height) / 2,
                   width, height)

pdf = FPDF(orientation='P', unit='mm', format=(210, 297))
helper = PdfHelper()

# imagelist is the list with all image filenames
# imagelist = ['./res/screenshot_01.png', './res/screenshot_02.png', './res/screenshot_03.png', './res/screenshot_04.png']
pdf.add_page('P')
helper.image('https://pbs.twimg.com/media/ELEXwNJUwAAnZzc?format=jpg&name=small')
# imagelist = ['./res/screenshot_combined.png']
# for image in imagelist:
#     pdf.add_page('P')
#     helper.centreImage(pdf, image)

pdf.output("./res/converted.pdf", "F")
