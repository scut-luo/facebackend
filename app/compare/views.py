from flask import request, jsonify
from sharedmodels.models import APIKey
import numpy as np
import openface
import base64
from . import compare


def _check_required_parameters(request):
    required_paras = ['api_key', 'face_token1', 'face_token2']
    missing_paras = ''
    for para in required_paras:
        if para not in request.form:
            missing_paras = missing_paras + ' ' + para

    return missing_paras


@compare.route('/compare', methods=['POST'])
def compare():
    # Check required parameters
    missing_paras = _check_required_parameters(request)
    if len(missing_paras) > 0:
        return (jsonify({'error_message':
                         'MISSING_ARGUMENTS: ' + missing_paras}), 400)

    api_key_str = request.form['api_key']
    face_token1_str = request.form['face_token1']
    face_token2_str = request.form['face_token2']

    # Get api key info
    api_key = APIKey.query.filter_by(apikey=api_key_str).first()
    if api_key is None:
        return (jsonify({'error_message':
                         'AUTHORIZATION_ERROR'}), 401)
    user = api_key.user

    # Check all of face token are valid
    invalid_face_tokens = ''
    face1 = user.faces.filter_by(token=face_token1_str).first()
    face2 = user.faces.filter_by(token=face_token2_str).first()
    if face1 is None:
        invalid_face_tokens = invalid_face_tokens + ' ' + face_token1_str
    if face2 is None:
        invalid_face_tokens = invalid_face_tokens + ' ' + face_token2_str
    if len(invalid_face_tokens) > 0:
        return (jsonify({'error_message':
                         'INVALID_FACE_TOKEN: ' + invalid_face_tokens}), 400)

    # Get face encodings
    face1_encoding = np.frombuffer(base64.b64decode(face1.encoding),
                                   dtype=np.float32)
    face2_encoding = np.frombuffer(base64.b64decode(face2.encoding),
                                   dtype=np.float32)

    # Calculate similarity
    face_distance = openface.face_distance([face1_encoding], face2_encoding)[0]
    similarity = 1 - face_distance

    # Construct response
    response = jsonify({'similarity': similarity})

    return (response, 200)
