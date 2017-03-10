from google.appengine.ext import ndb
from template import render_str
from user import User
from comment import Comment


class Post(ndb.Model):
    owner = ndb.KeyProperty(User)
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    likes = ndb.KeyProperty(User, repeated=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, parent, post_id):
        key = ndb.Key(Post, int(post_id), parent=parent)
        return key.get()

    def is_owned_by(self, user):
        return self.owner.id() == user.key.id()

    def likes_it(self, user):
        return user.key in self.likes

    def comments(self):
        return Comment.query(ancestor=self.key).order(-Comment.created).fetch()

    @property
    def text(self):
        return self.content.replace('\n', '<br>')

    # TODO: move to a function
    def render(self, current_user=None):
        return render_str("post.html", p=self, user=current_user)

