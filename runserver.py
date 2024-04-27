from api.app import create_app
from api.config.config import config_dict, Config
app = create_app()

if(__name__ == '__main__'):
    app.run(debug=config_dict[Config.TYPE].DEBUG, port=config_dict[Config.TYPE].PORT)