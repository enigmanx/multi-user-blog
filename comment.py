from google.appengine.ext import ndb
from user import User


class Comment(ndb.Model):
    owner = ndb.KeyProperty(User, required=True)
    message = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, parent, comment_id):
        key = ndb.Key(Comment, int(comment_id), parent=parent)
        return key.get()

    def is_owned_by(self, user):
        return self.owner.id() == user.key.id()
