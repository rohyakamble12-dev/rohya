import pytest
import os
from veda.core.memory import VedaMemory

@pytest.fixture
def memory():
    db_path = "test_memory.db"
    mem = VedaMemory(db_path=db_path)
    yield mem
    if os.path.exists(db_path):
        os.remove(db_path)

def test_memory_facts(memory):
    memory.store_fact("user_name", "Tony")
    summary = memory.get_all_facts_summary()
    assert "user_name: Tony" in summary

def test_memory_episodes(memory):
    memory.store_episode("test_event", "Test Content")
    episodes = memory.get_recent_episodes()
    assert "test_event: Test Content" in episodes
