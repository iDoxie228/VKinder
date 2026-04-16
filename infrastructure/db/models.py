from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, BigInteger, String, Text, Date, TIMESTAMP, ForeignKey, Boolean, UniqueConstraint
from infrastructure.db.session import Base

# AppUser
# Candidate
# CandidatePhoto
# Favorite
# Blacklist
# ShownCandidate
# SearchSession

class AppUser(Base):
    __tablename__ = "app_users"

    id = Column(Integer, primary_key=True)
    vk_user_id = Column(BigInteger, nullable=False, unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    sex = Column(Integer)
    birth_date = Column(Date)
    age = Column(Integer)
    city_id = Column(Integer)
    city_name = Column(String(150))
    profile_url = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())

    favorites = relationship("Favorite", back_populates="app_user")
    blacklist_entries = relationship("Blacklist", back_populates="app_user")
    shown_candidates = relationship("ShownCandidate", back_populates="app_user")
    search_sessions = relationship("SearchSession", back_populates="app_user")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True)
    vk_candidate_id = Column(BigInteger, nullable=False, unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    sex = Column(Integer)
    birth_date = Column(Date)
    age = Column(Integer)
    city_id = Column(Integer)
    city_name = Column(String(150))
    profile_url = Column(Text, nullable=False)
    is_closed = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())

    photos = relationship("CandidatePhoto", back_populates="candidate")
    favorited_by = relationship("Favorite", back_populates="candidate")
    blacklisted_by = relationship("Blacklist", back_populates="candidate")
    shown_to_users = relationship("ShownCandidate", back_populates="candidate")


class CandidatePhoto(Base):
    __tablename__ = "candidate_photos"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id', ondelete="CASCADE"), nullable=False)
    vk_photo_id = Column(BigInteger, nullable=False)
    photo_url = Column(Text)
    likes_amount = Column(Integer, nullable=False, default=0) 
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())

    candidate = relationship("Candidate", back_populates="photos")  

    __table_args__ = (
        UniqueConstraint("candidate_id", "vk_photo_id", name="unique_photo"),
    )


class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True)
    app_user_id = Column(Integer, ForeignKey('app_users.id', ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())

    candidate = relationship("Candidate", back_populates="favorited_by")
    app_user = relationship("AppUser", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("app_user_id", "candidate_id", name="unique_favorite"),
    )


class Blacklist(Base):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True)
    app_user_id = Column(Integer, ForeignKey('app_users.id', ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())

    candidate = relationship("Candidate", back_populates="blacklisted_by") 
    app_user = relationship("AppUser", back_populates="blacklist_entries")  

    __table_args__ = (
        UniqueConstraint("app_user_id", "candidate_id", name="unique_blacklist"),
    )


class ShownCandidate(Base):
    __tablename__ = "shown_candidates"
    id = Column(Integer, primary_key=True)
    app_user_id = Column(Integer, ForeignKey('app_users.id', ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    shown_at = Column(TIMESTAMP, nullable=False, default=func.now())

    candidate = relationship("Candidate", back_populates="shown_to_users")
    app_user = relationship("AppUser", back_populates="shown_candidates")

    __table_args__ = (
        UniqueConstraint("app_user_id", "candidate_id", name="unique_shown_candidate"),
    )


class SearchSession(Base):
    __tablename__ = "search_sessions"
    id = Column(Integer, primary_key=True)
    app_user_id = Column(Integer, ForeignKey('app_users.id', ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())
    status = Column(String(20), nullable=False, default='active')

    app_user = relationship("AppUser", back_populates="search_sessions")