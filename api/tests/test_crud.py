import pytest
import uuid

# from api.models import Base, Song
from api.crud import get_songs, search_songs, rate_song, get_song, create_song
from api.schemas import RatingCreate, PaginatedResponse, SongResponse
from api.tests.utils_song_gen import create_random_song
from fastapi import status
from fastapi.exceptions import HTTPException


def test_create_song(db_session):
    song_data = create_random_song()

    song = create_song(db_session, song=song_data)
    assert isinstance(song, SongResponse)
    assert song.title == song_data.title
    assert song.danceability == song_data.danceability
    assert song.energy == song_data.energy
    assert song.key == song_data.key
    assert song.loudness == song_data.loudness
    assert song.mode == song_data.mode
    assert song.acousticness == song_data.acousticness
    assert song.instrumentalness == song_data.instrumentalness
    assert song.liveness == song_data.liveness
    assert song.valence == song_data.valence
    assert song.tempo == song_data.tempo
    assert song.duration_ms == song_data.duration_ms
    assert song.time_signature == song_data.time_signature
    assert song.num_bars == song_data.num_bars
    assert song.num_sections == song_data.num_sections
    assert song.num_segments == song_data.num_segments
    assert song.class_field == song_data.class_field


def test_get_songs(db_session):
    song_data1 = create_random_song()
    song_data2 = create_random_song()
    create_song(db_session, song=song_data1)
    create_song(db_session, song=song_data2)

    response = get_songs(db_session, page=1, limit=10)
    assert isinstance(response, PaginatedResponse)
    assert response.total_items >= 2
    assert response.current_page == 1
    assert len(response.data) >= 2
    assert all(isinstance(song, SongResponse) for song in response.data)


def test_search_songs(db_session):
    song_data = create_random_song()
    create_song(db_session, song=song_data)
    songs = search_songs(db_session, title=song_data.title)
    assert len(songs) == 1
    assert songs[0].title == song_data.title
    assert all(isinstance(song, SongResponse) for song in songs)


def test_rate_song(db_session):
    song_data = create_random_song()
    create_song(db_session, song=song_data)
    rating = RatingCreate(rating=5.0)
    song = rate_song(db_session, song_id=song_data.id, rating=rating)
    assert isinstance(song, SongResponse)
    assert song.rating == 5.0
    assert song.rating_count == 1


def test_get_song(db_session):
    song_data = create_random_song()
    create_song(db_session, song=song_data)
    song = get_song(db_session, song_id=song_data.id)
    assert isinstance(song, SongResponse)
    assert song.title == song.title


def test_get_nonexistent_song(db_session):
    # song = get_song(db_session, song_id="99")
    # assert song is None
    with pytest.raises(HTTPException) as exc:
        get_song(db_session, song_id=str(uuid.uuid4()))
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "Song not found"


def test_search_nonexistent_song(db_session):
    songs = search_songs(db_session, title="Nonexistent")
    assert len(songs) == 0


def test_rate_song_multiple_times(db_session):
    song_data = create_random_song()
    create_song(db_session, song=song_data)
    rating1 = RatingCreate(rating=4.0)
    rating2 = RatingCreate(rating=5.0)
    song = rate_song(db_session, song_id=song_data.id, rating=rating1)
    song = rate_song(db_session, song_id=song_data.id, rating=rating2)
    assert song.rating == 4.5  # 5+4/2
    assert song.rating_count == 2  # 1+1
