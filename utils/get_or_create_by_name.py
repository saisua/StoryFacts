def get_or_create_by_name(session, model: type, name: str, **kwargs) -> int:
    name = name.lower()
    obj = session.query(model)\
        .filter(model.name == name)\
        .first()
    if not obj:
        obj = model(name=name, **kwargs)
        session.add(obj)
        session.flush()
    return obj.id
