from google.appengine.ext import ndb
from template import render_str
from user import User


class PostLike(ndb.Model):
    """Represents a content posted by an user.

    Args:
        owner (ndb.Key): The user who posted this content
        content (str): The content of this post
        created (date): The creation date
        last_modified (date): The last time this post was modified
    """

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
        """Renders the post content.

        Renders the post content replacing line breaks with `<br>`.
        This function also accepts an ``abridged`` parameter that when `True`
        will render an abridged verion of this post content, that is,
        only 5 lines or 530 characters.

        Args:
            abridged (bool): Whenever to render the abridged version or not
        """
        content_lines = self.content.split('\n')
        more = ""
        if abridged:
            more_link = '... <a href="/blog/%s">(more)</a>' % self.key.id()
            max_lines = 5
            max_length = 530
            content_length = len(self.content)
            if len(content_lines) > max_lines:
                content_lines = content_lines[:max_lines]
                more = more_link
            elif content_length > max_length:
                content_lines = self.content[:max_length].split('\n')
                more = more_link

        return "<br>".join(content_lines) + more


class Post(PostLike):
    subject = ndb.StringProperty(required=True)
    likes = ndb.KeyProperty(User, repeated=True)

    def likes_it(self, user):
        return user.key in self.likes

    def comments(self):
        return Comment.query(ancestor=self.key).order(-Comment.created).fetch()


class Comment(PostLike):
    pass
