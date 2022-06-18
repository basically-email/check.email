from flask import Flask, jsonify

import os
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({"docs":{"usage":{"syntax":"/<email:string>","example":"/do@crime.su"},"features":{"tempmail":{"type":"bool","description":"returns if the email is from a tempmail service"},"deliverable":{"type":"bool","description":"returns if an email is deliverable to the email address (check if the email can accept incoming emails)","error":{"type":"bool","ifTrue":{"details":"details of the error"}},"host":{"type":"json","description":"gives information about the email host"}}}}})

@app.route('/<string:email>')
def check(email):
    result = {}

    blacklist = [x for x in requests.get('https://github.com/7c/fakefilter/blob/main/txt/data.txt?raw=true').text.split('\n') if not x.startswith('#') and x != '']
    try:
        domain=email.split('@')[1]
        tld=domain.split('.')
        if len(tld[0]) > 0 and len(tld[1]) > 0:
            result['error'] = False
        else:
            return jsonify({"error": True, "details": "Invalid Email"})
    except IndexError:
        return jsonify({"error": True, "details": "Invalid Email"})
    if domain in blacklist:
        result['tempmail'] = True
    else:
        result['tempmail'] = False

    link = "http://www.find-ip-address.org/email-lookup.php"
    s = requests.session()
    head = {'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    data = {'email': email}
    cek = s.post(link, headers=head, data=data).text
    soup = BeautifulSoup(cek, 'html.parser')
    ee = soup.find("div", class_="overstyle").text

    if "not" in ee:
        result["deliverable"]=False
        result["valid"]=False

    elif "You have been temporarily blocked" in ee:
        for key, value in ee.items():
            result[key] = value

    else:
        infos = soup.find("div", class_="okvir").text.split('Connected.')[0].split('host')
        result["deliverable"]=True
        result["host"]={}
        result["host"]['mx']=infos[1].split('\n')[0].replace("...", "").split(' ')[2].replace("\"", '')
        result["host"]['smtp']=infos[2].replace("...", "").split(" ")[2].replace("\"", '')
        result["valid"]=True

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
