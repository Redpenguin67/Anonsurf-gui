#!/usr/bin/env python3
"""
AnonSurf GUI Control Panel v2.1 - MINI Edition
Versione compatta per uso in angolo schermo

Caratteristiche:
- Finestra minimale e compatta
- IP reale + Exit Node (paese + bandiera)
- Pulsanti: Avvia, Stop, Cambia ID
- Stesso controllo ISP della versione completa
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
            'refresh_interval': '10000',
            'tor_verify_attempts': '15',
            'tor_verify_interval': '3'
        },
        'gui': {
            'window_width': '280',
            'window_height': '200',
        },
        'logging': {
            'enable_file_log': 'true',
            'log_filename': 'anonsurf_gui_mini.log',
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
    """Logger minimale"""
    
    def __init__(self):
        self.file_logger = None
        self._setup_file_logger()
    
    def _setup_file_logger(self):
        if not CONFIG.get_bool('logging', 'enable_file_log', True):
            return
        
        log_file = BASE_DIR / CONFIG.get('logging', 'log_filename', 'anonsurf_gui_mini.log')
        log_level = getattr(logging, CONFIG.get('logging', 'log_level', 'INFO').upper(), logging.INFO)
        max_size = CONFIG.get_int('logging', 'max_log_size', 5242880)
        backup_count = CONFIG.get_int('logging', 'log_backup_count', 3)
        
        self.file_logger = logging.getLogger('AnonSurfGUIMini')
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
    
    def info(self, message):
        self._log_to_file('INFO', message)
    
    def warning(self, message):
        self._log_to_file('WARNING', message)
    
    def error(self, message, diagnostic_key=None):
        self._log_to_file('ERROR', message)
    
    def debug(self, message):
        self._log_to_file('DEBUG', message)
    
    def success(self, message):
        self._log_to_file('INFO', f"SUCCESS: {message}")


class TorManager:
    """Gestisce operazioni AnonSurf/Tor"""
    
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
    
    def is_cancelled(self):
        return self._cancel_flag.is_set()
    
    def _reset_cancel(self):
        self._cancel_flag.clear()
    
    def execute(self, command, timeout=None):
        if not self.is_available():
            return False, "", "AnonSurf non trovato", -1
        
        if timeout is None:
            timeout = CONFIG.get_int('timing', 'anonsurf_timeout', 60)
        
        full_cmd = f"{self.anonsurf_path} {command}"
        
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
                return False, stdout, stderr, -1
            
            clean_stdout = re.sub(r'\x1b\[[0-9;]*m', '', stdout) if stdout else ""
            clean_stderr = re.sub(r'\x1b\[[0-9;]*m', '', stderr) if stderr else ""
            
            return returncode == 0, clean_stdout, clean_stderr, returncode
            
        except Exception as e:
            return False, "", str(e), -1
    
    def start(self, progress_callback=None):
        with self._operation_lock:
            if self._current_operation:
                return False
            self._current_operation = "start"
        
        self._reset_cancel()
        
        try:
            success, stdout, stderr, rc = self.execute('start')
            
            if not success:
                return False
            
            if self.is_cancelled():
                return False
            
            verify_attempts = CONFIG.get_int('timing', 'tor_verify_attempts', 15)
            verify_interval = CONFIG.get_int('timing', 'tor_verify_interval', 3)
            
            for attempt in range(1, verify_attempts + 1):
                if self.is_cancelled():
                    return False
                
                if progress_callback:
                    progress_callback(attempt, verify_attempts)
                
                is_tor, ip = self._check_tor_status(fast=True)
                
                if is_tor:
                    return True
                
                for _ in range(verify_interval):
                    if self.is_cancelled():
                        return False
                    time.sleep(1)
            
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
            success, _, _, _ = self.execute('stop')
            
            if success:
                stop_wait = CONFIG.get_int('timing', 'tor_stop_wait', 8)
                time.sleep(stop_wait)
                return True
            
            return False
        finally:
            with self._operation_lock:
                self._current_operation = None
    
    def change_identity(self):
        success, _, _, _ = self.execute('change', timeout=30)
        
        if success:
            time.sleep(3)
        
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
        except Exception:
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
    """Verifica se l'ISP blocca la rete Tor."""
    
    TOR_DIRECTORY_AUTHORITIES = [
        ("128.31.0.34", 9101),
        ("86.59.21.38", 443),
        ("194.109.206.212", 443),
        ("199.58.81.140", 443),
        ("204.13.164.118", 443),
    ]
    
    TOR_CHECK_ENDPOINTS = [
        "https://check.torproject.org",
        "https://bridges.torproject.org",
        "https://www.torproject.org",
    ]
    
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
    
    def _check_tcp_port(self, host, port, timeout=3):
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
        for url in self.INTERNET_CHECK_ENDPOINTS:
            if self._check_https_endpoint(url, self.check_timeout):
                self.results['internet_ok'] = True
                self.results['details'].append(f"✓ Internet OK")
                return True
        
        self.results['details'].append("✗ No Internet")
        return False
    
    def check_tor_sites(self):
        reachable = 0
        for url in self.TOR_CHECK_ENDPOINTS:
            if self._check_https_endpoint(url, self.check_timeout):
                reachable += 1
        
        self.results['tor_sites_ok'] = reachable > 0
        if reachable > 0:
            self.results['details'].append(f"✓ Tor sites OK")
        else:
            self.results['details'].append(f"✗ Tor sites blocked")
        return reachable > 0
    
    def check_tor_authorities(self):
        reachable = 0
        for host, port in self.TOR_DIRECTORY_AUTHORITIES:
            if self._check_tcp_port(host, port, timeout=3):
                reachable += 1
        
        self.results['tor_authorities_ok'] = reachable >= 2
        if reachable >= 2:
            self.results['details'].append(f"✓ Authorities OK ({reachable}/5)")
        else:
            self.results['details'].append(f"✗ Authorities blocked ({reachable}/5)")
        return reachable >= 2
    
    def run_full_check(self):
        self.results = {
            'internet_ok': False,
            'tor_sites_ok': False,
            'tor_authorities_ok': False,
            'likely_blocked': False,
            'details': []
        }
        
        if not self.check_internet_connectivity():
            self.results['likely_blocked'] = False
            return False, self.results
        
        self.check_tor_sites()
        self.check_tor_authorities()
        
        if self.results['internet_ok']:
            if not self.results['tor_sites_ok'] and not self.results['tor_authorities_ok']:
                self.results['likely_blocked'] = True
            elif not self.results['tor_authorities_ok']:
                self.results['likely_blocked'] = True
        
        return self.results['likely_blocked'], self.results
    
    @staticmethod
    def get_remediation_info():
        return {
            'title': "Blocco Tor Rilevato",
            'message': (
                "Il tuo ISP potrebbe bloccare Tor.\n\n"
                "SOLUZIONI:\n\n"
                "1. Configura Bridge Tor:\n"
                "   https://bridges.torproject.org\n\n"
                "2. In /etc/tor/torrc aggiungi:\n"
                "   UseBridges 1\n"
                "   Bridge obfs4 <IP:PORT> ...\n\n"
                "3. Installa obfs4proxy:\n"
                "   sudo apt install obfs4proxy\n\n"
                "Continuare comunque?"
            )
        }


REAL_IP_FILE = Path('/tmp/anonsurf_real_ip.txt')


class MiniApp:
    """Applicazione GUI minimale"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AnonSurf Mini")
        
        # Dimensioni compatte
        self.root.geometry("280x200")
        self.root.configure(bg="#2b2b2b")
        self.root.resizable(False, False)
        
        # Stato
        self.is_tor = False
        self.real_ip = "..."
        self.exit_country = "-"
        self.exit_country_code = "-"
        self.closing = False
        self.operation_in_progress = False
        
        # Cache bandiere
        self.flag_images = {}
        
        # Logger e Manager
        self.logger = AppLogger()
        self.tor_manager = TorManager(self.logger)
        self.isp_checker = ISPTorBlockChecker(self.logger)
        
        # Costruisci UI
        self.build_ui()
        self.load_saved_ip()
        
        # Gestione chiusura
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        signal.signal(signal.SIGTERM, lambda s, f: self.on_closing())
        signal.signal(signal.SIGINT, lambda s, f: self.on_closing())
        
        # Avvia
        self.root.after(100, self._initial_startup)
    
    def _initial_startup(self):
        threading.Thread(target=self._check_isp_and_start, daemon=True).start()
    
    def _check_isp_and_start(self):
        is_blocked, results = self.isp_checker.run_full_check()
        
        if not results['internet_ok']:
            self.root.after(0, self._proceed_with_startup)
            return
        
        if is_blocked:
            self.root.after(0, lambda: self._show_isp_block_dialog(results))
        else:
            self.root.after(0, self._proceed_with_startup)
    
    def _show_isp_block_dialog(self, results):
        info = ISPTorBlockChecker.get_remediation_info()
        
        if messagebox.askyesno(info['title'], info['message'], icon='warning'):
            self._proceed_with_startup()
        else:
            self.status_lbl.config(text="CONFIG", bg="#ff9800", fg="#000")
    
    def _proceed_with_startup(self):
        self.schedule_refresh()
    
    def _get_flag_image(self, country_code):
        if not country_code or country_code == '-':
            return None
        
        code = country_code.upper()
        
        if code in self.flag_images:
            return self.flag_images[code]
        
        if code in FLAGS_BASE64:
            try:
                img = tk.PhotoImage(data=FLAGS_BASE64[code])
                self.flag_images[code] = img
                return img
            except Exception:
                pass
        
        return None
    
    def build_ui(self):
        bg = "#2b2b2b"
        
        # Frame principale
        main = tk.Frame(self.root, bg=bg, padx=10, pady=5)
        main.pack(fill="both", expand=True)
        
        # Riga 1: Status compatto
        self.status_lbl = tk.Label(main, text="INIT", font=("Arial", 10, "bold"),
                                    bg="#666", fg="#fff", width=8, pady=2)
        self.status_lbl.pack(fill="x", pady=(0, 5))
        
        # Riga 2: IP Reale
        ip_frame = tk.Frame(main, bg=bg)
        ip_frame.pack(fill="x", pady=2)
        
        tk.Label(ip_frame, text="IP Reale:", font=("Arial", 9),
                 bg=bg, fg="#ffc107", width=8, anchor="w").pack(side="left")
        self.real_ip_lbl = tk.Label(ip_frame, text=self.real_ip, font=("Courier", 9, "bold"),
                                     bg=bg, fg="#ffc107")
        self.real_ip_lbl.pack(side="left", fill="x", expand=True)
        
        # Riga 3: Exit Node (bandiera + paese)
        exit_frame = tk.Frame(main, bg=bg)
        exit_frame.pack(fill="x", pady=2)
        
        tk.Label(exit_frame, text="Exit:", font=("Arial", 9),
                 bg=bg, fg="#4caf50", width=8, anchor="w").pack(side="left")
        
        self.exit_flag_lbl = tk.Label(exit_frame, text="", bg=bg)
        self.exit_flag_lbl.pack(side="left", padx=(0, 5))
        
        self.exit_country_lbl = tk.Label(exit_frame, text="-", font=("Arial", 9, "bold"),
                                          bg=bg, fg="#4caf50")
        self.exit_country_lbl.pack(side="left")
        
        # Riga 4: Pulsanti
        btn_frame = tk.Frame(main, bg=bg)
        btn_frame.pack(fill="x", pady=(10, 5))
        
        self.btn_start = tk.Button(btn_frame, text="▶", command=self.start_tor,
                                    bg="#4caf50", fg="#fff", font=("Arial", 12, "bold"),
                                    width=4, height=1)
        self.btn_start.pack(side="left", expand=True, padx=2)
        
        self.btn_stop = tk.Button(btn_frame, text="■", command=self.stop_tor,
                                   bg="#f44336", fg="#fff", font=("Arial", 12, "bold"),
                                   width=4, height=1)
        self.btn_stop.pack(side="left", expand=True, padx=2)
        
        self.btn_change = tk.Button(btn_frame, text="↻", command=self.change_id,
                                     bg="#9c27b0", fg="#fff", font=("Arial", 12, "bold"),
                                     width=4, height=1)
        self.btn_change.pack(side="left", expand=True, padx=2)
        
        # Progress label
        self.progress_lbl = tk.Label(main, text="", font=("Arial", 8), bg=bg, fg="#888")
        self.progress_lbl.pack()
    
    def load_saved_ip(self):
        if REAL_IP_FILE.exists():
            try:
                self.real_ip = REAL_IP_FILE.read_text().strip()
                self.real_ip_lbl.config(text=self.real_ip)
            except Exception:
                pass
    
    def schedule_refresh(self):
        if self.closing:
            return
        threading.Thread(target=self._do_refresh, daemon=True).start()
        refresh_interval = CONFIG.get_int('timing', 'refresh_interval', 10000)
        self.root.after(refresh_interval, self.schedule_refresh)
    
    def _do_refresh(self):
        status = self.tor_manager.get_status()
        self.root.after(0, lambda: self._update_ui(status))
    
    def _update_ui(self, info):
        is_tor = info.get('is_tor', False)
        ip = info.get('ip', '-')
        country = info.get('country', '-')
        country_code = info.get('country_code', '-')
        
        self.is_tor = is_tor
        
        if is_tor:
            self.status_lbl.config(text="● TOR", bg="#4caf50", fg="#fff")
            self.exit_country_lbl.config(text=f"{country} ({country_code})", fg="#4caf50")
            
            # Aggiorna bandiera
            img = self._get_flag_image(country_code)
            if img:
                self.exit_flag_lbl.config(image=img, text="")
            else:
                self.exit_flag_lbl.config(image="", text=country_code if country_code != '-' else "")
        else:
            self.status_lbl.config(text="○ OFF", bg="#f44336", fg="#fff")
            self.exit_country_lbl.config(text="-", fg="#666")
            self.exit_flag_lbl.config(image="", text="")
            
            # Auto-salva IP reale
            if self.real_ip == "..." and ip != '-':
                try:
                    REAL_IP_FILE.write_text(ip)
                    self.real_ip = ip
                    self.real_ip_lbl.config(text=ip)
                except Exception:
                    pass
    
    def _set_buttons_state(self, state):
        self.btn_start.config(state=state)
        self.btn_stop.config(state=state)
        self.btn_change.config(state=state)
    
    def start_tor(self):
        if self.operation_in_progress:
            return
        
        self.operation_in_progress = True
        self._set_buttons_state(tk.DISABLED)
        self.status_lbl.config(text="...", bg="#ff9800", fg="#000")
        
        def do_start():
            def progress(attempt, total):
                self.root.after(0, lambda: self.progress_lbl.config(text=f"{attempt}/{total}"))
            
            success = self.tor_manager.start(progress_callback=progress)
            
            self.root.after(0, lambda: self.progress_lbl.config(text=""))
            self.operation_in_progress = False
            self.root.after(0, lambda: self._set_buttons_state(tk.NORMAL))
            self.root.after(500, lambda: threading.Thread(target=self._do_refresh, daemon=True).start())
        
        threading.Thread(target=do_start, daemon=True).start()
    
    def stop_tor(self):
        if self.operation_in_progress:
            self.tor_manager.cancel_operation()
            return
        
        self.operation_in_progress = True
        self._set_buttons_state(tk.DISABLED)
        self.status_lbl.config(text="...", bg="#ff9800", fg="#000")
        
        def do_stop():
            self.tor_manager.stop()
            
            self.operation_in_progress = False
            self.root.after(0, lambda: self._set_buttons_state(tk.NORMAL))
            self.root.after(500, lambda: threading.Thread(target=self._do_refresh, daemon=True).start())
        
        threading.Thread(target=do_stop, daemon=True).start()
    
    def change_id(self):
        if not self.is_tor or self.operation_in_progress:
            return
        
        self.progress_lbl.config(text="...")
        
        def do_change():
            self.tor_manager.change_identity()
            self.root.after(0, lambda: self.progress_lbl.config(text=""))
            self.root.after(500, lambda: threading.Thread(target=self._do_refresh, daemon=True).start())
        
        threading.Thread(target=do_change, daemon=True).start()
    
    def on_closing(self):
        if self.closing:
            return
        
        self.closing = True
        
        def cleanup():
            self.tor_manager.stop()
            self.root.after(0, self.root.destroy)
        
        threading.Thread(target=cleanup, daemon=True).start()


def main():
    if os.geteuid() != 0:
        print("\033[1;33m[NOTA] Richiesti privilegi root\033[0m")
        print("Riavvio con sudo...")
        os.execvp('sudo', ['sudo', 'python3'] + sys.argv)
    
    root = tk.Tk()
    
    # Posiziona in alto a destra
    root.update_idletasks()
    w, h = 280, 200
    x = root.winfo_screenwidth() - w - 20
    y = 40
    root.geometry(f"{w}x{h}+{x}+{y}")
    
    # Sempre in primo piano (opzionale)
    root.attributes('-topmost', True)
    
    MiniApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
