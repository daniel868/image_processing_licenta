from flask import Flask, request, Response, url_for, redirect
from kafka_service import KafkaService
import requests
import json
import sys

app = Flask(__name__)
is_authenticated = False
kafka_service = KafkaService(sys.argv[1])


@app.route('/failed', methods=['GET'])
def loginFailed():
    return 'Login Failed'


@app.route('/video', methods=['GET'])
def video():
    global is_authenticated
    args = request.args
    if args.get("userToken") is None:
        return redirect(url_for('loginFailed'))

    if is_authenticated == False:

        is_authenticated = isUserAuthenticated()

        if is_authenticated == False:
            return redirect(url_for('loginFailed'))

    print('Redirecting to video jpg endpoint')
    return Response(
        kafka_service.produce_video_stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/video-png', methods=['GET'])
def video_png():
    global is_authenticated
    args = request.args
    if args.get("userToken") is None:
        return redirect(url_for('loginFailed'))

    if is_authenticated == False:

        is_authenticated = isUserAuthenticated()

        if is_authenticated == False:
            return redirect(url_for('loginFailed'))

    print('Redirecting to video png endpoint')
    return Response(
        kafka_service.produce_png_stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/read-video', methods=['GET'])
def read_video():
    return Response(
        kafka_service.read_file_stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


def isUserAuthenticated():
    response = requests.post(
        'http://localhost:8080/api/v1/user/checkValidAuthentication',
        {'username': kafka_service.user_name},
        headers={"Authorization": f"Bearer {kafka_service.user_token}"}
    )
    return response.status_code == 200


@app.route('/video-fps', methods=['GET'])
def get_video_fps():
    response = {'FPS': round(kafka_service.fps, 2)}
    json_response = json.dumps(response).encode("utf-8")
    return Response(
        json_response,
        mimetype="application/json"
    )


if __name__ == "__main__":
    app.run()
