'''
    Currently Unusable
'''
import cv2
from keras.backend import expand_dims
import numpy as np
from PIL import Image, ImageFilter
import time
import tensorflow as tf

# define a video capture object
vid = cv2.VideoCapture(0)

start_point = (200, 200)
end_point = (250, 250)
thickness = 1
color = (255, 0, 0)


prev_frame = None
is_prev_frame = False
threshhold = 27
curr_error = None

def getEdges(img):
    # return cv2.Canny(img)
    image = Image.fromarray(img)
    image = image.convert('L')
    image = image.filter(ImageFilter.FIND_EDGES)
    return np.asarray(image)

def mse(im1, im2):
    '''
        returns the mean squared error between two gray-scale images
    '''
    error = np.square(im1 - im2).mean(axis=None)
    return error

def isMotionDetected(f1, f2):
    global curr_error
    error = mse(f1, f2)
    curr_error = error
    
    return error > threshhold

def localizeObject(f1, f2):
    sub = (f1 == f2) + 0
    sub *= 255
    return sub
    
def loadModel(path="./"):
    model = tf.keras.models.load_model(path)
    return model

model = loadModel("./models/dogcatv31636093486")

def preprocess_img(img):
    img = cv2.resize(img, (224, 224))
    tensor = np.array(img)
    tensor = np.expand_dims(tensor, axis=0) / 255.0
    return tensor

def predict(model, img):
    result = model.predict(img)
    return result


start_time = time.time()
edged = None
prev_edged = None
classes = np.array(['cats', 'dogs'])

while(True):
      
    ret, frame = vid.read()
    frame = cv2.resize(frame, (500, 500))
    cur_time = time.time()

    time_elapsed = cur_time - start_time

   

    if time_elapsed > 1:
        if is_prev_frame:
            edged = getEdges(frame)
            prev_edged = getEdges(prev_frame)
            detected = isMotionDetected(prev_edged, edged)
            if detected:
                print("motion detected ", curr_error)
                preprocessed_frame = preprocess_img(frame)
                result = predict(model, preprocessed_frame)

                predicted_id = tf.math.argmax(result, axis=-1)
                predicted_label_batch = classes[predicted_id]
                print(predicted_label_batch)

        start_time = cur_time
        prev_frame = frame
        is_prev_frame = True

    # Display the resulting frame
    cv2.imshow('frame', frame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
vid.release()
cv2.destroyAllWindows()