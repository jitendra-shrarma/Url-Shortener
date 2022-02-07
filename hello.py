from flask import Flask, render_template, request, redirect
from flask import url_for, flash, abort, session, jsonify
from werkzeug.utils import secure_filename
import json
import os.path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['BASE_DIR'] = os.path.dirname(os.path.abspath(__file__)) + "\\"
app.config['STATIC'] = app.config['BASE_DIR'] + "static\\"
app.config['USER_FILES'] = app.config['STATIC'] + "user_files\\"


@app.route('/')
def home():
    """render home.html page"""
    return render_template('home.html', codes=session.keys())


@app.route('/your-url', methods=['GET', 'POST'])
def yourUrl():
    """render your_url.html page"""
    if request.method == 'POST':

        # empty urls dictionary
        urls = {}

        # if urls.json file exists in system, load it
        if os.path.exists('urls.json'):
            with open('urls.json') as urls_file:
                urls = json.load(urls_file)

        # if request.form['code'] is already used for another url, redirect to home page
        if request.form['code'] in urls.keys():
            flash('This short name has already been taken, user another name.')
            return redirect(url_for('home'))

        # 'url' is sent in request form
        if 'url' in request.form.keys():
            # map request.form['code'] : { 'url' : request.form['url']}
            urls[request.form['code']] = {'url':request.form['url']}
        else:
            # get file from request.files['file']
            file = request.files['file']
            # modify it's full_name with code
            full_name = request.form['code'] + secure_filename(file.filename)
            # save the file with new_name
            file.save(app.config['USER_FILES']+full_name)
            # map request.form['code'] : { 'file' : full_name}
            urls[request.form['code']] = {'file':full_name}

        # dump new url data into urls.json
        with open('urls.json', 'w') as url_file:
            json.dump(urls, url_file)
            session[request.form['code']] = True
        return render_template('your_url.html', code=request.form['code'])
    else:
        return redirect(url_for('home'))


@app.route('/<string:code>')
def redirectToURL(code):
    # if urls.json file exists in system, load it
    if os.path.exists('urls.json'):
        with open('urls.json') as urls_file:
            urls = json.load(urls_file)
            # if request code is saved
            if code in urls.keys():
                # code for url, redirect url
                if 'url' in urls[code].keys():
                    print(urls[code]['url'])
                    return redirect(urls[code]['url'])
                # code for file, redirect file
                else:
                    return redirect(url_for('static', filename='user_files/'+urls[code]['file']))
    return abort(404)


@app.errorhandler(404)
def pageNotFound(error):
    """custom errorhandler to render 404 error to page_not_found.html"""
    return render_template('page_not_found.html'), 404


@app.route('/api')
def sessionAPI():
    """returns all the session keys"""
    return jsonify(list(session.keys()))


if __name__ == '__main__':
    app.run(debug=True)
