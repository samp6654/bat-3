import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine = np.clip(cosine, -1.0, 1.0)

    angle = np.degrees(np.arccos(cosine))
    return angle


def classify_risk(elbow, knee, spine):
    score = 0

    if elbow < 130:
        score += 2
    elif elbow < 145:
        score += 1

    if knee < 140:
        score += 2
    elif knee < 155:
        score += 1

    if spine < 120:
        score += 2
    elif spine < 135:
        score += 1

    if score >= 4:
        return "HIGH"
    elif score >= 2:
        return "MEDIUM"
    else:
        return "LOW"


def analyze_video(video_path):
    pose = mp_pose.Pose()

    cap = cv2.VideoCapture(video_path)

    risks = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        if result.pose_landmarks:
            lm = result.pose_landmarks.landmark

            def get_point(i):
                return [lm[i].x, lm[i].y]

            elbow = calculate_angle(
                get_point(11), get_point(13), get_point(15)
            )

            knee = calculate_angle(
                get_point(23), get_point(25), get_point(27)
            )

            spine = calculate_angle(
                get_point(11), get_point(23), get_point(25)
            )

            risk = classify_risk(elbow, knee, spine)
            risks.append(risk)

    cap.release()

    # Calculate %
    high_count = risks.count("HIGH")
    total = len(risks)

    if total == 0:
        return {"risk_score": 0, "risk_level": "UNKNOWN"}

    percent = (high_count / total) * 100

    if percent > 60:
        level = "HIGH"
    elif percent > 30:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_score": round(percent, 2),
        "risk_level": level
    }