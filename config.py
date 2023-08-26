import warnings
from aiohttp import web
import logging


routes = web.RouteTableDef()
warnings.filterwarnings('ignore')
logging.basicConfig(level='INFO')
logger = logging.getLogger()
app = web.Application()
app.add_routes(routes)
