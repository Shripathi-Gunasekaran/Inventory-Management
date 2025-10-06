"""
Flask Inventory Management Application
This is a reference implementation using Flask and MySQL
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:aaaa@localhost/inventory_manage'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'description': self.description
        }

class Location(db.Model):
    __tablename__ = 'location'
    location_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)

    def to_dict(self):
        return {
            'location_id': self.location_id,
            'name': self.name,
            'address': self.address
        }

class ProductMovement(db.Model):
    __tablename__ = 'product_movement'
    movement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'movement_id': self.movement_id,
            'timestamp': self.timestamp.isoformat(),
            'from_location': self.from_location,
            'to_location': self.to_location,
            'product_id': self.product_id,
            'qty': self.qty
        }

# Routes

# Home
@app.route('/')
def index():
    return render_template('index.html')

# Product Routes
@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product = Product(
            product_id=request.form['product_id'],
            name=request.form['name'],
            description=request.form.get('description', '')
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('add_product.html')

@app.route('/products/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form.get('description', '')
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))

# Location Routes
@app.route('/locations')
def locations():
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location = Location(
            location_id=request.form['location_id'],
            name=request.form['name'],
            address=request.form.get('address', '')
        )
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('locations'))
    return render_template('add_location.html')

@app.route('/locations/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    if request.method == 'POST':
        location.name = request.form['name']
        location.address = request.form.get('address', '')
        db.session.commit()
        return redirect(url_for('locations'))
    return render_template('edit_location.html', location=location)

@app.route('/locations/delete/<location_id>')
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    return redirect(url_for('locations'))

# Movement Routes
@app.route('/movements')
def movements():
    movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movements.html', movements=movements)

@app.route('/movements/add', methods=['GET', 'POST'])
def add_movement():
    if request.method == 'POST':
        movement = ProductMovement(
            product_id=request.form['product_id'],
            from_location=request.form.get('from_location') or None,
            to_location=request.form.get('to_location') or None,
            qty=int(request.form['qty'])
        )
        db.session.add(movement)
        db.session.commit()
        return redirect(url_for('movements'))
    
    products = Product.query.all()
    locations = Location.query.all()
    return render_template('add_movement.html', products=products, locations=locations)

# Report Route
@app.route('/report')
def report():
    # Calculate stock balance
    movements = ProductMovement.query.all()
    stock_balance = {}
    
    for movement in movements:
        key = f"{movement.product_id}|{movement.to_location or 'OUT'}"
        
        if movement.to_location:
            if key not in stock_balance:
                stock_balance[key] = 0
            stock_balance[key] += movement.qty
        
        if movement.from_location:
            from_key = f"{movement.product_id}|{movement.from_location}"
            if from_key not in stock_balance:
                stock_balance[from_key] = 0
            stock_balance[from_key] -= movement.qty
    
    # Build report data
    report_data = []
    for key, quantity in stock_balance.items():
        if quantity > 0:
            product_id, location_id = key.split('|')
            if location_id != 'OUT':
                product = Product.query.get(product_id)
                location = Location.query.get(location_id)
                if product and location:
                    report_data.append({
                        'product': product.name,
                        'location': location.name,
                        'quantity': quantity
                    })
    
    report_data.sort(key=lambda x: (x['product'], x['location']))
    return render_template('report.html', report_data=report_data)

# API endpoints (optional - for AJAX)
@app.route('/api/products', methods=['GET', 'POST'])
def api_products():
    if request.method == 'POST':
        data = request.json
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return jsonify(product.to_dict()), 201
    
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/locations', methods=['GET', 'POST'])
def api_locations():
    if request.method == 'POST':
        data = request.json
        location = Location(**data)
        db.session.add(location)
        db.session.commit()
        return jsonify(location.to_dict()), 201
    
    locations = Location.query.all()
    return jsonify([l.to_dict() for l in locations])

@app.route('/api/movements', methods=['GET', 'POST'])
def api_movements():
    if request.method == 'POST':
        data = request.json
        movement = ProductMovement(**data)
        db.session.add(movement)
        db.session.commit()
        return jsonify(movement.to_dict()), 201
    
    movements = ProductMovement.query.all()
    return jsonify([m.to_dict() for m in movements])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
