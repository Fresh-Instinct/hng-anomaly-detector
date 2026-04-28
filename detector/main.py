from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>HNG Anomaly Detector LIVE!</h1><p>Dashboard at port 8080</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
