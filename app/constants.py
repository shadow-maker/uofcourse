#
# SITE INFO
#

SITE_NAME = "UofCourse"
SITE_LANG = "en"
DEF_DESCRIPTION = "UofCourse is a web application that helps students in their program course planning."
CURRENT_VERSION = "1.1"

TIMEZONE = "Canada/Mountain"

#
# URLS
#

UNI_URL = "https://www.ucalgary.ca/"
REDDIT_URL = "https://www.reddit.com/r/UCalgary/"

#
# OTHER
#

ALLOW_ACCOUNT_CREATION = True

MAX_ITEMS_PER_PAGE = 50

MESSAGES_TIMEOUT = 300 # seconds

COURSE_LEVELS = [1, 2, 3, 4, 5, 6, 7]

IFTTT_EVENTS = {
	"message": "uofcourse_message"
}

DISQUS_EMBED = "https://uofcourse.disqus.com/embed.js"

DEFAULT_EMOJI = 128218

ERROR_MESSAGES = {
	403: "You don't have permission to perform that action",
	404: "Page not found",
	500: "Server error"
}

# 400 level colors
COLORS_LIGHT = {
	"blue": 0x3d8bfd,
	"indigo": 0x8540f5,
	"purple": 0x8c68cd,
	"pink": 0xde5c9d,
	"red": 0xe35d6a,
	"orange": 0xfd9843,
	"yellow": 0xffcd39,
	"green": 0x479f76,
	"teal": 0x4dd4ac,
	"cyan": 0x3dd5f3
}

# 500 level colors
COLORS = {
	"blue": 0x0d6efd,
	"indigo": 0x6610f2,
	"purple": 0x6f42c1,
	"pink": 0xd63384,
	"red": 0xdc3545,
	"orange": 0xfd7e14,
	"yellow": 0xffc107,
	"green": 0x198754,
	"teal": 0x20c997,
	"cyan": 0x0dcaf0
}

# 600 level colors
COLORS_DARK = {
	"blue": 0x0a58ca,
	"indigo": 0x520dc2,
	"purple": 0x59359a,
	"pink": 0xab296a,
	"red": 0xb02a37,
	"orange": 0xca6510,
	"yellow": 0xcc9a06,
	"green": 0x146c43,
	"teal": 0x1aa179,
	"cyan": 0x0aa2c0
}

STARRED_COLOR = COLORS_LIGHT["yellow"]
STARRED_EMOJI = 11088
