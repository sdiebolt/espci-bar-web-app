# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask.helpers import get_debug_flag

from app import create_app, db
from app.models import User, Transaction, Item, GlobalSetting
from config import ProductionConfig, DevelopmentConfig

CONFIG = DevelopmentConfig if get_debug_flag() else ProductionConfig

app = create_app(CONFIG)


@app.shell_context_processor
def make_shell_context():
    """Create context when calling flask shell."""
    return {'db': db, 'User': User, 'Transaction': Transaction,
            'Item': Item, 'GlobalSetting': GlobalSetting}
