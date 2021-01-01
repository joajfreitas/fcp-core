from typing import *

from pathlib import Path
import sys
import hjson

import pdb

from sqlalchemy import Column, ForeignKey, Integer, Float, String, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

Base = declarative_base()


class Signal(Base):
    __tablename__ = "signals"
    parent = Column(String, ForeignKey('msgs.name'), primary_key=True)
    name = Column(String, primary_key=True, default="signal")
    start = Column(Integer, default=0)
    length = Column(Integer, default=0)
    scale = Column(Float, default=1.0)
    offset = Column(Float, default=0.0)
    unit = Column(String, default="")
    comment = Column(String, default="")
    min_value = Column(Integer, default=0)
    max_value = Column(Integer, default=0)
    type = Column(String, default="unsigned")
    byte_order = Column(String, default="little_endian")
    mux = Column(String, default="")
    mux_count = Column(Integer, default=1)
    alias = Column(String, default="")

    def from_dict(self, fcp, msg_name):
        self.parent = msg_name
        self.name = fcp["name"]
        self.start = fcp["start"]
        self.length = fcp["length"]
        self.scale = fcp["scale"]
        self.offset = fcp["offset"]
        self.unit = fcp["unit"]
        self.comment = fcp["comment"]
        self.min_value = fcp["min_value"]
        self.max_value = fcp["max_value"]
        self.type = fcp["type"]
        self.byte_order = fcp["byte_order"]
        self.mux = fcp["mux"]
        self.mux_count = fcp["mux_count"]
        self.alias = fcp["alias"]


class Message(Base):
    __tablename__ = "msgs"
    parent = Column(String, ForeignKey('devs.name'), primary_key=True)
    name = Column(String, primary_key=True, default="msg")
    id = Column(Integer, default=0)
    dlc = Column(Integer, default=0)
    frequency = Column(Integer, default=1.0)
    description = Column(String, default=0.0)

    def from_dict(self, fcp, dev_name):
        self.parent = dev_name
        self.name = fcp["name"]
        self.id = fcp["id"]
        self.dlc = fcp["dlc"]
        self.frequency = fcp["frequency"]
        self.description = fcp["description"]


class Device(Base):
    __tablename__ = "devs"
    name = Column(String, primary_key=True, default="dev")
    id = Column(Integer, default=0)

    def from_dict(self, fcp):
        self.name = fcp["name"]
        self.id = fcp["id"]

class Log(Base):
    __tablename__ = "logs"
    name = Column(String, primary_key=True, default="log")
    id = Column(Integer, default=0)
    n_args = Column(Integer, default=0)
    comment = Column(String, default="")
    string = Column(String, default="Undefined String")

    def from_dict(self, fcp):
        self.name = fcp["name"]
        self.id = fcp["id"]
        self.n_args = fcp["n_args"]
        self.comment = fcp["comment"]
        self.string = fcp["string"]

class Command(Base):
    __tablename__ = "cmds"
    parent = Column(String, ForeignKey('devs.name'), primary_key=True)
    name = Column(String, primary_key=True, default="cmd")
    id = Column(Integer, default=0)
    n_args = Column(Integer, default=0)
    comment = Column(String, default="")

    def from_dict(self, fcp, parent):
        self.parent = parent
        self.name = fcp["name"]
        self.id = fcp["id"]
        self.n_args = fcp["n_args"]
        self.comment = fcp["comment"]

class Config(Base):
    __tablename__ = "cfgs"
    parent = Column(String, ForeignKey('devs.name'), primary_key=True)
    name = Column(String, primary_key=True, default="cfg")
    id = Column(Integer, default=0)
    comment = Column(String, default="")

    def from_dict(self, fcp, parent):
        self.parent = parent
        self.name = fcp["name"]
        self.id = fcp["id"]
        self.comment = fcp["comment"]

def json_to_sql(session: Session, j: Dict[Any, Any]):
    for log in j["logs"].values():
        _log = Log()
        _log.from_dict(log)
        session.add(_log)
    for dev in j["devices"].values():
        device = Device()
        device.from_dict(dev)
        session.add(device)
        for msg in dev["msgs"].values():
            message = Message()
            message.from_dict(msg, dev["name"])
            session.add(message)
            for sig in msg["signals"].values():
                signal = Signal()
                signal.from_dict(sig, msg["name"])
                session.add(signal)

        for cmd in dev["cmds"].values():
            command = Command()
            command.from_dict(cmd, dev["name"])
            session.add(command)

        for cfg in dev["cfgs"].values():
            config = Config()
            config.from_dict(cfg, dev["name"])
            session.add(config)

    session.commit()

def get_session(db_path: Path) -> Session:
    engine = create_engine("sqlite:///" + str(db_path))
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session: Session = DBSession()

    return session


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        j = hjson.loads(f.read())

    session = get_session("db")
    json_to_sql(session, j)

