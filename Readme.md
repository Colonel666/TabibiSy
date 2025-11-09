# مشروع تطبيق سلامتك 


## Django backend setup

After creating a virtual environment and activating it, follow these steps to set up the Django backend:
1. **Install Django and Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Apply Migrations**:
   ```bash
   python manage.py migrate
    ```
3. **Create a Superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   
4. **Run the Development Server**:
   ```bash
    python manage.py runserver 0.0.0.0:8002
   ```
   
5. **Access the Admin Panel**:
   Open your web browser and navigate to `http://localhost:8002/admin` to access the Django admin panel.


### Auth API Endpoints
The endpoints for authentication can be found in the `tabibi_auth` app in the `urls.py` file.

An example of each endpoint can be found in `tabibi_requests/auth`
