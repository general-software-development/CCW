def title() -> str:
    return "Bad Initialisation"

def identifier() -> int:
    return 1

def description() -> tuple[str]:
    return (
        "Used when variable or data are initialised before being used, but are not initialised properly.",
        "For example: if you have an array of 1024 items to initialise, but due to faulty logic, only the first 1023 items are initialised, or if you initialise everything to zeros while the rest of the code expects ones."
    )
