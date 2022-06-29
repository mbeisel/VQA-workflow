from api.controller import objectiveFns

MODULES = (objectiveFns,)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        api.register_blueprint(module.blp)
