#!/usr/bin/env python3
"""
AnonSurf GUI Control Panel v2.1
Compatibile con Python 3.10+ incluso 3.13

NOVITÀ v2.1:
- Integrazione nel menu di sistema
- Due voci: GUI completa + GUI Mini
- Installazione in /opt/anonsurf-gui
- Link simbolici in /usr/local/bin
- Bandiere nazionali embedded (PNG base64)
- 68 paesi supportati
- Zero dipendenze esterne per le bandiere
- Funziona offline e sotto Tor
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import sys
import json
import ssl
import urllib.request
import threading
import subprocess
import shutil
import atexit
import signal
import configparser
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
import time
import re

# Directory base (dove si trova lo script)
BASE_DIR = Path(__file__).parent.absolute()

# ============================================================================
# BANDIERE PNG EMBEDDED (Base64) - 32x24 pixel
# ============================================================================
FLAGS_BASE64 = {
    "AE": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAL0lEQVR4nGNk6HFloCVgoqnpoxaMWkAVwPj//3+aWjD0g2jUghFgwSgYBaOAgQEARg0D7Wn50FQAAAAASUVORK5CYII=",
    "AR": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAMUlEQVR4nGNkCFrKQEvARFPTRy0YtYAqgPH///80tWDoB9GoBSPAAsbR+mDUglELGAChkgUZyuU5UgAAAABJRU5ErkJggg==",
    "AT": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAL0lEQVR4nGP8z0BbwERj80ctGLWACoCF4T9tc8LQD6JRC0aABYyj9cGoBaMWMAAADq4ELZ4GLhcAAAAASUVORK5CYII=",
    "AU": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJklEQVR4nGNkUKlloCVgoqnpoxaMWjBqwagFoxaMWjBqwagFVAMAmgsA0bAdUPoAAAAASUVORK5CYII=",
    "BE": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAMElEQVR4nGNkwAv+n8UrbYxfNwMDAwMTYSWUgVELRi0YtWDUglELRi0YtWDUAuoAAMZzAi+aQA43AAAAAElFTkSuQmCC",
    "BG": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8//8/Ay0BE01NH7Vg1AKqAEaGHleaWjD0g2jUghFgASNta4PhEESjFowACwD4LQT7g+cFmgAAAABJRU5ErkJggg==",
    "BR": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAMklEQVR4nGNk6HFloCVgoqnpoxaMWkAVwPj/LG0tGPpBNGrBCLCAhXH/aH0wasGItwAARlQD012oiyQAAAAASUVORK5CYII=",
    "BY": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAL0lEQVR4nGP8z0BbwERj80ctGLWACoCRoceVphYM/SAatWAEWMA4Wh+MWjBqAQMA3koC/YN3KEUAAAAASUVORK5CYII=",
    "CA": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAL0lEQVR4nO3NsREAAAjCQHD/nXUDLLRMWuXerVjHu53Xkmr9OAYAAAAAAAAA8NMA4ZoDL2N5Cq8AAAAASUVORK5CYII=",
    "CH": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAS0lEQVR4nGP8z0BbwERj80ctGAQWsJCg9j9qimNkJEbT0A8imlvAiDMn/ycxj+OIkqEfREPfAtyRjAlGMxptAClxQBYY+kE09C0AALACCiuvs936AAAAAElFTkSuQmCC",
    "CL": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALUlEQVR4nGP8//8/Ay0BE01NH7Vg1IJRC4aJBYy0LYmGQxCNWjBqwagFdLAAAI3fBCtjrH6FAAAAAElFTkSuQmCC",
    "CN": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJElEQVR4nGP8z0BbwERj80ctGLVg1IJRC0YtGLVg1IJRC6gEAPHIAS8Wxt4fAAAAAElFTkSuQmCC",
    "CO": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8f5aBpoCJtsaPWjBqATUAI4NKLU0tGPpBNGrBCLCA8T+NLRj6QTRqwQiwAAACeQOazt9irAAAAABJRU5ErkJggg==",
    "CZ": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALUlEQVR4nGP8//8/Ay0BE01NH7Vg1IJRC4aJBYy0LYmGQxCNWjBqwagFdLAAAI3fBCtjrH6FAAAAAElFTkSuQmCC",
    "DE": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAK0lEQVR4nGNgGAWjYBQw/qexBUw0Nn/UglELqABYGM7S1oKhH0SjFowACwDlXwHuaIlc7wAAAABJRU5ErkJggg==",
    "DK": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAPElEQVR4nGP8z4AD/EeSYWTEpYogYCJb56gFoxaMWkA0YPz/H2depgoY+kFEhzjAJTNamo5aMGrB0LEAAN52CSl9AuS6AAAAAElFTkSuQmCC",
    "EE": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALUlEQVR4nGNkCFrKQEvARFPTRy0YtWAUjIJRQCXA+P//f5paMPSLilELRoAFAGIZBBN65YmPAAAAAElFTkSuQmCC",
    "EG": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALElEQVR4nGP8z0BbwERj80ctGLWACoCF4T9tc8LQD6JRC0aABaNgFIwCBgYA8jkDH0x7T+gAAAAASUVORK5CYII=",
    "ES": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALklEQVR4nGP8z0BbwERj80ctGLWACoCF4SxtLRj6QTRqwQiwgHG0Phi1YNQCBgDYhwL8DyvpsQAAAABJRU5ErkJggg==",
    "FI": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAPklEQVR4nGP8//8/AzbAGLwMzv6/NgqrGmIAE9k6Ry0YtWDUAqIBI0PQUppaQDDHv2MAACAASURBVEM/iGgfB6Ol6agFoxYMAwsAAR5MNHw8P/GIAAAAASUVORK5CYII=",
    "FR": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAN0lEQVR4nGNkUKllwA3+327CI8vAyIhPloGBgYGBiaAKCsGoBaMWjFowasGoBaMWjFowagF1AADWlgMv2avmuQAAAABJRU5ErkJggg==",
    "GB": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJklEQVR4nGNkUKlloCVgoqnpoxaMWjBqwagFoxaMWjBqwagFVAMAmgsA0bAdUPoAAAAASUVORK5CYII=",
    "GR": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAOklEQVR4nGNkCFrKQEvARFPTGRgYGP///09TC2jvg9E4IARG44AgGI0DgmA0DgiCoR8HoxaMWkA5AABNgxDvX1sPCgAAAABJRU5ErkJggg==",
    "HK": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJElEQVR4nGP8z0BbwERj80ctGLVg1IJRC0YtGLVg1IJRC6gEAPHIAS8Wxt4fAAAAAElFTkSuQmCC",
    "HR": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8z0BbwERj80ctGLWACoCF4T9tc8LQD6JRC0aABYwMKrU0tWDoB9GoBSPAAgDw4APPxZnTvQAAAABJRU5ErkJggg==",
    "HU": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8z0BbwERj80ctGLWACoCF4T9tc8LQD6JRC0aABYwMPa40tWDoB9GoBSPAAgCCRwP/kxcb+AAAAABJRU5ErkJggg==",
    "ID": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALUlEQVR4nGP8z0BbwERj80ctGLVg1IJhYQELw3/alkZDP4hGLRi1YNQCOlgAAAVjAy/40EQfAAAAAElFTkSuQmCC",
    "IE": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAN0lEQVR4nGNk6HFlwA3+F+/CI8vQy4hPloGBgYGBiaAKCsGoBaMWjFowasGoBaMWjFowagF1AACzuQO7jF+TGgAAAABJRU5ErkJggg==",
    "IL": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAMUlEQVR4nGP8//8/Ay0BE01NH7Vg1AKqAEYGlVqaWjD0g2jUghFgAeNofTBqwagFDADalQbJA1E9uwAAAABJRU5ErkJggg==",
    "IN": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANklEQVR4nGP838NAU8BEW+NHLRi1gBqA8f///zS1YOgH0agFI8ACRoYeV5paMPSDaNSCEWABAHG1BYfTQCZwAAAAAElFTkSuQmCC",
    "IR": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGNk6HFloCVgoqnpoxaMWkAVwPj//3+aWjD0g2jUghFgASNtc8FwCKJRC0aABQBicwT7Jmh/twAAAABJRU5ErkJggg==",
    "IS": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAQUlEQVR4nGNkUKllwAbu/NoBZ6uweWBVQwxgIlvnqAWjFoxaQDRgvCNnSlMLhn4Q0dwCFlwl5WhpOmrBqAVDyAIAktoIc9zOjs8AAAAASUVORK5CYII=",
    "IT": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAN0lEQVR4nGNk6HFlwA3+F+/CI8vAyIhPloGBgYGBiaAKCsGoBaMWjFowasGoBaMWjFowagF1AADcNgMv1W1gqgAAAABJRU5ErkJggg==",
    "JP": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAb0lEQVR4nO2VQQ7AIAgEu03//2U81ZswmNraKCcOZEdYgjKzY2ScQ9U34KcAKVV+9ejWHKw466D1atANAPgqEWNCkx8GkJ1xayIAOYVuzecjegPgTymaIeugpQIcwqeiaknI+TvyHiS/2BlMXh1QAHrHFzG5L0uyAAAAAElFTkSuQmCC",
    "KE": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALElEQVR4nGNgGAWjYBQw/qexBUw0Nn/UglELqAAYGXpcaWrB0A+iUQtGgAUA6BoB7ymMPJIAAAAASUVORK5CYII=",
    "KR": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJklEQVR4nO3NMQEAAAjDMMC/52ECvlRA00nqs3m9AwAAAAAAAJy1C7oDLV5LB/0AAAAASUVORK5CYII=",
    "LT": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8f5aBpoCJtsaPWjBqATUAC+N+V5paMPSDaNSCEWAB438aWzD0g2jUghFgAQByeAQBuEf21AAAAABJRU5ErkJggg==",
    "LU": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8z0BbwERj80ctGLWACoCF4T9tc8LQD6JRC0aABYwMQUtpasHQD6JRC0aABQD0ywQlq8j2jQAAAABJRU5ErkJggg==",
    "LV": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAMUlEQVR4nGOcraLMQEvARFPTRy0YtYAqgPH///80tWDoB9GoBSPAAsbR+mDUglELGAClcQTv0dn2iQAAAABJRU5ErkJggg==",
    "MA": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJElEQVR4nGP8z0BbwERj80ctGLVg1IJRC0YtGLVg1IJRC6gEAPHIAS8Wxt4fAAAAAElFTkSuQmCC",
    "MD": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAM0lEQVR4nGNkUKllwA3+r2zGI8tgjE8SApgIK6EMjFowasGoBaMWjFowasGoBaMWUAcAANDYAy92gKBFAAAAAElFTkSuQmCC",
    "MX": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAN0lEQVR4nGNk6HFlwA3+F+/CI8vAyIhPloGBgYGBiaAKCsGoBaMWjFowasGoBaMWjFowagF1AADcNgMv1W1gqgAAAABJRU5ErkJggg==",
    "MY": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANUlEQVR4nGP8z0BbwERj82lvAQvDf9oG0tAPIsbRVEQIjKYigmA0FREEo6mIIBhNRaMWUA4AhWIKKRD7uykAAAAASUVORK5CYII=",
    "NG": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGNk6HFlwA3+F+/CI8vY64ZHFgKYCKqgEIxaMGrBqAWjFoxaMGrBqAWjFlAHAAAfPgQBGDQDFQAAAABJRU5ErkJggg==",
    "NL": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8z0BbwERj80ctGLWACoCF4T9tc8LQD6JRC0aABYwMKrU0tWDoB9GoBSPAAgDw4APPxZnTvQAAAABJRU5ErkJggg==",
    "NO": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAO0lEQVR4nGP8z4AdMCpEw9n/HyzFoYowYCJb56gFoxaMWkA0YGRAyrG0AEM/iGgfB6Ol6agFoxYMAwsACVMIpwUa+RAAAAAASUVORK5CYII=",
    "NZ": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJklEQVR4nGNkUKlloCVgoqnpoxaMWjBqwagFoxaMWjBqwagFVAMAmgsA0bAdUPoAAAAASUVORK5CYII=",
    "PE": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAL0lEQVR4nO3NsREAAAjCQHD/nXUDLLRMWuXerVjHu53Xkmr9OAYAAAAAAAAA8NMA4ZoDL2N5Cq8AAAAASUVORK5CYII=",
    "PH": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALUlEQVR4nGNkUKlloCVgoqnpoxaMWjBqwTCxgPE/jS0Y+kE0asGoBaMW0MECABw/Ac9XhTanAAAAAElFTkSuQmCC",
    "PK": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJklEQVR4nGNk6HFloCVgoqnpoxaMWjBqwagFoxaMWjBqwagFVAMAToEBARE0704AAAAASUVORK5CYII=",
    "PL": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALUlEQVR4nGP8//8/Ay0BE01NH7Vg1IJRC4aJBYy0LYmGQxCNWjBqwagFdLAAAI3fBCtjrH6FAAAAAElFTkSuQmCC",
    "PT": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALklEQVR4nGNk6HFlwA3+l+zGI0sMYKJQ/6gFoxaMWjBqwagFoxaMWjBqAZ0sAADccgMvytfIggAAAABJRU5ErkJggg==",
    "RO": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAM0lEQVR4nGNkUKllwA3+r2zGI8tgjE8SApgIK6EMjFowasGoBaMWjFowasGoBaMWUAcAANDYAy92gKBFAAAAAElFTkSuQmCC",
    "RS": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8z0BbwERj80ctGLWACoCRQaWWphYM/SAatWAEWMD4/z9ta4ShH0SjFowACwDAsgTLJ2FBigAAAABJRU5ErkJggg==",
    "RU": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8//8/Ay0BE01NH7Vg1AKqAEYGlVqaWjD0g2jUghFgASNta4PhEESjFowACwDVRgTLejW+TAAAAABJRU5ErkJggg==",
    "SA": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJklEQVR4nGNk6HFloCVgoqnpoxaMWjBqwagFoxaMWjBqwagFVAMAToEBARE0704AAAAASUVORK5CYII=",
    "SE": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAP0lEQVR4nGNkyFrOgA38T46EsxnnYldDDGAiW+eoBaMWjFpANGD8f5a2Fgz9IKK5BSy4SsrR0nTUglELhpAFANZoClOH1rXNAAAAAElFTkSuQmCC",
    "SG": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALUlEQVR4nGP8z0BbwERj80ctGLVg1IJhYQELw3/alkZDP4hGLRi1YNQCOlgAAAVjAy/40EQfAAAAAElFTkSuQmCC",
    "SI": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8//8/Ay0BE01NH7Vg1AKqAEYGlVqaWjD0g2jUghFgASNta4PhEESjFowACwDVRgTLejW+TAAAAABJRU5ErkJggg==",
    "SK": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8//8/Ay0BE01NH7Vg1AKqAEYGlVqaWjD0g2jUghFgASNta4PhEESjFowACwDVRgTLejW+TAAAAABJRU5ErkJggg==",
    "TH": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAO0lEQVR4nGP8z0BbwERj84eBBSwM/2kbC0M/iGhuASNDjytNLRj6QUT7OPg/mg8G2gJGBpVamlow9INo1IIRYAEAcRkHm+Bynt0AAAAASUVORK5CYII=",
    "TR": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJElEQVR4nGP8z0BbwERj80ctGLVg1IJRC0YtGLVg1IJRC6gEAPHIAS8Wxt4fAAAAAElFTkSuQmCC",
    "TW": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJElEQVR4nGP8z0BbwERj80ctGLVg1IJRC0YtGLVg1IJRC6gEAPHIAS8Wxt4fAAAAAElFTkSuQmCC",
    "UA": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAALklEQVR4nGNkCFrKQEvARFPTRy0YtWDUgmFiAeP/s7S1YOgH0agFoxaMWkAHCwDMVwLyEM5jTAAAAABJRU5ErkJggg==",
    "US": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANUlEQVR4nGP8z0BbwERj82lvAQvDf9oG0tAPIsbRVEQIjKYigmA0FREEo6mIIBhNRaMWUA4AhWIKKRD7uykAAAAASUVORK5CYII=",
    "VE": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAANElEQVR4nGP8f5aBpoCJtsaPWjBqATUAI4NKLU0tGPpBNGrBCLCA8T+NLRj6QTRqwQiwAAACeQOazt9irAAAAABJRU5ErkJggg==",
    "VN": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAJElEQVR4nGP8z0BbwERj80ctGLVg1IJRC0YtGLVg1IJRC6gEAPHIAS8Wxt4fAAAAAElFTkSuQmCC",
    "ZA": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAIAAAAUMWhjAAAAQUlEQVR4nGP8z0BbwERj84eBBSwM/2kbC0M/iGhuASNDjytNLRj6QUT7OPg/mg8G2gJGBpVamlow9INo1IIRYAEAcRkHm+Bynt0AAAAASUVORK5CYII=",
}
# Totale: 68 bandiere


class Config:
    """Gestisce la configurazione da config.ini"""
    
    DEFAULT_CONFIG = {
        'network': {
            'tor_check_api': 'https://check.torproject.org/api/ip',
            'ip_apis': 'https://api.ipify.org,https://icanhazip.com,https://checkip.amazonaws.com',
            'geo_api': 'http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,isp,reverse,query',
        },
        'timing': {
            'api_timeout': '10',
            'api_timeout_fast': '5',
            'anonsurf_timeout': '60',
            'tor_bootstrap_wait': '45',
            'tor_stop_wait': '8',
            'refresh_interval': '15000',
            'auto_change_interval': '100000',
            'tor_verify_attempts': '15',
            'tor_verify_interval': '3'
        },
        'gui': {
            'window_width': '700',
            'window_height': '750',
            'max_log_lines': '100'
        },
        'logging': {
            'enable_file_log': 'true',
            'log_filename': 'anonsurf_gui.log',
            'log_level': 'INFO',
            'max_log_size': '5242880',
            'log_backup_count': '3'
        }
    }
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = BASE_DIR / 'config.ini'
        self._load_config()
    
    def _load_config(self):
        for section, values in self.DEFAULT_CONFIG.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in values.items():
                self.config.set(section, key, value)
        
        if self.config_file.exists():
            try:
                self.config.read(self.config_file)
            except Exception as e:
                print(f"Errore lettura config.ini: {e}")
    
    def get(self, section, key, fallback=None):
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def get_int(self, section, key, fallback=0):
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_bool(self, section, key, fallback=False):
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_list(self, section, key, fallback=None):
        try:
            value = self.config.get(section, key)
            return [x.strip() for x in value.split(',')]
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback or []


CONFIG = Config()


class AppLogger:
    """Logger con supporto file e GUI"""
    
    DIAGNOSTIC_MESSAGES = {
        'tor_not_starting': (
            "Tor non si avvia. Possibili cause:\n"
            "  • Servizio Tor già in esecuzione\n"
            "  • Porte 9050/9051 occupate\n"
            "  • Firewall che blocca\n"
            "Prova: sudo systemctl stop tor && sudo anonsurf start"
        ),
        'tor_bootstrap_timeout': (
            "Bootstrap Tor timeout. Possibili cause:\n"
            "  • Connessione internet instabile\n"
            "  • ISP che blocca Tor\n"
            "  • Necessità di bridge Tor\n"
            "Verifica connessione e riprova."
        ),
        'anonsurf_not_found': (
            "AnonSurf non trovato.\n"
            "Esegui: sudo ./install.sh"
        ),
        'operation_cancelled': (
            "Operazione annullata dall'utente."
        )
    }
    
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.file_logger = None
        self._setup_file_logger()
    
    def _setup_file_logger(self):
        if not CONFIG.get_bool('logging', 'enable_file_log', True):
            return
        
        log_file = BASE_DIR / CONFIG.get('logging', 'log_filename', 'anonsurf_gui.log')
        log_level = getattr(logging, CONFIG.get('logging', 'log_level', 'INFO').upper(), logging.INFO)
        max_size = CONFIG.get_int('logging', 'max_log_size', 5242880)
        backup_count = CONFIG.get_int('logging', 'log_backup_count', 3)
        
        self.file_logger = logging.getLogger('AnonSurfGUI')
        self.file_logger.setLevel(log_level)
        self.file_logger.handlers.clear()
        
        if max_size > 0:
            handler = RotatingFileHandler(log_file, maxBytes=max_size, backupCount=backup_count)
        else:
            handler = logging.FileHandler(log_file)
        
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        self.file_logger.addHandler(handler)
    
    def _log_to_file(self, level, message):
        if self.file_logger:
            log_func = getattr(self.file_logger, level.lower(), self.file_logger.info)
            log_func(message)
    
    def _log_to_gui(self, message):
        if self.gui_callback:
            self.gui_callback(message)
    
    def info(self, message, gui=True):
        self._log_to_file('INFO', message)
        if gui:
            self._log_to_gui(message)
    
    def warning(self, message, gui=True):
        self._log_to_file('WARNING', message)
        if gui:
            self._log_to_gui(f"⚠ {message}")
    
    def error(self, message, diagnostic_key=None, gui=True):
        self._log_to_file('ERROR', message)
        if gui:
            self._log_to_gui(f"✗ {message}")
        
        if diagnostic_key and diagnostic_key in self.DIAGNOSTIC_MESSAGES:
            diag_msg = self.DIAGNOSTIC_MESSAGES[diagnostic_key]
            self._log_to_file('ERROR', f"DIAGNOSTICA: {diag_msg}")
    
    def debug(self, message):
        self._log_to_file('DEBUG', message)
    
    def success(self, message, gui=True):
        self._log_to_file('INFO', f"SUCCESS: {message}")
        if gui:
            self._log_to_gui(f"✓ {message}")


class NetworkStateManager:
    """Gestisce salvataggio e ripristino stato rete"""
    
    def __init__(self, logger):
        self.state_dir = Path('/tmp/anonsurf_gui_state')
        self.tor_was_active_on_start = False
        self.network_saved = False
        self.logger = logger
        self.original_ip = None
    
    def save_network_state(self):
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            
            resolv_conf = Path('/etc/resolv.conf')
            if resolv_conf.exists():
                shutil.copy2(resolv_conf, self.state_dir / 'resolv.conf.backup')
            
            try:
                result = subprocess.run(['iptables-save'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    (self.state_dir / 'iptables.backup').write_text(result.stdout)
            except Exception:
                pass
            
            state_info = {
                'timestamp': datetime.now().isoformat(),
                'tor_was_active': self.tor_was_active_on_start,
                'original_ip': self.original_ip
            }
            (self.state_dir / 'state.json').write_text(json.dumps(state_info))
            
            self.network_saved = True
            return True
        except Exception as e:
            self.logger.debug(f"Errore salvataggio stato rete: {e}")
            return False
    
    def restore_network_state(self):
        if not self.network_saved or not self.state_dir.exists():
            return False
        
        try:
            backup_resolv = self.state_dir / 'resolv.conf.backup'
            if backup_resolv.exists():
                shutil.copy2(backup_resolv, '/etc/resolv.conf')
            
            for cmd in [
                ['iptables', '-F'],
                ['iptables', '-t', 'nat', '-F'],
                ['iptables', '-t', 'mangle', '-F'],
                ['iptables', '-P', 'INPUT', 'ACCEPT'],
                ['iptables', '-P', 'FORWARD', 'ACCEPT'],
                ['iptables', '-P', 'OUTPUT', 'ACCEPT']
            ]:
                subprocess.run(cmd, capture_output=True, timeout=10)
            
            for service in ['NetworkManager', 'networking', 'systemd-networkd']:
                try:
                    result = subprocess.run(['systemctl', 'restart', service], capture_output=True, timeout=30)
                    if result.returncode == 0:
                        break
                except Exception:
                    continue
            
            return True
        except Exception as e:
            self.logger.debug(f"Errore ripristino rete: {e}")
            return False
    
    def cleanup(self):
        try:
            if self.state_dir.exists():
                shutil.rmtree(self.state_dir)
        except Exception:
            pass


class TorManager:
    """Gestisce operazioni AnonSurf/Tor con cancellazione"""
    
    def __init__(self, logger):
        self.logger = logger
        self.anonsurf_path = None
        self._find_anonsurf()
        
        self._cancel_flag = threading.Event()
        self._operation_lock = threading.Lock()
        self._current_operation = None
    
    def _find_anonsurf(self):
        paths = ['/usr/bin/anonsurf', '/usr/local/bin/anonsurf', '/usr/sbin/anonsurf']
        
        for path in paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                self.anonsurf_path = path
                return path
        
        try:
            result = subprocess.run(['which', 'anonsurf'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.anonsurf_path = result.stdout.strip()
                return self.anonsurf_path
        except Exception:
            pass
        
        return None
    
    def is_available(self):
        if not self.anonsurf_path:
            self._find_anonsurf()
        return self.anonsurf_path is not None
    
    def cancel_operation(self):
        self._cancel_flag.set()
        self.logger.info("Richiesta annullamento operazione...")
    
    def is_cancelled(self):
        return self._cancel_flag.is_set()
    
    def _reset_cancel(self):
        self._cancel_flag.clear()
    
    def execute(self, command, timeout=None):
        if not self.is_available():
            self.logger.error("AnonSurf non disponibile", diagnostic_key='anonsurf_not_found')
            return False, "", "AnonSurf non trovato", -1
        
        if timeout is None:
            timeout = CONFIG.get_int('timing', 'anonsurf_timeout', 60)
        
        full_cmd = f"{self.anonsurf_path} {command}"
        self.logger.info(f"Esecuzione: {full_cmd}")
        
        try:
            process = subprocess.Popen(
                full_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                returncode = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                self.logger.error(f"Timeout comando '{command}'")
                return False, stdout, stderr, -1
            
            clean_stdout = re.sub(r'\x1b\[[0-9;]*m', '', stdout) if stdout else ""
            clean_stderr = re.sub(r'\x1b\[[0-9;]*m', '', stderr) if stderr else ""
            
            if clean_stdout.strip():
                for line in clean_stdout.strip().split('\n')[:5]:
                    self.logger.debug(f"  > {line[:60]}")
            
            success = returncode == 0
            if success:
                self.logger.success(f"Comando '{command}' completato")
            else:
                self.logger.warning(f"Comando '{command}' codice {returncode}")
            
            return success, stdout, stderr, returncode
            
        except Exception as e:
            self.logger.error(f"Errore esecuzione: {e}")
            return False, "", str(e), -1
    
    def start(self, progress_callback=None):
        with self._operation_lock:
            if self._current_operation:
                self.logger.warning("Operazione già in corso")
                return False
            self._current_operation = "start"
        
        self._reset_cancel()
        
        try:
            self.logger.info("Avvio AnonSurf...")
            
            success, stdout, stderr, rc = self.execute('start')
            
            if not success:
                self.logger.error("Comando start fallito", diagnostic_key='tor_not_starting')
                return False
            
            if self.is_cancelled():
                self.logger.info("Avvio annullato")
                return False
            
            verify_attempts = CONFIG.get_int('timing', 'tor_verify_attempts', 15)
            verify_interval = CONFIG.get_int('timing', 'tor_verify_interval', 3)
            
            self.logger.info(f"Verifica bootstrap ({verify_attempts} tentativi)...")
            
            for attempt in range(1, verify_attempts + 1):
                if self.is_cancelled():
                    self.logger.info("Verifica annullata", diagnostic_key='operation_cancelled')
                    return False
                
                if progress_callback:
                    progress_callback(attempt, verify_attempts)
                
                is_tor, ip = self._check_tor_status(fast=True)
                
                if is_tor:
                    self.logger.success(f"Tor ATTIVO! IP: {ip}")
                    return True
                
                self.logger.debug(f"Tentativo {attempt}/{verify_attempts}: non ancora attivo")
                
                for _ in range(verify_interval):
                    if self.is_cancelled():
                        return False
                    time.sleep(1)
            
            self.logger.error(
                f"Tor non attivo dopo {verify_attempts * verify_interval}s",
                diagnostic_key='tor_bootstrap_timeout'
            )
            return False
            
        finally:
            with self._operation_lock:
                self._current_operation = None
    
    def stop(self):
        if self._current_operation == "start":
            self.cancel_operation()
            time.sleep(1)
        
        with self._operation_lock:
            self._current_operation = "stop"
        
        try:
            self.logger.info("Arresto AnonSurf...")
            success, _, _, _ = self.execute('stop')
            
            if success:
                stop_wait = CONFIG.get_int('timing', 'tor_stop_wait', 8)
                time.sleep(stop_wait)
                self.logger.success("AnonSurf fermato")
                return True
            
            return False
        finally:
            with self._operation_lock:
                self._current_operation = None
    
    def change_identity(self):
        self.logger.info("Cambio identità...")
        success, _, _, _ = self.execute('change', timeout=30)
        
        if success:
            time.sleep(3)
            self.logger.success("Identità cambiata")
        
        return success
    
    def _check_tor_status(self, fast=False):
        api_url = CONFIG.get('network', 'tor_check_api', 'https://check.torproject.org/api/ip')
        
        if fast:
            timeout = CONFIG.get_int('timing', 'api_timeout_fast', 5)
        else:
            timeout = CONFIG.get_int('timing', 'api_timeout', 10)
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'curl/7.68.0'})
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                data = json.loads(r.read().decode())
                return data.get('IsTor', False), data.get('IP', '')
        except Exception as e:
            self.logger.debug(f"Check Tor fallito: {e}")
            return False, ""
    
    def get_status(self):
        is_tor, ip = self._check_tor_status()
        
        if not ip:
            ip = self._get_simple_ip()
        
        result = {
            'is_tor': is_tor,
            'ip': ip or '-',
            'timestamp': datetime.now().isoformat()
        }
        
        if ip and ip != '-':
            geo = self._get_geo_info(ip)
            result.update(geo)
        
        return result
    
    def _get_simple_ip(self):
        apis = CONFIG.get_list('network', 'ip_apis', ['https://api.ipify.org'])
        timeout = CONFIG.get_int('timing', 'api_timeout_fast', 5)
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        for url in apis:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                    ip = r.read().decode().strip()
                    if ip and len(ip) < 50:
                        return ip
            except Exception:
                continue
        
        return None
    
    def _get_geo_info(self, ip):
        geo_api = CONFIG.get('network', 'geo_api', 'http://ip-api.com/json/{ip}')
        url = geo_api.replace('{ip}', ip)
        timeout = CONFIG.get_int('timing', 'api_timeout', 10)
        
        result = {
            'city': '-', 'country': '-', 'country_code': '-',
            'region': '-', 'isp': '-', 'hostname': '-'
        }
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = json.loads(r.read().decode())
                if data.get('status') == 'success':
                    result['city'] = data.get('city', '-') or '-'
                    result['country'] = data.get('country', '-') or '-'
                    result['country_code'] = data.get('countryCode', '-') or '-'
                    result['region'] = data.get('regionName', '-') or '-'
                    result['isp'] = data.get('isp', '-') or '-'
                    result['hostname'] = data.get('reverse', '-') or '-'
        except Exception:
            pass
        
        return result


class ISPTorBlockChecker:
    """
    Verifica se l'ISP blocca la rete Tor.
    Testa la connettività verso Directory Authorities e servizi Tor.
    """
    
    # Tor Directory Authorities (IP e porte ORPort pubbliche)
    TOR_DIRECTORY_AUTHORITIES = [
        ("128.31.0.34", 9101),      # moria1 (MIT)
        ("86.59.21.38", 443),       # tor26
        ("194.109.206.212", 443),   # dizum
        ("199.58.81.140", 443),     # Faravahar
        ("204.13.164.118", 443),    # bastet
    ]
    
    # Endpoint per test connettività Tor
    TOR_CHECK_ENDPOINTS = [
        "https://check.torproject.org",
        "https://bridges.torproject.org",
        "https://www.torproject.org",
    ]
    
    # Endpoint per verificare connettività internet generale
    INTERNET_CHECK_ENDPOINTS = [
        "https://www.google.com",
        "https://www.cloudflare.com",
        "https://www.amazon.com",
    ]
    
    def __init__(self, logger=None):
        self.logger = logger
        self.check_timeout = 5
        self.results = {
            'internet_ok': False,
            'tor_sites_ok': False,
            'tor_authorities_ok': False,
            'likely_blocked': False,
            'details': []
        }
    
    def _log(self, message, level='info'):
        if self.logger:
            getattr(self.logger, level, self.logger.info)(message)
    
    def _check_tcp_port(self, host, port, timeout=3):
        """Verifica se una porta TCP è raggiungibile"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def _check_https_endpoint(self, url, timeout=5):
        """Verifica se un endpoint HTTPS è raggiungibile"""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return r.status == 200
        except Exception:
            return False
    
    def check_internet_connectivity(self):
        """Verifica connettività internet generale"""
        self._log("Verifica connettività internet...")
        
        for url in self.INTERNET_CHECK_ENDPOINTS:
            if self._check_https_endpoint(url, self.check_timeout):
                self.results['internet_ok'] = True
                self.results['details'].append(f"✓ Internet OK ({url})")
                return True
        
        self.results['details'].append("✗ Connessione internet non disponibile")
        return False
    
    def check_tor_sites(self):
        """Verifica raggiungibilità siti Tor Project"""
        self._log("Verifica siti Tor Project...")
        
        reachable = 0
        for url in self.TOR_CHECK_ENDPOINTS:
            if self._check_https_endpoint(url, self.check_timeout):
                reachable += 1
                self.results['details'].append(f"✓ Raggiungibile: {url}")
            else:
                self.results['details'].append(f"✗ Non raggiungibile: {url}")
        
        self.results['tor_sites_ok'] = reachable > 0
        return reachable > 0
    
    def check_tor_authorities(self):
        """Verifica connettività verso Tor Directory Authorities"""
        self._log("Verifica Directory Authorities Tor...")
        
        reachable = 0
        for host, port in self.TOR_DIRECTORY_AUTHORITIES:
            if self._check_tcp_port(host, port, timeout=3):
                reachable += 1
                self.results['details'].append(f"✓ Authority {host}:{port} raggiungibile")
            else:
                self.results['details'].append(f"✗ Authority {host}:{port} bloccato")
        
        # Consideriamo OK se almeno 2 authority sono raggiungibili
        self.results['tor_authorities_ok'] = reachable >= 2
        return reachable >= 2
    
    def run_full_check(self):
        """
        Esegue il controllo completo.
        Ritorna: (is_blocked, results_dict)
        """
        self.results = {
            'internet_ok': False,
            'tor_sites_ok': False,
            'tor_authorities_ok': False,
            'likely_blocked': False,
            'details': []
        }
        
        # Step 1: Verifica internet
        if not self.check_internet_connectivity():
            self.results['likely_blocked'] = False  # Non è blocco ISP, è assenza di connessione
            return False, self.results
        
        # Step 2: Verifica siti Tor
        self.check_tor_sites()
        
        # Step 3: Verifica Directory Authorities
        self.check_tor_authorities()
        
        # Determina se c'è blocco ISP
        # Blocco probabile se: internet OK ma sia siti Tor che authorities bloccati
        if self.results['internet_ok']:
            if not self.results['tor_sites_ok'] and not self.results['tor_authorities_ok']:
                self.results['likely_blocked'] = True
                self._log("⚠ Rilevato possibile blocco Tor da parte dell'ISP", 'warning')
            elif not self.results['tor_authorities_ok']:
                # Solo authorities bloccate - blocco parziale, potrebbe funzionare con bridge
                self.results['likely_blocked'] = True
                self._log("⚠ Directory Authorities bloccate - consigliato uso bridge", 'warning')
        
        return self.results['likely_blocked'], self.results
    
    @staticmethod
    def get_remediation_info():
        """Ritorna le informazioni per le attività correttive"""
        return {
            'title': "Rilevato Possibile Blocco Tor",
            'message': (
                "Il tuo ISP potrebbe bloccare l'accesso alla rete Tor.\n"
                "Le Directory Authorities di Tor non sono raggiungibili.\n\n"
                "ATTIVITÀ CORRETTIVE CONSIGLIATE:\n\n"
                "1. CONFIGURA BRIDGE TOR (Consigliato)\n"
                "   I bridge sono relay Tor non pubblici che aiutano\n"
                "   a bypassare la censura.\n\n"
                "   • Ottieni bridge da: https://bridges.torproject.org\n"
                "   • Oppure invia email a: bridges@torproject.org\n"
                "     con oggetto: get transport obfs4\n\n"
                "2. CONFIGURA /etc/tor/torrc:\n"
                "   Aggiungi le seguenti righe:\n"
                "   ─────────────────────────────\n"
                "   UseBridges 1\n"
                "   ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy\n"
                "   Bridge obfs4 <IP:PORT> <FINGERPRINT> cert=... iat-mode=0\n"
                "   ─────────────────────────────\n\n"
                "3. TRASPORTI PLUGGABLE ALTERNATIVI:\n"
                "   • obfs4 - Offuscamento traffico (più comune)\n"
                "   • meek-azure - Usa CDN Microsoft Azure\n"
                "   • snowflake - Usa WebRTC peer-to-peer\n\n"
                "4. INSTALLA OBFS4PROXY:\n"
                "   sudo apt install obfs4proxy\n\n"
                "5. VERIFICA FIREWALL LOCALE:\n"
                "   Assicurati che iptables/nftables non blocchi\n"
                "   il traffico in uscita sulle porte 443, 9001, 9030\n\n"
                "Vuoi continuare comunque con l'avvio?\n"
                "(Potrebbe fallire o essere molto lento)"
            ),
            'buttons': ['Continua Comunque', 'Annulla e Configura']
        }


REAL_IP_FILE = Path('/tmp/anonsurf_real_ip.txt')


class App:
    """Applicazione principale GUI con bandiere PNG embedded"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AnonSurf Control Panel v2.1")
        
        width = CONFIG.get_int('gui', 'window_width', 700)
        height = CONFIG.get_int('gui', 'window_height', 750)
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg="#2b2b2b")
        self.root.resizable(False, False)
        
        # Stato
        self.is_tor = False
        self.real_ip = "Non rilevato"
        self.current_ip = "..."
        self.auto_change_var = tk.BooleanVar(value=False)
        self.closing = False
        self.operation_in_progress = False
        
        # Cache bandiere (PhotoImage)
        self.flag_images = {}
        
        # Logger
        self.logger = AppLogger(gui_callback=self.log)
        
        # Manager
        self.network_manager = NetworkStateManager(self.logger)
        self.tor_manager = TorManager(self.logger)
        self.isp_checker = ISPTorBlockChecker(self.logger)
        
        # Costruisci UI
        self.build_ui()
        self.load_saved_ip()
        
        # Gestione chiusura
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        atexit.register(self._cleanup_on_exit)
        
        # Avvia controllo iniziale
        self.root.after(100, self._initial_startup)
    
    def _signal_handler(self, signum, frame):
        self.on_closing()
    
    def _cleanup_on_exit(self):
        if not self.closing:
            self._perform_cleanup()
    
    def _initial_startup(self):
        self.logger.info("Inizializzazione AnonSurf GUI v2.1...")
        self.logger.info(f"Bandiere: {len(FLAGS_BASE64)} paesi supportati")
        
        # Controllo ISP in un thread separato
        threading.Thread(target=self._check_isp_and_start, daemon=True).start()
    
    def _check_isp_and_start(self):
        """Verifica blocco ISP prima di procedere con l'avvio"""
        self.root.after(0, lambda: self.logger.info("Verifica accessibilità rete Tor..."))
        
        # Esegui controllo ISP
        is_blocked, results = self.isp_checker.run_full_check()
        
        if not results['internet_ok']:
            # Nessuna connessione internet
            self.root.after(0, lambda: self.logger.warning("Connessione internet non disponibile"))
            self.root.after(0, lambda: self._proceed_with_startup())
            return
        
        if is_blocked:
            # Mostra dialogo nel thread principale
            self.root.after(0, lambda: self._show_isp_block_dialog(results))
        else:
            self.root.after(0, lambda: self.logger.success("Rete Tor accessibile"))
            self.root.after(0, lambda: self._proceed_with_startup())
    
    def _show_isp_block_dialog(self, results):
        """Mostra dialogo di avviso blocco ISP"""
        info = ISPTorBlockChecker.get_remediation_info()
        
        # Crea finestra di dialogo personalizzata
        dialog = tk.Toplevel(self.root)
        dialog.title(info['title'])
        dialog.configure(bg="#2b2b2b")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centra la finestra
        dialog.geometry("620x650")
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 620) // 2
        y = (dialog.winfo_screenheight() - 650) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.resizable(False, False)
        
        # Icona warning
        tk.Label(dialog, text="⚠️", font=("Arial", 48), bg="#2b2b2b", fg="#ff9800").pack(pady=(15, 5))
        
        # Titolo
        tk.Label(dialog, text=info['title'], font=("Arial", 14, "bold"), 
                 bg="#2b2b2b", fg="#ff9800").pack(pady=(0, 10))
        
        # Frame per dettagli tecnici
        details_frame = tk.LabelFrame(dialog, text="Dettagli Diagnostici", font=("Arial", 9, "bold"),
                                       bg="#3a3a3a", fg="#aaa", padx=10, pady=5)
        details_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        details_text = "\n".join(results.get('details', []))
        tk.Label(details_frame, text=details_text, font=("Courier", 8), 
                 bg="#3a3a3a", fg="#90caf9", justify="left", anchor="w").pack(anchor="w")
        
        # Messaggio principale scrollabile
        msg_frame = tk.Frame(dialog, bg="#2b2b2b")
        msg_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        msg_text = scrolledtext.ScrolledText(msg_frame, height=18, bg="#1e1e1e", 
                                              fg="#ddd", font=("Courier", 9), wrap="word")
        msg_text.pack(fill="both", expand=True)
        msg_text.insert("1.0", info['message'])
        msg_text.config(state="disabled")
        
        # Variabile per il risultato
        result_var = tk.BooleanVar(value=False)
        
        def on_continue():
            result_var.set(True)
            dialog.destroy()
        
        def on_cancel():
            result_var.set(False)
            dialog.destroy()
        
        # Frame pulsanti
        btn_frame = tk.Frame(dialog, bg="#2b2b2b")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        tk.Button(btn_frame, text="🚀 Continua Comunque", command=on_continue,
                  bg="#ff9800", fg="#000", font=("Arial", 10, "bold"),
                  width=20, height=2).pack(side="left", padx=(0, 10))
        
        tk.Button(btn_frame, text="❌ Annulla", command=on_cancel,
                  bg="#f44336", fg="#fff", font=("Arial", 10, "bold"),
                  width=20, height=2).pack(side="right")
        
        # Attendi la chiusura del dialogo
        dialog.wait_window()
        
        if result_var.get():
            self.logger.warning("Utente ha scelto di continuare nonostante il blocco ISP")
            self._proceed_with_startup()
        else:
            self.logger.info("Avvio annullato - configurare bridge Tor prima di procedere")
            self.status_lbl.config(text="○ CONFIGURAZIONE RICHIESTA", bg="#ff9800")
            self.status_frame.config(bg="#ff9800")
    
    def _proceed_with_startup(self):
        """Procede con l'avvio normale dopo il controllo ISP"""
        threading.Thread(target=self._check_and_handle_tor_on_start, daemon=True).start()
    
    def _check_and_handle_tor_on_start(self):
        self.root.after(0, lambda: self.logger.info("Verifica stato rete..."))
        
        status = self.tor_manager.get_status()
        tor_was_active = status.get('is_tor', False)
        current_ip = status.get('ip', '-')
        
        self.network_manager.tor_was_active_on_start = tor_was_active
        self.network_manager.original_ip = current_ip if not tor_was_active else None
        
        self.root.after(0, lambda: self.logger.info("Salvataggio stato rete..."))
        self.network_manager.save_network_state()
        
        if tor_was_active:
            self.root.after(0, lambda: self.logger.warning("Tor ATTIVO - Riavvio sessione..."))
            self.tor_manager.stop()
            time.sleep(3)
            
            self.root.after(0, lambda: self.logger.info("Avvio nuova sessione..."))
            
            def progress(attempt, total):
                self.root.after(0, lambda: self.logger.info(f"Bootstrap {attempt}/{total}..."))
            
            success = self.tor_manager.start(progress_callback=progress)
            
            if success:
                self.root.after(0, lambda: self.logger.success("Sessione Tor avviata"))
            else:
                self.root.after(0, lambda: self.logger.warning("Problema avvio sessione"))
        else:
            self.root.after(0, lambda: self.logger.success("Rete normale - stato salvato"))
        
        self.root.after(2000, self.schedule_refresh)
        self.root.after(100000, self.schedule_auto_change)
    
    def on_closing(self):
        if self.closing:
            return
        
        self.closing = True
        
        if messagebox.askyesno(
            "Chiusura",
            "Chiudere AnonSurf GUI?\n\n"
            "Tor verrà fermato e la rete ripristinata."
        ):
            self.logger.info("Chiusura in corso...")
            self.status_lbl.config(text="● CHIUSURA...", bg="#ff9800")
            self.status_frame.config(bg="#ff9800")
            
            self.tor_manager.cancel_operation()
            
            def cleanup_and_close():
                self._perform_cleanup()
                self.root.after(0, self.root.destroy)
            
            threading.Thread(target=cleanup_and_close, daemon=True).start()
        else:
            self.closing = False
    
    def _perform_cleanup(self):
        try:
            self.tor_manager.stop()
            time.sleep(2)
            self.network_manager.restore_network_state()
            self.network_manager.cleanup()
        except Exception as e:
            print(f"Errore cleanup: {e}")
    
    def _set_buttons_state(self, state):
        for btn in self.buttons:
            btn.config(state=state)
    
    def _get_flag_image(self, country_code):
        """Ottiene PhotoImage per la bandiera del paese"""
        if not country_code or country_code == '-':
            return None
        
        code = country_code.upper()
        
        # Controlla cache
        if code in self.flag_images:
            return self.flag_images[code]
        
        # Cerca nei dati embedded
        if code in FLAGS_BASE64:
            try:
                img = tk.PhotoImage(data=FLAGS_BASE64[code])
                self.flag_images[code] = img
                return img
            except Exception as e:
                print(f"Errore caricamento bandiera {code}: {e}")
        
        return None
    
    def build_ui(self):
        bg = "#2b2b2b"
        
        # Titolo
        title_frame = tk.Frame(self.root, bg=bg)
        title_frame.pack(pady=10)
        
        tk.Label(title_frame, text="ANONSURF CONTROL PANEL", 
                 font=("Arial", 18, "bold"), bg=bg, fg="#00bcd4").pack()
        tk.Label(title_frame, text="v2.1 - System Menu Edition",
                 font=("Arial", 9), bg=bg, fg="#666").pack()
        
        # Status
        self.status_frame = tk.Frame(self.root, bg="#666666", pady=12)
        self.status_frame.pack(fill="x", padx=20)
        self.status_lbl = tk.Label(self.status_frame, text="Inizializzazione...",
                                   font=("Arial", 13, "bold"), bg="#666666", fg="white")
        self.status_lbl.pack()
        
        # Frame IP
        ip_frame = tk.Frame(self.root, bg=bg)
        ip_frame.pack(fill="x", padx=20, pady=15)
        
        # IP Reale
        left = tk.LabelFrame(ip_frame, text="IP REALE", font=("Arial", 10, "bold"),
                             bg="#3a3a3a", fg="#ffc107", padx=10, pady=10)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.real_ip_lbl = tk.Label(left, text=self.real_ip, font=("Courier", 15, "bold"),
                                    bg="#3a3a3a", fg="#ffc107")
        self.real_ip_lbl.pack(pady=8)
        
        tk.Button(left, text="Salva IP", command=self.save_ip, bg="#ffc107", fg="#000",
                  font=("Arial", 10, "bold")).pack()
        
        # IP Corrente
        right = tk.LabelFrame(ip_frame, text="IP CORRENTE", font=("Arial", 10, "bold"),
                              bg="#3a3a3a", fg="#00bcd4", padx=10, pady=10)
        right.pack(side="left", fill="both", expand=True)
        
        self.curr_ip_lbl = tk.Label(right, text=self.current_ip, font=("Courier", 15, "bold"),
                                    bg="#3a3a3a", fg="#00bcd4")
        self.curr_ip_lbl.pack(pady=3)
        
        loc_frame = tk.Frame(right, bg="#3a3a3a")
        loc_frame.pack()
        
        tk.Label(loc_frame, text="Posizione: ", font=("Arial", 10),
                 bg="#3a3a3a", fg="#81c784").pack(side="left")
        
        # Label bandiera per IP corrente
        self.loc_flag_lbl = tk.Label(loc_frame, text="", bg="#3a3a3a")
        self.loc_flag_lbl.pack(side="left", padx=(0, 5))
        
        self.loc_lbl = tk.Label(loc_frame, text="-", font=("Arial", 10),
                                bg="#3a3a3a", fg="#81c784")
        self.loc_lbl.pack(side="left")
        
        self.isp_lbl = tk.Label(right, text="ISP: -", font=("Arial", 9),
                                bg="#3a3a3a", fg="#90caf9")
        self.isp_lbl.pack()
        
        # Exit Node
        exit_frame = tk.LabelFrame(self.root, text="TOR EXIT NODE", font=("Arial", 10, "bold"),
                                   bg="#3a3a3a", fg="#4caf50", padx=15, pady=10)
        exit_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        grid = tk.Frame(exit_frame, bg="#3a3a3a")
        grid.pack()
        
        self.exit_labels = {}
        self.exit_flag_lbl = None
        
        fields = ["IP", "Hostname", "Paese", "Città", "Regione", "ISP"]
        for i, name in enumerate(fields):
            r, c = i // 2, (i % 2) * 2
            tk.Label(grid, text=name + ":", font=("Arial", 10, "bold"),
                     bg="#3a3a3a", fg="#9e9e9e", width=10, anchor="e").grid(row=r, column=c, padx=5, pady=3)
            
            if name == "Paese":
                paese_frame = tk.Frame(grid, bg="#3a3a3a")
                paese_frame.grid(row=r, column=c + 1, padx=5, pady=3, sticky="w")
                
                # Label bandiera per exit node
                self.exit_flag_lbl = tk.Label(paese_frame, text="", bg="#3a3a3a")
                self.exit_flag_lbl.pack(side="left", padx=(0, 5))
                
                lbl = tk.Label(paese_frame, text="-", font=("Courier", 10, "bold"),
                               bg="#3a3a3a", fg="#4caf50")
                lbl.pack(side="left")
                self.exit_labels[name] = lbl
            else:
                lbl = tk.Label(grid, text="-", font=("Courier", 10, "bold"),
                               bg="#3a3a3a", fg="#4caf50", width=22, anchor="w")
                lbl.grid(row=r, column=c + 1, padx=5, pady=3)
                self.exit_labels[name] = lbl
        
        # Pulsanti
        btn_frame = tk.Frame(self.root, bg=bg)
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.buttons = []
        btns = [
            ("AVVIA", "#4caf50", self.start_tor),
            ("FERMA", "#f44336", self.stop_tor),
            ("CAMBIA ID", "#9c27b0", self.change_id),
            ("AGGIORNA", "#2196f3", self.manual_refresh),
        ]
        
        for text, color, cmd in btns:
            btn = tk.Button(btn_frame, text=text, command=cmd, bg=color, fg="#fff",
                           font=("Arial", 11, "bold"), width=12, height=2)
            btn.pack(side="left", expand=True, padx=3)
            self.buttons.append(btn)
        
        # Auto-change
        auto_frame = tk.Frame(self.root, bg=bg)
        auto_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        tk.Checkbutton(auto_frame, text="Cambio automatico ID ogni 100s",
                       variable=self.auto_change_var, bg=bg, fg="#ffb74d",
                       selectcolor="#3a3a3a", activebackground=bg,
                       font=("Arial", 10, "bold")).pack(side="left")
        
        self.auto_status_lbl = tk.Label(auto_frame, text="", font=("Arial", 9), bg=bg, fg="#888")
        self.auto_status_lbl.pack(side="right")
        
        # Progress
        self.progress_frame = tk.Frame(self.root, bg=bg)
        self.progress_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        self.progress_lbl = tk.Label(self.progress_frame, text="", font=("Arial", 9),
                                     bg=bg, fg="#aaa")
        self.progress_lbl.pack()
        
        # Log
        tk.Label(self.root, text="LOG OPERAZIONI", font=("Arial", 9, "bold"),
                 bg=bg, fg="#757575").pack(anchor="w", padx=20)
        
        self.log_box = scrolledtext.ScrolledText(self.root, height=8, bg="#1e1e1e",
                                                  fg="#aaa", font=("Courier", 9))
        self.log_box.pack(fill="x", padx=20, pady=(0, 10))
        
        # Footer
        self.footer = tk.Label(self.root, text="", font=("Arial", 9), bg=bg, fg="#555")
        self.footer.pack()
        
        tk.Label(self.root, text="Creato da Red-Penguin - MIT License",
                 font=("Arial", 8), bg=bg, fg="#666").pack(pady=(5, 10))
    
    def log(self, message):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{ts}] {message}\n")
        self.log_box.see("end")
        
        max_lines = CONFIG.get_int('gui', 'max_log_lines', 100)
        lines = int(self.log_box.index('end-1c').split('.')[0])
        if lines > max_lines:
            self.log_box.delete('1.0', f'{lines - max_lines}.0')
    
    def load_saved_ip(self):
        if REAL_IP_FILE.exists():
            try:
                self.real_ip = REAL_IP_FILE.read_text().strip()
                self.real_ip_lbl.config(text=self.real_ip)
            except Exception:
                pass
    
    def save_ip(self):
        if self.is_tor:
            messagebox.showwarning("Attenzione", "Disattiva Tor prima")
            return
        self.logger.info("Salvataggio IP reale...")
        threading.Thread(target=self._do_save_ip, daemon=True).start()
    
    def _do_save_ip(self):
        ip = self.tor_manager._get_simple_ip()
        if ip:
            try:
                REAL_IP_FILE.write_text(ip)
                self.real_ip = ip
                self.root.after(0, lambda: self.real_ip_lbl.config(text=ip))
                self.root.after(0, lambda: self.logger.success(f"IP salvato: {ip}"))
            except Exception as e:
                self.root.after(0, lambda: self.logger.error(f"Errore: {e}"))
    
    def _update_flag(self, label, country_code):
        """Aggiorna label con immagine bandiera"""
        img = self._get_flag_image(country_code)
        if img:
            label.config(image=img, text="")
        else:
            # Fallback: mostra codice paese come testo
            label.config(image="", text=country_code if country_code and country_code != '-' else "")
    
    def manual_refresh(self):
        self.logger.info("Aggiornamento...")
        threading.Thread(target=self._do_refresh, daemon=True).start()
    
    def schedule_refresh(self):
        if self.closing:
            return
        threading.Thread(target=self._do_refresh, daemon=True).start()
        refresh_interval = CONFIG.get_int('timing', 'refresh_interval', 15000)
        self.root.after(refresh_interval, self.schedule_refresh)
    
    def schedule_auto_change(self):
        if self.closing:
            return
        
        if self.auto_change_var.get() and self.is_tor and not self.operation_in_progress:
            self.logger.info("Auto-change ID...")
            threading.Thread(target=self._do_auto_change, daemon=True).start()
        
        self.root.after(100000, self.schedule_auto_change)
    
    def _do_auto_change(self):
        success = self.tor_manager.change_identity()
        ts = datetime.now().strftime("%H:%M:%S")
        
        if success:
            self.root.after(0, lambda: self.auto_status_lbl.config(text=f"OK: {ts}", fg="#81c784"))
        else:
            self.root.after(0, lambda: self.auto_status_lbl.config(text="Errore", fg="#ef5350"))
        
        time.sleep(2)
        self.root.after(0, lambda: threading.Thread(target=self._do_refresh, daemon=True).start())
    
    def _do_refresh(self):
        status = self.tor_manager.get_status()
        self.root.after(0, lambda: self._update_ui(status))
    
    def _update_ui(self, info):
        ip = info.get('ip', '-')
        is_tor = info.get('is_tor', False)
        
        self.is_tor = is_tor
        self.current_ip = ip
        
        self.curr_ip_lbl.config(text=ip)
        
        city = info.get('city', '-')
        country_code = info.get('country_code', '-')
        
        # Aggiorna bandiera per IP corrente
        self._update_flag(self.loc_flag_lbl, country_code)
        
        loc = f"{city}, {country_code}" if city != '-' else country_code
        self.loc_lbl.config(text=loc)
        
        isp = info.get('isp', '-')
        isp_display = isp[:40] + "..." if len(isp) > 40 else isp
        self.isp_lbl.config(text=f"ISP: {isp_display}")
        
        if is_tor:
            self.status_lbl.config(text="● TOR ATTIVO - Anonimizzato", bg="#4caf50")
            self.status_frame.config(bg="#4caf50")
            
            self.exit_labels["IP"].config(text=ip, fg="#4caf50")
            hostname = info.get('hostname', '-')
            self.exit_labels["Hostname"].config(text=hostname[:25] if len(hostname) > 25 else hostname, fg="#4caf50")
            
            # Aggiorna bandiera per exit node
            if self.exit_flag_lbl:
                self._update_flag(self.exit_flag_lbl, country_code)
            self.exit_labels["Paese"].config(text=country_code, fg="#4caf50")
            self.exit_labels["Città"].config(text=city, fg="#4caf50")
            self.exit_labels["Regione"].config(text=info.get('region', '-'), fg="#4caf50")
            self.exit_labels["ISP"].config(text=isp[:25] if len(isp) > 25 else isp, fg="#4caf50")
        else:
            self.status_lbl.config(text="○ TOR INATTIVO - Connessione Diretta", bg="#f44336")
            self.status_frame.config(bg="#f44336")
            
            for lbl in self.exit_labels.values():
                lbl.config(text="-", fg="#666")
            if self.exit_flag_lbl:
                self.exit_flag_lbl.config(image="", text="")
            
            if self.real_ip == "Non rilevato" and ip != '-':
                try:
                    REAL_IP_FILE.write_text(ip)
                    self.real_ip = ip
                    self.real_ip_lbl.config(text=ip)
                    self.logger.info(f"IP reale auto-salvato: {ip}")
                except Exception:
                    pass
        
        ts = datetime.now().strftime("%H:%M:%S")
        self.footer.config(text=f"Aggiornato: {ts}")
    
    def start_tor(self):
        if self.operation_in_progress:
            self.logger.warning("Operazione già in corso")
            return
        
        self.operation_in_progress = True
        self._set_buttons_state(tk.DISABLED)
        
        self.logger.info("Avvio AnonSurf...")
        self.status_lbl.config(text="● AVVIO IN CORSO...", bg="#ff9800")
        self.status_frame.config(bg="#ff9800")
        
        def do_start():
            def progress(attempt, total):
                self.root.after(0, lambda: self.progress_lbl.config(
                    text=f"Bootstrap Tor: {attempt}/{total}"
                ))
            
            success = self.tor_manager.start(progress_callback=progress)
            
            self.root.after(0, lambda: self.progress_lbl.config(text=""))
            
            if success:
                self.root.after(0, lambda: self.logger.success("AnonSurf ATTIVO"))
            else:
                if self.tor_manager.is_cancelled():
                    self.root.after(0, lambda: self.logger.info("Avvio annullato"))
                else:
                    self.root.after(0, lambda: self.logger.error("Avvio fallito"))
            
            self.operation_in_progress = False
            self.root.after(0, lambda: self._set_buttons_state(tk.NORMAL))
            self.root.after(500, lambda: threading.Thread(target=self._do_refresh, daemon=True).start())
        
        threading.Thread(target=do_start, daemon=True).start()
    
    def stop_tor(self):
        if self.operation_in_progress:
            self.tor_manager.cancel_operation()
            self.logger.info("Annullamento operazione...")
            return
        
        self.operation_in_progress = True
        self._set_buttons_state(tk.DISABLED)
        
        self.logger.info("Arresto AnonSurf...")
        self.status_lbl.config(text="● ARRESTO IN CORSO...", bg="#ff9800")
        self.status_frame.config(bg="#ff9800")
        
        def do_stop():
            success = self.tor_manager.stop()
            
            if success:
                self.root.after(0, lambda: self.logger.success("AnonSurf fermato"))
            else:
                self.root.after(0, lambda: self.logger.warning("Problema arresto"))
            
            self.operation_in_progress = False
            self.root.after(0, lambda: self._set_buttons_state(tk.NORMAL))
            self.root.after(500, lambda: threading.Thread(target=self._do_refresh, daemon=True).start())
        
        threading.Thread(target=do_stop, daemon=True).start()
    
    def change_id(self):
        if not self.is_tor:
            messagebox.showwarning("Attenzione", "Avvia prima AnonSurf")
            return
        
        if self.operation_in_progress:
            return
        
        self.logger.info("Cambio identità...")
        
        def do_change():
            success = self.tor_manager.change_identity()
            
            if success:
                self.root.after(0, lambda: self.logger.success("Identità cambiata"))
            else:
                self.root.after(0, lambda: self.logger.warning("Problema cambio ID"))
            
            self.root.after(500, lambda: threading.Thread(target=self._do_refresh, daemon=True).start())
        
        threading.Thread(target=do_change, daemon=True).start()


def main():
    if os.geteuid() != 0:
        print("\033[1;33m[NOTA] Richiesti privilegi root\033[0m")
        print("Riavvio con sudo...")
        os.execvp('sudo', ['sudo', 'python3'] + sys.argv)
    
    root = tk.Tk()
    
    root.update_idletasks()
    w = CONFIG.get_int('gui', 'window_width', 700)
    h = CONFIG.get_int('gui', 'window_height', 750)
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
