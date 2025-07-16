<!-- Create Virtual Environment -->
python -m venv venv
<!-- Activate Virual Environment -->
venv/scripts/activate
<!-- Install Dependencies from requirements.txt File -->
pip install -r requirements.txt

<!-- Create .env File and these data in it-->
SECRET_KEY=SecretKey
MYSQL_USER=root
MYSQL_PASSWORD=12345678
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=dev_ventures
GEMINI_API_KEY=

<!-- Setup Database -->
flask db init
<!-- Create database migration to put that into database -->
flask db migrate -m "Initial migration"
<!-- Add tables to Database -->
flask db upgrade

<!-- Run project -->
python run.py

<!-- Test API endpoint in Postman or ThunderClient -->
http://127.0.0.1:5000/api/users