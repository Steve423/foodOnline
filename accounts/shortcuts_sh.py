def get_object_or_none(klass, *args, **kwargs):
    """
    9-29-2023 code came from https://stackoverflow.com/questions/3090302/how-do-i-get-the-object-if-it-exists-or-none-if-it-does-not-exist-in-django
    
    Use get() to return an object, or returns None if the object
    does not exist instead of throwing an exception.
    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.
    Like with QuerySet.get(), MultipleObjectsReturned is raised if more than
    one object is found.
    """
    queryset =  klass._default_manager.all() if hasattr(klass, "_default_manager") else klass
    if not hasattr(queryset, "get"):
        klass__name = (
            klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        )
        raise ValueError(
            "First argument to get_object_or_none() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None