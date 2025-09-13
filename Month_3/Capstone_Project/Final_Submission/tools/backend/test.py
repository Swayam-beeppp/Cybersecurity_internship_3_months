import face_recognition

print("✅ face_recognition imported successfully!")

# Load a sample image (replace with your own)
image = face_recognition.load_image_file("your_image.jpg")
face_locations = face_recognition.face_locations(image)

print("Found", len(face_locations), "face(s) in this image.")
