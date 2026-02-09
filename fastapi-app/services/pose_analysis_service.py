import math
import statistics
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Landmark(BaseModel):
    x: float
    y: float
    z: float
    visibility: float

class PoseAnalysisService:
    def __init__(self):
        # MediaPipe Hand Landmark Indices
        self.HAND_WRIST = 0
        self.HAND_INDEX_FINGER_MCP = 5
        self.HAND_PINKY_MCP = 17

        # MediaPipe Pose Landmark Indices
        self.POSE_LEFT_WRIST = 15
        self.POSE_RIGHT_WRIST = 16
        self.POSE_LEFT_SHOULDER = 11
        self.POSE_RIGHT_SHOULDER = 12
        self.POSE_LEFT_HIP = 23
        self.POSE_RIGHT_HIP = 24
        
        # Thresholds (Normalized coordinates 0-1)
        self.NAVEL_PROXIMITY_THRESHOLD = 0.15  # ~15% of screen width
        self.CIRCULAR_VARIANCE_THRESHOLD = 0.005
        self.STATIC_THRESHOLD = 0.01

    def calculate_distance(self, p1: Landmark, p2: Landmark) -> float:
        """Euclidean distance between two 3D points"""
        return math.sqrt(
            (p1.x - p2.x)**2 + 
            (p1.y - p2.y)**2 + 
            (p1.z - p2.z)**2
        )

    def analyze_movement(self, history: List[List[Landmark]], wrist_index: int) -> str:
        """Analyze movement patterns from landmark history (last 10 frames)"""
        if not history or len(history) < 5:
            return "Movement data insufficient."

        # Track wrist position over time
        wrist_history = [frame[wrist_index] for frame in history if len(frame) > wrist_index]
        if len(wrist_history) < 5:
            return "Movement data insufficient."
        
        # Calculate variance in X and Y to detect motion type
        x_vals = [l.x for l in wrist_history]
        y_vals = [l.y for l in wrist_history]
        
        x_variance = statistics.variance(x_vals) if len(x_vals) > 1 else 0
        y_variance = statistics.variance(y_vals) if len(y_vals) > 1 else 0
        
        total_variance = x_variance + y_variance
        
        if total_variance < self.STATIC_THRESHOLD:
            return "Hand is static."
        
        # Check for circular motion (simplified: significant variance in both axes)
        # A true circle check would require more complex geometry, but this is a good heuristic
        if x_variance > self.CIRCULAR_VARIANCE_THRESHOLD and y_variance > self.CIRCULAR_VARIANCE_THRESHOLD:
             # Check if bounds are roughly equal (indicative of circle/square vs line)
            x_range = max(x_vals) - min(x_vals)
            y_range = max(y_vals) - min(y_vals)
            ratio = x_range / y_range if y_range > 0 else 0
            
            if 0.5 < ratio < 2.0:
                return "Circular massaging motion detected."
        
        return "Hand is moving actively."

    def get_visual_description(self,
                             landmarks: List[Dict[str, float]],
                             history: List[List[Dict[str, float]]],
                             target_zone: str = "navel") -> str:
        """
        Main entry point: Converts landmarks to semantic description.
        Assumes landmarks are standard MediaPipe Hands format.
        """
        if not landmarks:
            return "No hands detected."

        # Convert dicts to objects for easier handling
        current_frame = [Landmark(**l) for l in landmarks]

        is_pose = len(current_frame) >= 33
        if is_pose:
            left_wrist = current_frame[self.POSE_LEFT_WRIST]
            right_wrist = current_frame[self.POSE_RIGHT_WRIST]
            left_ok = left_wrist.visibility >= 0.4
            right_ok = right_wrist.visibility >= 0.4
            if left_ok and right_ok:
                wrist = left_wrist if left_wrist.visibility >= right_wrist.visibility else right_wrist
            elif left_ok:
                wrist = left_wrist
            elif right_ok:
                wrist = right_wrist
            else:
                return "No hands detected."

            left_hip = current_frame[self.POSE_LEFT_HIP]
            right_hip = current_frame[self.POSE_RIGHT_HIP]
            left_shoulder = current_frame[self.POSE_LEFT_SHOULDER]
            right_shoulder = current_frame[self.POSE_RIGHT_SHOULDER]

            hip = Landmark(
                x=(left_hip.x + right_hip.x) / 2,
                y=(left_hip.y + right_hip.y) / 2,
                z=(left_hip.z + right_hip.z) / 2,
                visibility=min(left_hip.visibility, right_hip.visibility)
            )
            shoulder = Landmark(
                x=(left_shoulder.x + right_shoulder.x) / 2,
                y=(left_shoulder.y + right_shoulder.y) / 2,
                z=(left_shoulder.z + right_shoulder.z) / 2,
                visibility=min(left_shoulder.visibility, right_shoulder.visibility)
            )
            navel_proxy = Landmark(
                x=hip.x * 0.6 + shoulder.x * 0.4,
                y=hip.y * 0.6 + shoulder.y * 0.4,
                z=hip.z * 0.6 + shoulder.z * 0.4,
                visibility=min(hip.visibility, shoulder.visibility)
            )
            wrist_index = self.POSE_LEFT_WRIST if wrist is left_wrist else self.POSE_RIGHT_WRIST
        else:
            if len(current_frame) <= self.HAND_PINKY_MCP:
                return "No hands detected."
            wrist = current_frame[self.HAND_WRIST]
            navel_proxy = Landmark(x=0.5, y=0.7, z=0.0, visibility=1.0)
            wrist_index = self.HAND_WRIST
        
        # 2. Check Proximity
        dist_to_navel = self.calculate_distance(wrist, navel_proxy)
        
        position_desc = ""
        if dist_to_navel < self.NAVEL_PROXIMITY_THRESHOLD:
            position_desc = "Hand is correctly positioned over the uterus/abdomen."
        elif wrist.y < navel_proxy.y - 0.2:
            position_desc = "Hand is too high (above navel)."
        elif wrist.y > navel_proxy.y + 0.2:
            position_desc = "Hand is too low."
        else:
            position_desc = "Hand is near the abdomen but off-center."

        # 3. Analyze Motion
        # Convert history dicts to objects
        history_objs = [[Landmark(**l) for l in frame] for frame in history]
        motion_desc = self.analyze_movement(history_objs, wrist_index)

        if is_pose:
            pressure_desc = "Pressure appears firm." if wrist.z < navel_proxy.z else "Pressure appears light."
        else:
            fingers_z = statistics.mean([
                current_frame[self.HAND_INDEX_FINGER_MCP].z,
                current_frame[self.HAND_PINKY_MCP].z
            ])
            pressure_desc = "Pressure appears firm." if fingers_z < wrist.z else "Pressure appears light."

        return f"{position_desc} {motion_desc} {pressure_desc}"

pose_analysis_service = PoseAnalysisService()
