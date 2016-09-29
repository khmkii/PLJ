import datetime

from peewee import *
from flask.ext.bcrypt import generate_password_hash


DATABASE = SqliteDatabase('plj.db')


class BaseModel(Model):

    class Meta:
        database = DATABASE


class User(BaseModel):

    username = CharField(unique=True)
    password = CharField(max_length=50)
    is_admin = BooleanField(default=False)
    authenticated = BooleanField(default=False)

    def is_authenticated(self):
        return self.authenticated

    def get_id(self):
        return self.id

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    @classmethod
    def make_user(cls, username, password):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    password=generate_password_hash(password, 5),
                )
        except IntegrityError:
            raise ValueError("That user already exists")


class Entry(BaseModel):

    title = CharField(unique=True)
    date = DateTimeField(default=datetime.datetime.now)
    time = IntegerField()
    learned = TextField(default='')
    resources = TextField(default='')
    learner = ForeignKeyField(
        rel_model=User,
        related_name='entries'
    )

    def print_date1(self):
        return datetime.datetime.strftime(self.date, '%d/%m/%Y')

    def print_date2(self):
        return datetime.datetime.strftime(self.date, '%B %d, %Y')

    @classmethod
    def make_entry(cls, title, date, time, learned, resources, learner):
        try:
            with DATABASE.transaction():
                cls.create(
                    title=title,
                    date=date,
                    time=time,
                    learned=learned,
                    resources=resources,
                    learner=learner
                )
        except IntegrityError:
            raise ValueError("That title already exists")

    class Meta:
        order_by = (
            '-date', 'time',
        )


def initialise():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry], safe=True)
    DATABASE.close()