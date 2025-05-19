from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime
from config import Config
from ai_service import AIRecommendationService

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db = SQLAlchemy(app)

# Existing Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

# Revenue model
class Revenue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

# Initialize AI Service
ai_service = AIRecommendationService()

# Create tables
with app.app_context():
    db.create_all()

@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from Flask with PostgreSQL!"})

# Existing message endpoints
@app.route('/api/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return jsonify([message.to_dict() for message in messages])

@app.route('/api/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Content is required"}), 400
    
    message = Message(content=data['content'])
    db.session.add(message)
    db.session.commit()
    return jsonify(message.to_dict()), 201

# Revenue endpoints
@app.route('/api/revenue', methods=['GET'])
def get_revenue():
    try:
        # Get query parameters for filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category = request.args.get('category')
        
        query = Revenue.query
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Revenue.date >= start_date)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Revenue.date <= end_date)
            
        if category:
            query = query.filter(Revenue.category == category)
            
        revenue_data = query.order_by(Revenue.date.desc()).all()
        return jsonify([item.to_dict() for item in revenue_data])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/revenue', methods=['POST'])
def add_revenue():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400
        
        # Create new revenue record
        revenue = Revenue(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            amount=float(data['amount']),
            category=data.get('category'),
            description=data.get('description')
        )
        
        db.session.add(revenue)
        db.session.commit()
        
        return jsonify(revenue.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/revenue/<int:id>', methods=['GET'])
def get_single_revenue(id):
    try:
        revenue = Revenue.query.get_or_404(id)
        return jsonify(revenue.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/revenue/<int:id>', methods=['PUT'])
def update_revenue(id):
    try:
        revenue = Revenue.query.get_or_404(id)
        data = request.get_json()
        
        if 'date' in data:
            revenue.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'amount' in data:
            revenue.amount = float(data['amount'])
        if 'category' in data:
            revenue.category = data['category']
        if 'description' in data:
            revenue.description = data['description']
            
        db.session.commit()
        return jsonify(revenue.to_dict())
    except ValueError as e:
        return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/revenue/<int:id>', methods=['DELETE'])
def delete_revenue(id):
    try:
        revenue = Revenue.query.get_or_404(id)
        db.session.delete(revenue)
        db.session.commit()
        return jsonify({"message": "Revenue record deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/revenue/categories', methods=['GET'])
def get_categories():
    try:
        categories = db.session.query(Revenue.category).distinct().all()
        # Filter out None values and flatten the list
        categories = [cat[0] for cat in categories if cat[0] is not None]
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# AI Recommendation Endpoints
@app.route('/api/ai/recommendations', methods=['GET'])
def get_ai_recommendations():
    try:
        # Get all revenue data
        revenue_data = Revenue.query.order_by(Revenue.date.asc()).all()
        
        # Convert to list of dicts
        revenue_list = [{
            'date': item.date.isoformat(),
            'amount': float(item.amount),
            'category': item.category,
            'description': item.description
        } for item in revenue_data]
        
        # Get AI analysis
        analysis = ai_service.analyze_revenue_trends(revenue_list)
        
        if analysis['status'] == 'error':
            return jsonify({
                'status': 'error',
                'message': analysis.get('message', 'AI analysis failed')
            }), 500
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/ai/marketing-ideas', methods=['GET'])
def get_marketing_ideas():
    try:
        business_type = request.args.get('business_type', 'e-commerce')
        target_audience = request.args.get('target_audience', 'general consumers')
        
        # Generate marketing ideas using AI
        prompt = f"Generate marketing ideas for a {business_type} business targeting {target_audience}. Focus on innovative strategies that can help grow the business and engage the target audience."
        
        ideas = ai_service.generate_text(prompt, max_length=500)
        
        return jsonify({
            'status': 'success',
            'marketing_ideas': ideas
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Revenue Dashboard Endpoints
@app.route('/api/dashboard/revenue-summary', methods=['GET'])
def get_revenue_summary():
    try:
        # Get monthly revenue summary
        result = db.session.execute(text("""
            SELECT 
                TO_CHAR(TO_DATE(month, 'YYYY-MM'), 'Mon YYYY') as month,
                subscription_revenue,
                product_revenue,
                total_revenue
            FROM revenue_summary
            ORDER BY TO_DATE(month, 'YYYY-MM')
        """))
        
        months = []
        subscription_data = []
        product_data = []
        total_data = []
        
        for row in result:
            months.append(row[0])
            subscription_data.append(float(row[1]))
            product_data.append(float(row[2]))
            total_data.append(float(row[3]))
            
        return jsonify({
            'months': months,
            'subscription_revenue': subscription_data,
            'product_revenue': product_data,
            'total_revenue': total_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/revenue-by-country', methods=['GET'])
def get_revenue_by_country():
    try:
        result = db.session.execute(text("""
            SELECT 
                c.country,
                COALESCE(SUM(p.amount), 0) as total_revenue,
                COUNT(DISTINCT c.id) as customer_count
            FROM customers c
            LEFT JOIN payments p ON c.id = p.customer_id
            GROUP BY c.country
            ORDER BY total_revenue DESC
            LIMIT 10
        """))
        
        countries = []
        revenue = []
        customer_counts = []
        
        for row in result:
            countries.append(row[0])
            revenue.append(float(row[1]) if row[1] else 0)
            customer_counts.append(int(row[2]))
            
        return jsonify({
            'countries': countries,
            'revenue': revenue,
            'customer_counts': customer_counts
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/recent-transactions', methods=['GET'])
def get_recent_transactions():
    try:
        result = db.session.execute(text("""
            SELECT 
                c.name as customer_name,
                p.amount,
                p.payment_date,
                p.payment_method,
                string_agg(ps.sale_date::text, ', ') as product_dates
            FROM payments p
            JOIN customers c ON p.customer_id = c.id
            LEFT JOIN product_sales ps ON p.customer_id = ps.customer_id 
                AND DATE(p.payment_date) = DATE(ps.sale_date)
            GROUP BY c.name, p.amount, p.payment_date, p.payment_method
            ORDER BY p.payment_date DESC
            LIMIT 10
        """))
        
        transactions = []
        for row in result:
            transactions.append({
                'customer': row[0],
                'amount': float(row[1]) if row[1] else 0,
                'date': row[2].strftime('%Y-%m-%d') if row[2] else None,
                'payment_method': row[3],
                'has_product_sale': bool(row[4])
            })
            
        return jsonify(transactions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/plan-distribution', methods=['GET'])
def get_plan_distribution():
    try:
        result = db.session.execute(text("""
            SELECT 
                p.name as plan_name,
                COUNT(s.id) as subscriber_count,
                SUM(CASE 
                    WHEN s.is_active THEN 1 
                    ELSE 0 
                END) as active_subscribers
            FROM plans p
            LEFT JOIN subscriptions s ON p.id = s.plan_id
            GROUP BY p.name
            ORDER BY subscriber_count DESC
        """))
        
        plans = []
        subscribers = []
        active_subscribers = []
        
        for row in result:
            plans.append(row[0])
            subscribers.append(int(row[1]))
            active_subscribers.append(int(row[2]))
            
        return jsonify({
            'plans': plans,
            'subscribers': subscribers,
            'active_subscribers': active_subscribers
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
