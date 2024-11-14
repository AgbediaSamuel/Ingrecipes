from Application import create_app 
from Application import db
app = create_app()

# with app.app_context():
#     db.create_all()
 
# app.register_blueprint(api, url_prefix='/api')


if __name__ == "__main__":
    app.run(debug=True, port=8000)
