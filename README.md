# Ecommerce using Django, DjangoRestFramework

## Description
This Django project serves as a Ecommerce. Where shop owner can upload their products and customers can buy them from the shop directly. 

## Installation

### Prerequisites
- Python 3.10
- Django 5.0

### Installation Steps
1. Clone the repository: 
    ```bash
    git clone https://github.com/the0therguy/ecommerce_drf.git
    ```
2. Navigate to the project directory:
    ```bash
    cd ecommerce_drf
    ```
3. Create a virtual environment:
    ```bash
    python -m venv env
    ```
4. Activate the virtual environment:
    - On Windows:
        ```bash
        env\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source env/bin/activate
        ```
5. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Database Setup
1. Make migrations:
    ```bash
    python manage.py makemigrations
    ```
2. Apply migrations:
    ```bash
    python manage.py migrate
    ```
3. Create static file:
    ```bash
   python manage.py collectstatic --no-input
   ```

## Usage
Run the development server:
```bash
python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`.

## Contact
For any inquiries, reach out to email: ifty545@gmail.com.

live URL: https://ecommerce-drf-59wk.onrender.com

swagger documentation URL: https://ecommerce-drf-59wk.onrender.com/docs

### Dockerize the Project
1. Build the Docker Container
   ```bash
   docker-compose build
   ```
2. Run the Docker Container
   ```bash
   docker-compose up
   ```