import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
from rest_framework.response import Response
from rest_framework.decorators import api_view
import tensorflow as tf
import numpy as np
import base64
import io
from PIL import Image

# Create your views here.
img_size = 24
channel = 1
unique = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

def process_image(img):
    img = tf.constant(img)
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = tf.image.rgb_to_grayscale(img)
    img = tf.image.resize(img, size=[img_size, img_size])
    return img

def load_model(path):
    return tf.compat.v2.keras.models.load_model(path)

model = load_model("./models/facial-expression-v1/saved_model_3")

def predict(img_arr):
    img = process_image(img_arr)
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    prediction = model.predict(img_array)
    score = tf.nn.softmax(prediction)
    label = unique[np.argmax(prediction)]
    print(f"Prediction - {label} score - {np.max(score[0])}")
    return label, np.max(score[0]), np.argmax(prediction)

@api_view(["POST", "GET"])
def facial_expression_analysis(request, *args, **kwargs):
    response = request.data
    if response == None:
        return Response({"msg": ""})
    else:
        data_str = response["image"]
        point = data_str.find(",")
        base64_str = data_str[point:]  # remove unused part like this: "data:image/jpeg;base64,"

        image = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(image))

        if img.mode != "RGB":
            img = img.convert("RGB")

        image_np = np.array(img)
        
        try:
            label, score, val = predict(image_np)
            return Response({"label": f"{label}", "score": f"{score}", "val": f"{val}"})
        except Exception as e:
            return Response({"msg": f"{e}",})
