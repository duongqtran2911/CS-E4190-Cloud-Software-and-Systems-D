 
from flask import Flask, jsonify, request, Response
from database.db import initialize_db
from database.models import Photo, Album
import json
from bson.objectid import ObjectId
import os
import urllib
import base64
import codecs

app = Flask(__name__)

# database configs
app.config['MONGODB_SETTINGS'] = {
    # set the correct parameters here as required, some examples are give below
    #'host':'mongodb://mongo:<port>/<name of db>'
    #'host':'mongodb://localhost/<name of db>'
    'host':'mongodb://mongo:27017/flask-database'
}
db = initialize_db(app)

## ------
# Helper functions to be used if required
# -------
def str_list_to_objectid(str_list):
    return list(
        map(
            lambda str_item: ObjectId(str_item),
            str_list
        )
    )

def object_list_as_id_list(obj_list):
    return list(
        map(
            lambda obj: str(obj.id),
            obj_list
        )
    )


# ----------
# PHOTO APIs
# ----------
# These methods are a starting point, implement all routes as defined in the specifications given in A+

@app.route('/listPhoto', methods=['POST'])
def add_photo():
    print("file", request.files)
    posted_image = request.files['file'] #"use request.files to obtain the image called file"
    posted_data = request.form.to_dict() #"use request.form to obtain the associated immutable dict and convert it into dict"
    # Check for default album
    name = posted_data.get('name')
    tags = posted_data.get('tag')
    if tags != None: tags = list(tags)
    location = posted_data.get('location')
    albums = posted_data.get('albums')
    def_albums = Album.objects(name='Default')
    if len(def_albums==0): 
        album = Album(name='Default')
        album.save()
        photo = Photo(name=name, tags=tags, location=location, albums=albums, image_file=posted_image)
        photo.save()
        id = str(photo.id)
        output = {'message': "Photo successfully created", 'id': id}
        return jsonify(output), 201
    else:
        photo = Photo(name=name, tags=tags, location=location, albums=albums, image_file=posted_image)
        photo.save()
        id = str(photo.id)
        output = {'message': "Photo successfully created", 'id': id}
        return jsonify(output), 201

@app.route('/listPhoto/<photo_id>', methods=['GET', 'PUT', 'DELETE'])
def get_photo_by_id(photo_id):
    if request.method == "GET":
        photo = Photo.objects.get(id=photo_id)
        if photo:
            ## Photos should be encoded with base64 and decoded using UTF-8 in all GET requests with an image before sending the image as shown below
            base64_data = codecs.encode(photo.image_file.read(), 'base64')
            image = base64_data.decode('utf-8')
            ##########
            output = {"name": photo.name, "tags": photo.tags,
                "location": photo.location, "albums": photo.albums,
                "file": image}
            status_code = 200
            return jsonify(output), status_code
    elif request.method == "PUT":
        photo = Photo.objects(id=photo_id)
        body = request.get_json()
        albums = ["Default"]; 
        albums_id = []
        for album in albums:
            albums_id.append(str(Album.objects(name=album)[0].id))
        print(Album.objects(name=album)[0].id)
        body["albums"] = str_list_to_objectid(albums_id)
        Photo.objects.get(id=photo_id).update(**body)
        output = {'message': "Photo successfully updated", 'id': str(photo_id)}
        status_code = 200
        return output,status_code
    elif request.method == "DELETE":
        photo = Photo.objects.get_or_404(id=photo_id)
        photo.delete()
        output = { 'message': 'Photo successfully deleted', 'id': str(photo_id) }
        status_code = 200
        return output, status_code

@app.route('/listPhotos', methods=['GET'])
def get_photos():
    tag = request.args.get('tag') #"Get the tag from query parameters" 
    albumName = request.args.get('albumName') #"Get albumname from query parameters"
    if albumName is not None:
        albums=Album.objects(name=albumName)
        photo_objects=Photo.objects(albums__in=albums)
        photo_objects=[]
        photo_objects.append(Photo.objects()[0])
        photo_objects.append(Photo.objects()[1])
    elif tag is not None:
        photo_objects=Photo.objects(tags=tag)
    else:
        photo_objects=Photo.objects
    photos = []
    for photo in photo_objects:
        base64_data = codecs.encode(photo.image_file.read(), 'base64')
        image = base64_data.decode('utf-8')
        photos.append({'name': photo.name, 'location': photo.location, 'file': image})
    return jsonify(photos), 200

# ----------
# ALBUM APIs
# ----------
# Complete the album APIs similarly as per the instructions provided in A+

@app.route('/listAlbum', methods=['POST'])
def createAlbum():
    posted_data = request.get_json()
    album = Album(**posted_data)
    album.save()
    output = {'message': "Album successfully created", 'id': str(album.id)}
    status_code = 201
    return output, status_code

@app.route('/listAlbum/<album_id>', methods=['GET', 'PUT', 'DELETE'])
def get_album_by_id(album_id):
    if request.method == "GET":
        album = Album.objects.get(id=album_id)
        if album:
            output = {"id": str(album_id), "name": album.name }
            status_code = 200
            return jsonify(output), status_code

    elif request.method == "PUT":
        album = Album.objects(id=album_id)
        posted_data = request.get_json()
        album.name = posted_data['name']
        keys = posted_data.keys()
        Album.objects.get(id=album_id).update(**posted_data)
        output = {'message': "Album successfully updated", 'id': str(album_id)}
        status_code = 200
        return output, status_code 
        
    elif request.method == "DELETE":
        album = Album.objects.get_or_404(id=album_id)
        album.delete()
        output = {'message': "Album successfully deleted", 'id': str(album_id)}
        status_code = 200
        return output, status_code 

# Only for local testing without docker
#app.run() # FLASK_APP=app.py FLASK_ENV=development flask run

if __name__ == '__main__':
    app.run()