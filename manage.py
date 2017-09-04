#!/usr/bin/env python

import os
from app import create_app, db
# from app.models import User, APIKey
from sharedmodels.models import User, APIKey, FaceSet, Face
from flask_script import Manager, Shell, Command
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


def make_shell_context():
    return dict(app=app, db=db, User=User, APIKey=APIKey)


class InitDB(Command):
    def run(self):
        db.drop_all()
        db.create_all()

        # data object
        user1 = User(username='luowanqian', password='123')
        user2 = User(username='admin', password='123')
        apikey1 = APIKey(application='Face Recognition',
                         apikey='f3b670b8-8bd0-11e7-8776-f45c89a4d2af',
                         user=user1)
        apikey2 = APIKey(application='Face Detect',
                         apikey='7c1b5b17-8d56-11e7-873c-f45c89a4d2af',
                         user=user2)
        faceset1 = FaceSet(token='15a44702-8d2c-11e7-8356-f45c89a4d2af',
                           display_name='Home', user=user1)
        faceset2 = FaceSet(token='25dd3000-8fe3-11e7-b600-f45c89a4d2af',
                           display_name='Lab', user=user1)
        faceset3 = FaceSet(token='b1d428b5-8fe5-11e7-acd5-f45c89a4d2af',
                           display_name='School', user=user1)
        faceset4 = FaceSet(token='03a216f0-8d2d-11e7-b399-f45c89a4d2af',
                           display_name='School', user=user2)
        face1 = Face(token='cb4992b8-8d59-11e7-8185-f45c89a4d2af',
                     user=user1)
        face2 = Face(token='407172f5-8d5a-11e7-88e6-f45c89a4d2af',
                     user=user1)
        face3 = Face(token='74224040-8d63-11e7-8c9d-f45c89a4d2af',
                     user=user2)

        face1.facesets.append(faceset2)
        face1.facesets.append(faceset3)

        # commit to database
        db.session.add_all([user1, user2,
                            apikey1, apikey2,
                            face1, face2, face3,
                            faceset1, faceset2,
                            faceset3, faceset4])
        db.session.commit()


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('initdb', InitDB())


if __name__ == '__main__':
    manager.run()
