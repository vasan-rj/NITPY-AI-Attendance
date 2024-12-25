from flask import Flask, render_template, jsonify ,request, send_file
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['OUTPUT_FOLDER'] = './outputs'

# Create folders if not exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# MongoDB Atlas Connection String
MONGO_URI="mongodb+srv://Vasan_R:6DV1CN0ukOF83RcP@cluster0.wcrsf.mongodb.net/Attendence?retryWrites=true&w=majority&appName=Cluster0/"
client = MongoClient(MONGO_URI)
db = client["Attendence"]
collection = db["Attendence_data"]

# Load the YOLO models
face_detection_model = YOLO(r"../ai_models/yolov8m-face.pt")  # Face detection model
trained_model = YOLO(r"../ai_models/best_2.pt")  # Custom trained model for roll numbers

attendance_records = []  # To store attendance details dynamically

def predict_and_label_faces_in_image(image_path, output_path):
    """
    Detect faces and recognize roll numbers. Annotate the image with results.
    Returns a list of detected roll numbers along with their confidence scores.
    """
    detected_roll_numbers = {}  # To store unique roll numbers and their confidence scores
    image = cv2.imread(image_path)
    
    # Step 1: Detect faces in the input image
    face_results = face_detection_model(image)
    for face_result in face_results:
        for box in face_result.boxes.xyxy:  # Iterate over each detected face
            x1, y1, x2, y2 = map(int, box)
            face = image[y1:y2, x1:x2]  # Crop the face
            
            # Step 2: Predict roll numbers using the trained model
            results = trained_model(face)
            for result in results:
                for class_id_tensor in result.boxes.cls:  # Iterate over detected classes
                    class_id = int(class_id_tensor.item())
                    if class_id in result.names:
                        roll_number = result.names[class_id]  # Extract roll number
                        confidence_score = result.boxes.conf[0].item()  # Get confidence score
                        
                        # Store roll number and confidence score if not already stored
                        if roll_number not in detected_roll_numbers:
                            tempx=confidence_score
                            temp=int(tempx*100)
                            # temp=int(temp)
                            confidence_score=temp
                            detected_roll_numbers[roll_number] = confidence_score
                        
                        # Annotate the image
                        for box in result.boxes.xyxy:
                            fx1, fy1, fx2, fy2 = map(int, box)
                            abs_x1, abs_y1, abs_x2, abs_y2 = x1 + fx1, y1 + fy1, x1 + fx2, y1 + fy2
                            cv2.rectangle(image, (abs_x1, abs_y1), (abs_x2, abs_y2), (0, 255, 0), 2)
                            cv2.putText(image, roll_number, (abs_x1, abs_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Step 3: Save the annotated image
    cv2.imwrite(output_path, image)
    
    # Convert the dictionary to a list of tuples
    return [{"roll_number": roll, "confidence_score": score} for roll, score in detected_roll_numbers.items()]


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        attendance_records.clear()
        file = request.files['file']
        if file:
            # Save the uploaded image
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            # Generate output path and timestamp
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"output_{filename}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Process the image and extract roll numbers
            detected_roll_numbers = predict_and_label_faces_in_image(input_path, output_path)
            
            # Update attendance records with detected roll numbers and their confidence scores
            for entry in detected_roll_numbers:
               
                attendance_records.append({
                        "roll_number": entry["roll_number"], 
                        "timestamp": timestamp, 
                        "confidence_score": entry["confidence_score"]
                    })
                
            return render_template('index.html', output_image=None, records=attendance_records)
    return render_template('index.html', output_image=None, records=attendance_records)

@app.route("/add-to-database", methods=["POST"])
def add_to_database():
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No data provided"}), 400

        collection.insert_one(data)
        return jsonify({"message": "Data successfully added to the database!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """
    Allow users to download the processed image.
    """
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
