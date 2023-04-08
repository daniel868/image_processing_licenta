from flask import Flask, request, Response, url_for, redirect
from kafka_service import KafkaService
import requests

app = Flask(__name__)
is_authenticated = False
kafka_service = KafkaService()


@app.route('/failed', methods=['GET'])
def loginFailed():
    return 'Login Failed'


@app.route('/video', methods=['GET'])
def video():
    global is_authenticated
    args = request.args
    if (args.get("userToken") is None):
        return redirect(url_for('loginFailed'))

    if (is_authenticated == False):

        is_authenticated = isUserAuthenticated()

        if (is_authenticated == False):
            return redirect(url_for('loginFailed'))

    print('Redirecting to video endpoint')
    return Response(
        kafka_service.produce_video_stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


def isUserAuthenticated():
    response = requests.post(
        'http://localhost:8080/api/v1/user/checkValidAuthentication',
        {'username': kafka_service.user_name},
        headers={"Authorization": f"Bearer {kafka_service.user_token}"}
    )
    return response.status_code == 200


if __name__ == "__main__":
    app.run()
