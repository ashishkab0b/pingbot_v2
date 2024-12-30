from celery import Celery

def make_celery(app):

    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND'],
        include=['tasks']  # Include modules where tasks are defined
    )
    celery.config_from_object(app.config, namespace='CELERY_')
    
    # Define a custom Task base class that ensures the app context is available
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery