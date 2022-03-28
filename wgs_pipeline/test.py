# -*- coding: utf-8 -*-

import os,sys,argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from lib.config import TestConfig
con=TestConfig()
print(con.get_docker("happy"))