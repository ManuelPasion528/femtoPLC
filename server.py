from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def home():
    return "Serv idor OTA para femtoPLC"

@app.route('/update', methods=['GET'])
def update_firmware():
    return send_file('update.py', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)