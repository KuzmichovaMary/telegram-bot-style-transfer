import os

import tensorflow as tf
import numpy as np
import cv2
import matplotlib.pyplot as plt


def load_img(path_to_img):
    img = tf.io.read_file(path_to_img)
    img = tf.io.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = img[tf.newaxis, :]
    return img

# Function to pre-process by resizing an central cropping it.
def preprocess_image(image, target_dim):
    shape = tf.cast(tf.shape(image)[1:-1], tf.float32)
    short_dim = min(shape)
    scale = target_dim / short_dim
    new_shape = tf.cast(shape * scale, tf.int32)
    image = tf.image.resize(image, new_shape)

    image = tf.image.resize_with_crop_or_pad(image, target_dim, target_dim)
    return image


def run_style_predict(preprocessed_style_image):
    # Load the model.
    interpreter = tf.lite.Interpreter(model_path="arbitrary_style_transfer/magenta_arbitrary-image-stylization-v1-256_fp16_prediction_1.tflite")

    # Set model input.
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    interpreter.set_tensor(input_details[0]["index"], preprocessed_style_image)

    # Calculate style bottleneck.
    interpreter.invoke()
    style_bottleneck = interpreter.tensor(
      interpreter.get_output_details()[0]["index"]
      )()

    return style_bottleneck


# Run style transform on preprocessed style image
def run_style_transform(style_bottleneck, preprocessed_content_image):
    # Load the model.
    interpreter = tf.lite.Interpreter(model_path="arbitrary_style_transfer/magenta_arbitrary-image-stylization-v1-256_fp16_transfer_1.tflite")

    # Set model input.
    input_details = interpreter.get_input_details()
    interpreter.allocate_tensors()

    # Set model inputs.
    interpreter.set_tensor(input_details[0]["index"], preprocessed_content_image)
    interpreter.set_tensor(input_details[1]["index"], style_bottleneck)
    interpreter.invoke()

    # Transform content image.
    stylized_image = interpreter.tensor(
        interpreter.get_output_details()[0]["index"]
      )()

    return stylized_image


def transfer_style(content_path, style_path):
    # Load the input images.
    content_image = load_img(content_path)
    style_image = load_img(style_path)

    # Preprocess the input images.
    preprocessed_content_image = preprocess_image(content_image, 384)
    preprocessed_style_image = preprocess_image(style_image, 256)

    style_bottleneck = run_style_predict(preprocessed_style_image)

    stylized_image = run_style_transform(style_bottleneck, preprocessed_content_image)

    if len(stylized_image.shape) > 3:
        stylized_image = tf.squeeze(stylized_image, axis=0)

    output = (stylized_image.numpy() * 255).astype(np.uint8)
    output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)

    output_path = f"stylized_images/{os.path.basename(content_path)}"
    cv2.imwrite(output_path, output)
    return output_path

if __name__ == '__main__':
    transfer_style("images_to_style/wolfie.jpg", "images_to_style/udnie.jpg")
