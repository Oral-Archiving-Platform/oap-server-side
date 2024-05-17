
# OAP Server Side

## Project Overview
The **Oral Archiving Platform (OAP)** is a digital repository designed to preserve and provide access to a vast collection of oral cultural heritage, including folktales, historical narratives, and personal testimonies from diverse communities. The platform uses Django for the server-side implementation, ensuring a robust and scalable backend for managing and delivering the content.

## Project Structure
The project is organized as follows:

- **oap_server_side/**: Main source directory containing the Django project.
  - **oap_server_side/**: Contains the settings and configuration for the Django project.
  - **manage.py**: A command-line utility that lets you interact with this Django project.
- **venv/**: Virtual environment for the project.
- **requirements.txt**: List of dependencies for the project.
- **README.md**: Project documentation.

## Getting Started
To get started with the project, follow these steps:

### Prerequisites
Ensure you have the following installed on your development environment:
- Python (>= 3.8)
- pip (>= 20.x)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/oap-server-side.git
   ```
2. Navigate to the project directory:
   ```sh
   cd oap-server-side
   ```
3. Create a virtual environment:
   ```sh
   python -m venv venv
   ```
4. Activate the virtual environment:
   On Windows:
   ```sh
   venv\Scripts\activate
   ```
   On macOS/Linux:
   ```sh
   source venv/bin/activate
   ```
5. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running the Application
To start the development server, run:
```sh
python manage.py runserver
```
This will start the server and you can access the application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

### Creating New Apps
To create a new Django app within the project, follow these steps:

1. Ensure the virtual environment is activated.
2. Run the following command:
   ```sh
   python manage.py startapp <app_name>
   ```
3. Add the new app to the `INSTALLED_APPS` list in the `settings.py` file.

## Best Practices

### Virtual Environment
- Always use a virtual environment to manage your project's dependencies. This keeps the project dependencies isolated and helps avoid conflicts.
- Activate the virtual environment before running any project-related commands.

### Requirements File
- Use the `requirements.txt` file to manage your project dependencies.
- After installing a new dependency, run the following command to update the `requirements.txt` file:
  ```sh
  pip freeze > requirements.txt
  ```

### Code Structure
- Organize your Django apps logically, keeping related models, views, and templates together.
- Use Django's built-in functionalities and follow the framework's conventions for better maintainability.

### Security
- Keep sensitive information such as secret keys and database credentials out of version control. Use environment variables or a separate configuration file for these settings.
- Follow Django's security best practices to protect the application from common vulnerabilities.

## Contribution Guidelines
If you wish to contribute to this project, please adhere to the following guidelines:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear and concise messages.
4. Create a pull request and provide a detailed description of your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact
For any questions or feedback, please contact Yassine Ibork at y.ibork1@gmail.com.
