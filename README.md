# GEMINI WEBAPP DEMO

not written by me, i asked gemini to make a webapp with login and user notes, it worked without any modification. instructions to run below

A basic Flask web application to track user logins and custom user notes.

## Features

* User Registration and Login
* Secure Password Hashing (SHA256 - **Note: For production, consider bcrypt or Argon2**)
* User-specific Note Creation, Viewing, Editing, and Deletion
* SQLite Database for data storage

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

5.  **Initialize the Database:**
    The database schema will be created.
    ```bash
    python database.py
    ```
    (Alternatively, running `app.py` for the first time will also initialize it if it doesn't exist.)

6.  **Run the Application:**
    ```bash
    flask run
    # Or for development:
    # python app.py
    ```

7.  **Access the Application:**
    Open your web browser and navigate to `http://127.0.0.1:5000/`

## Usage

* **Register:** Create a new user account.
* **Login:** Log in with your registered credentials.
* **Notes:** View, add, edit, and delete your personal notes.

## Security Warning

**IMPORTANT:** The password hashing used (`hashlib.sha256`) in this example is **not secure enough for a production environment**. For real-world applications, always use robust password hashing libraries like [Bcrypt](https://pypi.org/project/Flask-Bcrypt/) or [Argon2](https://pypi.org/project/argon2-cffi/). This example prioritizes simplicity for demonstration purposes.

## Contributing

Feel free to fork the repository and contribute!

## License

This project is open-source. (You might want to add a specific license here, e.g., MIT, Apache 2.0)