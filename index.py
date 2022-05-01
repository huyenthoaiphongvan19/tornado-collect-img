import tornado.web
import tornado.ioloop
import db
import uuid
from pathlib import Path
import base64
import os

class uploadImgHandler(tornado.web.RequestHandler):
    
    async def get(self):
        self.render("templates/index.html")
    
    async def post(self):

        files = self.request.files["imgFile"]

        for f in files:
            fh = open(f"public/img/{f.filename}", "wb")
            fh.write(f.body)
            fh.close()

        # lay duong dan den thu muc img chua hinh anh   
        # source_path = Path(__file__).resolve()
        # source_dir = source_path.parent

        pathig = "http://localhost:8088" + r"/public/img/" + f.filename
        
        
        # tao uuid cho hinh anh
        id = uuid.uuid1()

        x = {
              "_id": str(id),
              "pathimg": str(pathig)
        }

        #the result is a JSON string:
        z = db.mycol.insert_one(x)
        print(z)
        
       
        for y in db.mycol.find():
            print(y)

        self.write(y["_id"])
        

class downloadImgHandler(tornado.web.RequestHandler):

    async def post(self):
        uuidImg = self.get_argument("uuidImg","")
        
        myquery = {"_id": str(uuidImg)}

        exemyquery = db.mycol.find_one(myquery,{'_id':0,'pathimg':1})
        
        message = exemyquery["pathimg"]

        message_bytes = message.encode('ascii')
        
        base64_bytes = base64.b64encode(message_bytes)
        
        decode_img = base64.b64decode(base64_bytes)

        self.render( "templates/showimg.html" , decode_img = decode_img)


if (__name__ == "__main__"):

    app = tornado.web.Application([
        ("/", uploadImgHandler),
        ("/public/img/(.*)", tornado.web.StaticFileHandler, {"path": "public/img"}),
        ("/download",downloadImgHandler)
    ])

    TEMPLATES_ROOT = os.path.join(os.path.dirname(__file__), 'templates')
    
    settings = {
            'template_path': TEMPLATES_ROOT,
        }
        
    app.listen(8888)
    print("Listening on port 8888")
    tornado.ioloop.IOLoop.instance().start()