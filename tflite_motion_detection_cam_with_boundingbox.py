from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import tensorflow as tf
import numpy as np

import math_operations as mathops

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int,
                default=1000, help="minimum area size")
ap.add_argument("-ma", "--max-area", type=int,
                default=90000, help="maximum area size")

args = vars(ap.parse_args())

NUM_BOXES = 10

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    vs = VideoStream(src=0).start()
    time.sleep(2.0)
# otherwise, we are reading from a video file
else:
    vs = cv2.VideoCapture(args["video"])


def cropImg(frame, x, y, w, h):
    croped_img = frame[y:(y+h), x:(x+w)]
    return croped_img
    cv2.imwrite(f"{time.time()}.png", croped_img)


def loadModel(path="./"):
    model = tf.keras.models.load_model(path)
    return model


def preproccess_img(img):
    img = cv2.resize(img, (224, 224))
    tensor = np.array(img, dtype=np.float32)
    tensor = tensor / 255.0
    # tensor = np.expand_dims(tensor, axis=0) / 255.0
    return tensor


# model = loadModel("./models/dogcat_from_ML_V3")
model = None

classes = np.array(['cat', 'dog', 'nothing', 'nothing'])

def getClassesFromModelResult(result):
    predicted_id = tf.math.argmax(result, axis=-1)
    predicted_label_batch = classes[predicted_id]
    return predicted_label_batch


def predict(model, imgs):
    result = model.predict(imgs)
    predicted_id = tf.math.argmax(result, axis=-1)
    predicted_label_batch = classes[predicted_id]
    return predicted_label_batch


def initTflite(path_to_model='./models/dogcat_from_ML_V3.tflite'):
    # Load TFLite model and allocate tensors.
    interpreter = tf.lite.Interpreter(model_path=path_to_model)
    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    # input details
    # print("interpreter-input-details : ", input_details)
    # output details
    # print("interpreter-output-details : ", output_details)
    interpreter.allocate_tensors()
    return interpreter, input_details, output_details


def tflitePredict(interpreter, IOdetails, image):
    interpreter.set_tensor(IOdetails[0][0]['index'], [image])
    interpreter.invoke()
    output_data = interpreter.get_tensor(IOdetails[1][0]['index'])
    return output_data


interpreter, input_details, output_details = initTflite(path_to_model="./models/dogcat_nothing.tflite")


# initialize the first frame in the video stream
firstFrame = None
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    frame = vs.read()
    frame = frame if args.get("video", None) is None else frame[1]
    text = "Unoccupied"
    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if frame is None:
        break
        # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue
    # compute the absolute difference between the current frame and
        # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(
        thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    # loop over the contours
    count = 0
    box_list = []
    frame_copy = np.array(frame, copy=True)  
    for c in cnts:
        if count >= NUM_BOXES:
            break
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            # print("Min-box skipped")
            continue
        if cv2.contourArea(c) > args['max_area']:
            # print("Maxed box skipped")
            continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        box_list.append((x, y, w, h))

        cropedFrame = cropImg(frame, x, y, w, h)
        processed_img = preproccess_img(cropedFrame)

        # predict with tflite
        tf_lite_pred_output = tflitePredict(interpreter, (input_details,
                      output_details), processed_img)
        result = getClassesFromModelResult(tf_lite_pred_output)
        # print(result)

        count += 1

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"
    if len(box_list) > 1:
        unioned_box = mathops.getUnionOfRects(rect_list=box_list)
        if unioned_box is not None:
            x, y, w, h = unioned_box[0], unioned_box[1], unioned_box[2], unioned_box[3]
            unioned_image = cropImg(frame_copy, x, y, w, h)
            # predict here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            unioned_image_preprocessed = preproccess_img(unioned_image)
            tf_lite_pred_output = tflitePredict(interpreter, (input_details,
            output_details), processed_img)
            result = getClassesFromModelResult(tf_lite_pred_output)
            print(result)

            try:
                print( "writing image ", unioned_box)
                cv2.imwrite(f"{time.time()}.{result}.png", unioned_image)
            except:
                print("error writing image ", unioned_box)


    # draw the text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    # cv2.imshow("Thresh", thresh)
    # cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break
    firstFrame = gray  #if we only want to detect the object when it moves


# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
