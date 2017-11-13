from . import db
from .usuario_lab import UsuarioLab
from .laboratorio import Laboratorio

class Preferencia_Usuario(UsuarioLab):
	def __init__(self, user_id, nome, laboratorio=None, lab_id=None, temp_min=None, temp_max=None, id=None):
		super().__init__(nome, user_id, laboratorio, lab_id)
		self.user_id = user_id
		self.nome = nome
		self.lab_id = lab_id
		self.laboratorio = laboratorio
		self.temp_min = temp_min
		self.temp_max = temp_max
		self.id = id