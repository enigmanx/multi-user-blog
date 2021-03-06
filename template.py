import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True,
                               extensions=["jinja2.ext.with_"])


def render_str(template, **kwargs):
    """Renders jinja2 templates from the `templates` folder.

    Args:
        template (str): The template file
        **kwargs: The list of parameters
    """
    t = jinja_env.get_template(template)
    return t.render(kwargs)
