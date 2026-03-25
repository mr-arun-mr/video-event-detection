import cv2
import json
import os
from datetime import datetime
from ultralytics import YOLO

# ===============================
# CONFIG
# ===============================

VIDEO_PATH = "sample.mp4"
EVENT_FILE = "events/events.json"
DEBUG_SAVE_EVERY = 50  # save frame every N frames
FRAME_FOLDER = "frames"



# ===============================
# EVENT GENERATOR
# ===============================

def create_event(frame_number, label, confidence):
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "frame_number": frame_number,
        "event_type": "HUMAN_DETECTED" if label == "person" else "VEHICLE_DETECTED",
        "object": label,
        "confidence": float(confidence)
    }


def save_events(events):
    with open(EVENT_FILE, "a") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")


# ===============================
# MAIN PROGRAM
# ===============================

def main():

    # Load YOLO model
    model = YOLO("yolov8n.pt")

    # Open video
    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print("❌ Error opening video")
        return

    # Print video info (very useful for debugging)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    print("=================================")
    print("Video Loaded Successfully")
    print(f"Resolution: {width} x {height}")
    print(f"FPS: {fps}")
    print("Press Q to stop")
    print("=================================")

    frame_number = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_number += 1

        # Run detection
        results = model(frame)

        events = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                confidence = float(box.conf[0])

                # Only detect humans + vehicles
                if label in ["person", "car", "truck", "bus", "motorbike"]:

                    # Create event
                    event = create_event(frame_number, label, confidence)
                    events.append(event)

                    # Draw bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    text = f"{label} {confidence:.2f}"
                    cv2.putText(frame, text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Save events
        if events:
            save_events(events)
            print(f"Frame {frame_number} -> {len(events)} event(s)")

        # Show frame (debug window)
        cv2.imshow("Video Event Detection - Debug", frame)

        # create folder if it does not exist
        os.makedirs(FRAME_FOLDER, exist_ok=True)

        # Save debug frames
        if frame_number % DEBUG_SAVE_EVERY == 0:
           # cv2.imwrite(f"debug_frame_{frame_number}.jpg", frame)
            file_path = os.path.join(FRAME_FOLDER, f"debug_frame_{frame_number}.jpg")
            cv2.imwrite(file_path, frame)


    # Press Q to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("✅ Processing completed")


# ===============================
# START
# ===============================

if __name__ == "__main__":
    main()