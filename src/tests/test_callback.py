from src.util.callback import (is_include_ga_like_or_really_like,
                               is_include_like_or_really_like_and_yoro,
                               is_liked_or_really_liked_surface,
                               select_from_surface)


def test_is_liked_or_really_liked_surface():
    # case not include
    assert not is_liked_or_really_liked_surface(
        "きもい",
        "おれだね"
    )
    # include it as last case
    assert is_liked_or_really_liked_surface(
        "こんにちは",
        "先輩が今まで好きでした"
    )
    # include it as first case
    assert is_liked_or_really_liked_surface(
        "こんにちはが好きですね",
        "わろた"
    )
    # include both
    assert is_liked_or_really_liked_surface(
        "好きです!先輩!",
        "先輩が今まで好きでした"
    )


def test_is_include_like_or_really_like_and_yoro():
    assert is_include_like_or_really_like_and_yoro(
        "大好き",
        "よろしくお願いします"
    )
    assert is_include_like_or_really_like_and_yoro(
        "好き",
        "よろしくお願いします"
    )
    assert is_include_like_or_really_like_and_yoro(
        "よろしくお願いします",
        "好き"
    )
    assert is_include_like_or_really_like_and_yoro(
        "よろしくお願いします",
        "大好き"
    )
    assert is_include_like_or_really_like_and_yoro(
        "よろしくお願いしますqq",
        "好きQQ"
    )
    assert is_include_like_or_really_like_and_yoro(
        "よろしくお願いしますeee",
        "大好きvv"
    )
    assert not is_include_like_or_really_like_and_yoro(
        "よqろしくお願いしますeee",
        "大好きvv"
    )
    assert not is_include_like_or_really_like_and_yoro(
        "よろしくお願いしますeee",
        "aaa"
    )
    assert is_include_like_or_really_like_and_yoro(
        "おれが好きです",
        "よろしくお願いします"
    )


def test_is_include_ga_like_or_really_like():
    assert is_include_ga_like_or_really_like(
        "金魚が",
        "好きです"
    )
    assert is_include_ga_like_or_really_like(
        "金魚が",
        "大好きです"
    )
    assert not is_include_ga_like_or_really_like(
        "金魚も",
        "大好きです"
    )
    assert not is_include_ga_like_or_really_like(
        "金魚も",
        "好きです"
    )
    assert not is_include_ga_like_or_really_like(
        "金魚が",
        "ガービン"
    )
    assert is_include_ga_like_or_really_like(
        "金魚が",
        "よろしくお願いします好きです"
    )
    assert not is_include_ga_like_or_really_like(
        "好きです",
        "金魚が"
    )


def test_select_from_surface():
    assert "from_surface" == select_from_surface(
        "from_surface",
        "to_surface"
    )
    assert not "to_surface" == select_from_surface(
        "from_surface",
        "to_surface"
    )
