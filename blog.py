import webapp2

from webapp2_extras import sessions
from google.appengine.ext import ndb
from template import render_str
from security import make_secure_val, check_secure_val
from user import User
from post import Post, Comment

BLOG_KEY = ndb.Key('Blog', 'default')


class BlogHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()

    def flash(self, message, level):
        self.session.add_flash(message, level, key="_messages")

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        params['flash_messages'] = self.session.get_flashes(key="_messages")
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def redirect_to_referer(self):
        self.redirect(self.request.referer or '/blog')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


class MainPage(BlogHandler):
    def get(self):
        self.redirect("/blog")


class BlogFront(BlogHandler):
    def get(self):
        posts = Post.query(ancestor=BLOG_KEY).order(-Post.created)
        self.render('front.html', posts=posts)


class PostPage(BlogHandler):
    def get(self, post_id):
        post = Post.by_id(BLOG_KEY, post_id)

        if not post:
            self.error(404)
            return

        self.render("post-permalink.html", p=post)


class NewPost(BlogHandler):
    def get(self, post_id=""):
        if self.user:
            params = {}
            # TODO: refactor
            if post_id:
                p = Post.by_id(BLOG_KEY, post_id)
                if p:
                    params = dict(subject=p.subject,
                                  content=p.content,
                                  post_id=post_id)

            self.render("newpost.html", **params)
        else:
            self.redirect("/login")

    def post(self, post_id=""):
        if not self.user:
            self.redirect('/blog')

        owner = self.user
        subject = self.request.get('subject')
        content = self.request.get('content')
        redirect_to = self.request.get('redirect_to')

        if subject and content:
            if post_id:
                p = Post.by_id(BLOG_KEY, post_id)
                own = p and p.is_owned_by(self.user)
                if own:
                    p.subject = subject
                    p.content = content
                else:
                    self.flash(
                        "you can't edit other's posts",
                        "danger")

            else:
                p = Post(parent=BLOG_KEY,
                         owner=owner.key,
                         subject=subject,
                         likes=[],
                         content=content)
            p.put()
            self.redirect('/blog/%s' % p.key.id())

        else:
            error = "subject and content, please!"
            self.render("newpost.html",
                        subject=subject,
                        content=content,
                        post_id=post_id,
                        error=error)


class DeletePost(BlogHandler):
    def post(self, post_id):
        if self.user:
            p = Post.by_id(BLOG_KEY, post_id)
            own = p and p.is_owned_by(self.user)
            if own:
                p.key.delete()
            else:
                self.flash(
                    "you can't delete other's posts",
                    "danger")

            self.redirect("/blog ")
        else:
            self.redirect("/login")


class LikePost(BlogHandler):
    def post(self, post_id):
        if self.user:
            p = Post.by_id(BLOG_KEY, post_id)
            own = p and p.is_owned_by(self.user)
            if own:
                self.flash("you can't like your own posts", "danger")
            else:
                likes = p.likes
                if p.likes_it(self.user):
                    likes.remove(self.user.key)
                else:
                    likes.append(self.user.key)
                p.likes = likes
                p.put()

            self.redirect_to_referer()
        else:
            self.redirect("/login")


class NewComment(BlogHandler):
    def post(self, post_id):
        if self.user:
            message = self.request.get('message')
            p = Post.by_id(BLOG_KEY, post_id)
            comment = Comment(parent=p.key,
                              owner=self.user.key,
                              content=message)
            comment.put()
            self.redirect('/blog/%s' % post_id)
        else:
            self.redirect("/login")


# TODO: message can't be empty
class EditComment(BlogHandler):
    def post(self, post_id, comment_id):
        postKey = ndb.Key(Post, int(post_id), parent=BLOG_KEY)
        comment = Comment.by_id(postKey, comment_id)
        if self.user:
            if comment and comment.is_owned_by(self.user):
                message = self.request.get('message')
                comment.content = message
                comment.put()
            else:
                self.flash("you can't edit other's comments", "danger")

            self.redirect('/blog/%s' % post_id)
        else:
            self.redirect("/login")


class DeleteComment(BlogHandler):
    def post(self, post_id, comment_id):
        if self.user:
            postKey = ndb.Key(Post, int(post_id), parent=BLOG_KEY)
            c = Comment.by_id(postKey, comment_id)
            own = c and c.is_owned_by(self.user)
            if own:
                c.key.delete()
            else:
                self.flash(
                    "you can't delete other's comments",
                    "danger")

            self.redirect('/blog/%s#comments-section' % post_id)
        else:
            self.redirect("/login")


class Register(BlogHandler):
    def get(self):
        self.render("signup-form.html", errors={})

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        errors = User.validate_new(username, password, verify, email)
        if len(errors) > 0:
            params = dict(username=username,
                          email=email,
                          errors=errors)
            self.render('signup-form.html', **params)
        else:
            u = User.register(username, password, email)
            u.put()
            self.login(u)
            self.redirect('/blog')


class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')

app_config = {}
app_config['webapp2_extras.sessions'] = {
    'secret_key': 'not soo secret',
}

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog/?', BlogFront),
    ('/blog/([0-9]+)', PostPage),
    ('/blog/([0-9]+)/delete', DeletePost),
    ('/blog/newpost', NewPost),
    ('/blog/([0-9]+)/edit', NewPost),
    ('/blog/([0-9]+)/like', LikePost),
    ('/blog/([0-9]+)/comments/new', NewComment),
    ('/blog/([0-9]+)/comments/([0-9]+)/edit', EditComment),
    ('/blog/([0-9]+)/comments/([0-9]+)/delete', DeleteComment),
    ('/signup', Register),
    ('/login', Login),
    ('/logout', Logout)
    ],
    config=app_config,
    debug=True)
