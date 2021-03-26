from flask import Flask, render_template, request, session
from dbconn import UseDatabase, ConnectionError, CredentialsError, SQLError
from checker import check_logged_in
from threading import Thread

app = Flask(__name__)

app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'root',
                          'password': '',
                          'database': 'klopa'}


@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return 'You are now logged in.'


@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')
    return 'You are now logged out'


def zapamti(req: 'flask_request') -> None:
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into porudzbine
            (Ime, Hrana, Prilozi, Dodatno, Cena)
            values
            (%s,%s,%s,%s,%s)"""
        cursor.execute(_SQL, (
            request.form['ime'],
            request.form['hrana'],
            request.form['prilozi'],
            request.form['dodatno'],
            request.form['cena']
        ))


@app.route('/')
def hello() -> 'html':
    return render_template('entry.html',
                           the_title='Dobrodosli')


@app.route('/porudzbina', methods=['POST'])
def porudzbina() -> 'html':
    ime = request.form['ime']
    hrana = request.form['hrana']
    prilozi = request.form['prilozi']
    dodatno = request.form['dodatno']
    cena = request.form['cena']
    try:
        zapamti(request)
    except Exception as err:
        print('****Problem sa logovanjem na bazu: ', str(err))
    return render_template('results.html',
                           the_title='Vasa porudzbina je:',
                           ime=ime,
                           hrana=hrana,
                           prilozi=prilozi,
                           dodatno=dodatno,
                           cena=cena)


@app.route('/pregled')
@check_logged_in
def pregled() -> 'html':
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """ select Ime, Hrana, Prilozi, Dodatno, Cena, ts from porudzbine"""
        cursor.execute(_SQL)
        contents = cursor.fetchall()
        por_cena = 0
        for por in contents:
            por_cena += int(por[4])

        titles = ('Ime', 'Hrana', 'Prilozi', 'Dodatno', 'Cena', 'Vreme')
        return render_template('viewlog.html',
                               the_title='Sve porudzbine su:',
                               the_row_titles=titles,
                               the_data=contents,
                               ukupan_iznos=por_cena, )


app.secret_key = 'YouWillNeverGuess...'

if __name__ == '__main__':
    app.run(debug=True)
