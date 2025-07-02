import boto3
import json
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

DB_USER = 'root'
DB_PASS = 'ventas123'
DB_HOST = 'data-ventas.cw7awmw0s20d.us-east-1.rds.amazonaws.com'
DB_NAME = 'ventas'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELO DE LA TABLA
class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    id_sales = db.Column(db.Integer, unique=True, nullable=False)
    ordernumber = db.Column(db.String(50))
    quantityordered = db.Column(db.Integer)
    priceeach = db.Column(db.Float)
    orderlinenumber = db.Column(db.String(10))
    sales = db.Column(db.Float)
    orderdate = db.Column(db.String(20))
    status = db.Column(db.String(20))
    qtr_id = db.Column(db.String(10))
    month_id = db.Column(db.String(10))
    year_id = db.Column(db.String(10))
    productline = db.Column(db.String(50))
    msrp = db.Column(db.Float)
    productcode = db.Column(db.String(50))
    customername = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    addressline1 = db.Column(db.String(200))
    addressline2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    postalcode = db.Column(db.String(20))
    country = db.Column(db.String(50))
    territory = db.Column(db.String(50))
    contactlastname = db.Column(db.String(50))
    contactfirstname = db.Column(db.String(50))
    dealsize = db.Column(db.String(20))
    numericcode = db.Column(db.String(20))
    msrp_issue = db.Column(db.Boolean)

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
            "ORDERNUMBER": venta.ordernumber,
            "QUANTITYORDERED": venta.quantityordered,
            "PRICEEACH": venta.priceeach,
            "ORDERLINENUMBER": venta.orderlinenumber,
            "SALES": venta.sales,
            "ORDERDATE": venta.orderdate,
            "STATUS": venta.status,
            "QTR_ID": venta.qtr_id,
            "MONTH_ID": venta.month_id,
            "YEAR_ID": venta.year_id,
            "PRODUCTLINE": venta.productline,
            "MSRP": venta.msrp,
            "PRODUCTCODE": venta.productcode,
            "CUSTOMERNAME": venta.customername,
            "PHONE": venta.phone,
            "ADDRESSLINE1": venta.addressline1,
            "ADDRESSLINE2": venta.addressline2,
            "CITY": venta.city,
            "STATE": venta.state,
            "POSTALCODE": venta.postalcode,
            "COUNTRY": venta.country,
            "TERRITORY": venta.territory,
            "CONTACTLASTNAME": venta.contactlastname,
            "CONTACTFIRSTNAME": venta.contactfirstname,
            "DEALSIZE": venta.dealsize,
            "NUMERICCODE": venta.numericcode,
            "MSRP_ISSUE": venta.msrp_issue
        })
    return jsonify({'error': 'ID_SALES no encontrado'}), 404


@app.route('/add-sale', methods=['POST'])
def add_sale():
    data = request.get_json()
    try:
        id_sales = int(data['ID_SALES'])
        if Venta.query.filter_by(id_sales=id_sales).first():
            return jsonify({'error': 'Ya existe una venta con ese ID_SALES'}), 400

        venta = Venta(
            id_sales = id_sales,
            ordernumber = data.get('ORDERNUMBER'),
            quantityordered = data.get('QUANTITYORDERED'),
            priceeach = data.get('PRICEEACH'),
            orderlinenumber = data.get('ORDERLINENUMBER'),
            sales = data.get('SALES'),
            orderdate = data.get('ORDERDATE'),
            status = data.get('STATUS'),
            qtr_id = data.get('QTR_ID'),
            month_id = data.get('MONTH_ID'),
            year_id = data.get('YEAR_ID'),
            productline = data.get('PRODUCTLINE'),
            msrp = data.get('MSRP'),
            productcode = data.get('PRODUCTCODE'),
            customername = data.get('CUSTOMERNAME'),
            phone = data.get('PHONE'),
            addressline1 = data.get('ADDRESSLINE1'),
            addressline2 = data.get('ADDRESSLINE2'),
            city = data.get('CITY'),
            state = data.get('STATE'),
            postalcode = data.get('POSTALCODE'),
            country = data.get('COUNTRY'),
            territory = data.get('TERRITORY'),
            contactlastname = data.get('CONTACTLASTNAME'),
            contactfirstname = data.get('CONTACTFIRSTNAME'),
            dealsize = data.get('DEALSIZE'),
            numericcode = data.get('NUMERICCODE'),
            msrp_issue = data.get('MSRP_ISSUE')
        )

        db.session.add(venta)
        db.session.commit()

        return jsonify({'message': 'Venta registrada correctamente'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# IMPORTAR JSON DESDE S3
@app.route('/import-from-s3', methods=['POST'])
def import_from_s3():
    bucket_name = "bucket-json-clear"
    json_key = "sales_data_dirty_20_errores.json"  

    try:
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket_name, Key=json_key)
        data = json.loads(response['Body'].read())
        registros_insertados = 0

        for item in data:
            id_sales = int(item['ID_SALES'])
            if Venta.query.filter_by(id_sales=id_sales).first():
                continue

            venta = Venta(
                id_sales = id_sales,
                ordernumber = item.get('ORDERNUMBER'),
                quantityordered = item.get('QUANTITYORDERED'),
                priceeach = item.get('PRICEEACH'),
                orderlinenumber = item.get('ORDERLINENUMBER'),
                sales = item.get('SALES'),
                orderdate = item.get('ORDERDATE'),
                status = item.get('STATUS'),
                qtr_id = item.get('QTR_ID'),
                month_id = item.get('MONTH_ID'),
                year_id = item.get('YEAR_ID'),
                productline = item.get('PRODUCTLINE'),
                msrp = item.get('MSRP'),
                productcode = item.get('PRODUCTCODE'),
                customername = item.get('CUSTOMERNAME'),
                phone = item.get('PHONE'),
                addressline1 = item.get('ADDRESSLINE1'),
                addressline2 = item.get('ADDRESSLINE2'),
                city = item.get('CITY'),
                state = item.get('STATE'),
                postalcode = item.get('POSTALCODE'),
                country = item.get('COUNTRY'),
                territory = item.get('TERRITORY'),
                contactlastname = item.get('CONTACTLASTNAME'),
                contactfirstname = item.get('CONTACTFIRSTNAME'),
                dealsize = item.get('DEALSIZE'),
                numericcode = item.get('NUMERICCODE'),
                msrp_issue = item.get('MSRP_ISSUE', False)
            )

            db.session.add(venta)
            registros_insertados += 1

        db.session.commit()
        return jsonify({'message': f'{registros_insertados} registros insertados desde S3'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# INICIAR APP
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
