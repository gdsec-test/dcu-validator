import werkzeug
from dcustructuredloggingflask.flasklogger import add_request_logging

werkzeug.cached_property = werkzeug.utils.cached_property

from rest_service.api import create_app  # noqa: E402

app = create_app()

add_request_logging(app, 'dcu-validator-rest')

if __name__ == '__main__':
    app.run()
