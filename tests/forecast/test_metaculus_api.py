



mark = .mark.skipif(
    not .getenv("METACULUS_API_KEY"),
    reason="Metaculus API key not set; skipping live API tests.",
)

 MetaculusForecastSource


print_schema(name, obj):
    if obj is None:
        print(f"{name}: None (endpoint unavailable or error)")
    elif isinstance(obj, list):
        print(f"{name}: list of length {len(obj)}")
        if obj:
            first = obj[0]
            if isinstance(first, dict):
                print(f"  First item keys: {list(first.keys())}")
            else:
                print(f"  First item type: {type(first)}; attributes: {dir(first)}")
    elif isinstance(obj, dict):
        print(f"{name}: dict with keys {list(obj.keys())}")
    else:
        print(f"{name}: {type(obj)}")


test_list_questions():
    src = MetaculusForecastSource.from_env()
    questions = src.list_questions()
    print_schema("questions", questions)
    assert isinstance(questions, list) and len(questions) > 0


test_list_users():
    src = MetaculusForecastSource.from_env()
    users = src.list_users()
    print_schema("users", users)
    assert users is None or isinstance(users, (list, dict))


test_list_predictions():
    src = MetaculusForecastSource.from_env()
    preds = src.list_predictions()
    print_schema("predictions", preds)
    assert preds is None or isinstance(preds, (list, dict))





test_list_series():
    src = MetaculusForecastSource.from_env()
    series = src.list_series()
    print_schema("series", series)
    assert series is None or isinstance(series, (list, dict))


test_list_groups():
    src = MetaculusForecastSource.from_env()
    groups = src.list_groups()
    print_schema("groups", groups)
    assert groups is None or isinstance(groups, (list, dict))
