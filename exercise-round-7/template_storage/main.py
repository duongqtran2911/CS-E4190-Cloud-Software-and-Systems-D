import os
import io # To read from saved file
from google.cloud import storage, vision
import functions_framework
# Add any imports that you may need, but make sure to update requirements.txt

@functions_framework.cloud_event
def image_to_text_storage(cloud_event):
    # TODO: Add logic here
    data = cloud_event.data
    storageClient = storage.Client()
    visionClient = vision.ImageAnnotatorClient()
    bucketName = data["bucket"]
    bucket = storageClient.bucket(bucketName)
    extd = data["name"]
    if extd.endswith('.txt'):
        return
    blob = bucket.blob(extd)
    file_path = '/tmp/{}'.format(extd)
    with open(file_path, "wb") as fileObject:
        blob.download_to_file(fileObject)
    
    with io.open(file_path, 'rb') as imageFile:
        content = imageFile.read()
    image = vision.Image(content=content)

    response = visionClient.text_detection(image=image)
    texts = response.full_text_annotation.text
    name = extd.split(".")[0]
    response = "{}.txt".format(name)
    predictionFile = bucket.blob(response)
    predictionFile.upload_from_string(texts)
    return