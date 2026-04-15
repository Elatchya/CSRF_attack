from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret"

# dummy user
users = {
    "user": {"password": "1234"}
}

@app.route('/')
def home():
    if 'user' in session:
        return render_template('home.html', user=session['user'])
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        if u in users and users[u]['password'] == p:
            session['user'] = u
            return redirect('/')
        else:
            return render_template('invalid.html')

    return render_template('login.html')

@app.route('/change-password-page')
def change_page():
    if 'user' in session:
        return render_template('change_password.html')
    return redirect('/login')

@app.route('/change-password', methods=['POST'])
def change_password():
    if 'user' in session:
        new_pass = request.form['new_password']
        users[session['user']]['password'] = new_pass
        print("⚠️ Password changed (CSRF possible)")
        return render_template('success.html')
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)