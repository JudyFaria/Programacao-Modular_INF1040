from pathlib import Path
import src.sb.persistence as persistence


def test_save_and_load(tmp_path):
    # Use a temporary entity name so we don't conflict with app data
    entity = 'test_entity'
    data = {'a': 1, 'b': [1, 2, 3]}

    # ensure data dir inside repo exists
    repo_data = Path(__file__).resolve().parents[1] / 'data'
    if repo_data.exists():
        # ensure starting clean for this entity
        p = repo_data / f"{entity}.json"
        if p.exists():
            p.unlink()

    persistence.save(entity, data)

    loaded = persistence.load(entity)

    assert loaded == data

    # cleanup
    p = repo_data / f"{entity}.json"
    if p.exists():
        p.unlink()
