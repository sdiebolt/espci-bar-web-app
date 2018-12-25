"""Flask app, run by gunicorn."""
from app import create_app, db
from app.models import User, Transaction, Item, GlobalSetting

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Create context when calling flask shell."""
    return {'db': db, 'User': User, 'Transaction': Transaction,
            'Item': Item, 'GlobalSetting': GlobalSetting}
