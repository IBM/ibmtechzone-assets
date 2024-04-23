import pytesseract
import matplotlib.pyplot as plt

#ßConvert pdf to images
# import module
from pdf2image import convert_from_path


# Store Pdf with convert_from_path function
images = convert_from_path('pdffile')

for i in range(len(images)):

	# Save pages as images in the pdf
	images[i].save('foldername//page'+ str(i) +'.jpg', 'JPEG')

tesseract_preds = []
for img in images:
    tesseract_preds.append(pytesseract.image_to_string(img))
print(tesseract_preds[0])
plt.imshow(images[0])
plt.title("First Image");


print(tesseract_preds[1])
plt.imshow(images[1])
plt.title("Second Image");


print(tesseract_preds[2])
plt.imshow(images[2])
plt.title("Third Image");
