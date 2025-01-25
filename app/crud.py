from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import User, MenstrualEvent, EventType
from .schemas import UserCreate, MenstrualEventCreate
from .auth import get_password_hash, verify_password


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_user_events(db: Session, user_id: int):
    return db.query(MenstrualEvent).filter(
        MenstrualEvent.user_id == user_id
    ).order_by(MenstrualEvent.event_date).all()


def create_user_event(db: Session, event: MenstrualEventCreate, user_id: int):
    db_event = MenstrualEvent(
        **event.dict(),
        user_id=user_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def analyze_cycle_patterns(db: Session, user_id: int):
    events = get_user_events(db, user_id)

    # Extract cycle start events
    cycle_starts = [e for e in events if e.event_type == EventType.CYCLE_START]

    # Calculate cycle lengths
    cycle_lengths = []
    for i in range(1, len(cycle_starts)):
        cycle_length = (cycle_starts[i].event_date - cycle_starts[i - 1].event_date).days
        cycle_lengths.append(cycle_length)

    # Comprehensive cycle analysis
    analysis = {
        'total_cycles': len(cycle_starts),
        'average_cycle_length': round(sum(cycle_lengths) / len(cycle_lengths), 2) if cycle_lengths else None,
        'shortest_cycle': min(cycle_lengths) if cycle_lengths else None,
        'longest_cycle': max(cycle_lengths) if cycle_lengths else None,

        # Additional detailed insights
        'recent_cycles': [
            {
                'start_date': start.event_date,
                'related_events': [
                    e for e in events
                    if e.event_date >= start.event_date and
                       (cycle_starts[i + 1].event_date if i + 1 < len(cycle_starts) else None) is None
                ]
            } for i, start in enumerate(cycle_starts[-3:])  # Last 3 cycles
        ]
    }

    return analysis


def get_event_statistics(db: Session, user_id: int):
    # Count events by type
    event_counts = db.query(
        MenstrualEvent.event_type,
        func.count(MenstrualEvent.id)
    ).filter(
        MenstrualEvent.user_id == user_id
    ).group_by(
        MenstrualEvent.event_type
    ).all()

    return dict(event_counts)
