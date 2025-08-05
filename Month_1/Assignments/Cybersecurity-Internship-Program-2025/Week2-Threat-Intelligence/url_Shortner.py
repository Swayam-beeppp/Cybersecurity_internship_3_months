from flask import Flask, request, redirect, render_template_string
import string, random

app = Flask(__name__)
url_mapping = {}

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        long_url = request.form['long_url']
        short_code = generate_short_code()
        url_mapping[short_code] = long_url
        return f"Shortened URL: http://localhost:5000/{short_code}"
    return '''
        <form method="POST">
            Long URL: <input name="long_url">
            <input type="submit">
        </form>
    '''

@app.route('/<short_code>')
def redirect_to_long_url(short_code):
    long_url = url_mapping.get(short_code)
    if long_url:
        return redirect(long_url)
    return "URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)
