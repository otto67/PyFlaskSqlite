
from flask import Flask, url_for, render_template, redirect, request, session, make_response, jsonify
from markupsafe import escape
import json
import os
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def index():
   return render_template('index.html')


@app.route('/add_member', methods=['POST'])
def add_member():
    input_data = request.get_data()
    # session['input'] = input_data.decode()
    # Convert to list before passing to simulator
    mylist = json.loads(input_data.decode())
    id = int(mylist[0])
    fn = mylist[1]
    ln = mylist[2]
    eaddr = mylist[3]
    retval = add_row(id, fn, ln, eaddr)
    if (retval < 0):
        mylist[0] = "-1"
    template_context = jsonify(mylist)
    return make_response(template_context)

@app.route('/list_all_members', methods=['GET'])
def list_all_members():
    mylist = print_all()
    session['input'] = mylist;
    template_context = jsonify("Success")
    return make_response(template_context)

@app.route('/list_all', methods=['GET'])
def list_all():
    mylist = session['input']
    return render_template('memberlist.html', list_entries=mylist)


@app.route('/find_member/<entry_id>', methods=['GET'])
def find_member(entry_id):
    id = int(entry_id)
    mylist = find_entry(id)
    template_context = jsonify(mylist)
    return make_response(template_context)

@app.route('/remove_member/<entry_id>', methods=['GET'])
def remove_member(entry_id):
    id = int(entry_id)
    mylist = remove_entry(id)
    template_context = jsonify(mylist)
    return make_response(template_context)

def create_table():
    conn = sqlite3.connect('member.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS members (
        member_id integer PRIMARY KEY,
        first_name text NOT NULL,
        last_name text NOT NULL,
        email text
    )""")
    conn.commit()
    conn.close()

def add_row(id, name_1, name_2, email):
    conn = sqlite3.connect('member.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO members VALUES (?, ?, ?, ?)", (id, name_1, name_2, email))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        print("Unsuccessful add. Id " + str(id) + " already exists")
        conn.close()
        return -1
    return 0

def find_entry(id):
    conn = sqlite3.connect('member.db')
    if not conn:
        return None

    print("Find entry: id is: ", id)
    c = conn.cursor()
    c.execute('SELECT * FROM members WHERE member_id=?', (id,))
    retval = c.fetchall()
    conn.close()
    return retval

def remove_entry(id):
    conn = sqlite3.connect('member.db')
    if not conn:
        return None

    print("Remove entry: id is: ", id)
    c = conn.cursor()
    try:
        c.execute('DELETE FROM members WHERE member_id=?', (id,))
        retval = c.rowcount
        conn.commit()
        conn.close()
    except:
        print("Failed to remove entry")
        conn.close()
        retval = None

    return retval

def print_all():
    conn = sqlite3.connect('member.db')
    if not conn:
        return None

    c = conn.cursor()
    c.execute("SELECT * FROM members")
    retval = c.fetchall()
    conn.close()
    return retval

if __name__ == "__main__":
    create_table()
    app.run(host='0.0.0.0')