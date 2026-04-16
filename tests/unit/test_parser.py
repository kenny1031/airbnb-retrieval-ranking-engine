from retrieval.parser import parse_query


def test_parse_query_apartment_sydney():
    parsed = parse_query("cheap apartment for two in Sydney with good reviews")

    assert parsed.wants_cheap is True
    assert parsed.accommodates == 2
    assert parsed.neighbourhood == "Sydney"
    assert parsed.property_type == "Apartment"
    assert parsed.wants_good_reviews is True


def test_parse_query_bondi_alias():
    parsed = parse_query("private room near Bondi beach")

    assert parsed.room_type == "Private room"
    assert parsed.neighbourhood == "Waverley"


def test_parse_query_manly_entire_home():
    parsed = parse_query("entire home in Manly with wifi")

    assert parsed.room_type == "Entire home/apt"
    assert parsed.neighbourhood == "Manly"


def test_parse_query_flexible_cancellation():
    parsed = parse_query("private room in Waverley with flexible cancellation")

    assert parsed.room_type == "Private room"
    assert parsed.neighbourhood == "Waverley"
    assert parsed.wants_flexible_cancellation is True


def test_parse_query_instant_bookable():
    parsed = parse_query("cheap apartment in Sydney that is instant bookable")

    assert parsed.property_type == "Apartment"
    assert parsed.neighbourhood == "Sydney"
    assert parsed.wants_cheap is True
    assert parsed.wants_instant_bookable is True