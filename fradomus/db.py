# -*- coding: utf-8 -*-


import sqlalchemy
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String

from sqlalchemy.types import DateTime, Boolean, LargeBinary, Text

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


from version import DB_VERSION, VERSION

DB_VERSION_LABEL = 'DB_VERSION'
VERSION_LABEL = 'VERSION'
Base = declarative_base()

class DbSchemaTooNew(Exception):
    pass

class DbNoVersionSet(Exception):
    pass

def migrate():
    """Place holder for futur DB migration scripts"""
    pass

class DbAds(Base):
    __tablename__ = 'ads'

    # definition of the fields
    id = Column(Integer, primary_key=True, nullable=False)
    source = Column(String(30), nullable=False, index=True)
    price = Column(Float, index=True)
    price_unit = Column(String(30))
    room = Column(Integer, index=True)
    surface = Column(Float, index=True)
    surface_unit = Column(String(30))
    city = Column(String(255))
    postal_code = Column(String(16), nullable=False, index=True)
    date = Column(DateTime(), nullable=False index=True)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    source = Column(String(30), nullable=False)
    description = Column(Text, nullable=False)
    link = Column(String(255), nullable=False)
    displayed = Column(Boolean, nullable=False, index=True)
    search_id = Column(Integer, nullable=False, index=True)
    raw = Column(JSON, nullable=False)

    # relationships
    proximity = relationship("DbAdsProximity")
    picture = relationship("DbAdsPictures")


class DbAdsProximity(Base):
    __tablename__ = 'ads_pictures'
    id = Column(Integer, primary_key=True)
    place = Column(String(256), unique=True)
    ad_id = Column(Integer, ForeignKey('ad.id'))


class DbAdsPictures(Base):
    __tablename__ = 'ads_pictures'
    id = Column(Integer, primary_key=True)
    link = Column(String(256), unique=True)
    ad_id = Column(Integer, ForeignKey('ad.id'))


class DbVersion(Base):
    __tablename__ = 'version'
    id = Column(Integer, primary_key=True)
    version = Column(String(10))
    vtype = Column(String(10), nullable=False, unique=True)


def get_dbsession(config):

    engine = create_engine(
            config['uri'],
            echo=(config['echo_sql'] in ['true', 'True', 'TRUE']),
#            pool_size = int(config['pool_size']),
#            pool_timeout = int(config['pool_timeout']),
#            pool_recycle = int(config['pool_recycle'])
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    # we try to get the version, if it doesn't succeed, we create the DB
    try:
        version = session.query(DbVersion).filter_by(vtype=DB_VERSION_LABEL).first()
    except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.ProgrammingError):
        Base.metadata.create_all(engine)
        # committing between schema creation and
        # setting the version is necessary on postgres
        session.commit()
        # we set the version
        counter = 0
        while counter < 10:
            try:
                session.add_all([
                    DbVersion(vtype = DB_VERSION_LABEL, version = DB_VERSION),
                    DbVersion(vtype = VERSION_LABEL, version = VERSION),
                ])
                session.commit()
                version = session.query(DbVersion).filter_by(vtype=DB_VERSION_LABEL).first()
                break
            except:
                counter += 1
                time.sleep(1)

    # the version of the DB is newer than the version of certascale
    # this should not happen so we raise an exception
    if version is None:
        raise DbNoVersionSet
    if int(version.version) > int(DB_VERSION):
        raise DbSchemaTooNew

    # the version of the DB is older than the certascale definition
    # so we launch the schema update script
    elif int(version.version) < int(DB_VERSION):
        migrate()

return Session
