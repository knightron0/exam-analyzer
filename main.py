import os, io
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image
from pdf2image import convert_from_path



pth2file = input("Enter the path to the pdf file you would like to analyze: ")
pth2json = input("Enter the path to the json file for the ServiceAccountToken: ")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = pth2json
client = vision.ImageAnnotatorClient()

last = 1
pages = convert_from_path(pth2file, 500)
for i in range(1, len(pages)+1):
    fn = "page_" + str(i) + ".png"
    pages[i-1].save(fn)
questions = [[0,0,0,0]]
pgs = [0]
for i in range(1, len(pages)+1):
    pth = "page_" + str(i) + ".png" 
    with io.open(pth, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    im = Image.open(pth)
    width, height = im.size
    response = client.text_detection(image=image)
    texts = response.text_annotations
    for text in texts:
        req1 = str(last)+"."
        req2 = str(last)+")"
        req3 = str(last)
        miny =  1000000000000000000000000000000000000000        
        if(str(text.description) == req1 or str(text.description) == req2 or str(text.description) == req3):
            pgs.append(i)
            for j in text.bounding_poly.vertices:
                miny = min(miny, j.y)
            questions.append([0, miny, width, height])
            if pgs[len(pgs)-1] == pgs[len(pgs)-2]:
                questions[last-1][2] = width
                questions[last-1][3] = miny
            last += 1
for i in range(1, len(questions)):
    pth = "page_" + str(pgs[i]) + ".png" 
    image = Image.open(pth)
    cropped = image.crop((questions[i][0], questions[i][1], questions[i][2], questions[i][3]))
    fname = "question" + str(i) + ".png"
    cropped.save(fname)
