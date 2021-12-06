from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
#import tensorflow as tf
import numpy as np
from tflite_runtime.interpreter import Interpreter
import math_operations as mathops
from logger import Logger

pred_logger = Logger(logFile="prediction")
pred_logger.log("init")

IS_SAVING_IMAGE = False

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-f", "--frametoskip", default=30, help="frames to skip")
ap.add_argument("-d", "--delay", help="delay of the frames play in seconds")

ap.add_argument("-a", "--min-area", type=int,
                default=1000, help="minimum area size, area = (w x h) in pixel")
ap.add_argument("-ma", "--max-area", type=int,
                default=90000, help="maximum area size")

args = vars(ap.parse_args())

print(args.get("video"))


delay = args.get("delay", None)

NUM_BOXES = 20

# if the video argument is None, then we are reading from webcam
# if args.get("video", None) is None:
#     vs = VideoStream(src=0).start()
#     time.sleep(2.0)
# # otherwise, we are reading from a video file
# else:
#     vs = cv2.VideoCapture(args["video"])
vs = cv2.VideoCapture(0, cv2.CAP_V4L)

def cropImg(frame, x, y, w, h):
    croped_img = frame[y:(y+h), x:(x+w)]
    return croped_img
    #cv2.imwrite(f"{time.time()}.png", croped_img)


def loadModel(path="./"):
    #model = tf.keras.models.load_model(path)
    #return model
    pass


def preproccess_img(img):
    img = cv2.resize(img, (224, 224))
    tensor = np.array(img, dtype=np.float32)
    # tensor = tensor / 255.0
    # tensor = np.expand_dims(tensor, axis=0) / 255.0
    return tensor


# model = loadModel("./models/dogcat_from_ML_V3")
model = None

# classes = np.array(['cat', 'dog', 'nothing', 'nothing'])
classes = np.array(["Animal", "Nothing"])
def getClassesFromModelResult(result):
    predicted_id = np.argmax(result, axis=-1)
    predicted_label_batch = classes[predicted_id]
    
    return predicted_label_batch
    return result

def predict(model, imgs):
    result = model.predict(imgs)
    predicted_id = tf.math.argmax(result, axis=-1)
    predicted_label_batch = classes[predicted_id]
    return predicted_label_batch


def initTflite(path_to_model='./models/dogcat_from_ML_V3.tflite'):
    # Load TFLite model and allocate tensors.
    interpreter = Interpreter(model_path=path_to_model)
    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.allocate_tensors()
    return interpreter, input_details, output_details


def tflitePredict(interpreter, IOdetails, image):
    interpreter.set_tensor(IOdetails[0][0]['index'], [image])
    interpreter.invoke()
    output_data = interpreter.get_tensor(IOdetails[1][0]['index'])
    return output_data


test_models = ["./models/dogcat_from_ML_V3.tflite", "./models/dogcat_nothing.tflite", "./models/animals_roadv2.tflite"]

interpreter, input_details, output_details = initTflite(path_to_model=test_models[2])

# initialize the first frame in the video stream
firstFrame = None
start_time = time.time()
curr_time = time.time()

frames_to_skip = 30
frame_count = 0

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


    #for skipping
    frame_count += 1
    if args.get("video", None) is not None and  frame_count < frames_to_skip:
        continue
    frame_count = 0
    # resize the frame, convert it to grayscale, and blur it
    #print(frame, type(frame))
    frame = frame[1]
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
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

        count += 1

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    indexes_to_exclude = []
    if len(box_list) >= 1:
        unioned_box, indexes_to_exclude = mathops.getUnionOfRects(rect_list=box_list)
        if unioned_box is not None:
            x, y, w, h = unioned_box[0], unioned_box[1], unioned_box[2], unioned_box[3]

            #show the union box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            unioned_image = cropImg(frame_copy, x, y, w, h)

            # predict here 
            unioned_image_preprocessed = preproccess_img(unioned_image)
            tf_lite_pred_output = tflitePredict(interpreter, (input_details,
            output_details), processed_img)
            result = getClassesFromModelResult(tf_lite_pred_output)
            print(result)
            cv2.putText(frame, "{result}".format(result=result), (x + w // 2, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            pred_logger.log("[result:{result}]".format(result=result))
            try:
                if IS_SAVING_IMAGE:
                    print( "writing image ", unioned_box)
                    cv2.imwrite("{time.time()}.{result}.png".format(time=time, result=result), unioned_image)
            except:
                print("error writing image ", unioned_box)

                
        for bi in range(len(box_list)):
            if bi not in indexes_to_exclude:
                (x, y, w, h) = box_list[bi]

                cropedFrame = cropImg(frame_copy, x, y, w, h)
                processed_img = preproccess_img(cropedFrame)



                # predict with tflite
                tf_lite_pred_output = tflitePredict(interpreter, (input_details,
                            output_details), processed_img)
                result = getClassesFromModelResult(tf_lite_pred_output)
                print(result, " (not union result)")
                cv2.putText(frame, "{result}".format(result=result), (x + w // 2, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                pred_logger.log("[result:{result}]".format(result=result))

                if IS_SAVING_IMAGE:
                    cv2.imwrite("{time.time()}.{result}.png".format(time=time, result=result), cropedFrame)

    # show the frame and record if the user presses a key
    #cv2.imshow("Animal Cam", frame)
    # cv2.imshow("Thresh", thresh)
    # cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break
    curr_time = time.time()
    if curr_time - start_time > 0.5:  #taking the frame of previous 0.5 sec ago as firstFrame to compare with the current
            firstFrame = gray  #if we only want to detect the object when it moves
            start_time = curr_time
    if delay is not None:
        time.sleep(int(delay))

    # firstFrame = gray  #if we only want to detect the object when it moves

# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
pred_logger.end()

