import subprocess
from subprocess import Popen, PIPE, STDOUT
import json 
import requests
import re


cmd = "ssh -R 80:localhost:8080 ssh.localhost.run"

TOKEN = "1384286787:AAGEmu47rGPr4VqOtbgLUc8pfH92wau0OL4"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content



def send_message(text, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)
 
p = subprocess.Popen(cmd, shell=True,stdout = PIPE, stderr = STDOUT)
f = open('output.txt', 'a')

temp = 0
while True:
  line = p.stdout.readline()
  content = line.decode("utf8")
  web = re.findall("http://pi-\w+[.]localhost[.]run",content)
  if(web and temp == 0):
  	send_message("Streaming link: " + web[0], 1296216215)
  	send_message('Setting link: https://admin.localhost.run/', 1296216215)
  	temp = 1
  if not line:
  	f.close()
  	break
















