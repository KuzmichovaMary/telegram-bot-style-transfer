import os

import tensorflow as tf
import numpy as np
import cv2

# Reference: https://www.tensorflow.org/lite/models/style_transfer/overview
def load_img(path_to_img):
    img = cv2.imread(path_to_img)
    img = img.astype(np.float32) / 127.5 - 1
    img = np.expand_dims(img, 0)
    img = tf.convert_to_tensor(img)
    return img

# Function to pre-process by resizing an central cropping it.
def preprocess_image(image, target_dim=512):
    # Resize the image so that the shorter dimension becomes the target dim.
    shape = tf.cast(tf.shape(image)[1:-1], tf.float32)
    short_dim = min(shape)
    scale = target_dim / short_dim
    new_shape = tf.cast(shape * scale, tf.int32)
    image = tf.image.resize(image, new_shape)

    # Central crop the image.
    image = tf.image.resize_with_crop_or_pad(image, target_dim, target_dim)

    return image

def cartoonize_image(image_path):
    image_name = os.path.basename(image_path)

    preprocessed_source_image = preprocess_image(load_img(image_path))

    interpreter = tf.lite.Interpreter(model_path="cartoon_gan/lite-model_cartoongan_dr_1.tflite")
    input_details = interpreter.get_input_details()

    interpreter.allocate_tensors()
    interpreter.set_tensor(input_details[0]['index'], preprocessed_source_image)
    interpreter.invoke()

    raw_prediction = interpreter.tensor(interpreter.get_output_details()[0]['index'])()

    output = (np.squeeze(raw_prediction)+1.0)*127.5
    output = np.clip(output, 0, 255).astype(np.uint8)
    output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)

    output_path = f"stylized_images/{image_name}"
    cv2.imwrite(output_path, output)
    return output_path

