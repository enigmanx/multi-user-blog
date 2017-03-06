from google.appengine.ext import db
from template import render_str


# TODO: move. it's duplicated on the blog.py
def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        return db.get(key)

    # TODO: move to a function
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)

