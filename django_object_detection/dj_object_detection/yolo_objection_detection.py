import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    
import pathlib
import tensorflow as tf
tf.get_logger().setLevel('ERROR')  
import time
from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder         
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import warnings
import cv2
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')  
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
def download_images():
    base_url = "E:/tensor_flow/data_set/object_detection_testdata"
    image_paths = []
    for i in os.listdir(base_url):
        i = base_url +"/"+ i
        image_paths.append(str(i))
    return image_paths
    # base_url = "C:/Users/VC/.keras/datasets/"
    # filenames = ['image6.jpg']
    # image_paths = []
    # for filename in filenames:
    #     image_path = tf.keras.utils.get_file(fname=filename,
    #                                         origin=base_url + filename,
    #                                         untar=False)
    #     image_path = pathlib.Path(image_path)
    #     image_paths.append(str(image_path))
    # print(image_paths)
    # return image_paths
IMAGE_PATHS = download_images()
def download_model():
    model_dir="E:/tensorflow_projects/custom_models/centernet_hg104_1024x1024_coco17_tpu-32"
    # base_url = 'http://download.tensorflow.org/models/object_detection/tf2/'
    # model_file = model_name + '.tar.gz'
    # model_dir = tf.keras.utils.get_file(fname=model_name,
    #                                     origin=base_url + model_date + '/' + model_file,
    #                                     untar=True)
    return str(model_dir)

# MODEL_DATE = '20200711'
# MODEL_NAME = 'centernet_hg104_1024x1024_coco17_tpu-32'
PATH_TO_MODEL_DIR = download_model()
def download_labels(filename):
    label_dir = "E:/tensorflow_projects/custom_models/mscoco_label_map.pbtxt"
    # base_url = 'https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/data/'
    # label_dir = tf.keras.utils.get_file(fname=filename,
    #                                     origin=base_url + filename,
    #                                     untar=False)
    # label_dir = pathlib.Path(label_dir)
    return str(label_dir)
LABEL_FILENAME = 'mscoco_label_map.pbtxt'
PATH_TO_LABELS = download_labels(LABEL_FILENAME)
PATH_TO_CFG = PATH_TO_MODEL_DIR + "/pipeline.config"
PATH_TO_CKPT = PATH_TO_MODEL_DIR + "/checkpoint"
start_time = time.time()
configs = config_util.get_configs_from_pipeline_file(PATH_TO_CFG)
model_config = configs['model']
detection_model = model_builder.build(model_config=model_config, is_training=False)

ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(PATH_TO_CKPT, 'ckpt-0')).expect_partial()

@tf.function
def detect_fn(image):
    """Detect objects in image."""

    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)

    return detections

end_time = time.time()
elapsed_time = end_time - start_time
print('Done! Took {} seconds'.format(elapsed_time))


category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS,
                                                                    use_display_name=True)




def load_image_into_numpy_array(path):
   
    return np.array(Image.open(path))


for image_path in IMAGE_PATHS:

    print('Running inference for {}... '.format(image_path), end='')

    image_np = load_image_into_numpy_array(image_path)

    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)

    detections = detect_fn(input_tensor)

    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections

    # detection_classes should be ints.
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    label_id_offset = 1
    image_np_with_detections = image_np.copy()
    viz=viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            detections['detection_boxes'],
            detections['detection_classes']+label_id_offset,
            detections['detection_scores'],
            category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=200,
            min_score_thresh=.30,
            agnostic_mode=False)
    count = viz[1]
    print("The person count is ",count)
    array = Image.fromarray(image_np_with_detections)
    array.save('E:/tensor_flow/test_dataset/'+IMAGE_PATHS[0].split('/')[-1])
    img=cv2.resize(image_np_with_detections,(500,500))
    cv2.imshow('img',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows
