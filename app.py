import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol or not shares:
            return apology("Symbol and shares are required")
        shares = int(shares)
        if shares < 1:
            return apology("Shares must be a positive integer")
        data = lookup(symbol)
        if not data:
            return apology("Symbol not found")
        user_balance = db.execute(
            "SELECT cash FROM users WHERE id = ?;", session["user_id"]
        )
        user_balance = user_balance[0]["cash"]
        total_price = data["price"] * shares
        if user_balance < total_price:
            return apology("Not enough balance")
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?;",
            user_balance - total_price,
            session["user_id"],
        )
        db.execute(
            """
            INSERT INTO transactions (user_id, symbol, price, shares)
            VALUES (?, ?, ?, ?);
            """,
            session["user_id"],
            symbol,
            data["price"],
            shares,
        )
        user_balance = db.execute(
            "SELECT cash FROM users WHERE id = ?;", session["user_id"]
        )[0]["cash"]
        return redirect("/")

    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("No symbol provided")
        data = lookup(symbol)
        price = usd(data["price"])
        return render_template("quoted.html", symbol=symbol, price=price)
    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("Username is required", 400)
        if not password:
            return apology("Password is required", 400)
        if not confirmation:
            return apology("Password confirmation is required", 400)
        if password != confirmation:
            return apology("Passwords don't match", 400)
        try:
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?);",
                username,
                generate_password_hash(password),
            )
            return redirect("/login")
        except ValueError:
            return apology("Username already exists", 400)

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
