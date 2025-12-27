from fastapi import HTTPException, status


class EntityAlreadyExists(HTTPException):
    def __init__(self, entity_name: str = "Entity"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="{} already exists".format(entity_name).capitalize(),
        )


class EntityNotFound(HTTPException):
    def __init__(self, entity_name: str = "Entity"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{} not found".format(entity_name).capitalize(),
        )


class NotEnoughPrivileges(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges"
        )
