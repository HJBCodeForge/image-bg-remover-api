"""
Hybrid MediaPipe + rembg Background Removal System

This module combines MediaPipe and rembg to provide intelligent image detection
and optimal background removal based on image content.
"""

import logging
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import io
from typing import Tuple, Optional, Dict, Any
import gc

logger = logging.getLogger(__name__)

class HybridBackgroundRemover:
    """
    Hybrid system that uses:
    1. MediaPipe for human detection and human background removal
    2. rembg for object detection and object background removal
    3. Intelligent routing based on image content analysis
    """
    
    def __init__(self):
        self.mp_selfie_segmentation = None
        self.mp_pose = None
        self.mp_face_detection = None
        self.rembg_sessions = {}
        self.detection_confidence = 0.5
        
    def _init_mediapipe(self):
        """Initialize MediaPipe models lazily"""
        if self.mp_selfie_segmentation is None:
            logger.info("Initializing MediaPipe selfie segmentation...")
            self.mp_selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(
                model_selection=1  # 1 for general model, 0 for landscape
            )
            
        if self.mp_pose is None:
            logger.info("Initializing MediaPipe pose detection...")
            self.mp_pose = mp.solutions.pose.Pose(
                static_image_mode=True,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=self.detection_confidence
            )
            
        if self.mp_face_detection is None:
            logger.info("Initializing MediaPipe face detection...")
            self.mp_face_detection = mp.solutions.face_detection.FaceDetection(
                model_selection=1,  # 1 for full range, 0 for short range
                min_detection_confidence=self.detection_confidence
            )
    
    def _init_rembg_session(self, model_name: str):
        """Initialize rembg session for a specific model"""
        if model_name not in self.rembg_sessions:
            try:
                from rembg import new_session
                logger.info(f"Initializing rembg session for model: {model_name}")
                self.rembg_sessions[model_name] = new_session(model_name)
            except Exception as e:
                logger.error(f"Failed to initialize rembg session for {model_name}: {str(e)}")
                return None
        return self.rembg_sessions[model_name]
    
    def detect_image_content(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze image content using both MediaPipe and visual analysis
        
        Returns:
            Dict containing detection results and confidence scores
        """
        # Convert PIL to CV2 format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        
        detection_result = {
            'primary_type': 'general',
            'confidence': 0.0,
            'detected_humans': 0,
            'detected_faces': 0,
            'has_pose': False,
            'image_characteristics': {},
            'recommended_remover': 'rembg',
            'recommended_model': 'u2net'
        }
        
        try:
            self._init_mediapipe()
            
            # 1. Face Detection
            face_results = self.mp_face_detection.process(rgb_image)
            if face_results.detections:
                detection_result['detected_faces'] = len(face_results.detections)
                detection_result['confidence'] += 0.4
                logger.info(f"Detected {len(face_results.detections)} faces")
            
            # 2. Pose Detection
            pose_results = self.mp_pose.process(rgb_image)
            if pose_results.pose_landmarks:
                detection_result['has_pose'] = True
                detection_result['confidence'] += 0.3
                logger.info("Detected human pose")
            
            # 3. Image characteristics analysis
            height, width = rgb_image.shape[:2]
            detection_result['image_characteristics'] = {
                'aspect_ratio': width / height,
                'resolution': f"{width}x{height}",
                'is_portrait': height > width,
                'is_high_res': width > 1000 or height > 1000
            }
            
            # 4. Determine image type and best removal method
            human_confidence = detection_result['confidence']
            
            if human_confidence >= 0.6:  # Strong human detection
                detection_result['primary_type'] = 'human'
                detection_result['detected_humans'] = 1
                
                # For humans, choose between MediaPipe and rembg based on image characteristics
                if (detection_result['image_characteristics']['is_portrait'] and 
                    detection_result['detected_faces'] > 0):
                    # Portrait with face - MediaPipe excels here
                    detection_result['recommended_remover'] = 'mediapipe'
                else:
                    # Full body or complex human scenes - rembg human models
                    detection_result['recommended_remover'] = 'rembg'
                    detection_result['recommended_model'] = 'u2net_human_seg'
                    
            elif human_confidence >= 0.3:  # Possible human
                detection_result['primary_type'] = 'human_possible'
                detection_result['recommended_remover'] = 'rembg'
                detection_result['recommended_model'] = 'u2net_human_seg'
                
            else:  # Likely object/product
                detection_result['primary_type'] = 'object'
                detection_result['recommended_remover'] = 'rembg'
                
                # Choose best rembg model for objects
                if detection_result['image_characteristics']['is_portrait']:
                    detection_result['recommended_model'] = 'u2net'
                else:
                    detection_result['recommended_model'] = 'isnet-general-use'
            
            logger.info(f"Detection result: {detection_result['primary_type']} "
                       f"(confidence: {detection_result['confidence']:.2f}) "
                       f"-> {detection_result['recommended_remover']}")
            
        except Exception as e:
            logger.error(f"Error in content detection: {str(e)}")
            # Fallback to rembg general model
            detection_result['recommended_remover'] = 'rembg'
            detection_result['recommended_model'] = 'u2net'
            
        return detection_result
    
    def remove_background_mediapipe(self, image: Image.Image) -> Image.Image:
        """Remove background using MediaPipe selfie segmentation"""
        try:
            self._init_mediapipe()
            
            # Convert to format MediaPipe expects
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.mp_selfie_segmentation.process(rgb_image)
            
            if results.segmentation_mask is not None:
                # Create mask
                mask = results.segmentation_mask
                mask = (mask > 0.5).astype(np.uint8) * 255
                
                # Convert back to PIL
                mask_pil = Image.fromarray(mask, mode='L')
                
                # Apply mask to original image
                image_rgba = image.convert('RGBA')
                image_rgba.putalpha(mask_pil)
                
                logger.info("MediaPipe background removal completed")
                return image_rgba
            else:
                logger.warning("MediaPipe segmentation failed, falling back to rembg")
                return self.remove_background_rembg(image, 'u2net_human_seg')
                
        except Exception as e:
            logger.error(f"MediaPipe background removal failed: {str(e)}")
            return self.remove_background_rembg(image, 'u2net_human_seg')
    
    def remove_background_rembg(self, image: Image.Image, model_name: str) -> Image.Image:
        """Remove background using rembg with specified model"""
        try:
            from rembg import remove
            
            session = self._init_rembg_session(model_name)
            if session:
                result = remove(image, session=session)
                logger.info(f"rembg background removal completed with model: {model_name}")
                return result
            else:
                # Fallback to basic rembg without session
                result = remove(image)
                logger.info("rembg background removal completed with default model")
                return result
                
        except Exception as e:
            logger.error(f"rembg background removal failed: {str(e)}")
            raise
    
    def process_image(self, image: Image.Image) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Main processing function that detects image content and removes background
        using the optimal method
        """
        # Step 1: Detect image content
        detection_result = self.detect_image_content(image)
        
        # Step 2: Remove background using recommended method
        try:
            if detection_result['recommended_remover'] == 'mediapipe':
                processed_image = self.remove_background_mediapipe(image)
            else:
                processed_image = self.remove_background_rembg(
                    image, 
                    detection_result['recommended_model']
                )
            
            # Clean up memory
            gc.collect()
            
            return processed_image, detection_result
            
        except Exception as e:
            logger.error(f"Background removal failed: {str(e)}")
            # Final fallback
            try:
                processed_image = self.remove_background_rembg(image, 'u2net')
                detection_result['recommended_remover'] = 'rembg'
                detection_result['recommended_model'] = 'u2net'
                return processed_image, detection_result
            except Exception as fallback_error:
                logger.error(f"Fallback removal also failed: {str(fallback_error)}")
                raise Exception("All background removal methods failed")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.mp_selfie_segmentation:
                self.mp_selfie_segmentation.close()
            if self.mp_pose:
                self.mp_pose.close()
            if self.mp_face_detection:
                self.mp_face_detection.close()
            
            # Clear sessions
            self.rembg_sessions.clear()
            gc.collect()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
