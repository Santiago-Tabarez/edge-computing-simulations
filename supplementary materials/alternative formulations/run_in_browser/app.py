import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'change-this-to-a-random-secret'

YAML_FILE   = 'config.yaml'
CONFIG_FILE = 'config.py'

@app.route('/', methods=['GET', 'POST'])
def edit_files():
    # ensure both exist
    for fn in (YAML_FILE, CONFIG_FILE):
        if not os.path.exists(fn):
            open(fn, 'w').close()

    if request.method == 'POST':
        # RAW overwrite of config.yaml
        new_yaml = request.form.get('yaml_content', '')
        with open(YAML_FILE, 'w', newline='') as f:
            f.write(new_yaml)

        # RAW overwrite of config.py
        new_config = request.form.get('config_content', '')
        with open(CONFIG_FILE, 'w', newline='') as f:
            f.write(new_config)

        flash('Files saved verbatim.', 'success')
        return redirect(url_for('edit_files'))

    # on GET, load them verbatim
    with open(YAML_FILE, 'r')   as f: yaml_content   = f.read()
    with open(CONFIG_FILE, 'r') as f: config_content = f.read()

    return render_template('editor.html',
                           yaml_content=yaml_content,
                           config_content=config_content)

if __name__ == '__main__':
    app.run(debug=True)
