from planner import changelog
from planner.constants import *

constants = {
	"SITE_NAME": SITE_NAME,
	"CURRENT_VERSION": CURRENT_VERSION,
	"CURRENT_VERSION_BETA": changelog[CURRENT_VERSION]["beta"] if CURRENT_VERSION in changelog else False,
}
