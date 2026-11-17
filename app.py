import os
import psycopg2
from flask import Flask, request, jsonify, make_response
from markupsafe import escape

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
    termino = request.args.get('q', '').strip()
    if len(termino) > 50:
        return jsonify({"error": "Parámetro de búsqueda demasiado largo"}), 400

    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT id, username, nombre_completo, saldo FROM usuarios WHERE nombre_completo ILIKE %s;"
    try:
        cur.execute(query, (f"%{termino}%",))
        filas = cur.fetchall()
        resultados = [{"id": f[0], "username": f[1], "nombre": f[2], "saldo": float(f[3])} for f in filas]
        termino_seguro = escape(termino)
        mensaje = f"Resultados obtenidos para el criterio: {termino_seguro}"
        return make_response(jsonify({"filtro": mensaje, "data": resultados}), 200)
    except Exception:
        return jsonify({"error": "Error interno al procesar la búsqueda"}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/socios/<int:usuario_id>/perfil', methods=['GET'])
def ver_perfil(usuario_id):
    user_id_header = request.headers.get('X-User-Id')
    if not user_id_header or str(usuario_id) != str(user_id_header):
        return jsonify({"error": "Acceso denegado: no tiene permisos para consultar este perfil"}), 403

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, username, nombre_completo, ci, saldo, rol FROM usuarios WHERE id = %s;", (usuario_id,))
        u = cur.fetchone()
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
    finally:
        cur.close()
        conn.close()

@app.route('/api/comentarios', methods=['GET', 'POST'])
def comentarios():
    conn = get_connection()
    cur = conn.cursor()
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            autor = str(escape(data.get('autor', 'Anonimo')))[:50]
            mensaje = str(escape(data.get('mensaje', '')))[:300]
            cur.execute("INSERT INTO comentarios (autor, mensaje) VALUES (%s, %s);", (autor, mensaje))
            conn.commit()
            return jsonify({"status": "comentario registrado"}), 201
        else:
            cur.execute("SELECT autor, mensaje FROM comentarios ORDER BY id DESC;")
            items = cur.fetchall()
            return jsonify([{"autor": str(escape(i[0])), "mensaje": str(escape(i[1]))} for i in items]), 200
    finally:
        cur.close()
        conn.close()

@app.after_request
def aplicar_cabeceras(response):
    # Ocultar completamente la versión del servidor Werkzeug/Python
    response.headers['Server'] = 'SecureAPI-Service'
    response.headers.pop('X-Powered-By', None)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'; frame-ancestors 'none';"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
