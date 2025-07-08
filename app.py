import io
from flask import Flask, request, send_file, render_template_string
from PIL import Image

app = Flask(__name__)

HTML_FORM = """
<!doctype html>
<title>AI Image Resizer</title>
<h1>Upload Image and Set Target Size (inches)</h1>
<form method=post enctype=multipart/form-data>
  <label>Image file:</label>
  <input type=file name=file required><br><br>
  <label>Width (inches):</label>
  <input type=number name=width_in step=0.01 min=0.1 required><br>
  <label>Height (inches):</label>
  <input type=number name=height_in step=0.01 min=0.1 required><br>
  <label>DPI (optional, default 300):</label>
  <input type=number name=dpi value=300 min=72 max=1200><br><br>
  <input type=submit value=Resize>
</form>
"""

@app.route('/', methods=['GET', 'POST'])
def upload_and_resize():
    if request.method == 'POST':
        # Validate file upload
        if 'file' not in request.files or request.files['file'].filename == '':
            return "No file uploaded.", 400
        file = request.files['file']

        # Validate and parse form fields
        try:
            width_in = float(request.form['width_in'])
            height_in = float(request.form['height_in'])
            dpi = int(request.form.get('dpi', 300))
            if width_in <= 0 or height_in <= 0 or dpi <= 0:
                raise ValueError
        except Exception:
            return "Invalid input for width, height, or DPI.", 400

        # Open and process image
        try:
            img = Image.open(file.stream)
            width_px = int(width_in * dpi)
            height_px = int(height_in * dpi)
            # Use high-quality Lanczos filter for resizing
            img = img.convert('RGB')  # Ensures compatibility for JPEG
            resized_img = img.resize((width_px, height_px), Image.LANCZOS)
            output = io.BytesIO()
            resized_img.save(output, format='JPEG', dpi=(dpi, dpi))
            output.seek(0)
        except Exception as e:
            return f"Image processing failed: {str(e)}", 500

        return send_file(output, mimetype='image/jpeg', as_attachment=True, download_name='resized.jpg')

    # GET: Show upload form
    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    app.run(debug=True)
