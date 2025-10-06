import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from typing import Optional, Dict, Any, List
import imagehash
from PIL import Image


class AnomalyType:
    VISUAL_CHANGE = "visual_change"
    SOFTLOCK = "softlock"
    PERFORMANCE_DROP = "performance_drop"
    CRASH = "crash"


class Analyzer:
    
    def __init__(self, ssim_threshold: float = 0.95, softlock_threshold: int = 30):
        self.ssim_threshold = ssim_threshold
        self.softlock_threshold = softlock_threshold
        self.previous_frame = None
        self.previous_hash = None
        self.identical_frame_count = 0
        self.frame_history: List[np.ndarray] = []
        self.max_history = 10
    
    def analyze_frame(self, current_frame: np.ndarray) -> Dict[str, Any]:
        result = {
            "anomalies": [],
            "ssim_score": None,
            "frame_difference": None,
            "is_static": False
        }
        
        if current_frame is None:
            return result
        
        gray_current = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        
        if self.previous_frame is not None:
            gray_previous = cv2.cvtColor(self.previous_frame, cv2.COLOR_BGR2GRAY)
            
            if gray_current.shape == gray_previous.shape:
                ssim_score = ssim(gray_previous, gray_current)
                result["ssim_score"] = ssim_score
                
                frame_diff = cv2.absdiff(gray_current, gray_previous)
                result["frame_difference"] = float(np.mean(frame_diff))
                
                if ssim_score > self.ssim_threshold:
                    self.identical_frame_count += 1
                    result["is_static"] = True
                else:
                    self.identical_frame_count = 0
                
                if self.identical_frame_count >= self.softlock_threshold:
                    result["anomalies"].append({
                        "type": AnomalyType.SOFTLOCK,
                        "description": f"Frame unchanged for {self.identical_frame_count} captures",
                        "severity": "high"
                    })
                
                if ssim_score < 0.5 and result["frame_difference"] > 50:
                    result["anomalies"].append({
                        "type": AnomalyType.VISUAL_CHANGE,
                        "description": "Large visual change detected",
                        "severity": "medium",
                        "ssim": ssim_score
                    })
        
        self.previous_frame = current_frame.copy()
        
        self.frame_history.append(current_frame)
        if len(self.frame_history) > self.max_history:
            self.frame_history.pop(0)
        
        return result
    
    def detect_template(self, frame: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> List[Dict[str, Any]]:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(gray_frame, gray_template, cv2.TM_CCOEFF_NORMED)
        
        locations = np.where(result >= threshold)
        matches = []
        
        for pt in zip(*locations[::-1]):
            matches.append({
                "x": int(pt[0]),
                "y": int(pt[1]),
                "confidence": float(result[pt[1], pt[0]])
            })
        
        return matches
    
    def compute_perceptual_hash(self, frame: np.ndarray) -> str:
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        phash = imagehash.phash(pil_image)
        return str(phash)
    
    def compare_hashes(self, hash1: str, hash2: str) -> int:
        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
        return h1 - h2
    
    def detect_edges(self, frame: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return edges
    
    def reset(self):
        self.previous_frame = None
        self.previous_hash = None
        self.identical_frame_count = 0
        self.frame_history.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "identical_frame_count": self.identical_frame_count,
            "frame_history_size": len(self.frame_history),
            "ssim_threshold": self.ssim_threshold,
            "softlock_threshold": self.softlock_threshold
        }

