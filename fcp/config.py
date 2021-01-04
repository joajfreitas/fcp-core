import time
from pathlib import Path

from sqlalchemy import Column, ForeignKey, Integer, Float, String, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy import select, update

from .sql import create_session
from .dirs import get_config_dir


ConfigBase = declarative_base()


class File(ConfigBase):
    __tablename__ = "files"

    path = Column(String, primary_key=True)
    time_used = Column(Float)

    def __repr__(self):
        return f"{self.path} {self.time_used}"

    def recent_files(session):
        return session.query(File).order_by(File.time_used.desc()).all()

    def exists(session, path: Path) -> bool:
        files = [x[0] for x in session.query(File.path).all()]
        return str(path) in files

    def access(session, path: Path):
        if not File.exists(session, path):
            file = File(path=str(path), time_used=time.time())
            session.add(file)

        session.execute(
            update(File).where(File.path == str(path)).values(time_used=time.time())
        )

        session.commit()


def config_session():
    config = Path(get_config_dir()) / "config"
    return create_session(config, ConfigBase)


def main():
    session = config_session()

    session.add(File(os.path.abspath("json/fst10e.hjson", time.time())))
    session.commit()


if __name__ == "__main__":
    main()
