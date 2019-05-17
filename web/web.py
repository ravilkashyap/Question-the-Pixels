from flask import Flask, request, render_template, jsonify
from tinydb import TinyDB, Query, where
from tinydb.operations import set
import os
import subprocess
#import pyttsx3
import re
app = Flask(__name__)

''' Constants (should be moved to another file) '''
IMAGE_URL = '..//static//test_images//'
IMAGE_PATH = 'web//static//test_images//'

''' Text to speech Init '''


''' DB COnfiguration '''
db = TinyDB('db/db.json')
db_query = Query()

''' DB INIT '''
    # db.insert({"image_url": "", "conversation": [{"type": "sent", "message": "Hi how are you ?"}]})

''' Index page route '''
@app.route('/', methods=["GET","POST"])
def index():
    init_data = db.all()
    print(init_data)
    return render_template("index.html", data = init_data[0])

@app.route('/upload', methods= ['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        print("Hi upload POST call", request.args)

        file_name = os.path.basename(request.args['file'])
        file_url = IMAGE_URL + file_name
        file_path = IMAGE_PATH + file_name

        db.update(set("img_url", file_url), db_query.chat_id == 1)
        db.update(set("img_path", file_path), db_query.chat_id == 1 )
        return file_url
    else:
        return '404'

@app.route('/tts', methods= ['GET', "POST"])
def tts():

    """if request.method == 'GET':
        message = request.args['message']
        print("TTS : " + message)
        message = re.sub(r'<br/>', "", message)
        # message.replace("<br/>", "")
        print("TTS : " + message)
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate-50) #set rate
        volume = engine.getProperty('volume')
        engine.setProperty('volume', volume+0.50) #set volume
        voices = engine.getProperty('voices')
        engine.setProperty('voice', 'english+f4') #voice id 0
        engine.say(message)     """
    #engine.runAndWait()
    return ''


@app.route('/convo', methods= ['GET', 'POST'])
def converstion():
    if request.method == 'GET':
        question = request.args['msg']
        print("MESSAGE : " + question)

        # subprocess call to vqa by mmoving out to root
        # print("current working dir prev " + os.getcwd())
        web_dir = os.getcwd()
        os.chdir("..")
        # print("current working dir after " + os.getcwd())

        img_path = db.search(db_query.chat_id == 1)[0]['img_path']
        print(img_path)

        std_out = open("web//output.txt", "r+")
        # std_out.write(question)
        s = subprocess.Popen(['python', 'demo.py', '-image_file_name', img_path, '-question', question], stdout = std_out)
        s.wait()
        os.chdir(web_dir)

        # parse the output to dict
        result_dict = parse_output()
        db.update(set("q_a", [{"question": question, "result": result_dict}]), db_query.chat_id == 1)

        return jsonify(result_dict)

def parse_output() :
    print("INSIDE PARSER : "+ os.getcwd())
    std_out = open("output.txt", "r+")
    result_dict = {}
    for line in std_out :
        if "%" in line :
            print(line.split(" %  "))
            value, key = line.split(" %  ")
            result_dict[key[:-1]] = value
    return(result_dict)



if __name__ == '__main__':
    app.debug = True
    app.run()
