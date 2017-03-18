from google.appengine.ext import ndb
from template import render_str
from user import User


class Postable(ndb.Model):
    owner = ndb.KeyProperty(User)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, parent, post_id):
        key = ndb.Key(cls, int(post_id), parent=parent)
        return key.get()

    def is_owned_by(self, user):
        return self.owner.id() == user.key.id()

    def render_text(self, abridged=False):
        content_lines = self.content.split('\n')
        more = ''
        if abridged:
            more_link = '... <a href="/blog/%s">(more)</a>' % self.key.id()
            max_lines = 5
            max_length = 530
            content_length = len(self.content)
            if len(content_lines) > max_lines:
                content_lines = content_lines[:max_lines]
                more = more_link
            elif content_length > max_length:
                print "here"
                content_lines = self.content[:max_length].split('\n')
                more = more_link

        return '<br>'.join(content_lines) + more


class Post(Postable):
    subject = ndb.StringProperty(required=True)
    likes = ndb.KeyProperty(User, repeated=True)

    def likes_it(self, user):
        return user.key in self.likes

    def comments(self):
        return Comment.query(ancestor=self.key).order(-Comment.created).fetch()


class Comment(Postable):
    pass
