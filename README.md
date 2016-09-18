# Symmetrical Snuffle
Guessing human emotions. One picture at a time.
Hack the North Project

This project uses Indico's API to guess what emotions are expressed on your face.
A live version of this website is available at symmetricalsnuffle.com. Feel free to take a picture using your phone or upload an existing picture on the website.

Stack:
- Bootstrap
- Python
- Flask
- PostgreSQL

To run and install:
1. Clone or download repository
2. Copy config-template.py -> config.py and modify the API key and DB connection string
3. Upload schema.sql to database server
4. run `python server.py`