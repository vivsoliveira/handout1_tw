import unittest
import sqlite3
from unittest.mock import patch, create_autospec
from pathlib import Path
import inspect

try:
    import database
except:
    database = None

DB_NAME = 'banco-teste'
DB_FILENAME = f'{DB_NAME}.db'
TABLE_NAME = 'note'


def error_message(msg):
    marker = '\033[91m'
    end_marker = '\033[0m'
    return f'\n{marker}{msg}{end_marker}\n'


def initial_setup(exercício):
    def decorate(clazz):
        if database is None:
            print(error_message(f'{exercício} O arquivo database.py não foi encontrado.'))
            return None

        database_found = False
        for name, obj in inspect.getmembers(database):
            if name == 'Database':
                database_found = True

        if not database_found:
            print(error_message(f'{exercício} A classe Database não foi encontrada.'))
            return None

        if object.__init__ == database.Database.__init__:
            print(error_message(f'{exercício} A classe Database não possui um método __init__ implementado.'))
            return None

        return clazz
    return decorate


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        db_file = Path.cwd() / DB_FILENAME
        # try:
        #     db_file.unlink()  # Apaga o arquivo, caso exista (TODO não funciona em alguns windows)
        # except FileNotFoundError:
        #     pass

    @initial_setup("EXERCÍCIO 01")
    def test_1_connect_on_init(self):
        mock_connection = create_autospec(sqlite3.Connection)
        nome_exercicio = 'EXERCÍCIO 01'
        with patch('sqlite3.connect', return_value=mock_connection) as mock_connect:
            db = database.Database(DB_NAME)

            assert mock_connect.called, error_message(f'{nome_exercicio} A função sqlite3.connect não foi chamada')
            assert mock_connect.call_args[0][0] == DB_FILENAME, error_message(f'{nome_exercicio} Nome do banco incorreto. Deveria ser {DB_FILENAME}')
            assert hasattr(db, 'conn'), error_message(f'{nome_exercicio} Não criou o atributo conn')
            assert db.conn is mock_connection, error_message(f'{nome_exercicio} Não armazenou a conexão no atributo conn')

    @initial_setup("EXERCÍCIO 02")
    def test_2_create_table_on_init(self):
        db_file = Path.cwd() / DB_FILENAME
        db = database.Database(DB_NAME)
        nome_exercicio = 'EXERCÍCIO 02'
        if not db_file.is_file():
            raise NotImplementedError(error_message(f'{nome_exercicio} A conexão com o banco não foi implementada ainda. Ignore se ainda não chegou neste exercício'))

        conn = sqlite3.connect(DB_FILENAME)
        cursor = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}';")
        assert len([row for row in cursor]) == 1, error_message(f'{nome_exercicio} A tabela {TABLE_NAME} não foi criada. Se você está no primeiro exercício, ignore este erro.')

        cursor = conn.execute(f"PRAGMA table_info({TABLE_NAME});")
        found_count = 0
        for i, (_, name, coltype, notnull, _, pk) in enumerate(cursor):
            if i == 0:
                assert name == 'id', error_message(f'{nome_exercicio} Para facilitar os testes, a primeira coluna deve obrigatoriamente ser a coluna id.')
                assert coltype == 'INTEGER', error_message(f'{nome_exercicio} A coluna id deveria ser do tipo inteiro')
                assert pk, error_message(f'{nome_exercicio} A coluna id deveria ser a chave primária')
            elif i == 1:
                assert name == 'title', error_message(f'{nome_exercicio} Para facilitar os testes, a segunda coluna deve obrigatoriamente ser a coluna title.')
                assert coltype == 'STRING' or coltype == 'TEXT', error_message(f'{nome_exercicio} A coluna title deveria ser do tipo texto')
                assert not notnull, error_message(f'{nome_exercicio} A coluna title deveria poder ser vazia')
                assert not pk, error_message(f'{nome_exercicio} A coluna title não deveria ser chave primária')
            elif i == 2:
                assert name == 'content', error_message(f'{nome_exercicio} Para facilitar os testes, a terceira coluna deve obrigatoriamente ser a coluna content.')
                assert coltype == 'STRING' or coltype == 'TEXT', error_message(f'{nome_exercicio} A coluna content deveria ser do tipo texto')
                assert notnull, error_message(f'{nome_exercicio} A coluna content não deveria poder ser vazia')
                assert not pk, error_message(f'{nome_exercicio} A coluna content não deveria ser chave primária')
            else:
                raise AssertionError(error_message(f'{nome_exercicio} Não deveria existir uma coluna chamada {name}'))
            found_count += 1

    @initial_setup("EXERCÍCIO 03")
    def test_3_add_rows(self):
        nome_exercicio = 'EXERCÍCIO 03'
        db = database.Database(DB_NAME)
        if not hasattr(db, 'add') or not hasattr(database, 'Note'):
            raise NotImplementedError(error_message(f'{nome_exercicio} Método add ou classe Note não foram implementadas ainda. Ignore se ainda não chegou neste exercício'))

        data = [
            ('Pão doce', 'Abra o pão e coloque o seu suco em pó favorito.'),
            ('', 'Lembrar de tomar água'),
        ]
        try:
            for title, content in data:
                db.add(database.Note(title=title, content=content))
        except sqlite3.OperationalError:
            raise SyntaxError(error_message(f"{nome_exercicio} Algo deu errado! Veja se não esqueceu as aspas em torno dos valores."))

        conn = sqlite3.connect(DB_FILENAME)
        cursor = conn.execute(f"SELECT * FROM {TABLE_NAME}")
        result = [(title, content) for _, title, content in cursor]
        result.sort(key=lambda r: r[1])
        assert data == result, error_message(f'{nome_exercicio} Os dados não foram inseridos corretamente. Era esperado: {data}\nporém foi obtido {result}')

    @initial_setup("EXERCÍCIO 04")
    def test_4_select_rows(self):
        nome_exercicio = 'EXERCÍCIO 04'
        db = database.Database(DB_NAME)
        if not hasattr(db, 'add') or not hasattr(db, 'get_all') or not hasattr(database, 'Note'):
            raise NotImplementedError(error_message(f'{nome_exercicio} Método add ou get_all ou a classe Note não foram implementadas ainda. Ignore se ainda não chegou neste exercício'))

        data = [
            database.Note(title='Hidratação', content='Lembrar de tomar água'),
            database.Note(
                title='Pão doce', content='Abra o pão e coloque o seu suco em pó favorito.'),
        ]
        for note in data:
            db.add(note)

        try:
            notes = sorted(db.get_all(), key=lambda n: n.title)
        except:
            raise Exception(error_message(f"{nome_exercicio} Verifique se o comando SELECT está correto."))

        assert isinstance(notes, list), error_message(f'{nome_exercicio} O método get_all deveria devolver uma lista. Obtido: {notes}')
        assert len(notes) > 0 and isinstance(notes[0], database.Note), error_message(f'{nome_exercicio} O método get_all deveria devolver uma lista de objetos do tipo Note. Obtido: {notes}')
        assert len(data) == len(notes), error_message(f'{nome_exercicio} A lista devolvida tem uma quantidade de elementos diferente do esperado. Esperado: {len(data)}. Obtido: {len(notes)}.')
        assert all(n.id != None for n in notes), error_message(f'{nome_exercicio} As notas estão sem a informação do id.')
        assert all(d.title == n.title and d.content == n.content for d, n in zip(data, notes)), error_message(f'{nome_exercicio} A lista de anotações é diferente da esperada. Esperada: {data}. Obtida: {notes}.')

    @initial_setup("EXERCÍCIO 05")
    def test_5_update_row(self):
        nome_exercicio = 'EXERCÍCIO 05'
        db = database.Database(DB_NAME)
        if not hasattr(db, 'add') or not hasattr(db, 'get_all') or not hasattr(db, 'update') or not hasattr(database, 'Note'):
            raise NotImplementedError(error_message(f'{nome_exercicio} Método add, get_all ou update ou a classe Note não foram implementadas ainda. Ignore se ainda não chegou neste exercício'))

        data = [
            database.Note(title='Hidratação', content='Lembrar de tomar água'),
            database.Note(
                title='Pão doce', content='Abra o pão e coloque o seu suco em pó favorito.'),
        ]
        for note in data:
            db.add(note)

        notes = sorted(db.get_all(), key=lambda n: n.title)
        new_title = 'Zebra'
        new_content = 'É um animal que começa com a letra Z.'
        updated_row = notes[1]
        updated_row.title = new_title
        updated_row.content = new_content

        try:
            db.update(updated_row)
        except sqlite3.OperationalError:
            raise SyntaxError(error_message(f"{nome_exercicio} Algo deu errado! Veja se não esqueceu as aspas em torno dos valores."))

        notes = sorted(db.get_all(), key=lambda n: n.title)

        data[1].title = new_title
        data[1].content = new_content
        assert isinstance(notes, list), error_message(f'{nome_exercicio} O método get_all deveria devolver uma lista. Obtido: {notes}')
        assert len(data) == len(notes), error_message(f'{nome_exercicio} A lista devolvida tem uma quantidade de elementos diferente do esperado. Esperado: {len(data)}. Obtido: {len(notes)}.')
        assert all(d.title == n.title and d.content == n.content for d, n in zip(data, notes)), error_message(f'{nome_exercicio} A lista de anotações é diferente da esperada. Esperada: {data}. Obtida: {notes}.')

    @initial_setup("EXERCÍCIO 06")
    def test_6_delete_row(self):
        nome_exercicio = 'EXERCÍCIO 06'
        db = database.Database(DB_NAME)
        if not hasattr(db, 'add') or not hasattr(db, 'get_all') or not hasattr(db, 'delete') or not hasattr(database, 'Note'):
            raise NotImplementedError(error_message(f'{nome_exercicio} Método add, get_all ou delete ou a classe Note não foram implementadas ainda. Ignore se ainda não chegou neste exercício'))

        data = [
            database.Note(title='Hidratação', content='Lembrar de tomar água'),
            database.Note(
                title='Pão doce', content='Abra o pão e coloque o seu suco em pó favorito.'),
        ]
        for note in data:
            db.add(note)

        db.delete(1)
        notes = sorted(db.get_all(), key=lambda n: n.title)
        assert isinstance(notes, list), error_message(f'{nome_exercicio} O método get_all deveria devolver uma lista. Obtido: {notes}')
        assert len(notes) == 1, error_message(f'{nome_exercicio} A lista devolvida deveria ter apenas 1 elemento. Obtido: {len(notes)}.')
        note = notes[0]
        assert data[1].title == note.title and data[1].content == note.content, error_message(f'{nome_exercicio} Foi removido o elemento errado.')


if __name__ == '__main__':
    unittest.main()
