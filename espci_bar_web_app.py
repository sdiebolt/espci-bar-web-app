from app import app, db
from app.models import User

@app.shell_context_processor
def make_shell_context():
    """ Used to create the context when calling
        flask shell. """
    return {'db': db, 'User': User}
