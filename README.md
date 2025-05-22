# Food Bank Manager

Food Bank Manager is a comprehensive web application designed to streamline and enhance the operations of food banks. It provides an integrated platform to manage donations, inventory, volunteers, events, and beneficiary requests efficiently. The application aims to improve the coordination and transparency of food bank activities, ensuring that resources are effectively distributed to those in need.

Built using Python Flask, the application leverages SQLAlchemy for robust database management and incorporates several Flask extensions to handle user authentication, form processing, and security features.

## Features

- User authentication and role management
- Food bank inventory management
- Donation tracking and management
- Event and volunteer management
- Request and distribution handling
- Messaging and notifications

## Technologies Used

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- Flask-Login
- Flask-WTF
- Gunicorn (for production server)
- SQLite (default database, can be configured to use other databases)

## Project Structure

- `app.py`: Main Flask application setup and initialization
- `routes.py`: Application routes and views
- `models.py`: Database models
- `forms.py`: Web forms using Flask-WTF
- `utils.py`: Utility functions
- `templates/`: HTML templates for rendering pages
- `static/`: Static files (CSS, JavaScript, images)
- `.render.yaml`: Render.com deployment configuration
- `requirements.txt`: Python dependencies

## Setup and Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd FoodBankManager2
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables:

   - `SESSION_SECRET`: Secret key for Flask sessions
   - `DATABASE_URL`: Database connection string (default uses SQLite `sqlite:///foodbank.db`)

5. Run the application locally:

   ```bash
   flask run
   ```

## Deployment

### Render.com

The application is configured for deployment on Render.com using the `.render.yaml` file.

- The service uses Python environment.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn main:app`
- Environment variables `SESSION_SECRET` and `DATABASE_URL` should be set as Render secrets.

### Vercel (Optional)

A `vercel.json` file is also included for deployment on Vercel with Python support.

## Notes

- The default database is SQLite, which is file-based and may not be suitable for production on serverless platforms. It is recommended to use a managed database and set the `DATABASE_URL` accordingly.
- Ensure environment variables are properly configured in your deployment environment.

## Application Screenshot

![Application Screenshot](https://via.placeholder.com/800x400.png?text=Food+Bank+Manager+Screenshot)

## Live Deployment

You can access the live application at: [Your Deployment URL Here](https://your-deployment-url.com)

## License

This project is licensed under the MIT License.
