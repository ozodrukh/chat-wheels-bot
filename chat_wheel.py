from typing import Optional

import dataset
import uuid, json
import sqlite3


class VoiceEncoder(json.JSONEncoder):
    def default(self, o):
        out = {}
        for k, v in o._data.items():
            if v is not None: out[k] = v
        return out


class Voice:
    def __init__(self, data=None):
        if data is None:
            data = {}

        self._data = data

    @property
    def id(self):
        return self._data["uuid"]

    @property
    def name(self):
        return self._data["name"]

    @name.setter
    def name(self, name: str):
        self._data["name"] = name

    @property
    def url(self):
        return self._data["url"]

    @url.setter
    def url(self, url: str):
        self._data["url"] = url

    @property
    def cache_id(self):
        return self._data["cache_id"]


class ChatWheelStorage(object):
    _database: dataset.Database = dataset.connect("sqlite:///voice_lines.db")

    def __init__(self):
        if "voice_lines" not in self._database.tables:
            database_con = sqlite3.connect("voice_lines.db")
            database_con.executescript("""
                CREATE TABLE voice_lines(
                    id integer primary key, 
                    name text, 
                    url text, 
                    uuid text not null unique, 
                    cache_id text);
                    
                CREATE VIRTUAL TABLE fts_voice_lines USING FTS5(name, uuid, content='voice_lines', content_rowid='id');
                                    
                CREATE INDEX ids_voice_lines_uuid ON voice_lines(uuid);
                
                CREATE TRIGGER voice_lines_si AFTER INSERT ON voice_lines 
                BEGIN
                    INSERT INTO fts_voice_lines(rowid, name, uuid) VALUES(new.id, new.name, new.uuid);
                END;
                
                CREATE TRIGGER voice_lines_sd AFTER DELETE ON voice_lines 
                BEGIN
                    INSERT INTO fts_voice_lines(fts_voice_lines, rowid, name, uuid) VALUES('delete', old.id, old.name, old.uuid);
                END;
                
                CREATE TRIGGER voice_lines_su AFTER UPDATE ON voice_lines 
                BEGIN
                    INSERT INTO fts_voice_lines(fts_voice_lines, rowid, name, uuid) VALUES('delete', old.id, old.name, old.uuid);
                    INSERT INTO fts_voice_lines(rowid, name, uuid) VALUES(new.id, new.name, new.uuid);
                END;
            """)
            database_con.close()

        self._voices_table = self._database["voice_lines"]

    @property
    def _voices(self) -> dataset.Table:
        return self._voices_table

    def clear(self):
        return self._voices.delete() > 0

    def search(self, query) -> list:
        voices = []

        for row in self._database.query("select uuid from fts_voice_lines WHERE name MATCH :s", s=query):
            voice = Voice(self._voices.find_one(uuid=row["uuid"]))
            voice._data["url"] = "https://chat-wheels-bot.herokuapp.com/get_wheel_voice_line?id=" + voice.id

            voices.append(voice)

        return voices

    def set_voice_cache_id(self, voice_id, cache_id):
        return self._voices.update({"uuid": voice_id, "cache_id": cache_id}, ["uuid"]) > 0

    def save_voice_object(self, voice_object: Voice):
        if "uuid" not in voice_object._data:
            voice_object._data["uuid"] = str(uuid.uuid4())

        return self._voices.insert(voice_object._data)

    def get_voice_object(self, id=None) -> Optional[Voice]:
        voice_line = self._voices.find_one(id=id)

        if voice_line is not None:
            return Voice(voice_line)
        else:
            return None
