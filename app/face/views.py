from flask import request, jsonify
from sharedmodels.models import APIKey
from . import face


def _check_required_parameters(request):
    required_paras = ['api_key', 'face_token']
    missing_paras = ''
    for para in required_paras:
        if para not in request.form:
            missing_paras = missing_paras + ' ' + para

    return missing_paras


@face.route('/getdetail', methods=['POST'])
def getdetail():
    # Check required parameters
    missing_paras = _check_required_parameters(request)
    if len(missing_paras) > 0:
        return (jsonify({'error_message':
                         'MISSING_ARGUMENTS: ' + missing_paras}), 400)

    api_key_str = request.form['api_key']
    face_token_str = request.form['face_token']

    # Get api key info and user info
    api_key = APIKey.query.filter_by(apikey=api_key_str).first()
    if api_key is None:
        return (jsonify({'error_message':
                         'AUTHORIZATION_ERROR'}), 401)
    user = api_key.user

    # Get face info
    face = user.faces.filter_by(token=face_token_str).first()
    if face is None:
        return (jsonify({'error_message': 'INVALID_FACE_TOKEN'}), 400)

    # Get faceset info
    facesets = face.facesets.all()

    # Construct response
    response_facesets = []
    for faceset in facesets:
        response_facesets.append({'faceset_token': faceset.token})
    response = jsonify({'face_token': face_token_str,
                        'facesets': response_facesets})

    return response, 200
