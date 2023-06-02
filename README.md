# UofCourse - UofC Course Planner

## Directory tree

```bash
uofcourse
└── app                # The main app directory
    ├── models         # SQLAlchemy Models that map to the database
    ├── routes         # Flask app routes for the web application
    │   ├── admin      # Flask-Admin ModelView classes and utilities
    │   ├── api        # API routes - endpoints return json data
    │   └── views      # View routes - render or redirect to templates
    ├── static         # Static files
    │   ├── scripts    # JavaScript files used in templates
    │   └── styles     # CSS files used in templates
    ├── templates      # Contains HTML template files
    │   ├── admin      # Template files for /admin/ pages
    │   ├── components # Jinja macros with args that can be inserted in other templates
    │   └── includes   # Stand-alone HTML components that can be inserted in other templates
    └── update         # Scripts to update the database based on uni data
```

## Configuration

### Flask environment variables

A `.flaskenv` file in the root project directory is used for variables related to the Flask app initialization. The following environment variables are needed:

* `FLASK_DEBUG`: Set to `True` to enable debug mode
* `FLASK_APP`: (Optional) Set to the name of the Flask app to use. Defaults to `app` in the root project directory

### Environment variables

A `.env` file in the root project directory is used to store secure variables. The following environment variables are needed:

* `DB_URI`: The URI of the database, if its value is not defined the following DB variables will be used:
    * `DB_TYPE`: The engine type of database - defaults to "mysql"
    * `DB_HOST`: The hostname for the database - defaults to "localhost"
    * `DB_PORT`: The port for the database - defaults to "3306"
    * `DB_NAME`: The name of the database - defaults to "main"
    * `DB_USER`: The username for the database - defaults to "root"
    * `DB_PSSW`: The password for the database - defaults to ""
* `SECRET_KEY`: The secret key for the application
* `GANALYTICS_ID`: The Google Analytics ID for the application (begins with "G-")
* `GADSENSE_ID`: The Google AdSense ID for the application
* `IFTTT_KEY`: The IFTTT key for the application, used to send requests to IFTTT events

## Database update

The project includes built-in scrape scripts that pull data from the UofC website and update the database. The scripts can be accesesed form the Flask CLI. To automatically update all tables in the database, run the command:

```bash
flask update all
```

Alternatively, to update specific tables, you can use the commands:

```bash
flask update terms
flask update grades
flask update courses
```

The last "courses" update command will take care of updating the `Faculty`, `Subject` and `Course` tables. Before running this command, make sure that there are rows in the `Calendar` command, which have to be inserted manually.

## Running the app

Run the app with the command:
    
```bash
flask run
```

## Style guidelines (all languages)

* Indentation - Use tab characters (`\t`) to denote full indentations
* Strings - Double quotes (`"..."`)
* Class names - `PascalCase`
* Function names - `camelCase`
