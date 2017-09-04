from flask import request, jsonify
# import io
# import cv2
import base64
import numpy as np
from scipy import misc
from . import search
# from ..models import APIKey, FaceSet
from sharedmodels.models import APIKey
import openface


def _check_required_parameters(request):
    required_paras = ['api_key', 'faceset_token']
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


@search.route('/search', methods=['POST'])
def search():
    # Check required parameters
    missing_paras = _check_required_parameters(request)
    if len(missing_paras) > 0:
        return (jsonify({'error_message':
                         'MISSING_ARGUMENTS: ' + missing_paras}), 400)

    api_key_str = request.form['api_key']
    faceset_token_str = request.form['faceset_token']
    img_file = request.files['image_file']

    # Get api key info
    api_key = APIKey.query.filter_by(apikey=api_key_str).first()
    if api_key is None:
        return (jsonify({'error_message':
                         'AUTHORIZATION_ERROR'}), 401)
    user = api_key.user

    # Get faceset info
    # faceset = FaceSet.query.filter_by(token=faceset_token_str).first()
    faceset = user.facesets.filter_by(token=faceset_token_str).first()
    if faceset is None:
        return (jsonify({'error_message':
                        'INVALID_FACESET_TOKEN'}), 400)
    if faceset.faces.count() == 0:
        return (jsonify({'error_message':
                         'EMPTY_FACESET'}), 400)

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
    face_locations.sort(key=openface.area_of_bb, reverse=True)

    # Found no face
    if len(face_locations) == 0:
        return jsonify({'faces': []})

    # Search similar faces
    face_location = face_locations[0]
    face_encoding = openface.face_encodings(img, [face_location])
    known_face_encodings = []
    known_face_tokens = []
    known_faces = faceset.faces.all()
    for face in known_faces:
        known_face_encoding = np.frombuffer(base64.b64decode(face.encoding),
                                            dtype=np.float32)
        known_face_encodings.append(known_face_encoding)
        known_face_tokens.append(face.token)

    # Calculate similarity
    face_distances = openface.face_distance(known_face_encodings,
                                            face_encoding)

    # Construct response
    response_faces = []
    response_results = []
    for face_location in face_locations:
        (left, top, right, bottom) = face_location
        response_faces.append({'face_rectangle': {'left': left,
                                                  'top': top,
                                                  'width': right - left,
                                                  'height': bottom - top}})
    for i, face_distance in enumerate(face_distances):
        face_similarity = 1 - face_distance
        response_results.append({'face_token': known_face_tokens[i],
                                 'similarity': face_similarity})
    response_results.sort(key=lambda x: x['similarity'], reverse=True)
    response = jsonify({'results': response_results,
                        'faces': response_faces})

    return response
