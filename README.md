# GEMINI WEBAPP DEMO

not written by me, i asked gemini to make a webapp with login and user notes, it worked without any modification. instructions to run below

# My Web App

A basic Flask web application to track user logins and custom user notes, with email verification.

## Features

* User Registration with Email and Email Verification
* Secure Password Hashing (SHA256 - **Note: For production, consider bcrypt or Argon2**)
* User-specific Note Creation, Viewing, Editing, and Deletion
* SQLite Database for data storage
* Email verification links expire after 1 hour.

## Setup and Installation

Follow these steps to get the application running on your local machine:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/my_webapp.git](https://github.com/YOUR_USERNAME/my_webapp.git)
    cd my_webapp
    ```

2.  **Create a Virtual Environment (Recommended):**
    A virtual environment isolates your project's dependencies from your system's Python packages.
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    * **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Email Settings (`.env` file):**
    Create a file named `.env` in the `my_webapp/` root directory (the same level as `app.py`).
    **Replace the placeholder values with your actual email credentials.**
    **Important:** Do not commit this file to public version control!
    ```
    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USE_SSL=False
    MAIL_USERNAME=your_email@gmail.com
    MAIL_PASSWORD=your_email_app_password
    # For Gmail, you'll need to generate an App Password for your account:
    # [https://support.google.com/accounts/answer/185833](https://support.google.com/accounts/answer/185833)
    SECRET_KEY=a_very_long_and_random_string_for_flask_session_and_tokens
    ```

6.  **Initialize the Database:**
    The database schema will be created with `email` and `verified` columns.
    If you previously ran the app without these columns, you might need to delete `database.db` and rerun this command, or manually `ALTER TABLE` to add the columns.
    ```bash
    python database.py
    ```

7.  **Run the Application:**
    ```bash
    flask run
    # Or for development (if `FLASK_APP=app.py` is set in your environment):
    # python app.py
    ```

8.  **Access the Application:**
    Open your web browser and navigate to `http://127.0.0.1:5000/`

## Usage

* **Register:** Provide a username, email, and password. A verification email will be sent to the provided address.
* **Verify Email:** Click the link in the email to confirm your account.
* **Login:** Once verified, log in with your credentials.
* **Notes:** View, add, edit, and delete your personal notes. Unverified users will be redirected to an "Account Not Verified" page.
* **Resend Verification:** If your link expires or you didn't receive it, use the option on the "Account Not Verified" page to resend.

## Security Warning

**IMPORTANT:**
1.  The password hashing used (`hashlib.sha256`) in this example is **not secure enough for a production environment**. For real-world applications, always use robust password hashing libraries like [Bcrypt](https://pypi.org/project/Flask-Bcrypt/) or [Argon2](https://pypi.org/project/argon2-cffi/). This example prioritizes simplicity for demonstration purposes.
2.  The `SECRET_KEY` in `.env` must be a **very long, random, and unique string** for your production application. Never share it.
3.  Ensure your `MAIL_PASSWORD` (or app password) is kept secure and never exposed in your code or committed to version control.

## Contributing

Feel free to fork the repository and contribute!

## Running in Docker

You can run this in a dockerized environment if you are not able to install or run python locally in your system, you will need to install Docker though

Once you install Docker, run the following commands in the root of the application (same folder where app.py is located),

```
chmod +x *.sh
```

1. Make sure you have an .env set up properly according to the instructions above.

2. clear out any old images that were running and remove any old copies of the database.db (the application will create it again when it first starts)
```
./clean.sh
```
2. Build the docker image that sets up python in the docker container
```
./build.sh
```
3. run the app in the container 

```
./run.sh
```

4. Navigate to http://localhost:5000 to test the app


## License

This project is open-source. (You might want to add a specific license here, e.g., MIT, Apache 2.0)