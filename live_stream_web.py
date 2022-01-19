# from flask import Flask, render_template, Response

# # import cv2
# # #Initialize the Flask app
# # app = Flask(__name__)
# # camera = cv2.VideoCapture(0)
# # def gen_frames():  
# #     while True:
# #         success, frame = camera.read()  # read the camera frame
# #         if not success:
# #             break
# #         else:
# #             ret, buffer = cv2.imencode('.jpg', frame)
# #             frame = buffer.tobytes()
# #             yield (b'--frame\r\n'
# #                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat f

# # @app.route('/')
# # def index():
# #     return render_template('index.html')

# # @app.route('/video_feed')
# # def video_feed():
# #     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# # if __name__ == "__main__":
# #     app.run(debug=True)

# app = Flask("LiveStreamer")
# class LiveStreamer:
#     def __init__(self) -> None:
#         self.buffer = []
#         pass
#     def gen_frames(self):
#         yield self.buffer[0]
#     @app.route('/')
#     def index():
#         return render_template('index.html')

#     @app.route('/video_feed')
#     def video_feed():
#         return Response(self.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  
#     def run(self):
#         app.run(debug=True)