from flask import request, jsonify, current_app
# import io
# import cv2
import uuid
import base64
import numpy as np
from scipy import misc
from . import detect
# from ..models import Face
from sharedmodels.models import Face, APIKey
from .. import db
import openface


def _check_required_parameters(request):
    required_paras = ['api_key']
    missing_paras = ''
    for para in required_paras:
        if para not in request.form:
            missing_paras = missing_paras + ' ' + para
    if 'image_file' not in request.files:
        missing_paras = missing_paras + ' image_file'

    return missing_paras


def _check_image_size(img):
    ret = True
    height = img.shape[0]
    width = img.shape[1]

    if min(height, width) < 48 or max(height, width) > 4096:
        ret = False

    return ret


@detect.route('/detect', methods=['POST'])
def detect():
    # Check required parameters
    missing_paras = _check_required_parameters(request)
    if len(missing_paras) > 0:
        return (jsonify({'error_message':
                         'MISSING_ARGUMENTS: ' + missing_paras}), 400)

    api_key_str = request.form['api_key']
    img_file = request.files['image_file']

    # Get api key info and user info
    api_key = APIKey.query.filter_by(apikey=api_key_str).first()
    if api_key is None:
        return (jsonify({'error_message':
                         'AUTHORIZATION_ERROR'}), 401)
    user = api_key.user

    '''
    # Convert the image data in post request to an OpenCV object
    memory_file = io.BytesIO()
    img_file.save(memory_file)
    img_data = np.fromstring(memory_file.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(img_data, 1)
    '''
    img = misc.imread(img_file, mode='RGB')

    # Check image size
    if not _check_image_size(img):
        return (jsonify({'error_message': 'INVALID_IMAGE_SIZE: image_file'}),
                400)

    # Detect faces
    face_locations = openface.face_locations(img)
    response_faces = []
    faces_token = []
    for i, face_location in enumerate(face_locations):
        left, top, right, bottom = face_location
        face_token = str(uuid.uuid1())
        faces_token.append(face_token)

        # DEBUG
        if 'DEBUG' in current_app.config and current_app.config['DEBUG']:
            print(('Face {} found at Left: {}, Top: {}, '
                   'Right: {}, Bottom: {}').format(i, left, top,
                                                   right, bottom))

        # Construct response
        response_face = {}
        response_face['face_token'] = face_token
        response_face['face_rectangle'] = {'left': left,
                                           'top': top,
                                           'width': right - left,
                                           'height': bottom - top}
        response_faces.append(response_face)
    response = jsonify({'faces': response_faces})

    # Encode faces
    encodings = openface.face_encodings(img, face_locations)
    faces = []
    if len(encodings) == len(face_locations):
        for i, encoding in enumerate(encodings):
            encoding = encoding.astype(np.float32)
            encoding_str = base64.b64encode(encoding)
            face = Face(token=faces_token[i], encoding=encoding_str, user=user)
            faces.append(face)
        db.session.add_all(faces)
        db.session.commit()
    else:
        if 'DEBUG' in current_app.config and current_app.config['DEBUG']:
            print('Error: Can not encode all of faces')

    return response
