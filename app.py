from flask import Flask, render_template, request
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import os


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'file' in request.files:
        file = request.files['file']
        if file:
            upload_folder = 'uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            for existing_file in os.listdir(upload_folder):
                file_path = os.path.join(upload_folder, existing_file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            file.save(os.path.join(upload_folder, file.filename))

            full_path = os.path.abspath(os.path.join(upload_folder, file.filename))
            return render_template('index.html', full_path=full_path)
    return render_template('about.html')


@app.route('/second', methods=['POST'])
def button():
    a = request.form["data_one"]
    b = request.form['data_two']
    adress = request.form.get('file_adress')

    if not adress or not os.path.exists(adress):
        return render_template('about.html')

    a = datetime.strptime(a, '%Y-%m-%d')
    b = datetime.strptime(b, '%Y-%m-%d')

    if a>b:
        return render_template('about.html', mistake='Неправильный диапазон дат')

    a = datetime.strftime(a, '%d.%m.%Y')
    b = datetime.strftime(b, '%d.%m.%Y')


    y1, y2, x = anym(a, b, adress)

    if not x:
        return render_template('about.html', mistake='Нет данных для посторения.')

    x = np.array(x)
    y1 = np.array(y1)
    y2 = np.array(y2)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f'picture_{timestamp}.png'
    plot_path = f'static/{plot_filename}'

    for old_plot in os.listdir('static'):
        if old_plot.startswith('picture_') and old_plot.endswith('.png'):
            os.remove(os.path.join('static', old_plot))

    plt.plot(x, y1, x, y2)
    plt.xticks(x, rotation=45)
    plt.yticks(np.arange(100, 1000, 100))
    plt.xlabel('Дата')
    plt.ylabel('Температура')
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.savefig(plot_path)
    plt.close()

    return render_template('base.html', plot_url=f'/static/{plot_filename}')


def anym(a, b, adress):
    rad1, rad2, rad3 = [], [], []

    with open(adress, 'r', encoding='utf-8') as my_file:
        lines = my_file.readlines()
        if not lines:
            return [], [], []

        first_date_in_file = lines[0][:10]
        last_date_in_file = lines[-1][:10]

    a_date = datetime.strptime(a, '%d.%m.%Y')
    b_date = datetime.strptime(b, '%d.%m.%Y')
    first_date = datetime.strptime(first_date_in_file, '%d.%m.%Y')
    last_date = datetime.strptime(last_date_in_file, '%d.%m.%Y')


    if a_date < first_date:
        a_date = first_date
    if b_date > last_date:
        b_date = last_date

    a = a_date.strftime('%d.%m.%Y')
    b = b_date.strftime('%d.%m.%Y')

    with open(adress, 'r', encoding='utf-8') as my_file:
        for line in my_file.readlines():
            if a in line[:10]:
                rad1.append(int(line[12:15]))
                rad2.append(int(line[17:20]))
                rad3.append(line[:10])
                a = datetime.strptime(a, '%d.%m.%Y')
                a += timedelta(days=1)
                a = datetime.strftime(a, '%d.%m.%Y')
                date1 = datetime.strptime(a, '%d.%m.%Y')
                date2 = datetime.strptime(b, '%d.%m.%Y')
                if date1 > date2:
                    break

    return rad1, rad2, rad3


if __name__ == '__main__':
    app.run(debug=True)



