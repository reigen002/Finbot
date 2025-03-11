import json
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np

class AIFinBot:
    def __init__(self):
        self.budgets = {"groceries": 300, "entertainment": 100}  # Default budgets
        self.expenses = []  # List of {"category": "groceries", "amount": 50}
        self.debts = []  # Format: {"name": "credit card", "balance": 5000, "apr": 18}
        self.income = 0  # Monthly income
        self.load_data()  # Load saved data
        self.add_ai_features()  # Initialize AI components

    def add_ai_features(self):
        """Initialize AI components"""
        self.spending_categories = list(self.budgets.keys())

    def log_expense(self, category, amount):
        """Log an expense and check budget"""
        if category not in self.budgets:
            print(f"⚠️ Category '{category}' not found. Use 'add [category] [budget]' to create it.")
            return

        self.expenses.append({"category": category, "amount": float(amount)})
        spent = sum(e["amount"] for e in self.expenses if e["category"] == category)
        remaining = self.budgets[category] - spent

        if remaining < 0:
            print(f"⚠️ Overspent on {category}! Exceeded by ${abs(remaining):.2f}.")
        else:
            print(f"✅ Logged ${float(amount):.2f} for {category}. Remaining: ${remaining:.2f}")

    def show_summary(self):
        """Show a summary of spending vs budgets"""
        print("\n--- Monthly Summary ---")
        for category, budget in self.budgets.items():
            spent = sum(e["amount"] for e in self.expenses if e["category"] == category)
            print(f"{category}: ${spent:.2f} / ${budget} | Remaining: ${(budget - spent):.2f}")

    def plot_spending(self):
        """Visualize spending using a bar chart"""
        if not self.expenses:
            print("❌ No expenses to plot!")
            return

        categories = list(self.budgets.keys())
        spent = [sum(e["amount"] for e in self.expenses if e["category"] == cat) for cat in categories]

        plt.figure(figsize=(10, 5))
        plt.bar(categories, spent)
        plt.title("Spending by Category")
        plt.ylabel("Amount ($)")
        plt.show()

    def analyze_spending_patterns(self):
        """Cluster expenses to find spending patterns"""
        if len(self.expenses) < 3:
            return None

        # Convert expenses to features (amount, category index)
        X = []
        category_map = {cat: idx for idx, cat in enumerate(self.spending_categories)}
        for expense in self.expenses:
            X.append([expense["amount"], category_map[expense["category"]]])

        kmeans = KMeans(n_clusters=2)
        kmeans.fit(X)
        return kmeans.cluster_centers_

    def generate_recommendations(self):
        """Generate personalized financial advice"""
        recommendations = []

        # Spending analysis
        category_spending = {cat: 0 for cat in self.budgets}
        for expense in self.expenses:
            category_spending[expense["category"]] += expense["amount"]

        # Recommendation 1: Overspending alerts
        for cat, budget in self.budgets.items():
            spent = category_spending.get(cat, 0)
            if spent > budget:
                recommendations.append(
                    f"Reduce {cat} spending by ${spent - budget:.2f} to stay within budget"
                )

        # Recommendation 2: Savings potential
        total_spent = sum(category_spending.values())
        if self.income > 0:
            savings_rate = (self.income - total_spent) / self.income
            if savings_rate < 0.2:
                recommendations.append(
                    f"Increase savings rate (current: {savings_rate:.0%}). Aim for 20%!"
                )

        # Recommendation 3: Debt payoff strategy
        if self.debts:
            highest_apr_debt = max(self.debts, key=lambda x: x["apr"])
            recommendations.append(
                f"Prioritize paying off {highest_apr_debt['name']} (APR: {highest_apr_debt['apr']}%) first"
            )

        return recommendations if recommendations else ["Great job! Your finances look healthy."]

    def debt_payoff_plan(self, method="avalanche"):
        """Optimize debt payoff strategy"""
        if method == "avalanche":
            sorted_debts = sorted(self.debts, key=lambda x: -x["apr"])
        else:  # snowball
            sorted_debts = sorted(self.debts, key=lambda x: x["balance"])

        plan = []
        for debt in sorted_debts:
            plan.append({
                "name": debt["name"],
                "action": f"Pay minimum + extra to {debt['name']} first"
            })
        return plan

    def financial_health_check(self):
        """Calculate financial health score"""
        if self.income == 0:
            return 0

        # Simple scoring formula (0-100)
        debt_ratio = sum(d["balance"] for d in self.debts) / self.income
        savings_ratio = (self.income - sum(e["amount"] for e in self.expenses)) / self.income

        score = min(100, max(0,
            50 * (1 - debt_ratio) +
            50 * savings_ratio
        ))
        return round(score)

    def ask_ai(self, question):
        """Basic NLP financial Q&A"""
        keywords = {
            "save": "Consider automating savings and reducing discretionary spending",
            "invest": "Start with low-cost index funds. Aim to invest 15% of income",
            "debt": "Focus on high-interest debt first. Consider balance transfers",
            "budget": "Try the 50/30/20 rule: Needs(50%), Wants(30%), Savings(20%)"
        }

        for kw, response in keywords.items():
            if kw in question.lower():
                return response
        return "I recommend reviewing your spending patterns and setting clear financial goals"

    def save_data(self, filename="finbot_data.json"):
        """Save budgets, expenses, debts, and income to a file"""
        data = {
            "budgets": self.budgets,
            "expenses": self.expenses,
            "debts": self.debts,
            "income": self.income
        }
        with open(filename, "w") as f:
            json.dump(data, f)
        print(f"✅ Data saved to {filename}")

    def load_data(self, filename="finbot_data.json"):
        """Load budgets, expenses, debts, and income from a file"""
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.budgets = data.get("budgets", self.budgets)
                self.expenses = data.get("expenses", [])
                self.debts = data.get("debts", [])
                self.income = data.get("income", 0)
            print(f"✅ Loaded data from {filename}")
        except FileNotFoundError:
            print("ℹ️  No existing data found. Starting fresh!")
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")

    def run_cli(self):
        """Run the command-line interface"""
        print("""\n💡 AI Financial Assistant - Smart Money Management
Commands:
  log [category] [amount]  - Record expense
  summary                  - Show budget status
  plot                     - Visualize spending
  add [category] [budget]  - Create new category
  set income [amount]      - Set monthly income
  add debt [name] [balance] [apr] - Add debt
  recommend                - Get personalized advice
  health                   - Check financial health
  plan debt [method]       - Debt payoff plan (avalanche/snowball)
  ask [question]           - Get financial advice
  save                     - Save progress
  load                     - Load previous data
  quit                     - Exit\n""")

        while True:
            command = input("\n> ").strip().lower()

            if command == "quit":
                self.save_data()
                print("Goodbye! 👋")
                break
            elif command == "summary":
                self.show_summary()
            elif command == "plot":
                self.plot_spending()
            elif command.startswith("log "):
                try:
                    _, category, amount = command.split()
                    self.log_expense(category, amount)
                except:
                    print("❌ Use: log [category] [amount]")
            elif command.startswith("add "):
                try:
                    _, category, budget = command.split()
                    self.budgets[category] = float(budget)
                    print(f"✅ Added category: {category} (Budget: ${float(budget):.2f})")
                except:
                    print("❌ Use: add [category] [budget]")
            elif command.startswith("set income "):
                try:
                    self.income = float(command.split()[-1])
                    print(f"✅ Monthly income set to ${self.income:.2f}")
                except:
                    print("❌ Invalid amount")
            elif command.startswith("add debt "):
                try:
                    _, _, name, balance, apr = command.split()
                    self.debts.append({
                        "name": name,
                        "balance": float(balance),
                        "apr": float(apr)
                    })
                    print(f"✅ Added debt: {name} (${balance} @ {apr}%)")
                except:
                    print("❌ Use: add debt [name] [balance] [apr]")
            elif command == "recommend":
                print("\n🤖 AI Recommendations:")
                for i, rec in enumerate(self.generate_recommendations(), 1):
                    print(f"{i}. {rec}")
            elif command.startswith("plan debt "):
                method = command.split()[-1]
                if method not in ["avalanche", "snowball"]:
                    print("❌ Use: plan debt [avalanche/snowball]")
                else:
                    print("\n🔗 Debt Payoff Strategy:")
                    for step in self.debt_payoff_plan(method):
                        print(f"- {step['action']}")
            elif command == "health":
                score = self.financial_health_check()
                print(f"\n🏥 Financial Health Score: {score}/100")
                print("💡 Interpretation:")
                if score > 75:
                    print("Excellent financial health! Maintain good habits")
                elif score > 50:
                    print("Good foundation, room for improvement")
                else:
                    print("Needs attention - focus on debt reduction and savings")
            elif command.startswith("ask "):
                question = command[4:]
                print(f"\n💬 AI Response: {self.ask_ai(question)}")
            elif command == "save":
                self.save_data()
            elif command == "load":
                self.load_data()
            else:
                print("❌ Unknown command. Type 'help' for options")

if __name__ == "__main__":
    bot = AIFinBot()
    bot.run_cli()