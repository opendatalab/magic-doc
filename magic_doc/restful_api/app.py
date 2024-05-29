import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent
root_dir = base_dir.parent.parent
sys.path.append(str(root_dir))

from api import create_app
import yaml

config_path = base_dir / "config/config.yaml"


class ConfigMap(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


with open(str(config_path), mode='r', encoding='utf-8') as fd:
    data = yaml.load(fd, Loader=yaml.FullLoader)
    _config = data.get(data.get("CurrentConfig", "DevelopmentConfig"))
config = ConfigMap()
for k, v in _config.items():
    config[k] = v
config['base_dir'] = base_dir
database = _config.get("database")
if database:
    if database.get("type") == "sqlite":
        database_uri = f'sqlite:///{base_dir}/{database.get("path")}'
    elif database.get("type") == "mysql":
        database_uri = f'mysql+pymysql://{database.get("user")}:{database.get("password")}@{database.get("host")}:{database.get("port")}/{database.get("database")}?'
    else:
        database_uri = ''
    config['SQLALCHEMY_DATABASE_URI'] = database_uri
app = create_app(config)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5556, debug=True)