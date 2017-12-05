from validator import create_app
import os

if __name__ == '__main__':
    env = os.getenv('sysenv') or 'dev'
    app = create_app(env)
    app.run()
