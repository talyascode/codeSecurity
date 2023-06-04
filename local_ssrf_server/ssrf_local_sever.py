"""
Flask Server
by Talya Gross
http://localhost:2000/admin
"""
import sys
from flask import Flask, request, jsonify

FAKE_DATA = "user: Admin , password: pass1234!"
app = Flask(__name__)

@app.route('/admin', methods=['GET'])
def user_input():
    """
    returning fake data to the client
    """
    if request.method == "GET":
        print('sending fake data')
        return jsonify({'image': FAKE_DATA})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(sys.argv[1]))
