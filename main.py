import os, io
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image
from pdf2image import convert_from_path
import sys
import json
import db

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
lasttext = ""
questiontexts = []
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
            miny -= 50
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

os.mkdir('other')
data = {}
alphabet = "abcdefghijklmnopqrstuvwxyz"
for i in range(1, len(questions)):
    pth = "question"+str(i)+".png"
    with io.open(pth, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    im = Image.open(pth)
    width, height = im.size
    response = client.text_detection(image=image)
    texts = response.text_annotations
    indlast = 1
    alphalast = 0
    options = [[0,0,0,0]]
    for text in texts:
        req = "("+ str(alphabet[alphalast])+")"
        miny =  1000000000000000000000000000000000000000
        if text.description == req:
            for j in text.bounding_poly.vertices:
                miny = min(miny, j.y)
            miny -= 50 
            options.append([0, miny, width, height])
            options[indlast-1][2] = width
            options[indlast-1][3] = miny
            indlast +=1
            alphalast += 1
    q = ""
    optiontxt = []
    for j in range(len(options)):
        image = Image.open(pth)
        cropped = image.crop((options[j][0], options[j][1], options[j][2], options[j][3]))
        fname = "other/question" + str(i) + "option" + str(j) + ".png"
        cropped.save(fname)
        with io.open(fname, 'rb') as image_file:
            content = image_file.read()
        image2 = vision.types.Image(content=content)
        response = client.text_detection(image=image2)
        texts2 = response.text_annotations
        if j == 0:
            q = texts2[0].description
        else:
            temp = texts2[0].description
            tofnd = "(" + str(alphabet[j-1]) + ")"
            fin2 = temp.replace(tofnd, "")
            fin = fin2.replace("\n", "")
            optiontxt.append(fin)
    temp = {}
    temp["question"] = q
    temp["options"] = optiontxt
    data[i] = temp
    db.addquestion(str(q))
    for j in optiontxt:
        db.addoptions(i, str(j))

with open('data.json', 'w') as outfile:
    json.dump(data, outfile)
