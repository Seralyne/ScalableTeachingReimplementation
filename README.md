# ScalableTeachingReimplementation

This is a reimplementation of the vertical slice of ScalableTeaching necessary for me to produce what I needed for my Bachelor's Thesis.

## Dependencies
	* Django
	* Requests
	* Bootstrap (Bundled from Bootstrap's CDN)
	* Flask

## Installation

1. Create a new Python virtual environment by running `python -m venv <venv>` where the last <venv> is the name of your virtual environment.
2. Enter the virtual environment as described below.
3. Run `pip install -r requirements.txt` to automatically install the required dependencies.
4. Run `python manage.py migrate` to 

## Entering the Virtual Environment

        * Windows (cmd): <venv>\Scripts\activate.bat
        * Linux/Mac (assuming bash/zsh): source <venv>/bin/activate
For other shells, see [the Python venv documentation](https://docs.python.org/3/library/venv.html)


## Configuring the project
Configuration is done inside of `ScalableTeaching/settings.py`.
To get the project running, it is recommended that you change the following variables:`ACHIEVEMENT_WEBHOOK_TOKEN` and `GITLAB_WEBHOOK_TOKEN`, as these are secrets you ideally do not want shared.

If you plan on changing the database backend from the default SQLite database, this is also where you'd do that. See the `DATABASES` variable and the [Django documentation on database backends](https://docs.djangoproject.com/en/5.2/ref/settings/#databases)

If you plan on running this against a real GitLab instance (not recommended - untested), also change the `GITLAB_URL` variable to point to your GitLab instance.


## Running the project

If you're running against the mocked GitLab instance, make sure to run that first using `flask --app gitlab_mock run`

1.  Ensure you've entered the previously created virtual environment and installed the dependencies by running the previous steps.
2.  Ensure you've changed the default settings for the tokens. 
3.  Ensure you've run all the migrations by running `python manage.py migrate`
3.  Run `python manage.py runserver`


## Running tests

If you're testing against the mocked GitLab instance, make sure to run that first using `flask --app gitlab_mock run`

1.  Ensure you've entered the previously created virtual environment and installed the dependencies by running the previous steps until (but not including) "Running the Project".
2.  Ensure you've run all the migrations by running `python manage.py migrate`
3.  Run `python manage.py test`



