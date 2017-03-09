import webapp2

from webapp2_extras import sessions
from google.appengine.ext import ndb
from template import render_str
from security import make_secure_val, check_secure_val
from user import User
from post import Post


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

        self.render("permalink.html", post=post)


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
                                  key=p.key)

            self.render("newpost.html", **params)
        else:
            self.redirect("/login")

    def post(self, post_id=""):
        if not self.user:
            self.redirect('/blog')

        owner = self.user
        subject = self.request.get('subject')
        content = self.request.get('content')

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
                         content=content)

            p.put()
            self.redirect('/blog/')
        else:
            error = "subject and content, please!"
            self.render("newpost.html",
                        subject=subject,
                        content=content,
                        error=error)


class EditPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")


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

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/([0-9]+)/delete', DeletePost),
                               ('/blog/newpost', NewPost),
                               ('/blog/([0-9]+)/edit', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout)
                               ],
                              config=app_config,
                              debug=True)
