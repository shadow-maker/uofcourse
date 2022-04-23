#
# SITE INFO
#

SITE_NAME = "UofCourse"
DEF_DESCRIPTION = "UofCourse is a web application that helps students in their program course planning."
CURRENT_VERSION = "0.4.2"

#
# URLS
#

UNI_URL = "https://www.ucalgary.ca"
UNI_CAL_URL = "https://www.ucalgary.ca/pubs/calendar/current/"
REDDIT_URL = "https://www.reddit.com/r/UCalgary/"

#
# OTHER
#

ALLOW_ACCOUNT_CREATION = False

MAX_ITEMS_PER_PAGE = 50

COURSE_LEVELS = [1, 2, 3, 4, 5, 6, 7]

IFTTT_EVENTS = {
	"message": "uofcourse_message"
}

DISQUS_EMBED = "https://uofcourse.disqus.com/embed.js"

DEFAULT_EMOJI = 128218

COLORS_DARK = {
	"red": 0xff0000,
	"orange": 0xffa500,
	"yellow": 0xffff00,
	"green": 0x00ff00,
	"cyan": 0x00ffff,
	"blue": 0x0000ff,
	"purple": 0x800080,
	"pink": 0xffc0cb
}

COLORS_LIGHT = {
	"red": 0xff0000,
	"orange": 0xffa500,
	"yellow": 0xffff00,
	"green": 0x00ff00,
	"cyan": 0x00ffff,
	"blue": 0x0000ff,
	"purple": 0x800080,
	"pink": 0xffc0cb
}

STARRED_COLOR = COLORS_DARK["yellow"]
STARRED_EMOJI = 11088