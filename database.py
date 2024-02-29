import sqlite3
from dataclasses import dataclass

@dataclass
class Note:
    id: int = None
    title: str = None
    content: str = ''

class Database:
    def __init__(self, base_de_dados):
        self.conn = sqlite3.connect(f'{base_de_dados}.db')

        # table if not exists para evitar erro caso a tabela já exista
        # mas da pra criar varias vezes
        # text not null impede que tenha uma linha sem conteudo
        comando = """
        CREATE TABLE IF NOT EXISTS note ( id INTEGER PRIMARY KEY,
                                            title TEXT,
                                            content TEXT NOT NULL);
        """
        self.conn.execute(comando)

    def add(self, note):
        self.conn.execute("INSERT INTO note (title, content) VALUES (?, ?);", (note.title, note.content))
        self.conn.commit()

    def get_all(self):
        cursor = self.conn.execute("SELECT id, title, content FROM note;")

        notes = []
        for linha in cursor:
            note = Note()
            note.id = linha[0]
            note.title = linha[1]
            note.content = linha[2]
            notes.append(note)
        return notes

    def update(self, entry):
        self.conn.execute(" UPDATE note SET title = ?, content = ? WHERE id = ?;", (entry.title, entry.content, entry.id))
        self.conn.commit()

    def delete(self, note_id):
        self.conn.execute("DELETE FROM note WHERE id = ?;", (note_id,))
        self.conn.commit()
