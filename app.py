from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
BASE_DATOS = "videojuegos.db"


def inicializar_bd():
    with sqlite3.connect(BASE_DATOS) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS juegos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                genero TEXT NOT NULL,
                desarrollador TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS puntajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                estrellas INTEGER CHECK(estrellas >= 1 AND estrellas <= 5),
                descripcion TEXT,
                juego_id INTEGER NOT NULL,
                FOREIGN KEY (juego_id) REFERENCES juegos(id) ON DELETE CASCADE
            )
        """)
        connection.commit()


@app.route("/")
def juegos_index():
    with sqlite3.connect(BASE_DATOS) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT j.id, j.nombre, j.genero, j.desarrollador, 
                   IFNULL(ROUND(AVG(p.estrellas), 2), 'N/A') as promedio
            FROM juegos j
            LEFT JOIN puntajes p ON j.id = p.juego_id
            GROUP BY j.id
        """)
        juegos = cursor.fetchall()
    return render_template("juegos/index.html", juegos=juegos)


@app.route("/juegos/crear", methods=["GET", "POST"])
def juegos_crear():
    if request.method == "POST":
        nombre = request.form["nombre"]
        genero = request.form["genero"]
        desarrollador = request.form["desarrollador"]
        with sqlite3.connect(BASE_DATOS) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO juegos (nombre, genero, desarrollador) VALUES (?, ?, ?)", 
                           (nombre, genero, desarrollador))
            connection.commit()
        return redirect(url_for("juegos_index"))
    return render_template("juegos/crear.html")


@app.route("/juegos/editar/<int:id>", methods=["GET", "POST"])
def juegos_editar(id):
    with sqlite3.connect(BASE_DATOS) as connection:
        cursor = connection.cursor()
        if request.method == "POST":
            nombre = request.form["nombre"]
            genero = request.form["genero"]
            desarrollador = request.form["desarrollador"]
            cursor.execute("UPDATE juegos SET nombre=?, genero=?, desarrollador=? WHERE id=?", 
                           (nombre, genero, desarrollador, id))
            connection.commit()
            return redirect(url_for("juegos_index"))
        cursor.execute("SELECT * FROM juegos WHERE id=?", (id,))
        juego = cursor.fetchone()
    return render_template("juegos/editar.html", juego=juego)


@app.route("/juegos/eliminar/<int:id>")
def juegos_eliminar(id):
    with sqlite3.connect(BASE_DATOS) as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM juegos WHERE id=?", (id,))
        connection.commit()
    return redirect(url_for("juegos_index"))


@app.route("/juegos/<int:id>")
def juegos_detalle(id):
    with sqlite3.connect(BASE_DATOS) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM juegos WHERE id=?", (id,))
        juego = cursor.fetchone()
        cursor.execute("SELECT * FROM puntajes WHERE juego_id=?", (id,))
        puntajes = cursor.fetchall()
        cursor.execute("SELECT ROUND(AVG(estrellas),2) FROM puntajes WHERE juego_id=?", (id,))
        promedio = cursor.fetchone()[0]
    return render_template("juegos/detalle.html", juego=juego, puntajes=puntajes, promedio=promedio)


@app.route("/puntajes/crear/<int:juego_id>", methods=["GET", "POST"])
def puntajes_crear(juego_id):
    if request.method == "POST":
        usuario = request.form["usuario"]
        estrellas = int(request.form["estrellas"])
        descripcion = request.form["descripcion"]
        with sqlite3.connect(BASE_DATOS) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO puntajes (usuario, estrellas, descripcion, juego_id) VALUES (?, ?, ?, ?)",
                           (usuario, estrellas, descripcion, juego_id))
            connection.commit()
        return redirect(url_for("juegos_detalle", id=juego_id))
    return render_template("puntajes/crear.html", juego_id=juego_id)


@app.route("/puntajes/editar/<int:id>", methods=["GET", "POST"])
def puntajes_editar(id):
    with sqlite3.connect(BASE_DATOS) as connection:
        cursor = connection.cursor()
        if request.method == "POST":
            usuario = request.form["usuario"]
            estrellas = int(request.form["estrellas"])
            descripcion = request.form["descripcion"]
            cursor.execute("UPDATE puntajes SET usuario=?, estrellas=?, descripcion=? WHERE id=?",
                           (usuario, estrellas, descripcion, id))
            connection.commit()
            cursor.execute("SELECT juego_id FROM puntajes WHERE id=?", (id,))
            juego_id = cursor.fetchone()[0]
            return redirect(url_for("juegos_detalle", id=juego_id))
        cursor.execute("SELECT * FROM puntajes WHERE id=?", (id,))
        puntaje = cursor.fetchone()
    return render_template("puntajes/editar.html", puntaje=puntaje)


@app.route("/puntajes/eliminar/<int:id>")
def puntajes_eliminar(id):
    with sqlite3.connect(BASE_DATOS) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT juego_id FROM puntajes WHERE id=?", (id,))
        juego_id = cursor.fetchone()[0]
        cursor.execute("DELETE FROM puntajes WHERE id=?", (id,))
        connection.commit()
    return redirect(url_for("juegos_detalle", id=juego_id))


if __name__ == "__main__":
    inicializar_bd()
    app.run(debug=True)
