import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import folium
import io
import cv2
from ultralytics import YOLO

class TerrainDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Terrain Detection")

        # Create latitude and longitude entry fields
        self.latitude_label = tk.Label(root, text="Latitude:")
        self.latitude_label.grid(row=0, column=0, padx=5, pady=5)
        self.latitude_entry = tk.Entry(root)
        self.latitude_entry.grid(row=0, column=1, padx=5, pady=5)

        self.longitude_label = tk.Label(root, text="Longitude:")
        self.longitude_label.grid(row=1, column=0, padx=5, pady=5)
        self.longitude_entry = tk.Entry(root)
        self.longitude_entry.grid(row=1, column=1, padx=5, pady=5)

        # Create buttons for getting coordinates and running the prediction
        self.get_coordinates_button = tk.Button(root, text="Get Coordinates", command=self.get_coordinates)
        self.get_coordinates_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="we")

        self.detect_terrain_button = tk.Button(root, text="Detect Terrain", command=self.detect_terrain)
        self.detect_terrain_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="we")

        # Create a label to display the image
        self.image_label = tk.Label(root)
        self.image_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Initialize variables
        self.latitude = None
        self.longitude = None

    def get_coordinates(self):
        try:
            self.latitude = float(self.latitude_entry.get())
            self.longitude = float(self.longitude_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid coordinates. Please enter valid latitude and longitude.")
            return

        messagebox.showinfo("Success", "Coordinates set successfully.")

    
    def generate_satellite_image(self, coordinates):
        # Increase the zoom level (higher value zooms in closer)
        zoom_level = 18  # Adjust this value as needed

        # Create a Folium map object with satellite imagery and attribution
        map_satellite = folium.Map(
            location=coordinates,
            zoom_start=zoom_level,  # Use zoom_start for initial zoom
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
        )

        # Convert the Folium map to PNG image
        img_data = map_satellite._to_png(5)  # Specify the delay (in seconds) for the image generation
        img = Image.open(io.BytesIO(img_data))

        # Save the image as a PNG file
        img_path = 'satellite_image.png'
        img.save(img_path)

        return img_path

    def detect_terrain(self):
        if self.latitude is None or self.longitude is None:
            messagebox.showerror("Error", "Please enter coordinates first.")
            return

        # Generate satellite image
        img_path = self.generate_satellite_image([self.latitude, self.longitude])

        # Define the path to your custom YOLOv8 weights file
        model_path = "weights.pt"

        # Create a YOLOv8 object with confidence threshold (optional)
        model = YOLO(model_path)  # Adjust confidence threshold as needed (0.0 to 1.0)

        # Make the prediction
        results = model(img_path, save=True)

        # Display the predicted image using OpenCV
        for result in results:
            predicted_image_path = 'runs\detect\predict28\satellite_image.png' # Get the path of the predicted image
            predicted_image = cv2.imread(predicted_image_path)  # Read the predicted image using OpenCV
            predicted_image = cv2.cvtColor(predicted_image, cv2.COLOR_BGR2RGB)  # Convert to RGB for display
            predicted_image = Image.fromarray(predicted_image)  # Convert to PIL Image
            predicted_image.thumbnail((400, 400))  # Resize the image
            predicted_image_tk = ImageTk.PhotoImage(predicted_image)  # Convert to ImageTk format
            self.image_label.configure(image=predicted_image_tk)  # Display the predicted image
            self.image_label.image = predicted_image_tk  # Keep a reference
            cv2.waitKey(0)  # Wait until a key is pressed
            cv2.destroyAllWindows()  # Close the window




# Create the Tkinter application
root = tk.Tk()
app = TerrainDetectionApp(root)
root.mainloop()
