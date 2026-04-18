# backend/services/face_auth_service.py
import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from scipy.spatial.distance import euclidean
from werkzeug.utils import secure_filename

# Configuration
REGISTERED_FOLDER = 'registered_faces'
UPLOAD_FOLDER = 'uploads'
SIMILARITY_THRESHOLD = 0.5

# Ensure folders exist
os.makedirs(REGISTERED_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- NEW MEDIAPIPE INITIALIZATION (Python 3.14 Compatible) ---
base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
# We need to download the task model first if not present
MODEL_PATH = "face_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print(f"⬇️ Downloading Face Landmarker model to {MODEL_PATH}...")
    import urllib.request
    url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("✅ Model downloaded.")

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_faces=1
)

detector = vision.FaceLandmarker.create_from_options(options)
# -------------------------------------------------------------

# In-memory storage: { "name": embedding_vector }
known_faces = {}

def load_known_faces_from_disk():
    """Loads all images from registered_faces folder."""
    global known_faces
    known_faces = {}
    allowed_ext = {'png', 'jpg', 'jpeg'}
    
    if not os.path.exists(REGISTERED_FOLDER):
        return

    for filename in os.listdir(REGISTERED_FOLDER):
        if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext:
            path = os.path.join(REGISTERED_FOLDER, filename)
            name = os.path.splitext(filename)[0]
            
            embedding = get_face_embedding(path)
            if embedding is not None:
                known_faces[name] = embedding
                print(f"✅ Face Loaded: {name}")
    
    print(f"💾 Total faces loaded: {len(known_faces)}")

def get_face_embedding(image_path):
    """Extracts facial landmarks vector using NEW MediaPipe API."""
    if not os.path.exists(image_path):
        return None
        
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    # Convert BGR to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Create MediaPipe Image object
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    
    # Detect
    result = detector.detect(mp_image)
    
    if not result.face_landmarks or len(result.face_landmarks) == 0:
        return None
    
    # Get the first face
    face_landmarks = result.face_landmarks[0]
    
    # Extract coordinates
    embedding = []
    h, w, _ = image.shape
    
    for landmark in face_landmarks:
        # landmark.x and .y are normalized (0.0 to 1.0)
        embedding.append(landmark.x * w)
        embedding.append(landmark.y * h)
        # z is relative depth, often less reliable for 2D matching but we include it
        embedding.append(landmark.z * w) 
    
    embedding = np.array(embedding, dtype=np.float32)
    
    # Normalize
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return None
    return embedding / norm

def register_new_face(file_storage, name: str):
    """Saves image and registers face."""
    filename = secure_filename(f"{name}.jpg")
    filepath = os.path.join(REGISTERED_FOLDER, filename)
    
    try:
        file_storage.save(filepath)
        embedding = get_face_embedding(filepath)
        
        if embedding is None:
            os.remove(filepath)
            return {"success": False, "message": "No face detected in image."}
        
        known_faces[name] = embedding
        return {"success": True, "message": f"User {name} registered.", "identity": name}
    
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return {"success": False, "message": str(e)}

def authenticate_face(file_storage):
    """Compares uploaded image against known faces."""
    filename = secure_filename(f"temp_{np.random.randint(10000)}.jpg")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file_storage.save(filepath)
        unknown_embedding = get_face_embedding(filepath)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            
        if unknown_embedding is None:
            return {"status": "denied", "message": "No face detected.", "identity": None}
        
        best_match_name = None
        best_distance = float('inf')
        
        for name, known_emb in known_faces.items():
            dist = euclidean(known_emb, unknown_embedding)
            if dist < best_distance:
                best_distance = dist
                best_match_name = name
        
        if best_match_name and best_distance < SIMILARITY_THRESHOLD:
            confidence = max(0, 100 - (best_distance * 100))
            return {
                "status": "granted", 
                "message": "Access Granted", 
                "identity": best_match_name,
                "confidence": f"{confidence:.2f}%"
            }
        else:
            return {
                "status": "denied", 
                "message": "Face not recognized.", 
                "identity": None,
                "closest_match": best_match_name
            }
            
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return {"status": "error", "message": str(e)}
