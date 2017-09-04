from flask import request, jsonify, current_app
import uuid
from . import faceset
from .. import db
# from ..models import APIKey, FaceSet, Face
from sharedmodels.models import APIKey, FaceSet


def _check_required_parameters(request, api):
    if api == 'create':
        request_paras = ['api_key']
    elif api == 'addface':
        request_paras = ['api_key', 'faceset_token', 'face_tokens']
    elif api == 'getdetail':
        request_paras = ['api_key', 'faceset_token']

    missing_paras = ''
    for para in request_paras:
        if para not in request.form:
            missing_paras = missing_paras + ' ' + para

    return missing_paras


@faceset.route('/create', methods=['POST'])
def faceset_create():
    # Check required parameters
    missing_paras = _check_required_parameters(request, 'create')
    if len(missing_paras) > 0:
        return (jsonify({'error_message':
                         'MISSING_ARGUMENTS: ' + missing_paras}), 400)

    # Get parameters
    api_key_str = request.form['api_key']
    if 'display_name' in request.form:
        display_name_str = request.form['display_name']
    else:
        display_name_str = None

    # Get api key info and user info
    api_key = APIKey.query.filter_by(apikey=api_key_str).first()
    if api_key is None:
        return (jsonify({'error_message':
                         'AUTHORIZATION_ERROR'}), 401)
    user = api_key.user

    # Construct faceset info and commit to database
    faceset_token = str(uuid.uuid1())
    faceset_display_name = display_name_str
    faceset = FaceSet(token=faceset_token, display_name=faceset_display_name,
                      user=user)
    db.session.add(faceset)
    db.session.commit()

    # Construct response
    response = jsonify({'faceset_token': faceset_token})

    return response


@faceset.route('/addface', methods=['POST'])
def faceset_addface():
    # Check required parameters
    missing_paras = _check_required_parameters(request, 'addface')
    if len(missing_paras) > 0:
        return (jsonify({'error_message':
                         'MISSING_ARGUMENTS: ' + missing_paras}), 400)

    api_key_str = request.form['api_key']
    faceset_token_str = request.form['faceset_token']
    face_tokens_str = request.form['face_tokens']

    # Query API Key
    apikey = APIKey.query.filter_by(apikey=api_key_str).first()
    if apikey is None:
        return (jsonify({'error_message':
                         'AUTHORIZATION_ERROR'}), 401)
    user = apikey.user

    # Query FaceSet
    # faceset = FaceSet.query.filter_by(token=faceset_token_str).first()
    faceset = user.facesets.filter_by(token=faceset_token_str).first()
    if faceset is None:
        return (jsonify({'error_message':
                         'INVALID_FACESET_TOKEN'}), 400)

    num_face_add = 0
    failure_detail = []
    face_tokens = face_tokens_str.strip().split(',')
    faces = []
    existed_faces = faceset.faces.all()
    for face_token in face_tokens:
        # face = Face.query.filter_by(token=face_token).first()
        face = user.faces.filter_by(token=face_token).first()
        if face is None:    # face is not existed
            if 'DEBUG' in current_app.config and current_app.config['DEBUG']:
                print('Face Token {} not exists'.format(face_token))
            failure_detail.append({'reason': 'INVALID_FACE_TOKEN',
                                   'face_token': face_token})
        elif face in existed_faces:     # face is existed in the faceset
            num_face_add = num_face_add + 1
        else:
            face.facesets.append(faceset)
            faces.append(face)
            num_face_add = num_face_add + 1
    db.session.add_all(faces)
    db.session.commit()

    num_face_exist = faceset.faces.count()

    # Construct response
    response = jsonify({'faceset_token': faceset_token_str,
                        'face_added': num_face_add,
                        'face_count': num_face_exist,
                        'failure_detail': failure_detail})

    return response, 200


@faceset.route('/getdetail', methods=['POST'])
def faceset_getdetail():
    # Check required parameters
    missing_paras = _check_required_parameters(request, 'getdetail')
    if len(missing_paras) > 0:
        return (jsonify({'error_message':
                         'MISSING_ARGUMENTS: ' + missing_paras}), 400)

    api_key_str = request.form['api_key']
    faceset_token_str = request.form['faceset_token']

    # Get api key info and user info
    api_key = APIKey.query.filter_by(apikey=api_key_str).first()
    if api_key is None:
        return (jsonify({'error_message':
                         'AUTHORIZATION_ERROR'}), 401)
    user = api_key.user

    faceset = user.facesets.filter_by(token=faceset_token_str).first()
    if faceset is None:
        return (jsonify({'error_message':
                         'INVALID_FACESET_TOKEN'}), 400)

    faces = faceset.faces.all()
    response_face_count = len(faces)
    response_face_tokens = []
    for face in faces:
        response_face_tokens.append(face.token)

    response = jsonify({'faceset_token': faceset_token_str,
                        'display_name': faceset.display_name,
                        'face_count': response_face_count,
                        'face_tokens': response_face_tokens})

    return response, 200
