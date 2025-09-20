from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/stats')
def stats():
    return render_template("stats.html")

@app.route('/explore')
def explore():
    return render_template("explore.html")

@app.route('/article')
def article():
    return render_template("article.html")

if __name__ == '__main__':
    app.run(debug=True)
