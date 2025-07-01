from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de conexión a RDS MySQL
DB_USER = 'root'
DB_PASS = 'ventas123'
DB_HOST = 'data-ventas.cw7awmw0s20d.us-east-1.rds.amazonaws.com'
DB_NAME = 'ventas'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de tabla
class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_sales = db.Column(db.Integer, unique=True, nullable=False)
    cliente = db.Column(db.String(100))
    monto = db.Column(db.Float)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/data-json-<int:id_sales>', methods=['GET'])
def get_data(id_sales):
    venta = Venta.query.filter_by(id_sales=id_sales).first()
    if venta:
        return jsonify({
            "ID_SALES": venta.id_sales,
            "CLIENTE": venta.cliente,
            "MONTO": venta.monto
        })
    return jsonify({'error': 'ID_SALES no encontrado'}), 404

@app.route('/add-sale', methods=['POST'])
def add_sale():
    data = request.get_json()
    if not data or not all(k in data for k in ("ID_SALES", "CLIENTE", "MONTO")):
        return jsonify({'error': 'Datos incompletos'}), 400

    if Venta.query.filter_by(id_sales=data['ID_SALES']).first():
        return jsonify({'error': 'Ya existe una venta con ese ID_SALES'}), 400

    venta = Venta(id_sales=data['ID_SALES'], cliente=data['CLIENTE'], monto=data['MONTO'])
    db.session.add(venta)
    db.session.commit()
    return jsonify({'message': 'Venta registrada correctamente'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
