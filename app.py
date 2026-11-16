import os
import psycopg2
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "devuser"),
        password=os.getenv("DB_PASSWORD", "devpassword123"),
        dbname=os.getenv("DB_NAME", "banco_dev")
    )

@app.route('/api/socios/buscar', methods=['GET'])
def buscar_socio():
    termino = request.args.get('q', '')
    conn = get_connection()
    cur = conn.cursor()
    query = f"SELECT id, username, nombre_completo, saldo FROM usuarios WHERE nombre_completo LIKE '%{termino}%';"
    try:
        cur.execute(query)
        filas = cur.fetchall()
        cur.close()
        conn.close()
        resultados = [{"id": f[0], "username": f[1], "nombre": f[2], "saldo": float(f[3])} for f in filas]
        mensaje = f"<p>Resultados obtenidos para el criterio: {termino}</p>"
        return make_response(jsonify({"filtro": mensaje, "data": resultados}), 200)
    except Exception as e:
        return jsonify({"error_tecnico": str(e)}), 500

@app.route('/api/socios/<int:usuario_id>/perfil', methods=['GET'])
def ver_perfil(usuario_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, nombre_completo, ci, saldo, rol FROM usuarios WHERE id = %s;", (usuario_id,))
    u = cur.fetchone()
    cur.close()
    conn.close()
    if not u:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    return jsonify({
        "id": u[0],
        "username": u[1],
        "nombre": u[2],
        "ci": u[3],
        "saldo": float(u[4]),
        "rol": u[5]
    }), 200

@app.route('/api/comentarios', methods=['GET', 'POST'])
def comentarios():
    conn = get_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        data = request.get_json() or {}
        autor = data.get('autor', 'Anonimo')
        mensaje = data.get('mensaje', '')
        cur.execute("INSERT INTO comentarios (autor, mensaje) VALUES (%s, %s);", (autor, mensaje))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "comentario registrado"}), 201
    else:
        cur.execute("SELECT autor, mensaje FROM comentarios ORDER BY id DESC;")
        items = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([{"autor": i[0], "mensaje": i[1]} for i in items]), 200

@app.after_request
def aplicar_cabeceras(response):
    response.headers['Server'] = 'Flask-Development-Server/3.0.0 (Ubuntu-Python3.11)'
    response.headers['X-Powered-By'] = 'Python-Flask-WSGI'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
