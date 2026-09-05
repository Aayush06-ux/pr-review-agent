from src.database.db_engine import get_db_connection, init_db
from src.database.repository import EventRepository

log_event = EventRepository.log_event
log_agent_trace = EventRepository.log_agent_trace
log_review = EventRepository.log_review
get_recent_events = EventRepository.get_recent_events
