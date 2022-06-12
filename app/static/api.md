## Introduction  {: #introduction }

UofCourse offers a public Web API to easily retrieve stored data. The API applies the RESTful API principles, but at the moment only GET requests are supported and no user-specific data can be retrieved. No authentication is required to make requests to the API.

**API BASE URL: ** `{{url_for('view.api', _external=True)}}`

Below you'll find a list of all available endpoints, each with a unique path that extends from the base url. To make a call to a specific endpoint, make a request to the base url + the endpoint path. Some endpoints support [URL parameters](https://www.semrush.com/blog/url-parameters/), which can be passed in the request URL to retrieve specific data.

## General structure {: #general-structure}

There are 5 main data tables that can be retrieved though the API's endpoints. Each data table has specific columns that correspond to its relevant data. The only column that is available for all the tables is the `id` column, which is the primary key for each row.

With the API the developer can retrieve all rows for a selected table, or a single row by passing its `id` (or `code`, if aplicable) to the endpoint.

### Retrieving a single row {: #retrieve-single}

If a single row is retrieved, the API will return a JSON object where every key-value pair corresponds to column data in the table. No URL parameters are supported when requesting a single row.

### Retrieving all rows {: #retrieve-all}

If all rows are retrieved, the results will be paginated and the API will return a JSON object of the following structure:

| Key {: .col-2} | Value type {: .col-2} | Value contents                                               |
| -------------- | --------------------- | ------------------------------------------------------------ |
| `page`         | int                   | Current page                                                 |
| `pages`        | int                   | Total amount of pages                                        |
| `results`      | array of objects      | JSON array where each element is a JSON object with the same structure as the single row |
| `total`        | int                   | Total amount of results                                      |

The following URL parameters are available when requesting all results for a particular table:

| Parameter {: .col-2} | Parameter type {: .col-2} | Parameter contents                                           | Default {: .col-2} |
| -------------------- | ------------------------- | ------------------------------------------------------------ | ------------------ |
| `asc`                | boolean                   | `1` (true) for results in ascending order, `0` (false) for results in descending order. The criteria from which results are ordered will depend on the `sort` parameter | `1`                |
| `limit`              | int                       | Amount of results per page (MAX 50)                          | `30`               |
| `page`               | int                       | Results page                                                 | `1`                |
| `sort`               | array of strings          | Array of table columns ordered in priority, which serve as the criteria from which to order the results. The columns permitted depend on the specific endpoint's table. | `id`           |

Some endpoints support other URL parameters to filter the results.

The endpoints will raise `400` level errors if the contents of the URL parameters are invalid, and `404` level errors if the `page` specified exceeds the amount of pages available. See [below](#error-handling) for more information on error handling.

### Error handling {: #error-handling}

The UofCourse API returns [HTTP status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) to state whether the request was successful or not. Whenever a request was successful, a status code of `200` should be returned (along with the requested data). If a request was unsuccessful a staus code of level `400` or `500` will be returned.

`400` level status codes are the most common type of request errors with the API, as they correspond to errors from the client. Whenever you receive a `400` level status code a JSON object with an `error` key will also be returned, which will contain a brief description of the error.

`500` level status codes are associated with server errors, and most likely mean internal bugs with the API.

## Endpoints {: #endpoints}

The API has 5 main endpoint paths that correspond to the available data tables:

- Grade - `/grade`
- Term - `/term`
- Course - `/course`
- Subject - `/subject`
- Faculty - `/faculty`

### Grades {: #grades}

The following data columns (key-value pairs) are available for the Grade table:

| Key {: .col-2} | Value type {: .col-2} | Can be null {: .col-2} | Value contents                                               |
| -------------- | --------------------- | ---------------------- | ------------------------------------------------------------ |
| `id`           | int                   | No                     | Unique ID                                                    |
| `symbol`       | string                | No                     | The grade symbol (sometimes known as letter), usually one or two characters long |
| `gpv`          | float                 | Yes                    | Corresponding Grade Point Value for the grade                |
| `passed`       | bool                  | No                     | Whether the grade correspond to a passing grade or not       |
| `desc`         | string                | Yes                    | Grade description, taken from the university's website       |

#### Get all grades {: #grades-1}

> **GET**{: .badge .bg-primary .me-1}  `/grades`
{: .p-0 .m-0}

Returns a JSON object of the paginated results. See [retrieving all rows](#retrieve-all) for more information.

The `results` key will contain an array of JSON objects, each of which corresponds to a row in the Grade table. Each element in the array will have the same key-value pairs as described [above](#grades).

This endpoint does not support other URL parameters apart from those specified in [retrieving all rows](#retrieve-all). The following columns are available to be used with the `sort` URL parameter:
{: .mb-0}

* `id`
* `symbol`
* `gpv`
* `passed`
* `desc`

A `400` error code will be returned if any other column name is used with the `sort` parameter.

#### Get a grade {: #grades-2}

> **GET**{: .badge .bg-primary .me-1}  `/grades/{id}`
{: .p-0 .m-0}

Returns a JSON object with the data for the Grade item with the specified `id`. The key-value pairs in the object are the same as specified in [Grades](#grades).

A `404` error code will be returned if the `id` specified does not correspond to a row in the Grade table.

### Terms {: #terms}

The following data columns (key-value pairs) are available for the Term table:

| Key {: .col-2} | Value type {: .col-2} | Can be null {: .col-2} | Value contents                                               |
| -------------- | --------------------- | ---------------------- | ------------------------------------------------------------ |
| `id`           | int                   | No                     | Unique ID                                                    |
| `year`         | int                   | No                     | Year of the term                                             |
| `season`       | string                | No                     | Name of the season of the term                               |
| `start`        | string                | Yes                    | Start date of the term, formatted in the ISO date standard YYYY-MM-DD |
| `end`          | string                | Yes                    | End date of the term, formatted in the ISO date standard YYYY-MM-DD |

#### Get all terms {: #terms-1}

> **GET**{: .badge .bg-primary .me-1}  `/terms`
{: .p-0 .m-0}

Returns a JSON object of the paginated results. See [retrieving all rows](#retrieve-all) for more information.

The `results` key will contain an array of JSON objects, each of which corresponds to a row in the Term table. Each element in the array will have the same key-value pairs as described [above](#terms).

This endpoint does not support other URL parameters apart from those specified in [retrieving all rows](#retrieve-all). The following columns are available to be used with the `sort` URL parameter:
{: .mb-0}

* `id`
* `year`
* `season`
* `start`
* `end`

A `400` error code will be returned if any other column name is used with the `sort` parameter.

#### Get a term {: #terms-2}

> **GET**{: .badge .bg-primary .me-1}  `/terms/{id}`
{: .p-0 .m-0}

Returns a JSON object with the data for the Term item with the specified `id`. The key-value pairs in the object are the same as specified in [Terms](#terms).

A `404` error code will be returned if the `id` specified does not correspond to a row in the Term table.

### Faculties {: #faculties}

The following data columns (key-value pairs) are available for the Faculty table:

| Key {: .col-2} | Value type {: .col-2} | Can be null {: .col-2} | Value contents                             |
| -------------- | --------------------- | ---------------------- | ------------------------------------------ |
| `id`           | int                   | No                     | Unique ID                                  |
| `name`         | string                | Yes                    | Name of the faculty                        |
| `url`          | string                | Yes                    | URL path for the faculty page in UofCourse |
| `url_uni`      | string                | Yes                    | Full URL for the official faculty site     |

#### Get all faculties {: #faculties-1}

> **GET**{: .badge .bg-primary .me-1}  `/faculties`
{: .p-0 .m-0}

Returns a JSON object of the paginated results. See [retrieving all rows](#retrieve-all) for more information.

The `results` key will contain an array of JSON objects, each of which corresponds to a row in the Faculty table. Each element in the array will have the same key-value pairs as described [above](#faculties).

This endpoint supports other URL parameters to assist in filtering the results:

| Parameter {: .col-2} | Parameter type {: .col-2} | Parameter contents                                           |
| -------------------- | ------------------------- | ------------------------------------------------------------ |
| `name`               | string                    | A search query to find faculties by a specific name. The search query must be included in the faculty's name to be returned in the results (not an exact match). |

The following columns are available to be used with the `sort` URL parameter:
{: .mb-0}

* `id`
* `name`

A `400` error code will be returned if any other column name is used with the `sort` parameter.

#### Get a faculty {: #faculties-2}

> **GET**{: .badge .bg-primary .me-1}  `/faculties/{id}`
{: .p-0 .m-0}

Returns a JSON object with the data for the Faculty item with the specified `id`. The key-value pairs in the object are the same as specified in [Faculties](#faculties).

A `404` error code will be returned if the `id` specified does not correspond to a row in the Faculty table.

#### Get faculty subjects {: #faculties-3}

> **GET**{: .badge .bg-primary .me-1}  `/faculties/{id}/subjects`
{: .p-0 .m-0}

Gets all the subjects of a selected faculty and returns a JSON object of the paginated results. See [retrieving all rows](#retrieve-all) for more information.

Alias for `/subjects?faculties={id}`, see [get all subjects](#subjects) for more information.

A `404` error code will be returned if the `id` specified does not correspond to a row in the Faculty table.

#### Get faculty courses {: #faculties-4}

> **GET**{: .badge .bg-primary .me-1}  `/faculties/{id}/courses`
{: .p-0 .m-0}

Gets all the courses of a selected faculty and returns a JSON object of the paginated results. See [retrieving all rows](#retrieve-all) for more information.

Alias for `/courses?faculties={id}`, see [get all courses](#courses) for more information.

A `404` error code will be returned if the `id` specified does not correspond to a row in the Faculty table.

### Subjects {: #subjects}

The following data columns (key-value pairs) are available for the Subject table:

| Key {: .col-2} | Value type {: .col-2} | Can be null {: .col-2} | Value contents                                               |
| -------------- | --------------------- | ---------------------- | ------------------------------------------------------------ |
| `id`           | int                   | No                     | Unique ID                                                    |
| `faculty_id`   | int                   | No                     | ID of the subject faculty                                    |
| `code`         | string                | No                     | Code of the subject, non-numeric and 3 or 4 characters long  |
| `name`         | string                | Yes                    | Name of the subject                                          |
| `emoji`        | string                | Yes                    | [Unicode](https://unicode.org/emoji/charts/full-emoji-list.html) emoji ID for the subject, in decimal form |
| `url`          | string                | Yes                    | URL path for the subject page in UofCourse                   |
| `url_uni`      | string                | Yes                    | Full URL for the subject page in the official uni calendar site |

#### Get all subjects {: #subjects-1}

> **GET**{: .badge .bg-primary .me-1} `/subjects`
{: .p-0 .m-0}

Returns a JSON object of the paginated results. See [retrieving all rows](#retrieve-all) for more information.

The `results` key will contain an array of JSON objects, each of which corresponds to a row in the Subject table. Each element in the array will have the same key-value pairs as described [above](#subjects).

This endpoint supports other URL parameters to assist in filtering the results:

| Parameter {: .col-2} | Parameter type {: .col-2} | Parameter contents                                           |
| -------------------- | ------------------------- | ------------------------------------------------------------ |
| `name`               | string                    | A search query to find subjects by a specific name. The search query must be included in the subject's name to be returned in the results (not an exact match). |
| `faculty`            | array of ints             | Array of faculty IDs. The returned subjects must have either of these faculties. |

The following columns are available to be used with the `sort` URL parameter:
{: .mb-0}

* `id`
* `faculty_id`
* `code`
* `name`
* `emoji`

A `400` error code will be returned if any other column name is used with the `sort` parameter.

#### Get a subject {: #subjects-2}

> **GET**{: .badge .bg-primary .me-1} `/subjects/id`
{: .p-0 .m-0}

Returns a JSON object with the data for the Subject item with the specified `id`. The key-value pairs in the object are the same as specified in [Subjects](#subjects).

A `404` error code will be returned if the `id` specified does not correspond to a row in the Subject table.

#### Get subject courses {: #subjects-3}

> **GET**{: .badge .bg-primary .me-1} `/subjects/{id}/courses`
{: .p-0 .m-0}

Gets all the courses of a selected subjectz and returns a JSON object of the paginated results. See [retrieving all rows](#retrieve-all) for more information.

Alias for `/courses?subjects={id}`, see [get all courses](#courses) for more information.

A `404` error code will be returned if the `id` specified does not correspond to a row in the Subject table.

#### Get a subject by its code {: #subjects-4}

> **GET**{: .badge .bg-primary .me-1} `/subjects/code/{subj}`
{: .p-0 .m-0}

Returns a JSON object with the data for the Subject item with the specified code (`subj`). The value of `subj` must be a non-numeric string of 3 or 4 characters. The key-value pairs in the object are the same as specified in [Subjects](#subjects).

A `404` error code will be returned if the `id` specified does not correspond to a row in the Subject table.

### Courses {: #courses}

The following data columns (key-value pairs) are available for the Course table:

| Key {: .col-2} | Value type {: .col-2} | Can be null {: .col-2} | Value contents                                               |
| -------------- | --------------------- | ---------------------- | ------------------------------------------------------------ |
| `id`           | int                   | No                     | Unique ID                                                    |
| `subject_id`   | int                   | No                     | ID of the course subject                                     |
| `number`       | int                   | No                     | Course 3-digit number                                        |
| `level`        | string                | No                     | Corresponding level of the course number (equal to the floor division of `number // 100`) |
| `code`         | string                | No                     | Concatenation of the subject code and the course number, separated by a `-` dash |
| `name`         | string                | Yes                    | Name of the course                                           |
| `aka`          | string                | Yes                    | Alternative or former name of the course                     |
| `emoji`        | int                   | Yes                    | The course subject's emoji ID                                |
| `units`        | float                 | Yes                    | Number of units (credits) of the course                      |
| `desc`         | string                | Yes                    | Description of the course                                    |
| `prereqs`      | string                | Yes                    | Pre-requisites of the course                                 |
| `coreqs`       | string                | Yes                    | Co-requisites of the course                                  |
| `antireqs`     | string                | Yes                    | Anti-requisites of the course                                |
| `notes`        | string                | Yes                    | Notes of the course                                          |
| `repeat`       | boolean               | No                     | Whether the course can be repeated for credit or not         |
| `countgpa`     | boolean               | No                     | Whether the course counts towards the overall GPA or not     |
| `url`          | string                | No                     | URL path for the course page in UofCourse                    |
| `url_uni`      | string                | Yes                    | Full URL for the course page in the official uni calendar site |

#### Get all courses {: #courses-1}

> **GET**{: .badge .bg-primary .me-1}  `/courses`
{: .p-0 .m-0}

Returns a JSON object of the paginated results. See [retrieving all rows](#retrieve-all) for more information.

The `results` key will contain an array of JSON objects, each of which corresponds to a row in the Course table. Each element in the array will have the same key-value pairs as described [above](#courses).

This endpoint supports other URL parameters to assist in filtering the results:

| Parameter {: .col-2} | Parameter type {: .col-2} | Parameter contents                                           |
| -------------------- | ------------------------- | ------------------------------------------------------------ |
| `name`               | string                    | A search query to find courses by a specific name. The search query must be included in the course's  to be returned in the results (not an exact match). |
| `number`             | array of ints             | Array of exact course numbers. The returned courses must have any of these course numbers. |
| `level`              | array of ints             | Array of levels (integers ranging from 1 to 7). The returned courses must be of either of these levels. |
| `subject`            | array of ints or strings  | Array of subject IDs or codes. The returned courses must have either of these subjects. |
| `faculty`            | array of ints             | Array of faculty IDs. The returned courses must have either of these faculties. |
| `repeat`             | boolean                   | Whether the course can be repeated for credit or not         |
| `countgpa`           | boolean                   | Whether the course counts towards the overall GPA or not     |

The following columns are available to be used with the `sort` URL parameter:
{: .mb-0}

* `id`
* `faculty_id`
* `subject_id`
* `subject_code`
* `number`
* `level`
* `code`
* `name`
* `aka`
* `units`
* `desc`
* `prereqs`
* `coreqs`
* `antireqs`
* `notes`
* `repeat`
* `countgpa`

A `400` error code will be returned if any other column name is used with the `sort` parameter.

#### Get a course {: #courses-2}

> **GET**{: .badge .bg-primary .me-1}  `/courses/{id}`
{: .p-0 .m-0}

Returns a JSON object with the data for the Course item with the specified `id`. The key-value pairs in the object are the same as specified in [Courses](#courses).

A `404` error code will be returned if the `id` specified does not correspond to a row in the Subject table.

#### Get a course by its code {: #courses-3}

> **GET**{: .badge .bg-primary .me-1}  `/courses/code/{subj}/{num}`
{: .p-0 .m-0}

Returns a JSON object with the data for the Course item with the specified subject code (`subj`) and course number (`num`). The value of `subj` must be a non-numeric string of 3 or 4 characters. The value of `num` must be a 3-digit number. The key-value pairs in the object are the same as specified in [Courses](#courses).

A `404` error code will be returned if the `id` specified does not correspond to a row in the Subject table.
