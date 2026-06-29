"""
TikTok Camera: Peace Sign Blur Effect
--------------------------------------
- Detects any one hand showing peace/victory sign → blur camera
- No peace sign → clear camera
- Background music playback (loop)
- Press ESC or TAB to exit

Dependencies:
    pip install opencv-python mediapipe==0.10.14 pygame numpy
"""

import os
import threading

import cv2
import mediapipe as mp
import numpy as np
import pygame


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Untuk WSL: ganti CAMERA_SOURCE ke URL HP kamu
# Contoh IP Webcam Android : "http://192.168.1.5:8080/video"
# Contoh DroidCam Android  : "http://192.168.1.5:4747/video"
# Untuk webcam lokal (Windows/Linux): set ke 0
CAMERA_SOURCE: str | int = "http://10.13.76.78:8080/video"

FRAME_WIDTH: int = 1280
FRAME_HEIGHT: int = 720

# Resolusi yang dikirim ke MediaPipe — lebih kecil = lebih cepat deteksi
DETECT_WIDTH: int = 320
DETECT_HEIGHT: int = 240

BLUR_KERNEL_SIZE: tuple[int, int] = (61, 61)
MUSIC_FILE: str = "music.mp3"
MUSIC_VOLUME: float = 0.5
MIN_DETECTION_CONFIDENCE: float = 0.7
MIN_TRACKING_CONFIDENCE: float = 0.5
WINDOW_NAME: str = "TikTok Blur Cam – Peace Sign"
WINDOW_WIDTH: int = 960
WINDOW_HEIGHT: int = 540
EXIT_KEYS: frozenset[int] = frozenset({27, 9})  # ESC = 27, TAB = 9

# MediaPipe finger landmark indices: (tip, pip)
_FINGER_PAIRS: tuple[tuple[int, int], ...] = (
    (8, 6),    # index
    (12, 10),  # middle
    (16, 14),  # ring
    (20, 18),  # pinky
)


# ---------------------------------------------------------------------------
# Frame reader (background thread — always returns the latest frame)
# ---------------------------------------------------------------------------

class FrameReader:
    """
    Reads frames from the camera in a background daemon thread.
    Solves IP stream buffer buildup by continuously draining the buffer
    and exposing only the most recent frame.
    """

    def __init__(self, cap: cv2.VideoCapture) -> None:
        self._cap = cap
        self._frame: np.ndarray | None = None
        self._lock = threading.Lock()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while self._running:
            ret, frame = self._cap.read()
            if ret:
                with self._lock:
                    self._frame = frame

    def latest(self) -> np.ndarray | None:
        """Return a copy of the most recent frame, or None if not ready yet."""
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def stop(self) -> None:
        self._running = False
        self._thread.join(timeout=2)


# ---------------------------------------------------------------------------
# Initialisation helpers
# ---------------------------------------------------------------------------

def init_camera() -> cv2.VideoCapture:
    """
    Open and configure the camera.
    Supports both local index (int) and network stream URL (str).
    Raises RuntimeError on failure.
    """
    cap = cv2.VideoCapture(CAMERA_SOURCE)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera source: {CAMERA_SOURCE!r}")
    if isinstance(CAMERA_SOURCE, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def init_hands() -> tuple:
    """Return (Hands detector, HAND_CONNECTIONS, drawing_utils)."""
    mp_hands = mp.solutions.hands
    detector = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    )
    return detector, mp_hands.HAND_CONNECTIONS, mp.solutions.drawing_utils


def init_music(path: str) -> bool:
    """
    Initialise pygame mixer and start looping music.
    Returns True if music started successfully, False otherwise.
    """
    try:
        pygame.mixer.init()
        if not os.path.exists(path):
            print(f"[WARN] Music file not found: {path!r}. Running without music.")
            return False
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(loops=-1)
        print(f"[INFO] Playing music: {path!r}")
        return True
    except Exception as exc:
        print(f"[WARN] Could not start music: {exc}")
        return False


# ---------------------------------------------------------------------------
# Hand / gesture helpers
# ---------------------------------------------------------------------------

def _is_extended(landmark, tip_idx: int, pip_idx: int) -> bool:
    """A finger is extended when its tip is above (lower y) its PIP joint."""
    return landmark[tip_idx].y < landmark[pip_idx].y


def is_peace_sign(hand_landmarks) -> bool:
    """
    Return True if the hand is showing a peace/victory sign.

    Criteria:
      - Index  finger: extended
      - Middle finger: extended
      - Ring   finger: curled
      - Pinky  finger: curled
    """
    lm = hand_landmarks.landmark
    index_up   = _is_extended(lm, *_FINGER_PAIRS[0])
    middle_up  = _is_extended(lm, *_FINGER_PAIRS[1])
    ring_down  = not _is_extended(lm, *_FINGER_PAIRS[2])
    pinky_down = not _is_extended(lm, *_FINGER_PAIRS[3])
    return index_up and middle_up and ring_down and pinky_down


# ---------------------------------------------------------------------------
# Frame processing
# ---------------------------------------------------------------------------

def apply_blur(frame: np.ndarray) -> np.ndarray:
    """Apply a strong Gaussian blur to the entire frame."""
    return cv2.GaussianBlur(frame, BLUR_KERNEL_SIZE, 0)


def draw_landmarks(
    frame: np.ndarray,
    multi_hand_landmarks,
    connections,
    drawing_utils,
) -> None:
    """Overlay MediaPipe hand skeleton on *frame* in-place."""
    if not multi_hand_landmarks:
        return
    for hand_lm in multi_hand_landmarks:
        drawing_utils.draw_landmarks(frame, hand_lm, connections)


def draw_ui(frame: np.ndarray, blurred: bool) -> None:
    """Overlay status text and hints on *frame* in-place."""
    h = frame.shape[0]

    status_text  = "BLUR ON – Peace!" if blurred else "BLUR OFF"
    status_color = (0, 220, 255) if blurred else (0, 255, 100)
    cv2.putText(frame, status_text, (20, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 1.3, status_color, 3, cv2.LINE_AA)

    cv2.putText(frame, "ESC / TAB  -  exit", (20, h - 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1, cv2.LINE_AA)


def process_frame(
    frame: np.ndarray,
    detector,
    connections,
    drawing_utils,
) -> np.ndarray:
    """
    Run hand detection on a downscaled copy of *frame* for speed,
    apply blur effect on full-res frame if peace sign detected,
    draw UI, and return the final output frame.
    """
    # Downscale only for MediaPipe — landmark coords are normalised (0-1)
    # so gesture logic works regardless of resolution
    small = cv2.resize(frame, (DETECT_WIDTH, DETECT_HEIGHT))
    rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    rgb.flags.writeable = False
    results = detector.process(rgb)

    peace_detected = any(
        is_peace_sign(hand) for hand in (results.multi_hand_landmarks or [])
    )

    output = apply_blur(frame) if peace_detected else frame

    if not peace_detected:
        draw_landmarks(output, results.multi_hand_landmarks, connections, drawing_utils)

    draw_ui(output, peace_detected)
    return output


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def cleanup(reader: FrameReader, cap: cv2.VideoCapture, detector) -> None:
    """Release all resources gracefully."""
    reader.stop()
    cap.release()
    detector.close()
    cv2.destroyAllWindows()
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    pygame.quit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> None:
    """Main application loop."""
    pygame.init()

    cap    = init_camera()
    reader = FrameReader(cap)
    detector, connections, drawing_utils = init_hands()
    init_music(MUSIC_FILE)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)
    print("[INFO] Camera started. Press ESC or TAB to exit.")

    try:
        while True:
            frame = reader.latest()
            if frame is None:
                # Thread belum dapat frame pertama, tunggu sebentar
                if cv2.waitKey(1) & 0xFF in EXIT_KEYS:
                    break
                continue

            frame  = cv2.flip(frame, 1)
            output = process_frame(frame, detector, connections, drawing_utils)
            cv2.imshow(WINDOW_NAME, output)

            if cv2.waitKey(1) & 0xFF in EXIT_KEYS:
                print("[INFO] Exit key pressed. Shutting down.")
                break
    finally:
        cleanup(reader, cap, detector)


if __name__ == "__main__":
    run()
