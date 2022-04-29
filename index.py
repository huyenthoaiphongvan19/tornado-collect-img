import tornado.web
import tornado.ioloop
import db
import uuid
from pathlib import Path
import base64
import os

import cv2
import io
from PIL import Image
import torch
from werkzeug.exceptions import BadRequest

# https://docs.ovh.com/asia/en/publiccloud/ai/training/web-service-yolov5/
class LogoDetection(tornado.web.RequestHandler):
    async def get(self):
        self.render("template/index.py")

    async def post(self):
        file = extract_img(request)
        img_bytes = file.read()
        # choice of the model
        results = LogoDetection.get_prediction(img_bytes,dictOfModels[request.form.get("model_choice")])
        print(f'User selected model : {request.form.get("model_choice")}')
        # updates results.imgs with boxes and labels
        results.render()
        # encoding the resulting image and return it
        for img in results.imgs:
          RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
          im_arr = cv2.imencode('.jpg', RGB_img)[1]
          response = make_response(im_arr.tobytes())
          response.headers['Content-Type'] = 'image/jpeg'
        # return your image with boxes and labels
        return response

    async def extract_img(request):
        # checking if image uploaded is valid
        if 'file' not in request.files:
          raise BadRequest("Missing file parameter!")
        file = request.files['file']
        if file.filename == '':
          raise BadRequest("Given file is invalid")
        return file

    async def get_prediction(img_bytes,model):
        img = Image.open(io.BytesIO(img_bytes))
        # inference
        results = model(img, size=640)  
        return results

    async def loadweight():
        # create a python dictionary for your models d = {<key>: <value>, <key>: <value>, ..., <key>: <value>}
        dictOfModels = {}
        # create a list of keys to use them in the select part of the html code
        listOfKeys = []
        for r, d, f in os.walk("models_train"):
          for file in f:
           if ".pt" in file:
            # example: file = "model1.pt"
            # the path of each model: os.path.join(r, file)
            dictOfModels[os.path.splitext(file)[0]] = torch.hub.load('ultralytics/yolov5', 'custom', path=os.path.join(r, file), force_reload=True)
            # you would obtain: dictOfModels = {"model1" : model1 , etc}
          for key in dictOfModels :
            listOfKeys.append(key)     # put all the keys in the listOfKeys
          print(listOfKeys)

class uploadImgHandler(tornado.web.RequestHandler):
    
    async def get(self):
        self.render("template/index.html")
    
    async def post(self):

        files = self.request.files["imgFile"]

        for f in files:
            fh = open(f"public/img/{f.filename}", "wb")
            fh.write(f.body)
            fh.close()

        # lay duong dan den thu muc img chua hinh anh   
        source_path = Path(__file__).resolve()
        source_dir = source_path.parent

        pathig = str(source_dir) + r"\public\img\\"+ f.filename
        
        
        # tao uuid cho hinh anh
        id = uuid.uuid1()

        x = {
              "_id": str(id),
              "pathimg": str(pathig)
        }

        # self.redirect(f"http://localhost:8088/img/{f.filename}")
        self.write(x["_id"])

        #the result is a JSON string:
        # z = db.mycol.insert_one(x)
        # print(z)
        
       
        # for y in db.mycol.find():
        #     print(y)

        # self.write(y["_id"])
        
        # Enable doan code de chay tren vscode
        # self.redirect(pathig)

        # Enable doan code de chay tren Docker
        #self.redirect(f"http://localhost:8088/img/{f.filename}")
        

class downloadImgHandler(tornado.web.RequestHandler):

    async def post(self):
        uuidImg = self.get_argument("uuidImg","")
        
        myquery = {"_id": str(uuidImg)}

        exemyquery = db.mycol.find_one(myquery,{'_id':0,'pathimg':1})
        
        message = exemyquery["pathimg"]

        message_bytes = message.encode('ascii')
        
        base64_bytes = base64.b64encode(message_bytes)
        
        decode_img = base64.b64decode(base64_bytes)

        self.render( "template/showimg.html" , decode_img = decode_img)


if (__name__ == "__main__"):
    app = tornado.web.Application([
        ("/", uploadImgHandler),
        ("/img/(.*)", tornado.web.StaticFileHandler, {"path": "img"}),
        ("/download",downloadImgHandler)
    ])

    TEMPLATES_ROOT = os.path.join(os.path.dirname(__file__), 'templates')
    
    settings = {
            'template_path': TEMPLATES_ROOT,
        }
        
    app.listen(8888)
    print("Listening on port 8888")
    tornado.ioloop.IOLoop.instance().start()