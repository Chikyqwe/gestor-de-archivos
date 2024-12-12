from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask import send_from_directory
import os
import shutil

app = Flask(__name__)

# Filtro para eliminar barras finales de la ruta
@app.template_filter('trim_trailing_slash')
def trim_trailing_slash(value):
    if value.endswith('/'):
        return value[:-1]
    return value

BASE_FOLDER = '/home'  # Asegúrate de poner la ruta correcta

@app.route('/')
def index():
    folder = request.args.get('folder', BASE_FOLDER)
    folder = os.path.normpath(folder)  # Normalizar la ruta
    files = []
    folders = []

    if os.path.exists(folder):
        for entry in os.listdir(folder):
            full_path = os.path.join(folder, entry)
            if os.path.isdir(full_path):
                folders.append(entry)
            else:
                files.append(entry)

    return render_template('index.html', files=files, folders=folders, current_folder=folder)

@app.route('/delete', methods=['POST'])
def delete():
    # Obtener la ruta completa del archivo desde el formulario
    filepath = request.form.get('filepath')

    if filepath:
        # Normalizar la ruta
        filepath = os.path.normpath(filepath)

        # Verificar si el archivo existe y eliminarlo
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                return f"Error al eliminar el archivo: {e}", 500

        # Redirigir a la carpeta actual
        folder = os.path.dirname(filepath)  # Obtener la carpeta donde estaba el archivo
        return redirect(url_for('index', folder=folder))
    
    return "Ruta no válida", 400


@app.route('/delete_folder', methods=['POST'])
def delete_folder():
    folderpath = request.form.get('folderpath')
    
    if os.path.exists(folderpath) and os.path.isdir(folderpath):
        try:
            shutil.rmtree(folderpath)  # Elimina la carpeta y su contenido
            parent_folder = os.path.dirname(folderpath)
            return redirect(url_for('index', folder=parent_folder))
        except Exception as e:
            return f"Error al eliminar la carpeta: {e}", 500
    else:
        return "Carpeta no encontrada", 404


@app.route('/download', methods=['POST'])
def download():
    # Obtener la ruta completa del archivo desde el formulario
    filepath = request.form.get('filepath')

    if filepath:
        # Normalizar la ruta
        filepath = os.path.normpath(filepath)

        # Verificar si el archivo existe
        if os.path.exists(filepath):
            # Enviar el archivo para su descarga
            return send_from_directory(os.path.dirname(filepath), os.path.basename(filepath), as_attachment=True)

    return "Archivo no encontrado", 404

@app.route('/upload', methods=['POST'])
def upload():
    folder = request.form.get('current_folder', BASE_FOLDER)  # Carpeta actual
    if not os.path.exists(folder):
        return "Carpeta no válida", 400

    if 'file' not in request.files:
        return redirect(url_for('index', folder=folder))
    
    file = request.files['file']
    if file.filename != '':
        file.save(os.path.join(folder, file.filename))
    
    return redirect(url_for('index', folder=folder))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
