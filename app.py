import os
import shutil
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from spleeter.separator import Separator

# --- Configuration ---
app = Flask(__name__)
# User uploads တွေနဲ့ output တွေအတွက် folder နေရာ
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
# MAX_CONTENT_LENGTH ကို 100MB သို့ တိုးမြှင့်လိုက်သည် (16MB ကနေ)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB file size limit

# Folder တွေ မရှိသေးရင် ဖန်တီးပါ
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Spleeter Separator ကို စတင်ခြင်း
# Spleeter:2stems model ကို အသုံးပြုမည်။ config.json ကို အလိုအလျောက် ရှာဖွေမည်။
separator = Separator('spleeter:2stems')

# --- Helper Functions ---
def clean_folder(folder_path):
    """Specified folder ထဲက content တွေအားလုံးကို ဖျက်ရှင်းခြင်း"""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

# --- Error Handler for large files (HTTP 413) ---
@app.errorhandler(413)
def request_entity_too_large(error):
    # ဖိုင်အရွယ်အစား ကြီးလွန်းလျှင် ပြမည့် Error Message
    return render_template('index.html', error="ဖိုင်အရွယ်အစား ကြီးလွန်းနေပါသည်။ 100MB အောက်ရှိသော ဖိုင်ကိုသာ တင်သွင်းပါ။"), 413

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 1. ဖိုင် လက်ခံခြင်း
        if 'audio_file' not in request.files:
            return render_template('index.html', error="No file selected.")
        
        file = request.files['audio_file']
        
        if file.filename == '':
            return render_template('index.html', error="No selected file.")
        
        if file:
            # File name ကို sanitize လုပ်ပြီး ထူးခြားတဲ့ နာမည်ပေး
            base_filename = os.path.splitext(file.filename)[0]
            unique_folder_name = base_filename.replace(' ', '_') + '_' + os.urandom(4).hex()
            
            # Input path နှင့် Output folder path များ သတ်မှတ်
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_folder_name + os.path.splitext(file.filename)[1])
            output_path_base = os.path.join(app.config['OUTPUT_FOLDER'], unique_folder_name)
            
            # Output folder အဟောင်းကို ဖျက်ပြီး အသစ်ပြန်ဖန်တီး
            if os.path.exists(output_path_base):
                shutil.rmtree(output_path_base)
            os.makedirs(output_path_base)
            
            # ဖိုင်ကို သိမ်းဆည်းခြင်း
            file.save(input_path)

            # 2. Spleeter ဖြင့် ခွဲထုတ်ခြင်း လုပ်ဆောင်ချက်
            try:
                # Spleeter ကို ခေါ်ယူခြင်း။ output_path_base folder ထဲမှာ files တွေ ရောက်လာမည်။
                separator.separate_to_file(
                    input_path, 
                    output_path_base,
                    codec='mp3' # config.json ကို မသုံးချင်ရင် ဒီနေရာမှာလည်း ထည့်နိုင်ပါသည်။
                )
                
                # အောင်မြင်ပါက input file ကို ဖြတ်ပစ်ခြင်း (Cleanup)
                os.remove(input_path)
                
                return redirect(url_for('result', folder_name=unique_folder_name))

            except Exception as e:
                # Error ဖြေရှင်းခြင်း
                print(f"Error during separation: {e}")
                # Clean up the input file if separation fails
                if os.path.exists(input_path):
                    os.remove(input_path)
                return render_template('index.html', error=f"An error occurred: {e}")

    # GET Request
    return render_template('index.html', error=None)

# ရလဒ်များကို ပြသပြီး Download link ပေးခြင်း
@app.route('/result/<folder_name>')
def result(folder_name):
    # Spleeter ရဲ့ output folder structure အရ၊ output files တွေက folder_name/original_filename ထဲမှာ ရှိနေနိုင်တယ်။
    # ဒါပေမယ့် Spleeter က output_path ကို folder အဖြစ် သတ်မှတ်ပြီး၊ folder ထဲမှာ vocals.mp3, instrumental.mp3 တွေ ထွက်ပါတယ်။
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], folder_name)
    
    if not os.path.exists(output_dir):
        return render_template('index.html', error="Result not found or expired.")
    
    # ခွဲထုတ်ထားတဲ့ ဖိုင်တွေ (ဥပမာ- vocals.mp3, accompaniment.mp3) ကို ရှာခြင်း
    stems = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
    
    return render_template('result.html', folder_name=folder_name, stems=stems)

# Download လုပ်ဖို့ API endpoint
@app.route('/download/<folder_name>/<filename>')
def download_file(folder_name, filename):
    return send_from_directory(os.path.join(app.config['OUTPUT_FOLDER'], folder_name),
                               filename, as_attachment=True)

if __name__ == '__main__':
    # Flask server စတင်ခြင်း
    app.run(debug=True)
