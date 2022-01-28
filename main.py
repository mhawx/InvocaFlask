<<<<<<< HEAD
from dataclasses import dataclass
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import engine
import datetime
from invoca_google import googlesheet
import os
from dotenv import load_dotenv

app = Flask(__name__)

app.secret_key = 'CRUD Table for Invoca'

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqldb://root:" + os.getenv('PASSWORD') + "@" + os.getenv(
    'PUBLIC_IP_ADDRESS') + "/" + os.getenv('DBNAME') + "?unix_socket=/cloudsql/" + os.getenv(
    'PROJECT_ID') + ":" + os.getenv('INSTANCE_NAME')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

db2 = engine.create_engine(
    f"mysql+mysqldb://root:" + os.getenv('PASSWORD') + "@" + os.getenv('PUBLIC_IP_ADDRESS') + "/" + os.getenv(
        'DBNAME') + "?unix_socket=/cloudsql/" + os.getenv('PROJECT_ID') + ":" + os.getenv('INSTANCE_NAME'))


@dataclass
class Invoca_Campaigns(db.Model):
    __tablename__ = "INVOCA_CAMPAIGNS"
    id: int = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    url: str = db.Column(db.String(250), nullable=False)
    destination: str = db.Column(db.String(15), nullable=False)
    forward: str = db.Column(db.String(15), nullable=False)
    utm_campaign: str = db.Column(db.String(150), nullable=False)
    utm_source: str = db.Column(db.String(75), nullable=False)
    utm_medium: str = db.Column(db.String(75), nullable=False)
    agency: str = db.Column(db.String(100), nullable=False)
    dcreated: datetime = db.Column(db.DateTime, default=datetime.date.today())
    test_url: str = db.Column(db.String(500),
                              default=url + '?utm_campaign=' + utm_campaign + '&utm_medium=' + utm_medium + '&utm_source=' + utm_source)

    def __init__(self, url, destination, forward, utm_campaign, utm_source, utm_medium, agency):
        self.url = url
        self.destination = destination
        self.forward = forward
        self.utm_campaign = utm_campaign
        self.utm_medium = utm_medium
        self.utm_source = utm_source
        self.agency = agency


@app.route('/')
def Index():
    invdata = Invoca_Campaigns.query
    return render_template('index.html', title='Invoca Pooling Campaigns',
                           invdata=invdata)


@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        url = request.form['url']
        destination = request.form['destination']
        forward = request.form['forward']
        utm_campaign = request.form['utm_campaign']
        utm_source = request.form['utm_source']
        utm_medium = request.form['utm_medium']
        agency = request.form['agency']

        form_data = Invoca_Campaigns(url, destination, forward, utm_campaign, utm_source, utm_medium, agency)
        db.session.add(form_data)
        db.session.commit()

        flash("Campaign added!")
        return redirect(url_for('Index'))


@app.route('/update/', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        inv_data = Invoca_Campaigns.query.get(request.form.get('id'))

        inv_data.url = request.form['url']
        inv_data.destination = request.form['destination']
        inv_data.forward = request.form['forward']
        inv_data.utm_campaign = request.form['utm_campaign']
        inv_data.utm_medium = request.form['utm_medium']
        inv_data.utm_source = request.form['utm_source']
        inv_data.agency = request.form['agency']

        db.session.commit()
        flash("Campaign Updated")

        return redirect(url_for('Index'))


@app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    inv_data = Invoca_Campaigns.query.get(id)

    db.session.delete(inv_data)
    db.session.commit()
    flash("Campaign Deleted")

    return redirect(url_for('Index'))


@app.route('/bulkupload')
def bulkadd():
    dbrun = db2.connect()

    df = pd.read_json('C:/Users/dmeyerjr/PycharmProjects/FlaskCrud/static/invoca_json_20220121.json')
    df = df.drop_duplicates()

    df['dcreated'] = datetime.date.today()
    df['test_url'] = df['url'] + '?utm_campaign=' + df['utm_campaign'] + '&utm_medium=' + df[
        'utm_medium'] + '&utm_source=' + df['utm_source']

    df.to_sql('INVOCA_CAMPAIGNS', dbrun, if_exists='append', index=False)

    flash("Bulk Upload from Invoca JSON Complete")
    return redirect(url_for('Index'))


@app.route('/newcampaign')
def newcamp():
    dbrun = db2.connect()

    new_camp = pd.read_excel(
        'https://docs.google.com/spreadsheets/d/e/2PACX-1vTZETwlh3UhjRBoarnmuCUZYH-kfbfnjr6p6JfcT6bObDIqpcvJcrY9E84PxVUPa2vM0YgiyVjoFCsa/pub?output=xlsx')

    df2 = pd.DataFrame(googlesheet(new_camp))
    df2 = df2.drop_duplicates()

    df2['dcreated'] = datetime.date.today()
    df2['test_url'] = df2['url'] + '?utm_campaign=' + df2['utm_campaign'] + '&utm_medium=' + df2[
        'utm_medium'] + '&utm_source=' + df2['utm_source']

    df2.to_sql('INVOCA_CAMPAIGNS', dbrun, if_exists='append', index=False)

    flash('New Campaigns Bulk Added')

    return redirect(url_for('Index'))


@app.route('/hmicampaign')
def hmicamp():
    dbrun = db2.connect()

    new_camp = pd.read_excel(
        'https://docs.google.com/spreadsheets/d/e/2PACX-1vTBKuULCG-38_jXLmxKcZE8ERmWa6es-Bv9HmiB1cpniKwqz-t60-dbJ53PKOtxBF0IV2ZbXhRSim7S/pub?output=xlsx')
    fcamp = new_camp[['Final URL', '&utm_campaign=', '&utm_medium=', 'utm_source=', 'Destination #', 'Forwarding #']]

    fcamp = fcamp.rename(columns={'Final URL': 'url', '&utm_campaign=': 'utm_campaign', '&utm_medium=': 'utm_medium',
                                  'utm_source=': 'utm_source', 'Destination #': 'destination',
                                  'Forwarding #': 'forward'})

    fcamp = fcamp.drop_duplicates()

    fcamp = fcamp.dropna()

    fcamp['agency'] = 'horizon'
    fcamp['dcreated'] = datetime.date.today()
    fcamp['test_url'] = fcamp['url'] + '?utm_campaign=' + fcamp['utm_campaign'] + '&utm_medium=' + fcamp[
        'utm_medium'] + '&utm_source=' + fcamp['utm_source']

    fcamp.to_sql('INVOCA_CAMPAIGNS', dbrun, if_exists='append', index=False)

    flash('Horizon Campaigns Bulk Added')

    return redirect(url_for('Index'))


@app.route('/makejson', methods=['GET'])
def makejson():
    inv_data = db.session.query(
        Invoca_Campaigns.url,
        Invoca_Campaigns.destination,
        Invoca_Campaigns.forward,
        Invoca_Campaigns.utm_campaign,
        Invoca_Campaigns.utm_medium,
        Invoca_Campaigns.utm_source,
        Invoca_Campaigns.agency
    ).all()

    out = []

    for row in inv_data:
        out.append(dict(row))

    return jsonify(out)


if __name__ == "__main__":
    app.run(debug=True)
=======
from dataclasses import dataclass
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import engine
import datetime
from invoca_google import googlesheet
import os
from dotenv import load_dotenv

app = Flask(__name__)

app.secret_key = 'CRUD Table for Invoca'

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqldb://root:" + os.getenv('PASSWORD') + "@" + os.getenv(
    'PUBLIC_IP_ADDRESS') + "/" + os.getenv('DBNAME') + "?unix_socket=/cloudsql/" + os.getenv(
    'PROJECT_ID') + ":" + os.getenv('INSTANCE_NAME')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

db2 = engine.create_engine(
    f"mysql+mysqldb://root:" + os.getenv('PASSWORD') + "@" + os.getenv('PUBLIC_IP_ADDRESS') + "/" + os.getenv(
        'DBNAME') + "?unix_socket=/cloudsql/" + os.getenv('PROJECT_ID') + ":" + os.getenv('INSTANCE_NAME'))


@dataclass
class Invoca_Campaigns(db.Model):
    __tablename__ = "INVOCA_CAMPAIGNS"
    id: int = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    url: str = db.Column(db.String(250), nullable=False)
    destination: str = db.Column(db.String(15), nullable=False)
    forward: str = db.Column(db.String(15), nullable=False)
    utm_campaign: str = db.Column(db.String(150), nullable=False)
    utm_source: str = db.Column(db.String(75), nullable=False)
    utm_medium: str = db.Column(db.String(75), nullable=False)
    agency: str = db.Column(db.String(100), nullable=False)
    dcreated: datetime = db.Column(db.DateTime, default=datetime.date.today())
    test_url: str = db.Column(db.String(500),
                              default=url + '?utm_campaign=' + utm_campaign + '&utm_medium=' + utm_medium + '&utm_source=' + utm_source)

    def __init__(self, url, destination, forward, utm_campaign, utm_source, utm_medium, agency):
        self.url = url
        self.destination = destination
        self.forward = forward
        self.utm_campaign = utm_campaign
        self.utm_medium = utm_medium
        self.utm_source = utm_source
        self.agency = agency


@app.route('/')
def Index():
    invdata = Invoca_Campaigns.query
    return render_template('index.html', title='Invoca Pooling Campaigns',
                           invdata=invdata)


@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        url = request.form['url']
        destination = request.form['destination']
        forward = request.form['forward']
        utm_campaign = request.form['utm_campaign']
        utm_source = request.form['utm_source']
        utm_medium = request.form['utm_medium']
        agency = request.form['agency']

        form_data = Invoca_Campaigns(url, destination, forward, utm_campaign, utm_source, utm_medium, agency)
        db.session.add(form_data)
        db.session.commit()

        flash("Campaign added!")
        return redirect(url_for('Index'))


@app.route('/update/', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        inv_data = Invoca_Campaigns.query.get(request.form.get('id'))

        inv_data.url = request.form['url']
        inv_data.destination = request.form['destination']
        inv_data.forward = request.form['forward']
        inv_data.utm_campaign = request.form['utm_campaign']
        inv_data.utm_medium = request.form['utm_medium']
        inv_data.utm_source = request.form['utm_source']
        inv_data.agency = request.form['agency']

        db.session.commit()
        flash("Campaign Updated")

        return redirect(url_for('Index'))


@app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    inv_data = Invoca_Campaigns.query.get(id)

    db.session.delete(inv_data)
    db.session.commit()
    flash("Campaign Deleted")

    return redirect(url_for('Index'))


@app.route('/bulkupload')
def bulkadd():
    dbrun = db2.connect()

    df = pd.read_json('C:/Users/dmeyerjr/PycharmProjects/FlaskCrud/static/invoca_json_20220121.json')
    df = df.drop_duplicates()

    df['dcreated'] = datetime.date.today()
    df['test_url'] = df['url'] + '?utm_campaign=' + df['utm_campaign'] + '&utm_medium=' + df[
        'utm_medium'] + '&utm_source=' + df['utm_source']

    df.to_sql('INVOCA_CAMPAIGNS', dbrun, if_exists='append', index=False)

    flash("Bulk Upload from Invoca JSON Complete")
    return redirect(url_for('Index'))


@app.route('/newcampaign')
def newcamp():
    dbrun = db2.connect()

    new_camp = pd.read_excel(
        'https://docs.google.com/spreadsheets/d/e/2PACX-1vTZETwlh3UhjRBoarnmuCUZYH-kfbfnjr6p6JfcT6bObDIqpcvJcrY9E84PxVUPa2vM0YgiyVjoFCsa/pub?output=xlsx')

    df2 = pd.DataFrame(googlesheet(new_camp))
    df2 = df2.drop_duplicates()

    df2['dcreated'] = datetime.date.today()
    df2['test_url'] = df2['url'] + '?utm_campaign=' + df2['utm_campaign'] + '&utm_medium=' + df2[
        'utm_medium'] + '&utm_source=' + df2['utm_source']

    df2.to_sql('INVOCA_CAMPAIGNS', dbrun, if_exists='append', index=False)

    flash('New Campaigns Bulk Added')

    return redirect(url_for('Index'))


@app.route('/hmicampaign')
def hmicamp():
    dbrun = db2.connect()

    new_camp = pd.read_excel(
        'https://docs.google.com/spreadsheets/d/e/2PACX-1vTBKuULCG-38_jXLmxKcZE8ERmWa6es-Bv9HmiB1cpniKwqz-t60-dbJ53PKOtxBF0IV2ZbXhRSim7S/pub?output=xlsx')
    fcamp = new_camp[['Final URL', '&utm_campaign=', '&utm_medium=', 'utm_source=', 'Destination #', 'Forwarding #']]

    fcamp = fcamp.rename(columns={'Final URL': 'url', '&utm_campaign=': 'utm_campaign', '&utm_medium=': 'utm_medium',
                                  'utm_source=': 'utm_source', 'Destination #': 'destination',
                                  'Forwarding #': 'forward'})

    fcamp = fcamp.drop_duplicates()

    fcamp = fcamp.dropna()

    fcamp['agency'] = 'horizon'
    fcamp['dcreated'] = datetime.date.today()
    fcamp['test_url'] = fcamp['url'] + '?utm_campaign=' + fcamp['utm_campaign'] + '&utm_medium=' + fcamp[
        'utm_medium'] + '&utm_source=' + fcamp['utm_source']

    fcamp.to_sql('INVOCA_CAMPAIGNS', dbrun, if_exists='append', index=False)

    flash('Horizon Campaigns Bulk Added')

    return redirect(url_for('Index'))


@app.route('/makejson', methods=['GET'])
def makejson():
    inv_data = db.session.query(
        Invoca_Campaigns.url,
        Invoca_Campaigns.destination,
        Invoca_Campaigns.forward,
        Invoca_Campaigns.utm_campaign,
        Invoca_Campaigns.utm_medium,
        Invoca_Campaigns.utm_source,
        Invoca_Campaigns.agency
    ).all()

    out = []

    for row in inv_data:
        out.append(dict(row))

    return jsonify(out)


if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> 6f0881e044d39a22ad01d03b0c93409edad40334
