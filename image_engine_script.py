import argparse
import io
import requests
import json
from google.cloud import vision
from google.cloud.vision import types
import pyodbc
import mysql.connector
from os import listdir
from os.path import isfile, join
import Photo2 as photo
from urllib2 import urlopen
import json

def getplace(lat, lon):
    url = "http://maps.googleapis.com/maps/api/geocode/json?"
    url += "latlng=%s,%s&sensor=false" % (lat, lon)
    v = urlopen(url).read()
    j = json.loads(v)
    components = j['results'][0]['address_components']
    country = town = None
    for c in components:
        if "country" in c['types']:
            country = c['long_name']
        if "postal_town" in c['types']:
            town = c['long_name']
    return town, country

onlyfiles = [f for f in listdir("./images/") if isfile(join("./images/", f))]
clothing_words = "dress garment raiment apparel garb vesture robe tog enclothe shirt fit out overdress adorn kilt coat vest cover gown underdress costume outfit jacket frock skirt invest drape habilitate sari insect equip chemise sarong hat wear dress shirt before present social status starve educate nourish seclude scrounge subsist prostituting disrobe dehumanize india china sumptuary law clothing cloak societies weather hiking hygienic ultraviolet primates underclothing darning sunburn wind plainclothes knitwear blouse glove waistcoat kimono modiste culture undershirt modesty religion mantua gender prim turn shoe corset habit fit underwear handbag scarves lace welry attire eyeglasses footwear quilt environment underclothes menswear Amaranth Amber Amethyst Apricot Aquamarine Azure Baby blue Beige Black Blue Blue-green Blue-violet Blush Bronze Brown Burgundy Byzantium Carmine Cerise Cerulean Champagne Chartreuse green Chocolate Cobalt blue Coffee Copper Coral Crimson Cyan Desert sand Electric blue Emerald Erin Gold Gray Green Harlequin Indigo Ivory Jade Jungle green Lavender Lemon Lilac Lime Magenta Magenta rose Maroon Mauve Navy blue Ocher Olive Orange Orange-red Orchid Peach Pear Periwinkle Persian blue Pink Plum Prussian blue Puce Purple Raspberry Red Red-violet Rose Ruby Salmon Sangria Sapphire Scarlet Silver Slate gray Spring bud Spring green Tan Taupe Teal Turquoise Violet Viridian White Yellow"

clw_list = clothing_words.split()
clw = [x.lower() for x in clw_list]

for filename in onlyfiles:
    detect_labels_uri(filename)

def detect_labels_uri(uri):
    path=uri
    response={}
    [date, (long, lat)] = photo.getMetaData(path)
    """Detects labels in the file located in Google Cloud Storage or on the Web."""
    client = vision.ImageAnnotatorClient()
    #image = types.Image()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    #print content
    image = types.Image(content=content)
    #image.source.image_uri = uri
    macy_keywords = []
    #print(dir(client))
    response_label = client.label_detection(image=image)
    response_web = client.web_detection(image=image)
    labels = response_label.label_annotations
    web_annotations = response_web.web_detection

    #print(dir(response_web))
    #print((dir(labels)))
    print('Labels:')

    for label in labels:
        print (label.description)
        if label.description in clw:
            print(label)
            macy_keywords.append(label.description)
    #for annotation in web_annotations():
        #print (annotation)

    for web_entity in web_annotations.web_entities:
        print (web_entity.description)
        if any(word in web_entity.description.lower() for word in clw):
            print(web_entity)
            macy_keywords.append(web_entity.description.lower())
    city, country = getplace(lat, long)
    response["date"]=date
    response["filename"]=uri
    response["keywords"]=set(macy_keywords)
    response["location"]=city
    print response
    print set(macy_keywords)
    pushsqldata(response)


def pushsqldata(response):
    pro_res=response
    conn = mysql.connector.connect(host= "localhost", user="macyuser", password="password", database="macy")
    x = conn.cursor()
    x.execute("USE macy")
    x.execute("CREATE TABLE IF NOT EXISTS macyimages(filename varchar(100), location varchar(100), date DATE, tags varchar(10)")
    x.execute("TRUNCATE TABLE macyimages")
    x.execute ("INSERT INTO macyimages VALUES(%s,%s,%s,%s,%s)", (str(pro_res["title"]), str(pro_res["imageurl"]), str(pro_res["producturl"]), str(pro_res["price"]), str(pro_res["review"])))
    conn.commit()
    #row = x.fetchall()
    #print row
   
#detect_labels_uri("./local-filename.jpg")
