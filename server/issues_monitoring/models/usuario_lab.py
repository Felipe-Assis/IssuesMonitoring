from datetime import datetime
from .usuario import Usuario
from . import db

class UsuarioLab(Usuario):
    def __init__(self, user_id, nome, email, data_aprovacao = None,
                 laboratorio = None, lab_id = None, data_entrada = None):
        super().__init__(nome, email, data_aprovacao)
        self.user_id = user_id
        self.nome = nome
        self.email = email
        self.data_aprovacao = data_aprovacao
        self.lab_id = lab_id
        self.laboratorio = laboratorio
        self.data_entrada = data_entrada

    def obter_todos():
        data = db.fetchall("""SELECT user_id, nome, email, data_aprov
                            FROM User_Lab;""")
        return [UsuarioLab(*d) for d in data]

    def registrar_presenca(eventos):
        usuarios_presenca = []
        tupla_eventos = []
        for e in eventos:
            usuarios_presenca += [(e.evento == "IN", e.user_id)]
            tupla_eventos += [(e.epoch,
                               e.user_id,
                               e.lab_id,
                               e.evento)]

        db.executemany("""
            UPDATE Presenca
            SET presente = ?
            WHERE user_id = ?;""",
            usuarios_presenca)
        db.executemany("""
            INSERT INTO Log_Presenca
            (data, user_id, lab_id, evento)
            VALUES (?, ?, ?, ?);""",
            tupla_eventos)

    def existe(user_id):
        return db.fetchone("""
            SELECT user_id
            FROM User_lab
            WHERE user_id = ?;""", (user_id,)) is not None

    def adicionar_ao_laboratorio(lab_id, user_id):
        if db.fetchone("""
                SELECT user_id
                FROM Presenca
                WHERE user_id = ?
                      AND lab_id = ?;""",
                (user_id, lab_id)) is not None:
            return

        db.execute("""
            INSERT INTO Presenca
            (lab_id, user_id, presente)
            VALUES (?, ?, ?);""",
            (lab_id,
             user_id,
             False))

    def presentes(lab_id):
        agora = datetime.now()
        hoje = int(datetime(day=agora.day,
                            month=agora.month,
                            year=agora.year).timestamp())
        data = db.fetchall("""SELECT u.user_id, u.nome, u.email,
                                     u.data_aprov, log.data
                            FROM User_Lab u
                            INNER JOIN Presenca p
                                ON p.user_id = u.user_id
                            INNER JOIN Log_Presenca log
                                ON log.user_id = u.user_id
                                   AND log.lab_id = p.lab_id
                            WHERE p.presente = 1
                                  AND p.lab_id = ?
                                  AND log.evento = "IN"
                                  AND log.data > ?
                            ORDER BY log.data DESC;""",
                            (lab_id,
                            hoje))
        usuarios = []
        usuarios_set = set()
        for d in data:
            if d[0] not in usuarios_set:
                usuarios_set.add(d[0])
                usuarios += [UsuarioLab(*d[:-1], data_entrada=d[-1])]
        return usuarios

    def cadastrar(self):
        values = (self.user_id,
                  self.nome,
                  self.email,
                  self.data_aprovacao)
        db.execute("""
            INSERT INTO User_Lab
            (user_id, nome, email, data_aprov)
            VALUES (?, ?, ?, ?);""", values)

        UsuarioLab.adicionar_ao_laboratorio(self.lab_id,
                                            self.user_id)

    def remover(lab_id, user_id):
        db.execute("""
            DELETE FROM Presenca
            WHERE lab_id = ? AND
                  user_id = ?;""", (lab_id, user_id))
        count = db.fetchone("""
            SELECT COUNT(presenca_id)
            FROM Presenca
            WHERE user_id = ?;""", (user_id,))[0]
        if count == 0:
            db.execute("""
                DELETE FROM User_Lab
                WHERE user_id = ?;""", (user_id,))
