# UofCourse - UofC Course Planner

## Directory tree

```bash
uofcourse
└── app                # The main app directory
    ├── db_update      # Scripts to update the database based on uni data
    ├── models         # SQLAlchemy Models that map to the database
    ├── routes         # Flask app routes for the web application
    │   ├── admin      # Flask-Admin ModelView classes and utilities
    │   ├── api        # API routes - endpoints return json data
    │   └── views      # View routes - render or redirect to templates
    ├── static         # Static files
    │   ├── scripts    # JavaScript files used in templates
    │   └── styles     # CSS files used in templates
    └── templates      # Contains HTML template files
        ├── admin      # Template files for /admin/ pages
        └── components # Components used (included) in other templates
```
