from typing import *

from appdirs import *
from pathlib import Path
import sys
import hjson

from hashlib import sha1

from sqlalchemy import Column, ForeignKey, Integer, Float, String, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from .dirs import get_config_dir


SpecBase = declarative_base()


class Signal(SpecBase):
    __tablename__ = "signals"
    _parent = Column(String, ForeignKey("msgs.name"), primary_key=True)
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
        self._parent = msg_name
        self.__dict__.update(fcp)
        # self.name = fcp["name"]
        # self.start = fcp["start"]
        # self.length = fcp["length"]
        # self.scale = fcp["scale"]
        # self.offset = fcp["offset"]
        # self.unit = fcp["unit"]
        # self.comment = fcp["comment"]
        # self.min_value = fcp["min_value"]
        # self.max_value = fcp["max_value"]
        # self.type = fcp["type"]
        # self.byte_order = fcp["byte_order"]
        # self.mux = fcp["mux"]
        # self.mux_count = fcp["mux_count"]
        # self.alias = fcp["alias"]

    def to_dict(self) -> Dict[Any, Any]:
        return {k: v for (k, v) in self.__dict__.items() if not k.startswith("_")}


class Message(SpecBase):
    __tablename__ = "msgs"
    _parent = Column(String, ForeignKey("devs.name"), primary_key=True)
    name = Column(String, primary_key=True, default="msg")
    id = Column(Integer, default=0)
    dlc = Column(Integer, default=0)
    frequency = Column(Integer, default=1.0)
    description = Column(String, default=0.0)

    def from_dict(self, fcp, dev_name):
        self._parent = dev_name
        self.name = fcp["name"]
        self.id = fcp["id"]
        self.dlc = fcp["dlc"]
        self.frequency = fcp["frequency"]
        self.description = fcp["description"]

    def to_dict(self) -> Dict[Any, Any]:
        return {k: v for (k, v) in self.__dict__.items() if not k.startswith("_")}


class Device(SpecBase):
    __tablename__ = "devs"
    name = Column(String, primary_key=True, default="dev")
    id = Column(Integer, default=0)

    def from_dict(self, fcp):
        self.name = fcp["name"]
        self.id = fcp["id"]

    def to_dict(self) -> Dict[Any, Any]:
        return {k: v for (k, v) in self.__dict__.items() if not k.startswith("_")}

    def __repr__(self):
        return f"<Device name={self.name} id={self.id}>"


class Log(SpecBase):
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

    def to_dict(self) -> Dict[Any, Any]:
        return {k: v for (k, v) in self.__dict__.items() if not k.startswith("_")}


class Command(SpecBase):
    __tablename__ = "cmds"
    parent = Column(String, ForeignKey("devs.name"), primary_key=True)
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


class Config(SpecBase):
    __tablename__ = "cfgs"
    parent = Column(String, ForeignKey("devs.name"), primary_key=True)
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


def sql_to_json(session: Session) -> Dict[Any, Any]:
    signals = session.query(Signal).all()
    devs = session.query(Device).all()

    json = {"devices": {}}
    json["version"] = 0.3

    for dev in devs:
        json["devices"][dev.name] = dev.to_dict()
        msgs = session.query(Message).filter(Message._parent == dev.name).all()
        json["devices"][dev.name]["msgs"] = {}
        for msg in msgs:
            json["devices"][dev.name]["msgs"][msg.name] = msg.to_dict()
            sigs = session.query(Signal).filter(Signal._parent == msg.name).all()
            json["devices"][dev.name]["msgs"][msg.name]["signals"] = {}
            for sig in sigs:
                json["devices"][dev.name]["msgs"][msg.name]["signals"][
                    sig.name
                ] = sig.to_dict()

    json["logs"] = {}
    logs = session.query(Log).all()
    for log in logs:
        json["logs"][log.name] = log.to_dict()

    return json


def create_session(db_path: Path, base) -> Session:
    engine = create_engine("sqlite:///" + str(db_path))
    base.metadata.create_all(engine)
    base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session: Session = DBSession()

    return session, engine


def init_session(file_path: Path) -> Session:
    print("file_path:", file_path)
    with file_path.open() as f:
        j = hjson.loads(f.read())

    abs = bytes(str(file_path.absolute()), "utf-8")
    db_path = Path(sha1(abs).hexdigest()[:16] + "-" + file_path.name)
    db_path: Path = Path(get_config_dir()) / db_path

    print("db_path:", db_path)

    if db_path.is_file():
        db_path.unlink()

    session, engine = create_session(db_path, SpecBase)
    json_to_sql(session, j)

    connection = engine.connect()
    # connection.execute()

    return session, engine


def spec_session(file_paht: Path) -> Session:
    db_path = Path(get_config_dir()) / hash(file_path)
    session, _ = create_session(db_path, SpecBase)

    return session


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        j = hjson.loads(f.read())

    session, _ = create_session("db", SpecBase)
    json_to_sql(session, j)
