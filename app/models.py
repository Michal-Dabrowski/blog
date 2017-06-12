from app import db

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )

thread_participants = db.Table('thread_participants',
                        db.Column('thread_id', db.Integer, db.ForeignKey('thread.id')),
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')
                                  )
                        )

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64), index=True, unique=False)
    email = db.Column(db.String(120), index=True, unique=True)
    about_me = db.Column(db.String(140))
    avatar = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    threads = db.relationship('Thread',
                              secondary=thread_participants,
                              backref=db.backref('participants', lazy='dynamic'),
                              lazy='dynamic')
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def join_thread(self, thread):
        self.threads.append(thread)
        return self

    def my_threads(self):
        return self.threads.all()

    def get_thread_with(self, user):
        for t in self.threads.all():
            if user in t.participants.all():
                return t
        return None

    def my_messages(self):
        sub = db.session.query(db.func.max(Message.timestamp).label('max_time')).group_by(
            Message.thread_id).subquery()
        return db.session.query(Message).join(Thread).filter(self.threads).filter(
            Message.timestamp == sub.c.max_time).order_by(Message.timestamp.desc()).all()

    def get_all_messages_with_user(self, user):
        thread = self.get_thread_with(user)
        messages = db.session.query(Message).join(Thread).filter(Thread.id == thread.id).order_by(Message.timestamp.asc()).all()
        return messages

    def count_new_messages(self):
        return db.session.query(Message).join(Thread).filter(self.threads).filter(Message.new == True).count()

    def __repr__(self):
        return '<User %r>' % (self.nickname)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(360))
    timestamp = db.Column(db.DateTime)
    new = db.Column(db.Boolean, default=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))

    def participants(self, user):
        thread = Thread.query.filter_by(id=self.thread_id).first()
        return thread.participants.filter(User.nickname != user.nickname).all()

    def __repr__(self):
        return '<Message %r>' % (self.body)

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
