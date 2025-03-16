from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from AIFinBot import AIFinBot
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes
bot = AIFinBot()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/log_expense', methods=['POST'])
def log_expense():
    try:
        data = request.json
        if not data or 'category' not in data or 'amount' not in data:
            return jsonify({"error": "Missing category or amount"}), 400
        
        if not isinstance(data['amount'], (int, float)) or float(data['amount']) <= 0:
            return jsonify({"error": "Invalid amount"}), 400
        
        bot.log_expense(data['category'], data['amount'])
        return jsonify({"message": "Expense logged successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_summary')
def get_summary():
    try:
        summary = []
        for category, budget in bot.budgets.items():
            spent = sum(e["amount"] for e in bot.expenses if e["category"] == category)
            summary.append({
                "category": category,
                "spent": spent,
                "budget": budget,
                "remaining": budget - spent,
                "percentage": (spent / budget * 100) if budget > 0 else 0
            })
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_plot')
def get_plot():
    try:
        if not bot.expenses:
            return jsonify({"error": "No expenses to plot"}), 400
            
        bot.plot_spending()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        plt.close()  # Close the figure to free memory
        buf.seek(0)
        return jsonify({
            "image": base64.b64encode(buf.read()).decode('utf-8'),
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_recommendations')
def get_recommendations():
    try:
        recommendations = bot.generate_recommendations()
        return jsonify({
            "recommendations": recommendations,
            "health_score": bot.financial_health_check()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_budget', methods=['POST'])
def add_budget():
    try:
        data = request.json
        if not data or 'category' not in data or 'budget' not in data:
            return jsonify({"error": "Missing category or budget"}), 400
        
        if not isinstance(data['budget'], (int, float)) or float(data['budget']) <= 0:
            return jsonify({"error": "Invalid budget amount"}), 400
        
        bot.budgets[data['category']] = float(data['budget'])
        return jsonify({"message": f"Budget added for {data['category']}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_health_check')
def get_health_check():
    try:
        score = bot.financial_health_check()
        return jsonify({
            "score": score,
            "status": "Excellent" if score > 75 else "Good" if score > 50 else "Needs Attention"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server...")
    try:
        port = 8000
        app.run(host='localhost', port=port, debug=True)
        print(f"Server is running on http://localhost:{port}")
    except Exception as e:
        print(f"Error starting server: {e}")
