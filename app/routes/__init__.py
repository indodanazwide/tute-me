from flask import Blueprint, render_template

router = Blueprint('main', __name__)

from . import public
from . import student
from . import tutor
from . import admin