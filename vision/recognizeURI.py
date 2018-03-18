import argparse
import io
import requests
import json
from google.cloud import vision
from google.cloud.vision import types

clothing_words = "dress garment raiment apparel garb vesture robe tog enclothe shirt fit out overdress adorn kilt coat vest cover gown underdress costume outfit jacket frock skirt invest drape habilitate sari insect equip chemise sarong hat wear dress shirt before present social status starve educate nourish seclude scrounge subsist prostituting disrobe dehumanize india china sumptuary law clothing cloak societies weather hiking hygienic ultraviolet primates underclothing darning sunburn wind plainclothes knitwear blouse glove waistcoat kimono modiste culture undershirt modesty religion mantua gender prim turn shoe corset habit fit underwear handbag scarves lace welry attire eyeglasses footwear quilt environment underclothes menswear Amaranth Amber Amethyst Apricot Aquamarine Azure Baby blue Beige Black Blue Blue-green Blue-violet Blush Bronze Brown Burgundy Byzantium Carmine Cerise Cerulean Champagne Chartreuse green Chocolate Cobalt blue Coffee Copper Coral Crimson Cyan Desert sand Electric blue Emerald Erin Gold Gray Green Harlequin Indigo Ivory Jade Jungle green Lavender Lemon Lilac Lime Magenta Magenta rose Maroon Mauve Navy blue Ocher Olive Orange Orange-red Orchid Peach Pear Periwinkle Persian blue Pink Plum Prussian blue Puce Purple Raspberry Red Red-violet Rose Ruby Salmon Sangria Sapphire Scarlet Silver Slate gray Spring bud Spring green Tan Taupe Teal Turquoise Violet Viridian White Yellow"

clw_list = clothing_words.split()
clw = [x.lower() for x in clw_list]
def detect_labels_uri(uri):
    """Detects labels in the file located in Google Cloud Storage or on the Web."""
    client = vision.ImageAnnotatorClient()
    image = types.Image()
    image.source.image_uri = uri
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

    print set(macy_keywords)
    get_macy_links(set(macy_keywords))

def get_macy_links(macy_keywords):
    search_string=' '.join(word for word in macy_keywords)
    print (search_string)
    # api-endpoint
    URL = "http://api.macys.com/v4/catalog/search?searchphrase="+str(search_string)
    # defining a params dict for the parameters to be sent to the API
    #PARAMS = {'address':location}
    headers = {'X-Macys-Webservice-Client-Id': 'hack4thon','Accept': 'application/json'}
    # sending get request and saving the response as response object
    r = requests.get(url = URL, headers=headers)
    # extracting data in json format
    response = []
    data = r.json()["searchresultgroups"][0]["products"]["product"]
    for product in data:
        print product["summary"]["name"]
        pro_res={}
        pro_res["title"]=product["summary"]["name"]
        print product["summary"]["producturl"]
        pro_res["producturl"]=product["summary"]["producturl"]
        for image in product["image"]:
            if image["imagetype"]=="PRIMARY_IMAGE":
                print image["imageurl"]
                pro_res["imageurl"]=image["imageurl"]
        response.append(pro_res)
    response_final={}
    response_final["response"]=response
    print json.dumps(response_final,indent=4)
    #print response
detect_labels_uri("https://dimg.dillards.com/is/image/DillardsZoom/main/emma-street-illusion-lace-mock-2-piece-dress/05015429_zi_blue_bell.jpg")
