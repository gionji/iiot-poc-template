from threading import Thread

from flask import Flask


class WebServer(Thread):

    def __init__(self, persistence):
        super().__init__()
        self.persistence = persistence
        self.app = Flask(__name__)

        @self.app.route('/')
        def alive():
            return {'success': True}

        @self.app.route('/<string:collection>', methods=['GET'])
        def get_all(collection):
            data = self.persistence.query(collection, {}, {})
            if data:
                return {
                    'success': True,
                    'rows': data
                }
            else:
                return {
                    'success': False
                }

        @self.app.route('/<string:collection>', methods=['DELETE'])
        def delete(collection):
            deleted = self.persistence.drop_table(collection, {}, {})
            return {
                'success': deleted,
            }

    def run(self) -> None:
        super().run()
        self.app.run(host='0.0.0.0', port=8003, debug=True, use_reloader=False)
