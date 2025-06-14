def Stringformat(text, *args, **kwargs):
    if not isinstance(text, str):
        return text

    result = text
    if args:
        for i, arg in enumerate(args):
            if arg is not None:
                try:
                    pattern = f"{{{i}}}"
                    result = result.replace(pattern, str(arg))
                except Exception:
                    continue
    elif kwargs:
        for key, value in kwargs.items():
            if value is not None:
                try:
                    pattern = f"{{{key}}}"
                    result = result.replace(pattern, str(value))
                except Exception:
                    continue
    return result
