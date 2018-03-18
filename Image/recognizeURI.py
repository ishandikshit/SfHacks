import argparse
import io
import requests
import json
from google.cloud import vision
from google.cloud.vision import types
import pyodbc
import mysql.connector
import webcolors

clothing_words = "dress garment raiment apparel garb vesture robe tog enclothe shirt fit out overdress adorn kilt coat vest cover gown underdress costume outfit jacket frock skirt invest drape habilitate sari insect equip chemise sarong hat wear dress shirt before present social status starve educate nourish seclude scrounge subsist prostituting disrobe dehumanize india china sumptuary law clothing cloak societies weather hiking hygienic ultraviolet primates underclothing darning sunburn wind plainclothes knitwear blouse glove waistcoat kimono modiste culture undershirt modesty religion mantua gender prim turn shoe corset habit fit underwear handbag scarves lace welry attire eyeglasses footwear quilt environment underclothes menswear Amaranth Amber Amethyst Apricot Aquamarine Azure Baby blue Beige Black Blue Blue-green Blue-violet Blush Bronze Brown Burgundy Byzantium Carmine Cerise Cerulean Champagne Chartreuse green Chocolate Cobalt blue Coffee Copper Coral Crimson Cyan Desert sand Electric blue Emerald Erin Gold Gray Green Harlequin Indigo Ivory Jade Jungle green Lavender Lemon Lilac Lime Magenta Magenta rose Maroon Mauve Navy blue Ocher Olive Orange Orange-red Orchid Peach Pear Periwinkle Persian blue Pink Plum Prussian blue Puce Purple Raspberry Red Red-violet Rose Ruby Salmon Sangria Sapphire Scarlet Silver Slate gray Spring bud Spring green Tan Taupe Teal Turquoise Violet Viridian White Yellow swim swimwear baby neckline flower bride shoulder collar button brief briefs male female hoodie lace sweater"

clw_list = clothing_words.split()
clw = [x.lower() for x in clw_list]
def detect_labels_uri(uri):
    path=uri
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
    response_image_properties = client.image_properties(image=image)
    image_props = response_image_properties.image_properties_annotation
    gender=""
    color=""
    for color in image_props.dominant_colors.colors:
        print int(color.color.red)
        xx, color = get_colour_name((int(color.color.red),int(color.color.green),int(color.color.blue)))
        print color, xx
        if xx is not None:
            color=xx
        break;

    #print(dir(response_web))
    #print((dir(labels)))
    print('Labels:')

    for label in labels:
        #print (label.description)
        if any(word in label.description.lower() for word in clw) and label.score>0.90 and label.description not in ["t shirt", "t-shirt", "long-sleeved t-shirt"]:
            if label.description.lower() in ["male","female"]:
                gender=label.description
            print(label.description, label.score)
            macy_keywords.append(label.description)
    #for annotation in web_annotations():
        #print (annotation)

    for web_entity in web_annotations.web_entities:
        #print (web_entity.description)
        if any(word in web_entity.description.lower() for word in clw) and web_entity.score>0.55 and web_entity.description.lower not in ["dress", "t-shirt", "t shirt", "long-sleeved t-shirt"]:
            #print(web_entity)
            if web_entity.description.lower() in ["male", "female"]:
                gender= web_entity.description
            macy_keywords.append(web_entity.description.lower())
    #print gender
    resp = set(macy_keywords[:3])
    resp.add(gender)
    resp.add(color)
    #print set(macy_keywords)
    return get_macy_links(resp)

def detect_labels_uri2(uri,tag):
    path=""+str(uri)
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
    #print('Labels:')

    for label in labels:
        #print (label.description)
        if label.description in clw:
            #print(label)
            macy_keywords.append(label.description)
    #for annotation in web_annotations():
        #print (annotation)

    for web_entity in web_annotations.web_entities:
        #print (web_entity.description)
        if any(word in web_entity.description.lower() for word in clw):
            #print(web_entity)
            macy_keywords.append(web_entity.description.lower())
    macy_keywords.append(tag)
    #print set(macy_keywords)
    return get_macy_links(set(macy_keywords[:3]))
def get_macy_links(macy_keywords):
    if "t shirt" in macy_keywords:
        macy_keywords.remove("t shirt")
    if "t-shirt" in macy_keywords:
        macy_keywords.remove("t-shirt")
    if "dress shirt" in macy_keywords:
        macy_keywords.remove("dress shirt")

    search_string=' '.join(word for word in macy_keywords)
    #print (search_string)
    # api-endpoint
    URL = "http://api.macys.com/v4/catalog/search?searchphrase="+str(search_string)
    #print URL
    # defining a params dict for the parameters to be sent to the API
    #PARAMS = {'address':location}
    headers = {'X-Macys-Webservice-Client-Id': 'hack4thon','Accept': 'application/json'}
    # sending get request and saving the response as response object
    r = requests.get(url = URL, headers=headers)
    #print "-------------------------"
    #print r.json()
    # extracting data in json format
    response = []
    data = r.json()["searchresultgroups"][0]["products"]["product"]
    count=6
    for product in data:
        #print product["summary"]["name"]
        pro_res={}
        pro_res["title"]=product["summary"]["name"]
        if product["price"].has_key("sale"):
            if product["price"]["sale"].has_key("value"):
                pro_res["price"]=product["price"]["sale"]["value"]
            else:
                pro_res["price"]=20
        elif product["price"].has_key("current"):
            pro_res["price"]=product["price"]["current"]["value"]
        elif product["price"].has_key("regular"):
            pro_res["price"]=product["price"]["regular"]["value"]
        elif product["price"].has_key("original"):
            pro_res["price"]=product["price"]["original"]["value"]
        if product.has_key("review_summary"):
            pro_res["review"]=product["review_summary"]["overallrating"]
        else:
            pro_res["review"]=0
        #print product["summary"]["producturl"]
        pro_res["producturl"]=product["summary"]["producturl"]
        for image in product["image"]:
            if image["imagetype"]=="PRIMARY_IMAGE":
                #print image["imageurl"]
                pro_res["imageurl"]=image["imageurl"]
        response.append(pro_res)
        count=count-1
        if count==0:
            break
    response_final={}
    response_final["response"]=response
    pushsqldata(response)
    #print response_final
    return response_final

def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
        try:
            closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
        except ValueError:
            closest_name = closest_colour(requested_colour)
            actual_name = None
        return actual_name, closest_name

def pushsqldata(response):
    conn = mysql.connector.connect(host= "localhost", user="macyuser", password="password", database="macy")
    x = conn.cursor()
    x.execute("USE macy")
    x.execute("CREATE TABLE IF NOT EXISTS macytable(title varchar(100), imageurl varchar(100), producturl varchar(100), price varchar(10), reviews varchar(10))")
    x.execute("TRUNCATE TABLE macytable")
    conn.commit()
    for pro_res in response:
        x.execute ("INSERT INTO macytable VALUES(%s,%s,%s,%s,%s)", (str(pro_res["title"]), str(pro_res["imageurl"]), str(pro_res["producturl"]), str(pro_res["price"]), str(pro_res["review"])))
    conn.commit()
    #row = x.fetchall()
    #print row
   
#detect_labels_uri2("/home/pkgishere/vision/images/IshanGreenHood.jpg", "hoodie")
